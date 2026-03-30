from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Avatar, User, Tag, Debate, Comment

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Avatars
    avatars = [
        Avatar(name='Fox', image_url='/static/images/avatars/fox.svg'),
        Avatar(name='Bear', image_url='/static/images/avatars/bear.svg'),
        Avatar(name='Owl', image_url='/static/images/avatars/owl.svg'),
        Avatar(name='Wolf', image_url='/static/images/avatars/wolf.svg'),
    ]
    db.session.add_all(avatars)

    # Tags
    tags = [
        Tag(name='Politics'),
        Tag(name='Technology'),
        Tag(name='Science'),
        Tag(name='Philosophy'),
        Tag(name='Environment'),
    ]
    db.session.add_all(tags)
    db.session.commit()

    # Users
    alice = User(
        username='alice',
        email='alice@example.com',
        password_hash='placeholder',
        bio='Loves debating technology and philosophy.',
        avatar_id=avatars[0].id,
    )
    bob = User(
        username='bob',
        email='bob@example.com',
        password_hash='placeholder',
        bio='Passionate about politics and the environment.',
        avatar_id=avatars[1].id,
    )
    db.session.add_all([alice, bob])
    db.session.flush()

    alice.interests = [tags[1], tags[3]]
    bob.interests = [tags[0], tags[4]]
    db.session.commit()

    # Debates
    debate1 = Debate(
        title='Is AI a threat to employment?',
        description='A discussion on how artificial intelligence is reshaping the job market.',
        creator_id=alice.id,
        status='open',
    )
    debate2 = Debate(
        title='Should social media be regulated?',
        description='Exploring the role of governments in regulating social media platforms.',
        creator_id=bob.id,
        status='open',
    )
    db.session.add_all([debate1, debate2])
    db.session.flush()

    debate1.tags = [tags[1], tags[2]]
    debate2.tags = [tags[0], tags[1]]
    db.session.commit()

    # Comments
    comments = [
        Comment(debate_id=debate1.id, user_id=bob.id, content='AI will create more jobs than it destroys.', side='no'),
        Comment(debate_id=debate1.id, user_id=alice.id, content='Not for low-skilled workers though.', side='yes'),
        Comment(debate_id=debate2.id, user_id=alice.id, content='Regulation risks stifling free speech.', side='no'),
        Comment(debate_id=debate2.id, user_id=bob.id, content='Without regulation, misinformation spreads unchecked.', side='yes'),
    ]
    db.session.add_all(comments)
    db.session.commit()

    print('Database seeded successfully.')
