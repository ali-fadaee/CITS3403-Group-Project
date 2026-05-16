import re
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from sqlalchemy import func, cast, Float
from sqlalchemy.orm import selectinload
from urllib.parse import urlparse
from app.extensions import db, limiter
from app.models import Avatar, Comment, CommentSide, Debate, Tag, User, Vote, debate_tags, saved_debates as saved_debates_table, user_tags
from app.forms import LoginForm, SignupForm
from flask_login import login_user, logout_user, login_required, current_user
from app.email import verify_token, send_verification_email

main = Blueprint('main', __name__)
MAX_COMMENT_LENGTH = 1000


def _json_auth_required():
    if current_user.is_authenticated:
        return None
    return jsonify({'error': 'login required'}), 401


def _parse_parent_id(raw_parent_id):
    if raw_parent_id in (None, '', 'root'):
        return None, None

    try:
        return int(raw_parent_id), None
    except (TypeError, ValueError):
        return None, 'parent_id must be root or an integer'


def _comment_to_dict(comment, liked_comment_ids=None):
    liked_comment_ids = liked_comment_ids or set()
    return {
        'id': comment.id,
        'debate_id': comment.debate_id,
        'parent_id': comment.parent_id,
        'side': comment.side.value,
        'content': comment.content,
        'author': comment.user.username if comment.user else 'unknown',
        'user_id': comment.user_id,
        'upvote_count': comment.upvote_count,
        'liked': comment.id in liked_comment_ids,
        'created_at': comment.created_at.isoformat() if comment.created_at else None,
    }


def _liked_comment_ids(comments):
    if not current_user.is_authenticated or not comments:
        return set()

    comment_ids = [comment.id for comment in comments]
    rows = (db.session.query(Vote.comment_id)
            .filter(Vote.user_id == current_user.id, Vote.comment_id.in_(comment_ids))
            .all())
    return {comment_id for (comment_id,) in rows}


@main.route('/')
def index():
    default_filter = 'for-you' if current_user.is_authenticated else 'popular'
    filter = request.args.get('filter', default_filter)
    tag_filter = request.args.get('tag', '').strip() or None
    page = max(1, request.args.get('page', 1, type=int))
    per_page = request.args.get('per_page', 10, type=int)
    if per_page not in (10, 25, 50, 100):
        per_page = 10

    query = Debate.query.options(selectinload(Debate.tags), selectinload(Debate.creator).selectinload(User.avatar))
    if tag_filter:
        query = query.filter(Debate.tags.any(func.lower(Tag.name) == tag_filter.lower()))

    if filter == 'popular':
        age_hours = (func.julianday('now') - func.julianday(Debate.updated_at)) * 24.0
        activity = Debate.comment_count + Debate.yes_count + Debate.no_count
        popularity_score = cast(activity, Float) / (age_hours + 2)
        query = query.order_by(popularity_score.desc())
    elif filter == 'top':
        top_score = (3 * Debate.comment_count) + (Debate.yes_count + Debate.no_count)
        query = query.order_by(top_score.desc(), Debate.created_at.desc())
    elif filter == 'for-you':
        age_hours = (func.julianday('now') - func.julianday(Debate.updated_at)) * 24.0
        activity = Debate.comment_count + Debate.yes_count + Debate.no_count
        popularity_score = cast(activity, Float) / (age_hours + 2)
        if current_user.is_authenticated and current_user.interests:
            user_id = current_user.id
            match_count = (
                db.session.query(func.count())
                .select_from(debate_tags)
                .join(user_tags, debate_tags.c.tag_id == user_tags.c.tag_id)
                .filter(user_tags.c.user_id == user_id)
                .filter(debate_tags.c.debate_id == Debate.id)
                .correlate(Debate)
                .scalar_subquery()
            )
            query = query.filter(match_count > 0).order_by(popularity_score.desc())
        else:
            query = query.order_by(popularity_score.desc())
    else:
        query = query.order_by(Debate.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    saved_ids = set()
    if current_user.is_authenticated:
        page_ids = [d.id for d in pagination.items]
        if page_ids:
            rows = db.session.execute(
                db.select(saved_debates_table.c.debate_id)
                .where(saved_debates_table.c.user_id == current_user.id)
                .where(saved_debates_table.c.debate_id.in_(page_ids))
            ).all()
            saved_ids = {row[0] for row in rows}
    all_tags = Tag.query.order_by(Tag.name).all()
    return render_template('index.html', debates=pagination.items, filter=filter,
                           tag_filter=tag_filter, all_tags=all_tags,
                           page=pagination.page, total_pages=pagination.pages or 1,
                           per_page=per_page, saved_ids=saved_ids)


@main.route('/verify/<token>')
def verify_email(token):
    email = verify_token(token)
    if not email:
        flash("Verification link is invalid or has expired.")
        return redirect(url_for('main.signup'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash("No account found for this verification link.")
    elif user.email_verified:
        flash("Email is already verified.")
    else:
        user.email_verified = True
        db.session.commit()
        flash("Email verified successfully. You can now log in.")
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.usernameEmail.data
        user = User.query.filter(
            (User.email == identifier.lower()) | (func.lower(User.username) == identifier.lower())
        ).first()

        if not user or not user.check_password(form.password.data):
            return render_template("login.html", form=form, login_error="Invalid username/email or password.")
        
        if not user.email_verified:
            return render_template("login.html", form=form, login_error="Please verify your email before logging in.")

        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if next_page and urlparse(next_page).netloc == '':
            return redirect(next_page)
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)


@main.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    interests_options = [
        'Sports','Music', 'Technology', 'Art', 'Science', 'Philosophy',
        'Environment', 'Economics', 'Education', 'Ethics', 'Health', 'Lifestyle'
    ]
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data.lower(),
        )

        user.set_password(form.password.data)
        interests = [i for i in request.form.getlist('interests[]') if i in interests_options]
        tags = []
        for interest in interests:
            tag = Tag.query.filter_by(name=interest).first()
            if not tag:
                tag = Tag(name=interest)
                db.session.add(tag)
            tags.append(tag)
        user.interests = tags
        db.session.add(user)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            return render_template('signup.html', form=form, interests=interests_options,
                                   signup_error='Could not create account. Please try again.')
        try:
            send_verification_email(user)
        except Exception:
            pass
        flash('Account created. Please check your email to verify your account before logging in.')
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form, interests=interests_options)


@main.route('/api/check-email')
@limiter.limit("10 per minute")
def api_check_email():
    email = request.args.get('email', '').strip().lower()
    if not email:
        return jsonify({'available': False})
    taken = User.query.filter_by(email=email).first() is not None
    return jsonify({'available': not taken})


@main.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/api/account/delete', methods=['POST'])
@login_required
def api_delete_account():
    user = db.session.get(User, current_user.id)
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return jsonify({'ok': True}), 200

@main.route('/profile')
@login_required
def profile():
    return redirect(url_for('main.index'))


@main.route('/create')
@login_required
def create():
    return redirect(url_for('main.index'))


@main.route('/debate')
def debate_redirect():
    debate = Debate.query.order_by(Debate.created_at.desc()).first()
    if not debate:
        return redirect(url_for('main.index'))
    return redirect(url_for('main.debate', debate_id=debate.id))


@main.route('/debate/<int:debate_id>')
def debate(debate_id):
    debate = db.get_or_404(Debate, debate_id)
    return render_template('debate.html', debate=debate)


@main.route('/api/debates/<int:debate_id>/thread')
def api_debate_thread(debate_id):
    debate = db.get_or_404(Debate, debate_id)
    parent_id, error = _parse_parent_id(request.args.get('parent_id', 'root'))
    if error:
        return jsonify({'error': error}), 400

    parent = None
    if parent_id is not None:
        parent = (Comment.query
                  .options(selectinload(Comment.user))
                  .filter_by(id=parent_id, debate_id=debate.id)
                  .first_or_404())

    query = (Comment.query
             .options(selectinload(Comment.user))
             .filter_by(debate_id=debate.id))

    if parent is None:
        query = query.filter(Comment.parent_id.is_(None))
        topic = {
            'id': 'root',
            'text': debate.title,
            'side': None,
            'parent_id': None,
        }
    else:
        query = query.filter(Comment.parent_id == parent.id)
        topic = {
            'id': parent.id,
            'text': parent.content,
            'side': parent.side.value,
            'parent_id': parent.parent_id,
            'author': parent.user.username if parent.user else 'unknown',
        }

    comments = query.order_by(Comment.upvote_count.desc(), Comment.created_at.asc()).all()
    liked_ids = _liked_comment_ids(comments)
    yes_comments = [comment for comment in comments if comment.side == CommentSide.yes]
    no_comments = [comment for comment in comments if comment.side == CommentSide.no]

    return jsonify({
        'debate': {
            'id': debate.id,
            'title': debate.title,
            'yes_count': debate.yes_count,
            'no_count': debate.no_count,
            'comment_count': debate.comment_count,
        },
        'topic': topic,
        'comments': {
            'yes': [_comment_to_dict(comment, liked_ids) for comment in yes_comments],
            'no': [_comment_to_dict(comment, liked_ids) for comment in no_comments],
        },
    })


@main.route('/api/debates/<int:debate_id>/comments', methods=['POST'])
@limiter.limit("30 per minute")
def api_create_comment(debate_id):
    auth_error = _json_auth_required()
    if auth_error:
        return auth_error

    debate = db.get_or_404(Debate, debate_id)
    data = request.get_json(silent=True) or {}
    content = (data.get('content') or '').strip()
    side_value = (data.get('side') or '').strip().lower()
    parent_id, error = _parse_parent_id(data.get('parent_id'))

    if error:
        return jsonify({'error': error}), 400

    if not content:
        return jsonify({'error': 'content is required'}), 400

    if len(content) > MAX_COMMENT_LENGTH:
        return jsonify({'error': f'content must be {MAX_COMMENT_LENGTH} characters or fewer'}), 400

    try:
        side = CommentSide(side_value)
    except ValueError:
        return jsonify({'error': 'side must be yes or no'}), 400

    if parent_id is not None:
        parent_exists = Comment.query.filter_by(id=parent_id, debate_id=debate.id).first()
        if not parent_exists:
            return jsonify({'error': 'parent comment not found'}), 404

    comment = Comment(
        debate_id=debate.id,
        parent_id=parent_id,
        user_id=current_user.id,
        content=content,
        side=side,
    )
    db.session.add(comment)
    db.session.commit()

    comment = (Comment.query
               .options(selectinload(Comment.user))
               .filter_by(id=comment.id)
               .one())
    return jsonify({'comment': _comment_to_dict(comment)}), 201


@main.route('/api/comments/<int:comment_id>/vote', methods=['POST'])
@limiter.limit("60 per minute")
def api_toggle_comment_vote(comment_id):
    auth_error = _json_auth_required()
    if auth_error:
        return auth_error

    comment = db.get_or_404(Comment, comment_id)
    existing_vote = Vote.query.filter_by(comment_id=comment.id, user_id=current_user.id).first()

    if existing_vote:
        db.session.delete(existing_vote)
        liked = False
    else:
        db.session.add(Vote(comment_id=comment.id, user_id=current_user.id))
        liked = True

    db.session.commit()
    db.session.refresh(comment)

    return jsonify({
        'comment_id': comment.id,
        'liked': liked,
        'upvote_count': comment.upvote_count,
    })


@main.route('/debates/mine')
@login_required
def my_activity():
    tab = request.args.get('tab', 'debates')
    page = max(1, request.args.get('page', 1, type=int))
    per_page = request.args.get('per_page', 10, type=int)
    if per_page not in (10, 25, 50, 100):
        per_page = 10

    user_id = current_user.id

    if tab == 'arguments':
        pagination = (Comment.query
                      .options(selectinload(Comment.debate).selectinload(Debate.tags))
                      .filter_by(user_id=user_id)
                      .order_by(Comment.created_at.desc())
                      .paginate(page=page, per_page=per_page, error_out=False))
    elif tab == 'saved':
        pagination = (Debate.query
                      .options(selectinload(Debate.tags), selectinload(Debate.creator).selectinload(User.avatar))
                      .filter(Debate.saved_by.any(User.id == user_id))
                      .order_by(Debate.updated_at.desc())
                      .paginate(page=page, per_page=per_page, error_out=False))
    else:
        pagination = (Debate.query
                      .options(selectinload(Debate.tags), selectinload(Debate.creator).selectinload(User.avatar))
                      .filter_by(creator_id=user_id)
                      .order_by(Debate.created_at.desc())
                      .paginate(page=page, per_page=per_page, error_out=False))

    return render_template('my_activity.html', tab=tab, items=pagination.items,
                           page=pagination.page, total_pages=pagination.pages or 1, per_page=per_page)


@main.route('/api/debates', methods=['POST'])
@limiter.limit("10 per minute")
def api_create_debate():
    auth_error = _json_auth_required()
    if auth_error:
        return auth_error

    data       = request.get_json() or {}
    title      = (data.get('title') or '').strip()
    categories = data.get('categories') or []
    if isinstance(categories, str):
        categories = [categories]
    categories = [c.strip() for c in categories if isinstance(c, str) and c.strip()]

    if not title:
        return jsonify({'error': 'title is required'}), 400
    if len(title) > 400:
        return jsonify({'error': 'title must be 400 characters or fewer'}), 400
    if not categories:
        return jsonify({'error': 'at least one category is required'}), 400
    if len(categories) > 10:
        return jsonify({'error': 'no more than 10 categories allowed'}), 400

    tags = Tag.query.filter(Tag.name.in_(categories)).all()
    missing = set(categories) - {t.name for t in tags}
    if missing:
        return jsonify({'error': f'invalid category: {", ".join(sorted(missing))}'}), 400

    debate = Debate(title=title, creator_id=current_user.id)
    debate.tags = tags
    db.session.add(debate)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'could not create debate'}), 500

    return jsonify({'id': debate.id}), 201


@main.route('/api/profile', methods=['POST'])
@limiter.limit("10 per minute")
def api_save_profile():
    guard = _json_auth_required()
    if guard:
        return guard
    user = current_user

    data = request.get_json() or {}
    password_changed = False

    if data.get('password'):
        if not user.check_password(data.get('current_password', '')):
            return jsonify({'error': '// current password is incorrect'}), 400
        new_pw = data['password']
        if len(new_pw) < 8 or not re.search(r'[a-z]', new_pw) or not re.search(r'[A-Z]', new_pw) or not re.search(r'\d', new_pw):
            return jsonify({'error': '// password must be 8+ chars with uppercase, lowercase, and a number'}), 400
        user.set_password(new_pw)
        user.rotate_session_token()
        password_changed = True

    if data.get('avatar_id'):
        avatar = db.session.get(Avatar, data['avatar_id'])
        if not avatar:
            return jsonify({'error': '// invalid avatar'}), 400
        user.avatar_id = avatar.id

    if 'bio' in data:
        if len(data['bio']) > 1000:
            return jsonify({'error': 'bio must be 1000 characters or less'}), 400
        user.bio = data['bio']

    if 'interests' in data:
        if not isinstance(data['interests'], list):
            return jsonify({'error': 'interests must be a list'}), 400
        tags = []
        for name in data['interests']:
            if not isinstance(name, str):
                continue
            tag = Tag.query.filter(db.func.lower(Tag.name) == name.lower()).first()
            if tag:
                tags.append(tag)
        user.interests = tags

    db.session.commit()

    if password_changed:
        login_user(user)

    return jsonify({'ok': True}), 200


@main.route('/api/avatars', methods=['GET'])
def api_avatars():
    avatars = Avatar.query.order_by(Avatar.name).all()
    return jsonify([{'id': a.id, 'name': a.name, 'url': a.image_url} for a in avatars])


@main.route('/api/tags', methods=['GET'])
def api_tags():
    tags = Tag.query.order_by(Tag.name).all()
    return jsonify([t.name for t in tags])


@main.route('/api/users/<username>', methods=['GET'])
def api_user_profile(username):
    user = User.query.filter(func.lower(User.username) == username.lower()).first_or_404()
    return jsonify({
        'username': user.username,
        'avatar': user.avatar.image_url if user.avatar else '/static/images/avatars/robot.svg',
        'bio': user.bio or '',
        'interests': [t.name for t in user.interests],
        'joined': user.created_at.strftime('%b %Y'),
    })


@main.route('/api/debates/<int:debate_id>/save', methods=['POST'])
@limiter.limit("30 per minute")
def api_save_debate(debate_id):
    guard = _json_auth_required()
    if guard:
        return guard
    debate = db.session.get(Debate, debate_id)
    if not debate:
        return jsonify({'error': 'not found'}), 404
    if debate not in current_user.saved:
        current_user.saved.append(debate)
        db.session.commit()
    return jsonify({'saved': True})


@main.route('/api/debates/<int:debate_id>/unsave', methods=['POST'])
@limiter.limit("30 per minute")
def api_unsave_debate(debate_id):
    guard = _json_auth_required()
    if guard:
        return guard
    debate = db.session.get(Debate, debate_id)
    if not debate:
        return jsonify({'error': 'not found'}), 404
    if debate in current_user.saved:
        current_user.saved.remove(debate)
        db.session.commit()
    return jsonify({'saved': False})
