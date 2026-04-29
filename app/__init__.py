from flask import Flask, render_template, request


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        debates = [
            {'title': 'Is AI a threat to employment?', 'tags': ['Technology', 'Science'], 'yes_count': 3, 'no_count': 1, 'created': '28 Mar 2026', 'last_activity': '30 Mar 2026'},
            {'title': 'Should social media be regulated?', 'tags': ['Politics', 'Technology'], 'yes_count': 2, 'no_count': 8, 'created': '25 Mar 2026', 'last_activity': '29 Mar 2026'},
            {'title': 'Am I a horrible person for cheating on my wife?', 'tags': ['Lifestyle', 'Relationships'], 'yes_count': 10, 'no_count': 2, 'created': '20 Mar 2026', 'last_activity': '30 Mar 2026'},
            {'title': 'Should university education be free?', 'tags': ['Education', 'Economics'], 'yes_count': 7, 'no_count': 4, 'created': '18 Mar 2026', 'last_activity': '28 Mar 2026'},
            {'title': 'Is remote work better than office work?', 'tags': ['Technology', 'Lifestyle'], 'yes_count': 5, 'no_count': 6, 'created': '15 Mar 2026', 'last_activity': '27 Mar 2026'},
            {'title': 'Should voting be mandatory?', 'tags': ['Politics', 'Ethics'], 'yes_count': 4, 'no_count': 9, 'created': '12 Mar 2026', 'last_activity': '26 Mar 2026'},
            {'title': 'Is space exploration worth the cost?', 'tags': ['Science', 'Economics'], 'yes_count': 8, 'no_count': 3, 'created': '10 Mar 2026', 'last_activity': '25 Mar 2026'},
            {'title': 'Should junk food be taxed?', 'tags': ['Ethics', 'Politics'], 'yes_count': 6, 'no_count': 5, 'created': '8 Mar 2026', 'last_activity': '24 Mar 2026'},
            {'title': 'Is philosophy still relevant in the modern world?', 'tags': ['Philosophy', 'Education'], 'yes_count': 9, 'no_count': 2, 'created': '5 Mar 2026', 'last_activity': '22 Mar 2026'},
            {'title': 'Should there be a global minimum wage?', 'tags': ['Economics', 'Politics'], 'yes_count': 3, 'no_count': 7, 'created': '2 Mar 2026', 'last_activity': '20 Mar 2026'},
            {'title': 'Is cancel culture harmful to free speech?', 'tags': ['Ethics', 'Politics'], 'yes_count': 11, 'no_count': 6, 'created': '28 Feb 2026', 'last_activity': '18 Mar 2026'},
        ]
        filter = request.args.get('filter', 'new')
        page = max(1, request.args.get('page', 1, type=int))
        per_page = 10
        total = len(debates)
        total_pages = max(1, -(-total // per_page))
        page = min(page, total_pages)
        start = (page - 1) * per_page
        paginated = debates[start:start + per_page]
        return render_template('index.html', debates=paginated, filter=filter,
                               page=page, total_pages=total_pages)

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