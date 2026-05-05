from flask import Flask, render_template, request, flash, redirect, url_for
from app.forms import LoginForm, SignupForm
from sqlalchemy.orm import selectinload
from app.extensions import db, migrate
from app.config import Config
from flask_login import login_user


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.models import Debate, User, Tag

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

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter(
                (User.email == form.usernameEmail.data) | (User.username == form.usernameEmail.data)
            ).first()

            if not user or not user.check_password(form.password.data):
                return render_template("login.html", form=form, login_error="Invalid username/email or password.")

            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        return render_template('login.html', form=form)
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        interests_options = [
            'Sports',
            'Music',
            'Technology',
            'Art',
            'Science',
            'Philosophy',
            'Environment',
            'Economics',
            'Education',
            'Ethics',
            'Health',
            'Lifestyle'
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
            return redirect(url_for('login'))
        return render_template('signup.html', form=form, interests=interests_options)
    
    @app.route('/profile')
    def profile():
        return render_template('profile.html')
    
    @app.route('/create')
    def create():
        return render_template('create.html')

    @app.route('/debate')
    def debate():
        return render_template('debate.html')

    return app