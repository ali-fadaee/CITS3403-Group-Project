from flask import Flask, render_template, request, flash, redirect, url_for
from app.forms import LoginForm, SignupForm
from sqlalchemy.orm import selectinload
from app.extensions import db, migrate
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models

    from app.models import Debate

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
            flash('Login successful')
            return redirect(url_for('index'))
        return render_template('login.html', form=form)
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        form = SignupForm()
        if form.validate_on_submit():
            interests = request.form.getlist('interests[]')
            flash('Account created successfully')
            return redirect(url_for('login'))
        return render_template('signup.html', form=form)
    
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