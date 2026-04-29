# CITS3403-Group-Project

~/debate-app

A web application for creating and participating in debates. Users post statements to begin a debate - adding tags categorisation tags to enable search. Debates are participate in by posting *for* or *against* arguments, and 'upvoting' the arguments of others that they find compelling. User have ccustomisable profiles so that they can provide others with their personal context.

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
├── app/
│   ├── __init__.py         # App factory and route definitions
│   ├── static/
│   │   ├── css/            # style.css, auth.css, debate.css
│   │   └── js/             # profile.js, debate.js, signup.js
│   └── templates/          # Jinja2 templates (base, index, login, signup, debate)
└── tests/                  # Test suite
```

## Routes

| Path       | Template                                    | Description                                         |
| ---------- | ------------------------------------------- | --------------------------------------------------- |
| `/`        | [index.html](app/templates/index.html)      | Home feed of debates with pagination and filtering  |
| `/login`   | [login.html](app/templates/login.html)      | Login page                                          |
| `/signup`  | [signup.html](app/templates/signup.html)    | Account creation page                               |
| `/debate`  | [debate.html](app/templates/debate.html)    | Individual debate view                              |

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

### 5. Run the development server

```bash
python run.py
```

The app starts on [http://127.0.0.1:5000](http://127.0.0.1:5000) with debug
mode enabled (auto-reload on file changes).

## Running Tests

```bash
python -m unittest discover -s tests
```

## Development Notes

- The home feed currently uses an in-memory list of mock debates defined in
  [app/\_\_init\_\_.py](app/__init__.py). Persistence (database, auth, voting)
  has not yet been wired up.
- Static assets are served from `app/static/` and referenced via Flask's
  `url_for('static', ...)`.
- The shared layout, navbar, footer, and the profile / create-debate modals
  live in [base.html](app/templates/base.html); page templates extend it.

## License

See [LICENSE](LICENSE).
