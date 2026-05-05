from flask import Flask, render_template, request, jsonify
from sqlalchemy.orm import selectinload
from app.extensions import db, migrate
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.models import Debate, Tag, DebateStatus

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
        return render_template('debate.html')
    
    
    @app.route('/api/debates', methods=['POST'])
    def create_debate():
        data = request.get_json()

        title = data.get('title', '').strip()
        category = data.get('category', '').strip()

        if not title:
            return jsonify({'error': 'title is required'}), 400

        tag = Tag.query.filter_by(name=category).first()
        if not tag:
            tag = Tag(name=category)
            db.session.add(tag)

        debate = Debate(
            title=title,
            creator_id=1,
            status=DebateStatus.open
        )
        debate.tags.append(tag)
        db.session.add(debate)
        db.session.commit()

        return jsonify({'id': debate.id}), 201

    return app