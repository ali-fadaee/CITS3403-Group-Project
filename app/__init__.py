from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from app.extensions import db, migrate
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.models import Comment, CommentSide, Debate, User, Vote

    def get_active_user():
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)
            if user:
                return user

        user = User.query.filter_by(username='user_dev').first()
        if user:
            return user

        user = User(username='user_dev', email='user_dev@example.com')
        user.set_password('dev-placeholder')
        db.session.add(user)
        db.session.commit()
        return user

    def parse_parent_id(value):
        if value in (None, '', 'root'):
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            abort(400, description='Invalid parent_id')

    def serialize_comment(comment, liked_ids=None):
        liked_ids = liked_ids or set()
        return {
            'id': comment.id,
            'side': comment.side.value,
            'author': comment.user.username if comment.user else 'unknown',
            'text': comment.content,
            'votes': comment.upvote_count,
            'liked': comment.id in liked_ids,
            'created_at': comment.created_at.isoformat() if comment.created_at else None,
        }

    def load_thread_comments(debate_id, parent_id):
        query = Comment.query.options(selectinload(Comment.user)).filter_by(debate_id=debate_id)

        if parent_id is None:
            query = query.filter(Comment.parent_id.is_(None))
        else:
            query = query.filter(Comment.parent_id == parent_id)

        return query.order_by(Comment.upvote_count.desc(), Comment.created_at.desc()).all()

    @app.route('/')
    def index():
        filter = request.args.get('filter', 'new')
        page = max(1, request.args.get('page', 1, type=int))
        per_page = 10

        query = Debate.query.options(selectinload(Debate.tags))
        if filter in ('popular', 'top'):
            query = query.order_by(Debate.comment_count.desc(), Debate.created_at.desc())
        else:
            query = query.order_by(Debate.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        return render_template('index.html', debates=pagination.items, filter=filter,
                               page=pagination.page, total_pages=pagination.pages or 1)

    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/signup')
    def signup():
        return render_template('signup.html')
    
    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    @app.route('/create')
    def create():
        return render_template('create.html')

    @app.route('/debate')
    def debate():
        first_debate = Debate.query.order_by(Debate.created_at.desc()).first()
        if not first_debate:
            abort(404)

        return redirect(url_for('debate_detail', debate_id=first_debate.id))

    @app.route('/debates/<int:debate_id>')
    def debate_detail(debate_id):
        debate = db.session.get(Debate, debate_id)
        if not debate:
            abort(404)

        return render_template('debate.html', debate=debate)

    @app.get('/api/debates/<int:debate_id>/thread')
    def debate_thread(debate_id):
        debate = db.session.get(Debate, debate_id)
        if not debate:
            abort(404)

        parent_id = parse_parent_id(request.args.get('parent_id', 'root'))
        parent_comment = None

        if parent_id is not None:
            parent_comment = Comment.query.filter_by(id=parent_id, debate_id=debate.id).first()
            if not parent_comment:
                abort(404)

        comments = load_thread_comments(debate.id, parent_id)
        active_user = get_active_user()
        comment_ids = [comment.id for comment in comments]

        liked_ids = set()
        if comment_ids:
            liked_ids = {
                row[0]
                for row in db.session.query(Vote.comment_id)
                .filter(Vote.user_id == active_user.id, Vote.comment_id.in_(comment_ids))
                .all()
            }

        yes_comments = [
            serialize_comment(comment, liked_ids)
            for comment in comments
            if comment.side == CommentSide.yes
        ]
        no_comments = [
            serialize_comment(comment, liked_ids)
            for comment in comments
            if comment.side == CommentSide.no
        ]

        return jsonify({
            'debate': {
                'id': debate.id,
                'title': debate.title,
                'description': debate.description,
                'yes_count': debate.yes_count,
                'no_count': debate.no_count,
                'comment_count': debate.comment_count,
            },
            'thread': {
                'parent_id': parent_id,
                'topic': parent_comment.content if parent_comment else debate.title,
                'yes_comments': yes_comments,
                'no_comments': no_comments,
            },
            'user': {
                'id': active_user.id,
                'username': active_user.username,
                'is_dev_fallback': 'user_id' not in session,
            },
        })

    @app.post('/api/debates/<int:debate_id>/comments')
    def create_comment(debate_id):
        debate = db.session.get(Debate, debate_id)
        if not debate:
            abort(404)

        data = request.get_json(silent=True) or request.form
        content = (data.get('content') or '').strip()
        side = (data.get('side') or '').strip().lower()
        parent_id = parse_parent_id(data.get('parent_id'))

        if side not in ('yes', 'no'):
            abort(400, description='Comment side must be yes or no')

        if not content:
            abort(400, description='Comment content is required')

        if len(content) > 2000:
            abort(400, description='Comment content is too long')

        if parent_id is not None:
            parent_comment = Comment.query.filter_by(id=parent_id, debate_id=debate.id).first()
            if not parent_comment:
                abort(404)

        active_user = get_active_user()
        comment = Comment(
            debate_id=debate.id,
            parent_id=parent_id,
            user_id=active_user.id,
            content=content,
            side=CommentSide(side),
        )

        db.session.add(comment)
        db.session.commit()

        return jsonify({
            'comment': serialize_comment(comment),
            'debate': {
                'yes_count': debate.yes_count,
                'no_count': debate.no_count,
                'comment_count': debate.comment_count,
            },
        }), 201

    @app.post('/api/comments/<int:comment_id>/vote')
    def toggle_comment_vote(comment_id):
        comment = Comment.query.options(selectinload(Comment.user)).filter_by(id=comment_id).first()
        if not comment:
            abort(404)

        active_user = get_active_user()
        vote = Vote.query.filter_by(comment_id=comment.id, user_id=active_user.id).first()

        if vote:
            db.session.delete(vote)
            liked = False
        else:
            db.session.add(Vote(comment_id=comment.id, user_id=active_user.id))
            liked = True

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            liked = True

        db.session.refresh(comment)

        return jsonify({
            'comment_id': comment.id,
            'liked': liked,
            'upvote_count': comment.upvote_count,
        })

    return app
