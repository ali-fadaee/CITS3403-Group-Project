import os
from flask import Flask, render_template, request
from sqlalchemy.orm import selectinload
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')

    db.init_app(app)

    with app.app_context():
        from app import models
        db.create_all()

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

    return app