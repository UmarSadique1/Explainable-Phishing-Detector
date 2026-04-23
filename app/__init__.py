from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-key-change-this-later"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import User
    from .routes import main
    from .auth_routes import auth

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()
        seed_admin_user()

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


def seed_admin_user():
    from .models import User

    admin_email = "admin@phishguard.co.uk"

    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        return

    admin_user = User(
        full_name="PhishGuard Admin",
        email=admin_email,
        role="admin"
    )
    admin_user.set_password("PhishGuard123!")

    db.session.add(admin_user)
    db.session.commit()