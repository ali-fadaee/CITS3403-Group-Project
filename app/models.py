import enum
import secrets
from datetime import datetime, timezone
from sqlalchemy import event, update, select
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import login_manager


class DebateStatus(enum.Enum):
    open = 'open'
    closed = 'closed'


class CommentSide(enum.Enum):
    yes = 'yes'
    no = 'no'


def _utcnow():
    return datetime.now(timezone.utc)


class Avatar(db.Model):
    __tablename__ = 'avatars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    image_url = db.Column(db.String(256), nullable=False)

    users = db.relationship('User', back_populates='avatar')


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    session_token = db.Column(db.String(32), nullable=False, default=lambda: secrets.token_hex(16))
    bio = db.Column(db.Text, nullable=True)
    avatar_id = db.Column(db.Integer, db.ForeignKey('avatars.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    def get_id(self):
        return f"{self.id}.{self.session_token}"

    def rotate_session_token(self):
        self.session_token = secrets.token_hex(16)

    avatar = db.relationship('Avatar', back_populates='users')
    debates = db.relationship('Debate', back_populates='creator', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    interests = db.relationship('Tag', secondary='user_tags', back_populates='interested_users')
    votes = db.relationship('Vote', back_populates='user', cascade='all, delete-orphan')
    saved = db.relationship('Debate', secondary='saved_debates', back_populates='saved_by')


saved_debates = db.Table(
    'saved_debates',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('debate_id', db.Integer, db.ForeignKey('debates.id', ondelete='CASCADE'), primary_key=True)
)

user_tags = db.Table(
    'user_tags',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

debate_tags = db.Table(
    'debate_tags',
    db.Column('debate_id', db.Integer, db.ForeignKey('debates.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)


class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)

    debates = db.relationship('Debate', secondary=debate_tags, back_populates='tags')
    interested_users = db.relationship('User', secondary='user_tags', back_populates='interests')


class Debate(db.Model):
    __tablename__ = 'debates'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.Enum(DebateStatus), default=DebateStatus.open, nullable=False)
    yes_count = db.Column(db.Integer, default=0, nullable=False)
    no_count = db.Column(db.Integer, default=0, nullable=False)
    comment_count = db.Column(db.Integer, default=0, nullable=False)
    yes_upvotes = db.Column(db.Integer, default=0, nullable=False)
    no_upvotes = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False, index=True)

    creator = db.relationship('User', back_populates='debates')
    tags = db.relationship('Tag', secondary=debate_tags, back_populates='debates')
    comments = db.relationship('Comment', back_populates='debate', cascade='all, delete-orphan')
    saved_by = db.relationship('User', secondary='saved_debates', back_populates='saved')


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), nullable=False, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    side = db.Column(db.Enum(CommentSide), nullable=False)
    upvote_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=_utcnow)

    debate = db.relationship('Debate', back_populates='comments')
    parent = db.relationship('Comment', remote_side=[id], back_populates='children')
    children = db.relationship('Comment', back_populates='parent', cascade='all, delete-orphan')
    user = db.relationship('User', back_populates='comments')
    votes = db.relationship('Vote', back_populates='comment', cascade='all, delete-orphan')


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=_utcnow)

    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id', name='uq_vote_comment_user'),)

    comment = db.relationship('Comment', back_populates='votes')
    user = db.relationship('User', back_populates='votes')


@event.listens_for(Comment, 'after_insert')
def _comment_after_insert(mapper, connection, target):
    # update debate counts
    field = 'yes_count' if target.side == CommentSide.yes else 'no_count'
    connection.execute(
        update(Debate).where(Debate.id == target.debate_id).values({
            field: getattr(Debate, field) + 1,
            'comment_count': Debate.comment_count + 1,
        })
    )


@event.listens_for(Comment, 'after_delete')
def _comment_after_delete(mapper, connection, target):
    field = 'yes_count' if target.side == CommentSide.yes else 'no_count'
    connection.execute(
        update(Debate).where(Debate.id == target.debate_id).values({
            field: getattr(Debate, field) - 1,
            'comment_count': Debate.comment_count - 1,
        })
    )


def _update_debate_upvotes(connection, comment_id, delta):
    # update side vote totals
    row = connection.execute(
        select(Comment.debate_id, Comment.side).where(Comment.id == comment_id)
    ).first()
    if row:
        side_val = row.side.value if isinstance(row.side, CommentSide) else row.side
        field = 'yes_upvotes' if side_val == 'yes' else 'no_upvotes'
        connection.execute(
            update(Debate).where(Debate.id == row.debate_id).values(
                {field: getattr(Debate, field) + delta}
            )
        )


@event.listens_for(Vote, 'after_insert')
def _vote_after_insert(mapper, connection, target):
    connection.execute(
        update(Comment).where(Comment.id == target.comment_id).values(
            upvote_count=Comment.upvote_count + 1
        )
    )
    _update_debate_upvotes(connection, target.comment_id, 1)


@event.listens_for(Vote, 'after_delete')
def _vote_after_delete(mapper, connection, target):
    connection.execute(
        update(Comment).where(Comment.id == target.comment_id).values(
            upvote_count=Comment.upvote_count - 1
        )
    )
    _update_debate_upvotes(connection, target.comment_id, -1)

@login_manager.user_loader
def load_user(user_id):
    try:
        uid, token = user_id.split('.', 1)
        user = db.session.get(User, int(uid))
        if user and user.session_token == token:
            return user
        return None
    except (ValueError, AttributeError):
        return None
