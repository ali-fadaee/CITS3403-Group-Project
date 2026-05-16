# CITS3403-Group-Project

~/debate-app

A web application for creating and participating in debates. Users can start new debates by posting statements and adding categorisation tags to enable search. Participation in debate involves posting *for* or *against* arguments, and 'upvoting' compelling contributions from others. User have customisable profiles so that they can provide others with their personal context.

## Contributors

| Name                  | Student ID | GitHub             |
| --------------------- | ---------- | ------------------ |
| Ali Fadaee            | 24262732   | ali-fadaee         |
| Gleb Mezin            | 23797926   | TheRofli           |
| Mathew Libby          | 21805584   | MathewLibby        |
| Sukhman Singh Dhillon | 24333718   | Sukhmandhillon2006 |

## Tech Stack

- **Backend:** Python 3, [Flask 3.1](https://flask.palletsprojects.com/),
  Jinja2 templates
- **Frontend:** Bootstrap 5.3 (loaded from CDN), vanilla JavaScript, custom CSS
- **Config:** `python-dotenv` for environment variables

See [requirements.txt](requirements.txt) for the full dependency list.

## Project Structure

```text
.
├── run.py                  # Entry point — creates and runs the Flask app
├── requirements.txt        # Python dependencies
├── .env.example            # Template for environment variables
├── seed.py                 # Seeds the database with sample data
├── app/
│   ├── __init__.py         # App factory and registration of routes/extensions
│   ├── config.py           # App configuration (Flask settings)
│   ├── email.py            # Email sending utilities
│   ├── extensions.py       # Flask extensions (db, login manager, etc.)
│   ├── forms.py            # WTForms form classes for user input and validation
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # Blueprint / route handlers
│   ├── static/
│   │   ├── css/            # style.css, auth.css, debate.css
│   │   └── js/             # profile.js, debate.js, signup.js, login.js, create.js, index.js, user-panel.js
│   └── templates/          # Jinja2 templates (base, index, login, signup, debate)
└── tests/                  # Test suite (unit + Selenium)
```

## Routes

| Path       | Template                                    | Description                                         |
| ---------- | ------------------------------------------- | --------------------------------------------------- |
| `/`                  | [index.html](app/templates/index.html)         | Home feed of debates with pagination and filtering   |
| `/login`             | [login.html](app/templates/login.html)         | Login page                                           |
| `/signup`            | [signup.html](app/templates/signup.html)       | Account creation page                                |
| `/debate/<int:id>`       | [debate.html](app/templates/debate.html)       | Individual debate view (by debate ID)                |
| `/debates/mine`      | [my_activity.html](app/templates/my_activity.html) | My activity (your debates, arguments, saved debates) |

The home page accepts `?filter=<new\|top\|...>` and `?page=<n>` query
parameters; pagination shows 10 debates per page.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ali-fadaee/CITS3403-Group-Project.git
cd CITS3403-Group-Project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Windows (CMD)
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Or create a `.env` file manually with the required variables.
At minimum, provide these keys in your `.env` (see `.env.example`):

```text
DATABASE_URL=sqlite:///app.db
SECRET_KEY=your-secret-key
SECURITY_PASSWORD_SALT=your-password-salt
MAIL_SERVER=...
MAIL_PORT=...
MAIL_USERNAME=...
MAIL_PASSWORD=...
```
.env is ignored by git and not included in the repository.

### 5. Create the instance directory

Create an `instance/` directory in the project root if it does not exist. This is where the SQLite database would be stored by default. The directory is ignored by git and not included in the repository.

```bash
mkdir -p instance
```

### 6. Set up the database
```bash
flask db upgrade
```

### 7. (Optional) Seed the database
Populates the database with sample data for testing purposes only.
```bash
python seed.py
```
### 8. Run the development server

```bash
python run.py
```

The app starts on [http://127.0.0.1:5000](http://127.0.0.1:5000) with debug
mode enabled (auto-reload on file changes).

## Running Tests

All tests are located in the `tests/` folder. Ensure the development server is not running when running tests to avoid port conflicts.

To run Selenium end-to-end tests:

```bash
python -m unittest tests/test_selenium.py
```

To run unit tests:

```bash
python -m unittest tests/test_unit.py
```

To run all tests in the folder:

```bash
python -m unittest discover -s tests
```

## Development Notes

- The app uses SQLAlchemy and Flask-Migrate for persistence; database models
  live in `app/models.py` and migrations are under `migrations/`.
- Static assets are served from `app/static/` and referenced via Flask's
  `url_for('static', ...)`.
- The shared layout, navbar, footer, and the profile/create-debate modals
  live in `app/templates/base.html`; page templates extend it.

## License

See [LICENSE](LICENSE).
