from flask import Flask, render_template, request, flash, redirect, url_for
from app.forms import LoginForm, SignupForm


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    @app.route('/')
    def index():
        debates = [
            {'title': 'Is AI a threat to employment?', 'tags': ['Technology', 'Science'], 'yes_count': 3, 'no_count': 1, 'created': '28 Mar 2026', 'last_activity': '30 Mar 2026'},
            {'title': 'Should social media be regulated?', 'tags': ['Politics', 'Technology'], 'yes_count': 2, 'no_count': 8, 'created': '25 Mar 2026', 'last_activity': '29 Mar 2026'},
            {'title': 'Am I a horrible person for cheating on my wife?', 'tags': ['Lifestyle', 'Relationships'], 'yes_count': 10, 'no_count': 2, 'created': '20 Mar 2026', 'last_activity': '30 Mar 2026'},
        ]
        filter = request.args.get('filter', 'new')
        return render_template('index.html', debates=debates, filter=filter)

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