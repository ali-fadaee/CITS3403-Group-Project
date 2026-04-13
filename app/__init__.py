from flask import Flask, render_template, request


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        debates = [
            {'title': 'Is AI a threat to employment?', 'tags': ['Technology', 'Science'], 'yes_count': 3, 'no_count': 1, 'created': '28 Mar 2026', 'last_activity': '30 Mar 2026'},
            {'title': 'Should social media be regulated?', 'tags': ['Politics', 'Technology'], 'yes_count': 2, 'no_count': 8, 'created': '25 Mar 2026', 'last_activity': '29 Mar 2026'},
            {'title': 'Am I a horrible person for cheating on my wife?', 'tags': ['Lifestyle', 'Relationships'], 'yes_count': 10, 'no_count': 2, 'created': '20 Mar 2026', 'last_activity': '30 Mar 2026'},
        ]
        filter = request.args.get('filter', 'new')
        return render_template('index.html', debates=debates, filter=filter)

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