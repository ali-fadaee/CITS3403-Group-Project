import enum
from datetime import datetime, timezone
from app.extensions import db


class DebateStatus(enum.Enum):
    open = 'open'
    closed = 'closed'


class CommentSide(enum.Enum):
    yes = 'yes'
    no = 'no'


class Avatar(db.Model):
    __tablename__ = 'avatars'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    image_url = db.Column(db.String(256), nullable=False)

    users = db.relationship('User', back_populates='avatar')


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    avatar_id = db.Column(db.Integer, db.ForeignKey('avatars.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    avatar = db.relationship('Avatar', back_populates='users')
    debates = db.relationship('Debate', back_populates='creator', cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='user', cascade='all, delete-orphan')
    interests = db.relationship('Tag', secondary='user_tags', back_populates='interested_users')
    votes = db.relationship('Vote', back_populates='user', cascade='all, delete-orphan')


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
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(DebateStatus), default=DebateStatus.open, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    creator = db.relationship('User', back_populates='debates')
    tags = db.relationship('Tag', secondary=debate_tags, back_populates='debates')
    comments = db.relationship('Comment', back_populates='debate', cascade='all, delete-orphan')

    @property
    def yes_count(self):
        return sum(1 for c in self.comments if c.side == CommentSide.yes)

    @property
    def no_count(self):
        return sum(1 for c in self.comments if c.side == CommentSide.no)


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    debate_id = db.Column(db.Integer, db.ForeignKey('debates.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    side = db.Column(db.Enum(CommentSide), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    debate = db.relationship('Debate', back_populates='comments')
    user = db.relationship('User', back_populates='comments')
    votes = db.relationship('Vote', back_populates='comment', cascade='all, delete-orphan')

    @property
    def upvote_count(self):
        return len(self.votes)


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (db.UniqueConstraint('comment_id', 'user_id', name='uq_vote_comment_user'),)

    comment = db.relationship('Comment', back_populates='votes')
    user = db.relationship('User', back_populates='votes')
