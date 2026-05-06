import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Avatar, User, Tag, Debate, Comment, DebateStatus, CommentSide, Vote

# Deterministic random data so the seeded set is identical across runs.
random.seed(42)

app = create_app()

with app.app_context():

    # Avatars
    avatars = [
        Avatar(name='Robot',        image_url='/static/images/avatars/robot.svg'),
        Avatar(name='Alien Monster',image_url='/static/images/avatars/alien_monster.svg'),
        Avatar(name='Cyborg',       image_url='/static/images/avatars/cyborg.svg'),
        Avatar(name='Brain',        image_url='/static/images/avatars/brain.svg'),
        Avatar(name='Alien',        image_url='/static/images/avatars/alien.svg'),
        Avatar(name='Dragon Face',  image_url='/static/images/avatars/dragon_face.svg'),
        Avatar(name='Lion',         image_url='/static/images/avatars/lion.svg'),
        Avatar(name='Tiger',        image_url='/static/images/avatars/tiger.svg'),
        Avatar(name='Eagle',        image_url='/static/images/avatars/eagle.svg'),
        Avatar(name='Octopus',      image_url='/static/images/avatars/octopus.svg'),
        Avatar(name='Squid',        image_url='/static/images/avatars/squid.svg'),
        Avatar(name='Scorpion',     image_url='/static/images/avatars/scorpion.svg'),
        Avatar(name='Zombie',       image_url='/static/images/avatars/zombie.svg'),
        Avatar(name='Vampire',      image_url='/static/images/avatars/vampire.svg'),
        Avatar(name='Mage',         image_url='/static/images/avatars/mage.svg'),
        Avatar(name='Ninja',        image_url='/static/images/avatars/ninja.svg'),
        Avatar(name='Ghost',        image_url='/static/images/avatars/ghost.svg'),
        Avatar(name='Skull',        image_url='/static/images/avatars/skull.svg'),
        Avatar(name='Joker',        image_url='/static/images/avatars/joker.svg'),
        Avatar(name='Bat',          image_url='/static/images/avatars/bat.svg'),
        Avatar(name='Dragon',       image_url='/static/images/avatars/dragon.svg'),
        Avatar(name='Crystal Ball', image_url='/static/images/avatars/crystal_ball.svg'),
        Avatar(name='UFO',          image_url='/static/images/avatars/ufo.svg'),
        Avatar(name='Lightning',    image_url='/static/images/avatars/lightning.svg'),
        Avatar(name='Dark Moon',    image_url='/static/images/avatars/dark_moon.svg'),
        Avatar(name='Masks',        image_url='/static/images/avatars/masks.svg'),
        Avatar(name='Wolf',         image_url='/static/images/avatars/wolf_emoji.svg'),
        Avatar(name='Fox',          image_url='/static/images/avatars/fox_emoji.svg'),
    ]
    db.session.add_all(avatars)

    # Tags — first 5 indices are referenced by the canned debate list below.
    tags = [
        Tag(name='Politics'),
        Tag(name='Technology'),
        Tag(name='Science'),
        Tag(name='Philosophy'),
        Tag(name='Environment'),
        Tag(name='Economics'),
        Tag(name='Education'),
        Tag(name='Ethics'),
        Tag(name='Health'),
        Tag(name='Lifestyle'),
    ]
    db.session.add_all(tags)
    db.session.commit()

    # Users
    alice = User(
        username='alice',
        email='alice@example.com',
        bio='Loves debating technology and philosophy.',
        avatar_id=avatars[0].id,
    )
    alice.set_password('placeholder')
    bob = User(
        username='bob',
        email='bob@example.com',
        bio='Passionate about politics and the environment.',
        avatar_id=avatars[1].id,
    )
    bob.set_password('placeholder')
    db.session.add_all([alice, bob])
    db.session.flush()

    alice.interests = [tags[1], tags[3]]
    bob.interests = [tags[0], tags[4]]
    db.session.commit()

    # Additional users
    extra_user_data = [
        ('charlie', 'charlie@example.com', 'Curious skeptic, asks questions for a living.'),
        ('dana', 'dana@example.com', 'Climate scientist who reads too much philosophy.'),
        ('eve', 'eve@example.com', 'Entrepreneur and ethics nerd.'),
        ('frank', 'frank@example.com', 'Retired teacher, lifelong reader.'),
        ('grace', 'grace@example.com', 'Software engineer with strong opinions.'),
        ('henry', 'henry@example.com', 'History buff and political junkie.'),
        ('ivy', 'ivy@example.com', 'Med student, loves a good argument.'),
        ('jack', 'jack@example.com', 'Economist who hates economics jokes.'),
        ('kate', 'kate@example.com', 'Designer thinking about the future of work.'),
        ('leo', 'leo@example.com', 'Journalist covering tech and policy.'),
        ('mia', 'mia@example.com', 'Lawyer with a soft spot for philosophy.'),
        ('nick', 'nick@example.com', 'Marketing pro and policy wonk.'),
    ]
    extra_users = [
        User(
            username=uname,
            email=email,
            bio=bio,
            avatar_id=avatars[i % len(avatars)].id,
        )
        for i, (uname, email, bio) in enumerate(extra_user_data)
    ]
    for u in extra_users:
        u.set_password('placeholder')
    db.session.add_all(extra_users)
    db.session.flush()

    for u in extra_users:
        u.interests = random.sample(tags, k=random.randint(1, 4))
    db.session.commit()

    all_users = [alice, bob] + extra_users

    # Debates
    debate1 = Debate(
        title='Is AI a threat to employment?',
        description='A discussion on how artificial intelligence is reshaping the job market.',
        creator_id=alice.id,
        status=DebateStatus.open,
    )
    debate2 = Debate(
        title='Should social media be regulated?',
        description='Exploring the role of governments in regulating social media platforms.',
        creator_id=bob.id,
        status=DebateStatus.open,
    )
    db.session.add_all([debate1, debate2])
    db.session.flush()

    debate1.tags = [tags[1], tags[2]]
    debate2.tags = [tags[0], tags[1]]
    db.session.commit()

    # Extra debates with staggered timestamps so pagination + sorting can be tested.
    # Each entry: (title, [tag indices], creator)
    extra_debates_data = [
        ('Am I a horrible person for cheating on my wife?', [0, 3], alice),
        ('Should university education be free?', [0, 1], bob),
        ('Is remote work better than office work?', [1, 4], alice),
        ('Should voting be mandatory?', [0, 3], bob),
        ('Is space exploration worth the cost?', [1, 2], alice),
        ('Should junk food be taxed?', [0, 4], bob),
        ('Is philosophy still relevant in the modern world?', [3], alice),
        ('Should there be a global minimum wage?', [0], bob),
        ('Is cancel culture harmful to free speech?', [0, 3], alice),
        ('Should we colonize Mars?', [1, 2], bob),
        ('Is nuclear power the answer to climate change?', [2, 4], alice),
        ('Should AI-generated art be copyrightable?', [1, 3], bob),
        ('Is capitalism compatible with sustainability?', [0, 4], alice),
        ('Should social media require ID verification?', [0, 1], bob),
        ('Is privacy dead in the digital age?', [1, 3], alice),
        ('Should genetic engineering of humans be allowed?', [2, 3], bob),
        ('Are zoos ethical?', [3, 4], alice),
        ('Should the death penalty be abolished worldwide?', [0, 3], bob),
        ('Is it ethical to eat meat?', [3, 4], alice),
        ('Should the internet be a basic human right?', [0, 1], bob),
    ]

    now = datetime.now(timezone.utc)
    extra_debates = []
    for i, (title, tag_idx, creator) in enumerate(extra_debates_data, start=1):
        ts = now - timedelta(days=i)
        d = Debate(
            title=title,
            description=f'A debate about: {title}',
            creator_id=creator.id,
            status=DebateStatus.open,
            created_at=ts,
            updated_at=ts,
        )
        extra_debates.append((d, tag_idx))

    db.session.add_all([d for d, _ in extra_debates])
    db.session.flush()

    for d, tag_idx in extra_debates:
        d.tags = [tags[i] for i in tag_idx]
    db.session.commit()

    # Comments
    comments = [
        Comment(debate_id=debate1.id, user_id=bob.id, content='AI will create more jobs than it destroys.', side=CommentSide.no),
        Comment(debate_id=debate1.id, user_id=alice.id, content='Not for low-skilled workers though.', side=CommentSide.yes),
        Comment(debate_id=debate2.id, user_id=alice.id, content='Regulation risks stifling free speech.', side=CommentSide.no),
        Comment(debate_id=debate2.id, user_id=bob.id, content='Without regulation, misinformation spreads unchecked.', side=CommentSide.yes),
    ]
    db.session.add_all(comments)
    db.session.commit()

    # Votes (each user upvotes the other's comments)
    c1, c2, c3, c4 = comments
    votes = [
        Vote(comment_id=c1.id, user_id=alice.id),
        Vote(comment_id=c2.id, user_id=bob.id),
        Vote(comment_id=c3.id, user_id=bob.id),
        Vote(comment_id=c4.id, user_id=alice.id),
    ]
    db.session.add_all(votes)
    db.session.commit()

    # Bulk comments for the 20 extra debates: 2-12 each, random author/side/content.
    comment_templates = [
        'This is exactly what we should be talking about.',
        'I disagree — the framing here is wrong.',
        "There's a strong empirical case for this.",
        'In my experience, this is far from settled.',
        'The history of this issue suggests otherwise.',
        'I used to think the same, then I changed my mind.',
        'This argument falls apart under scrutiny.',
        'Worth considering second-order effects too.',
        'A reasonable take, but it ignores the counterexamples.',
        "You're missing the most important variable.",
        'I broadly agree but want to push back on one point.',
        'This is the kind of thinking we need more of.',
        'Hard disagree — the data tells a different story.',
        'Both sides have merit; let me explain why.',
        'This depends entirely on context.',
        'Have you considered the long-term consequences?',
        "I'm persuaded by the opposite view, actually.",
        'This is a classic case of overgeneralization.',
        'Let me steelman the other side first.',
        'The asymmetry here is what nobody talks about.',
        "I'd be curious what experts in this field think.",
        'Reasonable minds will differ on this one.',
        "You're right in principle, wrong in practice.",
        "It's more nuanced than yes/no.",
        'The evidence base is thinner than people assume.',
        'This view has aged poorly.',
        'This is becoming the new consensus.',
        "I'll bite — here's why I disagree.",
    ]

    bulk_comments = []
    for d, _ in extra_debates:
        for _ in range(random.randint(2, 12)):
            bulk_comments.append(Comment(
                debate_id=d.id,
                user_id=random.choice(all_users).id,
                content=random.choice(comment_templates),
                side=random.choice([CommentSide.yes, CommentSide.no]),
            ))
    db.session.add_all(bulk_comments)
    db.session.commit()

    # Bulk votes: each comment gets a random subset of non-author users as voters.
    # Skip pairs that already have a vote (preserves the original 4 above).
    existing_vote_keys = {(v.comment_id, v.user_id) for v in Vote.query.all()}
    bulk_votes = []
    for c in Comment.query.all():
        candidates = [u for u in all_users if u.id != c.user_id]
        voters = random.sample(candidates, k=random.randint(0, min(len(candidates), 8)))
        for v in voters:
            key = (c.id, v.id)
            if key not in existing_vote_keys:
                bulk_votes.append(Vote(comment_id=c.id, user_id=v.id))
                existing_vote_keys.add(key)
    db.session.add_all(bulk_votes)
    db.session.commit()

    print(
        f'Seeded: {User.query.count()} users, {Tag.query.count()} tags, '
        f'{Debate.query.count()} debates, {Comment.query.count()} comments, '
        f'{Vote.query.count()} votes.'
    )
