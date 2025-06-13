import logging
from flask import Flask, render_template
from app.extensions import db, login_manager, migrate
from flask_admin import Admin
from app.admin import UserAdmin, SecureModelView, CategoryAdmin
from app.models import User, Post, Category
from app.utils import markdown_filter
from flask_mail import Mail

from flask import current_app
mail = Mail()

import config  # <-- Dodaj import config jeśli go nie było!

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

login_manager.login_view = "main.login"
login_manager.login_message = "Musisz być zalogowany, aby uzyskać dostęp."

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.logger.info(f"App environment: {app.config.get('ENV')}")
    app.logger.info(f"Using database: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    admin_panel = Admin(app, name="Panel Administracyjny", template_mode="bootstrap3")
    admin_panel.add_view(UserAdmin(User, db.session))
    admin_panel.add_view(SecureModelView(Post, db.session))
    admin_panel.add_view(CategoryAdmin(Category, db.session))
    admin_panel.add_view(SecureModelView(Category, db.session, name="Kategorie", endpoint="categories"))

    from app.utils import truncate_html
    app.jinja_env.filters['truncate_html'] = truncate_html

    # Rejestracja blueprintów
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.forms import LoginForm, RegisterForm
    @app.context_processor
    def inject_forms():
        return {
            "login_form": LoginForm(),
            "register_form": RegisterForm()
        }

    # Handlery błędów
    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("500.html"), 500

    # Automatyczne tworzenie tabel w trybie development
    if app.config.get("ENV") == "development":
        with app.app_context():
            db.create_all()
            app.logger.info("Database tables created")

        # Dodaj filtr markdown do Jinja
        app.jinja_env.filters['markdown'] = markdown_filter

    return app

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
