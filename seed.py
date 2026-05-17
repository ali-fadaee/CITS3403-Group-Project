import random
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import db
from app.models import (
    Avatar, User, Tag, Debate, Comment, DebateStatus, CommentSide, Vote,
    saved_debates as saved_debates_table,
)

# Deterministic so the demo dataset is identical across runs.
random.seed(42)


AVATARS = [
    ('Alien',        'alien.svg'),
    ('Alien Monster','alien_monster.svg'),
    ('Bat',          'bat.svg'),
    ('Brain',        'brain.svg'),
    ('Crystal Ball', 'crystal_ball.svg'),
    ('Cyborg',       'cyborg.svg'),
    ('Dark Moon',    'dark_moon.svg'),
    ('Dragon',       'dragon.svg'),
    ('Dragon Face',  'dragon_face.svg'),
    ('Eagle',        'eagle.svg'),
    ('Fox',          'fox.svg'),
    ('Ghost',        'ghost.svg'),
    ('Joker',        'joker.svg'),
    ('Lightning',    'lightning.svg'),
    ('Lion',         'lion.svg'),
    ('Mage',         'mage.svg'),
    ('Masks',        'masks.svg'),
    ('Ninja',        'ninja.svg'),
    ('Octopus',      'octopus.svg'),
    ('Robot',        'robot.svg'),
    ('Scorpion',     'scorpion.svg'),
    ('Skull',        'skull.svg'),
    ('Squid',        'squid.svg'),
    ('Tiger',        'tiger.svg'),
    ('UFO',          'ufo.svg'),
    ('Vampire',      'vampire.svg'),
    ('Wolf',         'wolf.svg'),
    ('Zombie',       'zombie.svg'),
]


TAGS = [
    'Politics', 'Law', 'Economics', 'Ethics', 'Culture', 'History',
    'Free Speech', 'Privacy', 'Education',
    'Technology', 'AI', 'Cryptocurrency', 'Gaming',
    'Science', 'Climate', 'Environment', 'Space',
    'Health', 'Mental Health', 'Psychology',
    'Art', 'Music', 'Film', 'Literature', 'Philosophy',
    'Lifestyle', 'Travel', 'Food', 'Sports', 'Business',
]


PERSONAS = [
    {
        'username': 'alice',
        'avatar': 'Robot',
        'interests': ['Technology', 'AI', 'Philosophy'],
        'bio': (
            'Full-stack developer obsessed with the social impact of AI. '
            'Spends weekends reading philosophy of mind and arguing about whether '
            'large language models are doing anything close to thinking. '
            'Believes the best debates happen over cold coffee at 2 am.'
        ),
    },
    {
        'username': 'bob',
        'avatar': 'Dragon',
        'interests': ['Politics', 'Environment', 'Economics'],
        'bio': (
            'Former campaign staffer turned environmental policy researcher. '
            'Convinced that climate change is the argument everyone is having wrong. '
            'Can quote both Rawls and the IPCC from memory, sometimes in the same sentence.'
        ),
    },
    {
        'username': 'charlie',
        'avatar': 'Brain',
        'interests': ['Philosophy', 'Ethics', 'Psychology'],
        'bio': (
            'Professional skeptic and amateur epistemologist. '
            'Works in UX research during the day and reads Hume at night. '
            'Never takes a position without first steelmanning the opposition.'
        ),
    },
    {
        'username': 'dana',
        'avatar': 'Dark Moon',
        'interests': ['Climate', 'Science', 'Environment'],
        'bio': (
            'Climate scientist at a public university with a soft spot for moral philosophy. '
            'Spends too much time thinking about whether individual action matters when '
            'the structures are broken. Still composts anyway.'
        ),
    },
    {
        'username': 'eve',
        'avatar': 'Lightning',
        'interests': ['Business', 'Technology', 'Ethics'],
        'bio': (
            'Serial entrepreneur who failed three times before getting it right. '
            'Writes and speaks about tech ethics because she wishes someone had '
            'given her that perspective earlier. Reads everything, sleeps rarely.'
        ),
    },
    {
        'username': 'frank',
        'avatar': 'Mage',
        'interests': ['Education', 'Literature', 'History'],
        'bio': (
            'Retired high school English teacher with forty years of watching people '
            'learn how to argue badly before learning to argue well. '
            'Opinionated about education reform and the Oxford comma.'
        ),
    },
    {
        'username': 'grace',
        'avatar': 'Cyborg',
        'interests': ['Technology', 'AI', 'Free Speech'],
        'bio': (
            'Senior software engineer who thinks most debates about AI '
            'are fought by people who have never written a for-loop. '
            'Strong opinions about type systems, distributed consensus, and open-source governance.'
        ),
    },
    {
        'username': 'henry',
        'avatar': 'Skull',
        'interests': ['History', 'Politics', 'Culture'],
        'bio': (
            'History PhD candidate specialising in 20th-century political movements. '
            'Convinced that the present is just the past with better graphics. '
            'Will cite a historical precedent whether you want one or not.'
        ),
    },
    {
        'username': 'ivy',
        'avatar': 'Alien',
        'interests': ['Health', 'Ethics', 'Mental Health'],
        'bio': (
            'Third-year medical student who treats every clinical ethics seminar '
            'as a live debate. Interested in healthcare access, triage ethics, '
            'and whether anyone actually reads informed-consent forms.'
        ),
    },
    {
        'username': 'jack',
        'avatar': 'Crystal Ball',
        'interests': ['Economics', 'Psychology', 'Business'],
        'bio': (
            'Behavioural economist deeply suspicious of the assumptions '
            'in mainstream economic models. Studies how people actually make '
            'decisions rather than how textbooks say they should.'
        ),
    },
    {
        'username': 'kate',
        'avatar': 'Ninja',
        'interests': ['Art', 'Culture', 'Technology'],
        'bio': (
            'Product designer thinking about the long-term consequences '
            'of the interfaces she builds. Reads speculative fiction for '
            'inspiration and futures studies to stay grounded.'
        ),
    },
    {
        'username': 'leo',
        'avatar': 'Fox',
        'interests': ['Politics', 'Law', 'Privacy'],
        'bio': (
            'Investigative journalist covering the intersection of technology '
            'and public policy. Has had two pieces referred to parliamentary committees '
            'and is quietly proud of both. Distrusts press releases on principle.'
        ),
    },
    {
        'username': 'mia',
        'avatar': 'Vampire',
        'interests': ['Law', 'Privacy', 'Free Speech'],
        'bio': (
            'Barrister specialising in civil liberties and data-privacy law. '
            'Argues for a living and finds recreational debate suspiciously relaxing. '
            'Particularly interested in questions where the law and ethics diverge.'
        ),
    },
    {
        'username': 'nick',
        'avatar': 'Joker',
        'interests': ['Business', 'Politics', 'Philosophy'],
        'bio': (
            'Brand strategist who thinks about persuasion for a living '
            'and is consequently very suspicious of persuasion. '
            'Also a policy wonk; believes these two interests are more related than they look.'
        ),
    },
    {
        'username': 'olive',
        'avatar': 'Octopus',
        'interests': ['Food', 'Health', 'Environment'],
        'bio': (
            'Food writer and registered dietitian focused on sustainable diets. '
            'Believes most public-health advice would land better if it admitted '
            'food is also about culture, pleasure, and community.'
        ),
    },
    {
        'username': 'paul',
        'avatar': 'Tiger',
        'interests': ['Sports', 'Health', 'Business'],
        'bio': (
            'Former professional rugby player turned sports business consultant. '
            'Spent ten years inside elite sport; now writes about its ethics, '
            'economics, and quiet damage to the people who play it.'
        ),
    },
    {
        'username': 'quinn',
        'avatar': 'Ghost',
        'interests': ['Gaming', 'Technology', 'Art'],
        'bio': (
            'Indie game designer and former AAA developer. '
            'Thinks games are the most undervalued art form of the last fifty years '
            'and that most arguments to the contrary are made by people who stopped playing in 2003.'
        ),
    },
    {
        'username': 'rosa',
        'avatar': 'Masks',
        'interests': ['Film', 'Culture', 'Art'],
        'bio': (
            'Independent filmmaker focused on social documentaries. '
            'Spends most of the year on the road and the rest cutting footage at home. '
            'Believes a good question is worth more than a good answer.'
        ),
    },
    {
        'username': 'sam',
        'avatar': 'Wolf',
        'interests': ['Music', 'Art', 'Business'],
        'bio': (
            'Session musician and music industry observer. '
            'Has watched streaming destroy and rebuild the economics of music in real time '
            'and has opinions about both halves of that story.'
        ),
    },
    {
        'username': 'tia',
        'avatar': 'Eagle',
        'interests': ['Travel', 'Culture', 'Environment'],
        'bio': (
            'Travel writer with a growing focus on sustainable and slow tourism. '
            'Spent five years writing destination guides and the last two unwriting them. '
            'Believes you can love a place and still be part of what is ruining it.'
        ),
    },
    {
        'username': 'uma',
        'avatar': 'Bat',
        'interests': ['Mental Health', 'Psychology', 'Lifestyle'],
        'bio': (
            'Clinical psychologist with a private practice and a complicated relationship '
            'with the wellness industry. Interested in what makes therapy actually help, '
            'as opposed to what makes it sell.'
        ),
    },
    {
        'username': 'victor',
        'avatar': 'Alien Monster',
        'interests': ['Cryptocurrency', 'Economics', 'Technology'],
        'bio': (
            'Crypto economist and on-chain analyst. '
            'Was a true believer, then a cynic, and is now somewhere in between. '
            'Particularly interested in stablecoins, regulation, and how this all ends.'
        ),
    },
    {
        'username': 'wendy',
        'avatar': 'UFO',
        'interests': ['Space', 'Science', 'Philosophy'],
        'bio': (
            'Astrophysicist studying exoplanet atmospheres. '
            'Believes the search for life elsewhere is the most underrated philosophical project of our time, '
            'and that NASA still does not get enough credit.'
        ),
    },
    {
        'username': 'xander',
        'avatar': 'Scorpion',
        'interests': ['Literature', 'Gaming', 'Film'],
        'bio': (
            'Speculative fiction novelist with two published books and a third about to die in revisions. '
            'Reads widely, plays games annoyingly slowly, and watches every Tarkovsky film at least once a year.'
        ),
    },
    {
        'username': 'yara',
        'avatar': 'Lion',
        'interests': ['Climate', 'Politics', 'Economics'],
        'bio': (
            'Climate policy analyst at an independent think tank. '
            'Works on carbon pricing, just transition policy, and the long political afterlife '
            'of every climate commitment that was meant to be the last one.'
        ),
    },
    {
        'username': 'zane',
        'avatar': 'Squid',
        'interests': ['Free Speech', 'Law', 'Culture'],
        'bio': (
            'Constitutional law researcher with a column on speech and platform regulation. '
            'Defends positions that annoy everyone in the room at least once a week, '
            'which he considers a sign things are going well.'
        ),
    },
    {
        'username': 'anna',
        'avatar': 'Dragon Face',
        'interests': ['Literature', 'Education', 'Culture'],
        'bio': (
            'Translator of contemporary fiction and an occasional university lecturer. '
            'Believes a translation is an argument the translator is having with the original, '
            'and that the same is true of education itself.'
        ),
    },
    {
        'username': 'boris',
        'avatar': 'Zombie',
        'interests': ['History', 'Politics', 'Culture'],
        'bio': (
            'Cold War history podcast host and former foreign correspondent. '
            'Has opinions about every collapse of every empire and is happy to share them, '
            'usually in the order they happened.'
        ),
    },
    {
        'username': 'cleo',
        'avatar': 'Joker',
        'interests': ['Art', 'Film', 'Lifestyle'],
        'bio': (
            'Independent art curator and small-gallery owner. '
            'Spends her week deciding what counts as art this season '
            'and her weekends being deeply suspicious of that decision.'
        ),
    },
    {
        'username': 'dex',
        'avatar': 'Mage',
        'interests': ['Space', 'Science', 'Philosophy'],
        'bio': (
            'Theoretical physics PhD with a side obsession in philosophy of mind. '
            'Spends his days on quantum field theory and his evenings asking '
            'whether anything he does could be derived from first principles.'
        ),
    },
]


# (title, [tag names], creator username, optional description)
DEBATES = [
    ('Is AI a threat to employment?',
     ['Technology', 'AI', 'Economics'], 'alice'),
    ('Should social media be regulated?',
     ['Politics', 'Technology', 'Privacy'], 'bob'),
    ('Should university education be free?',
     ['Education', 'Politics', 'Economics'], 'bob'),
    ('Is remote work better than office work?',
     ['Lifestyle', 'Business'], 'eve'),
    ('Should voting be mandatory?',
     ['Politics', 'Ethics'], 'leo'),
    ('Is space exploration worth the cost?',
     ['Space', 'Science', 'Economics'], 'wendy'),
    ('Should junk food be taxed?',
     ['Health', 'Food', 'Politics'], 'olive'),
    ('Is philosophy still relevant in the modern world?',
     ['Philosophy', 'Culture'], 'charlie'),
    ('Should there be a global minimum wage?',
     ['Economics', 'Politics', 'Ethics'], 'jack'),
    ('Is cancel culture harmful to free speech?',
     ['Free Speech', 'Culture', 'Politics'], 'zane'),
    ('Should we colonize Mars?',
     ['Space', 'Science', 'Ethics'], 'dex'),
    ('Is nuclear power the answer to climate change?',
     ['Climate', 'Environment', 'Science'], 'dana'),
    ('Should AI-generated art be copyrightable?',
     ['AI', 'Art', 'Law'], 'kate'),
    ('Is capitalism compatible with sustainability?',
     ['Economics', 'Climate', 'Environment', 'Philosophy'], 'yara'),
    ('Should social media require ID verification?',
     ['Privacy', 'Technology', 'Free Speech'], 'mia'),
    ('Is privacy dead in the digital age?',
     ['Privacy', 'Technology', 'Law'], 'leo'),
    ('Should genetic engineering of humans be allowed?',
     ['Science', 'Ethics', 'Health'], 'ivy'),
    ('Are zoos ethical?',
     ['Ethics', 'Environment', 'Lifestyle'], 'charlie'),
    ('Should the death penalty be abolished worldwide?',
     ['Politics', 'Ethics', 'Law'], 'mia'),
    ('Is it ethical to eat meat?',
     ['Food', 'Ethics', 'Environment'], 'olive'),
    ('Should the internet be a basic human right?',
     ['Politics', 'Technology', 'Law'], 'leo'),
    ('Is the housing crisis a moral failure of capitalism?',
     ['Economics', 'Politics', 'Philosophy'], 'jack'),
    ('Should video games be considered art?',
     ['Gaming', 'Art', 'Culture'], 'quinn'),
    ('Are streaming services killing cinema?',
     ['Film', 'Business', 'Culture'], 'rosa'),
    ('Should we tax wealth instead of income?',
     ['Economics', 'Politics'], 'jack'),
    ('Is therapy culture making us weaker?',
     ['Mental Health', 'Psychology', 'Culture'], 'uma'),
    ('Should music ownership be more strictly enforced?',
     ['Music', 'Law', 'Business'], 'sam'),
    ('Is the four-day work week the future?',
     ['Business', 'Lifestyle', 'Economics'], 'eve'),
    ('Should tourist destinations cap visitor numbers?',
     ['Travel', 'Environment', 'Culture'], 'tia'),
    ('Is the news cycle making us worse citizens?',
     ['Politics', 'Psychology', 'Mental Health'], 'leo'),
    ('Should crypto be regulated like a security?',
     ['Cryptocurrency', 'Law', 'Economics'], 'victor'),
    ('Has political polarization broken democracy?',
     ['Politics', 'History', 'Culture'], 'boris'),
    ('Is reading still the best form of learning?',
     ['Education', 'Literature', 'Philosophy'], 'frank'),
    ('Should sports betting be banned?',
     ['Sports', 'Ethics', 'Law'], 'paul'),
    ('Is professional sport ethical?',
     ['Sports', 'Health', 'Ethics'], 'paul'),
    ('Should governments fund the arts?',
     ['Art', 'Politics', 'Culture'], 'cleo'),
    ('Are open relationships actually healthier?',
     ['Lifestyle', 'Psychology'], 'uma'),
    ('Is the gig economy a scam?',
     ['Economics', 'Business', 'Lifestyle'], 'jack'),
    ('Has streaming destroyed musicianship?',
     ['Music', 'Business', 'Culture'], 'sam'),
    ('Should classical literature still be required reading?',
     ['Literature', 'Education', 'Culture'], 'anna'),
    ('Is AI consciousness possible?',
     ['AI', 'Philosophy', 'Science'], 'alice'),
    ('Should we abolish copyright entirely?',
     ['Law', 'Art', 'Culture'], 'kate'),
    ('Is the metaverse already dead?',
     ['Technology', 'Gaming', 'Business'], 'quinn'),
    ('Should hate speech be legally protected?',
     ['Free Speech', 'Law', 'Politics'], 'zane'),
    ('Has globalization helped or hurt the working class?',
     ['Economics', 'Politics', 'History'], 'boris'),
    ('Should we ban fast fashion?',
     ['Environment', 'Ethics', 'Lifestyle'], 'tia'),
    ('Is mindfulness culture a scam?',
     ['Mental Health', 'Lifestyle', 'Culture'], 'uma'),
    ('Should we have a universal basic income?',
     ['Economics', 'Politics', 'Ethics'], 'jack'),
    ('Is documentary filmmaking journalism?',
     ['Film', 'Culture', 'Politics'], 'rosa'),
    ('Should we limit screen time for children?',
     ['Health', 'Lifestyle', 'Education'], 'ivy'),
    ('Is the West in decline?',
     ['History', 'Politics', 'Culture'], 'boris'),
    ('Should private space companies be more tightly regulated?',
     ['Space', 'Politics', 'Economics'], 'wendy'),
    ('Is "therapy speak" ruining how we talk?',
     ['Mental Health', 'Culture', 'Psychology'], 'uma'),
    ('Should universities use trigger warnings?',
     ['Education', 'Free Speech', 'Culture'], 'frank'),
    ('Has dating been ruined by apps?',
     ['Lifestyle', 'Technology', 'Psychology'], 'uma'),
    ('Is identity politics a dead end?',
     ['Politics', 'Philosophy', 'Culture'], 'charlie'),
    ('Should self-driving cars make ethical decisions?',
     ['AI', 'Ethics', 'Technology'], 'alice'),
    ('Has true crime become exploitation?',
     ['Culture', 'Ethics', 'Film'], 'rosa'),
    ('Should we tax meat to fight climate change?',
     ['Climate', 'Food', 'Politics'], 'olive'),
    ('Is open source the only ethical software?',
     ['Technology', 'Ethics', 'Philosophy'], 'grace'),
    ('Should governments break up big tech?',
     ['Technology', 'Politics', 'Economics'], 'leo'),
    ('Is the humanities crisis real?',
     ['Education', 'Literature', 'History'], 'anna'),
    ('Should we replace police with social workers?',
     ['Politics', 'Ethics', 'Law'], 'henry'),
    ('Are we underestimating the cost of remote work?',
     ['Business', 'Lifestyle', 'Mental Health'], 'eve'),
    ('Is the singleplayer game era over?',
     ['Gaming', 'Culture', 'Business'], 'quinn'),
    ('Should we abolish standardised testing?',
     ['Education', 'Psychology', 'Politics'], 'frank'),
    ('Has Bitcoin already failed as a currency?',
     ['Cryptocurrency', 'Economics', 'Technology'], 'victor'),
    ('Is the influencer economy bad for democracy?',
     ['Politics', 'Business', 'Culture'], 'nick'),
    ('Should we be worried about AI in elections?',
     ['AI', 'Politics', 'Privacy'], 'grace'),
    ('Is veganism morally required?',
     ['Ethics', 'Food', 'Philosophy'], 'olive'),
]


COMMENT_BANK = [
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
    'There are at least three distinct claims tangled together here.',
    'I want to separate the descriptive and normative parts of this.',
    'The empirical question and the policy question are not the same.',
    'I keep coming back to who actually bears the cost of being wrong.',
    'My priors are strong here, but I should say what would change my mind.',
    'I think we agree on the diagnosis and disagree on the prescription.',
    'This is one of those debates where the labels do most of the work.',
]


REPLY_BANK = [
    'Fair point, but consider this counterexample.',
    'I think that overstates the evidence.',
    'Agreed — and this is exactly what gets glossed over.',
    "That's not what the data actually shows though.",
    "I think you're conflating two different things.",
    'Yes, but only under very specific conditions.',
    'Strongly seconded.',
    'I had the same instinct but changed my mind reading this.',
    "That's the strongest version of the argument, sure.",
    'Then how do you account for the obvious counterexample?',
    'Worth defining the terms more carefully before going further.',
    "I don't think the comparison holds.",
    'You might be technically right but this misses the actual stakes.',
    'The empirical record on this is more mixed than that.',
    'OK but who pays the cost in your version of this?',
    'This argument keeps proving too much.',
    'Honestly I think we agree on more than the wording suggests.',
    "I keep seeing this asserted and I'd love to see it argued.",
    'There is a much better version of your point you could make instead.',
    'Right, but the implication is harsher than you let on.',
]


app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # ---- Avatars ----
    avatars = [
        Avatar(name=name, image_url=f'/static/images/avatars/{fname}')
        for name, fname in AVATARS
    ]
    db.session.add_all(avatars)
    db.session.flush()
    av = {a.name: a for a in avatars}

    # ---- Tags ----
    tags = [Tag(name=n) for n in TAGS]
    db.session.add_all(tags)
    db.session.flush()
    tag_by_name = {t.name: t for t in tags}

    # ---- Users ----
    users = []
    for p in PERSONAS:
        u = User(
            username=p['username'],
            email=f"{p['username']}@example.com",
            bio=p['bio'],
            avatar_id=av[p['avatar']].id,
            email_verified=True,
        )
        u.set_password('Password1')
        users.append(u)
    db.session.add_all(users)
    db.session.flush()
    user_by_name = {u.username: u for u in users}

    for p in PERSONAS:
        user_by_name[p['username']].interests = [tag_by_name[t] for t in p['interests']]
    db.session.commit()

    persona_interests = {p['username']: set(p['interests']) for p in PERSONAS}

    # ---- Debates ----
    now = datetime.now(timezone.utc)
    debates = []
    for i, entry in enumerate(DEBATES):
        title, tag_names, creator_name = entry[0], entry[1], entry[2]
        description = entry[3] if len(entry) > 3 else f'A debate about: {title}'
        # Spread across roughly the last 70 days, jittered by hours/minutes.
        ts = now - timedelta(
            days=i,
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        d = Debate(
            title=title,
            description=description,
            creator_id=user_by_name[creator_name].id,
            status=DebateStatus.open,
            created_at=ts,
            updated_at=ts,
        )
        debates.append((d, tag_names))

    db.session.add_all([d for d, _ in debates])
    db.session.flush()
    for d, tag_names in debates:
        d.tags = [tag_by_name[t] for t in tag_names]
    db.session.commit()

    # ---- Comments + threaded replies ----
    # For each debate, bias toward users whose interests overlap the debate's tags,
    # with a random "leaning" (yes-weight) so some debates feel one-sided.
    all_top_level = []
    for d, tag_names in debates:
        tag_set = set(tag_names)
        interested = [
            u for u in users
            if u.id != d.creator_id and persona_interests[u.username] & tag_set
        ]
        uninterested = [
            u for u in users
            if u.id != d.creator_id and not (persona_interests[u.username] & tag_set)
        ]

        n_comments = random.randint(5, 18)
        yes_weight = random.uniform(0.25, 0.75)

        debate_top = []
        for _ in range(n_comments):
            if interested and random.random() < 0.75:
                author = random.choice(interested)
            elif uninterested:
                author = random.choice(uninterested)
            else:
                continue
            side = CommentSide.yes if random.random() < yes_weight else CommentSide.no
            c = Comment(
                debate_id=d.id,
                user_id=author.id,
                content=random.choice(COMMENT_BANK),
                side=side,
                created_at=d.created_at + timedelta(
                    hours=random.randint(1, 240),
                    minutes=random.randint(0, 59),
                ),
            )
            debate_top.append(c)
        db.session.add_all(debate_top)
        db.session.flush()
        all_top_level.extend(debate_top)

        # Threaded replies: ~35% of top-level comments get one or two replies.
        replies_to_add = []
        for parent in debate_top:
            if random.random() < 0.35:
                n_replies = random.randint(1, 2)
                for _ in range(n_replies):
                    replier_pool = [u for u in users if u.id != parent.user_id]
                    if not replier_pool:
                        continue
                    replier = random.choice(replier_pool)
                    # Reply side: 60% disagrees with parent, 40% agrees.
                    if random.random() < 0.6:
                        reply_side = (CommentSide.no if parent.side == CommentSide.yes
                                      else CommentSide.yes)
                    else:
                        reply_side = parent.side
                    replies_to_add.append(Comment(
                        debate_id=d.id,
                        parent_id=parent.id,
                        user_id=replier.id,
                        content=random.choice(REPLY_BANK),
                        side=reply_side,
                        created_at=parent.created_at + timedelta(
                            hours=random.randint(1, 72),
                            minutes=random.randint(0, 59),
                        ),
                    ))
        if replies_to_add:
            db.session.add_all(replies_to_add)
            db.session.flush()
    db.session.commit()

    # ---- Votes ----
    # Each comment gets a random subset of non-author users as voters; biased so
    # interested users are more likely to vote.
    vote_keys = set()
    bulk_votes = []
    for c in Comment.query.all():
        debate = db.session.get(Debate, c.debate_id)
        debate_tag_names = {t.name for t in debate.tags}
        candidates = [u for u in users if u.id != c.user_id]
        weighted = []
        for u in candidates:
            weight = 4 if persona_interests[u.username] & debate_tag_names else 1
            weighted.extend([u] * weight)
        # Sample without replacement from the weighted pool.
        chosen = []
        target = random.randint(0, 12)
        seen = set()
        attempts = 0
        while len(chosen) < target and attempts < 200:
            attempts += 1
            pick = random.choice(weighted) if weighted else None
            if pick is None or pick.id in seen:
                continue
            seen.add(pick.id)
            chosen.append(pick)
        for v in chosen:
            key = (c.id, v.id)
            if key not in vote_keys:
                bulk_votes.append(Vote(comment_id=c.id, user_id=v.id))
                vote_keys.add(key)
    db.session.add_all(bulk_votes)
    db.session.commit()

    # ---- Saved debates ----
    # Each user saves 4–9 debates, weighted heavily toward their interest tags.
    all_debates_objs = Debate.query.all()
    for u in users:
        user_tag_names = {t.name for t in u.interests}
        relevant = [
            d for d in all_debates_objs
            if d.creator_id != u.id
            and user_tag_names & {t.name for t in d.tags}
        ]
        others = [
            d for d in all_debates_objs
            if d.creator_id != u.id
            and not (user_tag_names & {t.name for t in d.tags})
        ]
        n_to_save = random.randint(4, 9)
        n_relevant = min(int(n_to_save * 0.8), len(relevant))
        n_other = min(n_to_save - n_relevant, len(others))
        saved = []
        if n_relevant:
            saved.extend(random.sample(relevant, n_relevant))
        if n_other:
            saved.extend(random.sample(others, n_other))
        u.saved = saved
    db.session.commit()

    # ---- Backdate updated_at to last activity ----
    # The Comment/Vote after_insert listeners issue UPDATE debates statements,
    # which fire Column.onupdate=_utcnow and overwrite each debate's updated_at
    # to the seed run time. That makes every "active" date on the index read
    # like today. Reset updated_at to the latest comment timestamp (or
    # created_at if no comments) so the demo feed shows a realistic spread.
    # Assigning updated_at explicitly bypasses the onupdate hook.
    latest_by_debate = dict(db.session.execute(
        db.select(Comment.debate_id, db.func.max(Comment.created_at))
          .group_by(Comment.debate_id)
    ).all())
    for d in all_debates_objs:
        latest = latest_by_debate.get(d.id)
        d.updated_at = latest if latest and latest > d.created_at else d.created_at
    db.session.commit()

    saved_count = db.session.execute(
        db.select(db.func.count()).select_from(saved_debates_table)
    ).scalar()
    print(
        f'Seeded: {User.query.count()} users, {Tag.query.count()} tags, '
        f'{Debate.query.count()} debates, {Comment.query.count()} comments, '
        f'{Vote.query.count()} votes, {saved_count} saved debates.'
    )
