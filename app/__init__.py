from flask import Flask, render_template, request


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        debates = [
            {'title': 'Is AI a threat to employment?', 'tags': ['Technology', 'Science'], 'yes_count': 3, 'no_count': 1, 'created': '28 Mar 2026', 'last_activity': '30 Mar 2026'},
            {'title': 'Should social media be regulated?', 'tags': ['Politics', 'Technology'], 'yes_count': 2, 'no_count': 8, 'created': '25 Mar 2026', 'last_activity': '29 Mar 2026'},
            {'title': 'Am I a horrible person for cheating on my wife?', 'tags': ['Lifestyle', 'Relationships'], 'yes_count': 10, 'no_count': 2, 'created': '20 Mar 2026', 'last_activity': '30 Mar 2026'},
            {'title': 'Is remote work here to stay?', 'tags': ['Technology', 'Lifestyle'], 'yes_count': 15, 'no_count': 6, 'created': '5 Apr 2026', 'last_activity': '21 Apr 2026'},
            {'title': 'Should nuclear power be expanded to fight climate change?', 'tags': ['Science', 'Environment'], 'yes_count': 22, 'no_count': 9, 'created': '12 Mar 2026', 'last_activity': '18 Apr 2026'},
            {'title': 'Is free will an illusion?', 'tags': ['Philosophy'], 'yes_count': 7, 'no_count': 11, 'created': '2 Apr 2026', 'last_activity': '20 Apr 2026'},
            {'title': 'Should billionaires exist?', 'tags': ['Politics', 'Economics'], 'yes_count': 18, 'no_count': 21, 'created': '28 Mar 2026', 'last_activity': '22 Apr 2026'},
            {'title': 'Is streaming killing cinema?', 'tags': ['Entertainment', 'Culture'], 'yes_count': 12, 'no_count': 4, 'created': '10 Apr 2026', 'last_activity': '19 Apr 2026'},
            {'title': 'Should university be free for everyone?', 'tags': ['Politics', 'Education'], 'yes_count': 31, 'no_count': 14, 'created': '1 Apr 2026', 'last_activity': '21 Apr 2026'},
            {'title': 'Is VAR ruining football?', 'tags': ['Sports'], 'yes_count': 9, 'no_count': 6, 'created': '14 Apr 2026', 'last_activity': '20 Apr 2026'},
            {'title': 'Should humans colonize Mars?', 'tags': ['Science', 'Technology'], 'yes_count': 13, 'no_count': 17, 'created': '18 Mar 2026', 'last_activity': '16 Apr 2026'},
        ]
        filter = request.args.get('filter', 'new')

        per_page = 10
        try:
            page = max(1, int(request.args.get('page', 1)))
        except ValueError:
            page = 1
        total = len(debates)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page = min(page, total_pages)
        start = (page - 1) * per_page
        paginated = debates[start:start + per_page]

        return render_template(
            'index.html',
            debates=paginated,
            filter=filter,
            page=page,
            total_pages=total_pages,
            has_prev=page > 1,
            has_next=page < total_pages,
        )

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