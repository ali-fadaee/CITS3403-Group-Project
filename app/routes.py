
from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models import Debate, Comment, User, Tag, debate_tags, user_tags
from app.forms import LoginForm, SignupForm
from flask_login import login_user, logout_user, login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    filter = request.args.get('filter', 'new')
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 10

    query = Debate.query.options(selectinload(Debate.tags))

    if filter == 'popular':
        query = query.order_by(Debate.comment_count.desc(), Debate.created_at.desc())
    elif filter == 'top':
        query = query.order_by((Debate.yes_count + Debate.no_count).desc(), Debate.created_at.desc())
    elif filter == 'for-you':
        user_id = session.get('user_id')
        if user_id:
            match_count = (
                db.session.query(func.count())
                .select_from(debate_tags)
                .join(user_tags, debate_tags.c.tag_id == user_tags.c.tag_id)
                .filter(user_tags.c.user_id == user_id)
                .filter(debate_tags.c.debate_id == Debate.id)
                .correlate(Debate)
                .scalar_subquery()
            )
            query = query.order_by(match_count.desc(), Debate.created_at.desc())
        else:
            query = query.order_by(Debate.created_at.desc())
    else:
        query = query.order_by(Debate.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', debates=pagination.items, filter=filter,
                           page=pagination.page, total_pages=pagination.pages or 1)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.email == form.usernameEmail.data) | (User.username == form.usernameEmail.data)
        ).first()

        if not user or not user.check_password(form.password.data):
            return render_template("login.html", form=form, login_error="Invalid username/email or password.")

        login_user(user, remember=form.remember.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', form=form)


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    interests_options = [
        'Sports','Music', 'Technology', 'Art', 'Science', 'Philosophy',
        'Environment', 'Economics', 'Education', 'Ethics', 'Health', 'Lifestyle'
    ]
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, 
                    email=form.email.data,
        )

        user.set_password(form.password.data)
        interests = request.form.getlist('interests[]')
        tags = []
        for interest in interests:
            tag = Tag.query.filter_by(name=interest).first()
            if not tag:
                tag = Tag(name=interest)
                db.session.add(tag)
            tags.append(tag)
        user.interests = tags
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('main.login'))
    return render_template('signup.html', form=form, interests=interests_options)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/api/account/delete', methods=['POST'])
@login_required
def api_delete_account():
    user = User.query.get(current_user.id)
    logout_user()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'ok': True}), 200

@main.route('/profile')
def profile():
    return render_template('profile.html')


@main.route('/create')
def create():
    return render_template('create.html')


@main.route('/debate/<int:debate_id>')
def debate(debate_id):
    return render_template('debate.html')


@main.route('/debates/mine')
def my_activity():
    tab = request.args.get('tab', 'debates')
    page = max(1, request.args.get('page', 1, type=int))
    per_page = 10

    user_id = session.get('user_id')
    if not user_id:
        return render_template('my_activity.html', tab=tab, items=[], total_pages=1, page=1)

    if tab == 'arguments':
        pagination = (Comment.query
                      .options(selectinload(Comment.debate))
                      .filter_by(user_id=user_id)
                      .order_by(Comment.created_at.desc())
                      .paginate(page=page, per_page=per_page, error_out=False))
    else:
        pagination = (Debate.query
                      .options(selectinload(Debate.tags))
                      .filter_by(creator_id=user_id)
                      .order_by(Debate.created_at.desc())
                      .paginate(page=page, per_page=per_page, error_out=False))

    return render_template('my_activity.html', tab=tab, items=pagination.items,
                           page=pagination.page, total_pages=pagination.pages or 1)


@main.route('/api/debates', methods=['POST'])
def api_create_debate():
    data     = request.get_json()
    title    = (data.get('title') or '').strip()
    category = (data.get('category') or 'Technology').strip()

    if not title:
        return jsonify({'error': 'title is required'}), 400

    user_id = current_user.id

    tag = Tag.query.filter_by(name=category).first()
    if not tag:
        tag = Tag(name=category)
        db.session.add(tag)

    debate = Debate(title=title, creator_id=user_id)
    debate.tags.append(tag)
    db.session.add(debate)
    db.session.commit()

    return jsonify({'id': debate.id}), 201


@main.route('/api/profile', methods=['POST'])
def api_save_profile():
    if not current_user.is_authenticated:
        return jsonify({'error': 'not logged in'}), 401
    user = current_user

    data = request.get_json()
    if data.get('password'):
        if not user.check_password(data.get('current_password', '')):
            return jsonify({'error': 'current password is incorrect'}), 400
        user.set_password(data['password'])
    if data.get('avatar_id'):
        user.avatar_id = data['avatar_id']
    if 'interests' in data:
        tags = []
        for name in data['interests']:
            tag = Tag.query.filter(db.func.lower(Tag.name) == name.lower()).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            tags.append(tag)
        user.interests = tags

    db.session.commit()
    return jsonify({'ok': True}), 200


@main.route('/api/avatars', methods=['GET'])
def api_avatars():
    from app.models import Avatar
    avatars = Avatar.query.all()
    return jsonify([{'id': a.id, 'name': a.name, 'url': a.image_url} for a in avatars])