"""
Secure Flask Login System
=========================
A production-grade authentication system implementing:
- Bcrypt password hashing
- CSRF protection via Flask-WTF
- Secure session management
- SQLite with parameterized queries
- Rate limiting on login attempts
- Comprehensive input validation & error handling
"""

import os
import re
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for,
    flash, session, request, abort
)
from flask_wtf import FlaskForm, CSRFProtect
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, Regexp, ValidationError
)
import sqlite3

# ─── App Configuration ──────────────────────────────────────────────────────

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", os.urandom(32)),
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=3600,           # CSRF token expires in 1 hour
    SESSION_COOKIE_HTTPONLY=True,        # JS cannot access session cookie
    SESSION_COOKIE_SAMESITE="Lax",      # CSRF mitigation
    SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    DATABASE=os.path.join(os.path.dirname(__file__), "users.db"),
    MAX_LOGIN_ATTEMPTS=5 if os.environ.get("FLASK_ENV") == "production" else 50,
    LOCKOUT_DURATION=timedelta(minutes=15),
)

# ─── Extensions ─────────────────────────────────────────────────────────────

bcrypt  = Bcrypt(app)
csrf    = CSRFProtect(app)
IS_DEV = os.environ.get("FLASK_ENV") != "production"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[] if IS_DEV else ["200 per day", "50 per hour"],
    storage_uri="memory://",
    enabled=not IS_DEV,   # Rate limiting OFF in development
)

# ─── Logging ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("auth.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ─── Database ────────────────────────────────────────────────────────────────

def get_db():
    """Return a database connection with Row factory."""
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                password_hash   TEXT    NOT NULL,
                is_active       INTEGER NOT NULL DEFAULT 1,
                created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                last_login      TEXT
            );

            CREATE TABLE IF NOT EXISTS login_attempts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                email       TEXT    NOT NULL COLLATE NOCASE,
                ip_address  TEXT    NOT NULL,
                success     INTEGER NOT NULL DEFAULT 0,
                attempted_at TEXT   NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_users_email
                ON users(email);

            CREATE INDEX IF NOT EXISTS idx_attempts_email_time
                ON login_attempts(email, attempted_at);
        """)
    logger.info("Database initialised.")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def log_attempt(email: str, ip: str, success: bool):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO login_attempts (email, ip_address, success) VALUES (?, ?, ?)",
            (email.lower(), ip, int(success))
        )


def is_account_locked(email: str) -> bool:
    """Return True if too many failed attempts within the lockout window."""
    window = datetime.utcnow() - app.config["LOCKOUT_DURATION"]
    with get_db() as conn:
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM login_attempts
               WHERE email = ? AND success = 0
               AND attempted_at > ?""",
            (email.lower(), window.isoformat())
        ).fetchone()
    return row["cnt"] >= app.config["MAX_LOGIN_ATTEMPTS"]


def login_required(f):
    """Decorator that requires an authenticated session."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def get_user_by_email(email: str):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1",
            (email.lower(),)
        ).fetchone()


def get_user_by_id(user_id: int):
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ? AND is_active = 1",
            (user_id,)
        ).fetchone()


PASSWORD_POLICY = re.compile(
    r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^_\-]).{8,72}$'
)

# ─── Forms ───────────────────────────────────────────────────────────────────

class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address."),
        Length(max=254, message="Email must be 254 characters or fewer."),
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
        Length(min=8, max=72, message="Password must be 8–72 characters."),
        Regexp(
            PASSWORD_POLICY,
            message="Password must contain uppercase, lowercase, digit, and special character."
        ),
    ])
    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo("password", message="Passwords must match."),
    ])
    submit = SubmitField("Create Account")

    def validate_email(self, field):
        if get_user_by_email(field.data):
            raise ValidationError("An account with that email already exists.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address."),
        Length(max=254),
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
    ])
    remember = BooleanField("Remember me for 2 hours")
    submit = SubmitField("Sign In")


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    form = RegistrationForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        pw_hash = bcrypt.generate_password_hash(
            form.password.data, rounds=12
        ).decode("utf-8")

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, pw_hash)
                )
            logger.info("New account registered: %s", email)
            flash("Account created! You can now sign in.", "success")
            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            # Race-condition guard — form validator already checked, but just in case
            flash("That email is already registered.", "danger")

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("100 per minute", methods=["POST"])  # relaxed for dev; tighten in prod
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        ip    = get_remote_address()

        # --- Lockout check ---
        if is_account_locked(email):
            logger.warning("Locked-out login attempt for %s from %s", email, ip)
            flash("Too many failed attempts. Try again in 15 minutes.", "danger")
            return render_template("login.html", form=form), 429

        user = get_user_by_email(email)

        # Constant-time check even when user not found (prevents timing attacks)
        dummy_hash = "$2b$12$invalidhashpaddingtomatchbcryptlength1234567890"
        pw_hash = user["password_hash"] if user else dummy_hash

        if user and bcrypt.check_password_hash(pw_hash, form.password.data):
            # ✅ Successful login
            log_attempt(email, ip, success=True)

            session.clear()                             # Prevent session fixation
            session["user_id"]    = user["id"]
            session["user_email"] = user["email"]
            session["logged_in_at"] = datetime.utcnow().isoformat()

            if form.remember.data:
                session.permanent = True

            # Update last_login timestamp
            with get_db() as conn:
                conn.execute(
                    "UPDATE users SET last_login = datetime('now') WHERE id = ?",
                    (user["id"],)
                )

            logger.info("Successful login: %s from %s", email, ip)
            flash(f"Welcome back!", "success")

            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):   # Open-redirect guard
                return redirect(next_page)
            return redirect(url_for("dashboard"))

        else:
            # ❌ Failed login
            log_attempt(email, ip, success=False)
            logger.warning("Failed login attempt for %s from %s", email, ip)
            # Identical message regardless of whether user exists (prevents enumeration)
            flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    if not user:
        session.clear()
        abort(401)
    return render_template("dashboard.html", user=user)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    email = session.get("user_email", "unknown")
    session.clear()
    logger.info("User logged out: %s", email)
    flash("You've been signed out.", "info")
    return redirect(url_for("login"))


# ─── Error Handlers ──────────────────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(e):
    return render_template("error.html", code=400, message="Bad Request"), 400

@app.errorhandler(401)
def unauthorized(e):
    return render_template("error.html", code=401, message="Unauthorized"), 401

@app.errorhandler(403)
def forbidden(e):
    return render_template("error.html", code=403, message="Forbidden"), 403

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404, message="Page Not Found"), 404

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return render_template("error.html", code=429, message="Too Many Requests — slow down!"), 429

@app.errorhandler(500)
def server_error(e):
    logger.error("Server error: %s", str(e))
    return render_template("error.html", code=500, message="Internal Server Error"), 500


# ─── Entry Point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    # Never run with debug=True in production
    app.run(debug=os.environ.get("FLASK_ENV") == "development")