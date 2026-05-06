from flask import Blueprint, render_template, request, session
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models import Debate, Comment, User, debate_tags, user_tags

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


@main.route('/login')
def login():
    return render_template('login.html')


@main.route('/signup')
def signup():
    return render_template('signup.html')


@main.route('/profile')
def profile():
    return render_template('profile.html')


@main.route('/create')
def create():
    return render_template('create.html')


@main.route('/debate')
def debate():
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
