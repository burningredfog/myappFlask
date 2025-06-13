import click
import os
from app import create_app, db
from app.models import User
from config import DevelopmentConfig, ProductionConfig

# wybór konfiguracji na podstawie FLASK_ENV
env = os.getenv('FLASK_ENV', 'production')
config = DevelopmentConfig if env == 'development' else ProductionConfig

app = create_app(config)

@app.cli.command("create-admin")
@click.argument("username")
@click.password_option("--password", prompt=True, confirmation_prompt=True)
def create_admin(username, password):
    """Utwórz nowego użytkownika-admin."""
    if User.query.filter_by(username=username).first():
        click.echo(f"⚠️  Użytkownik '{username}' już istnieje.")
        return
    user = User(username=username, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f"✅ Użytkownik-admin '{username}' utworzony pomyślnie.")

@app.cli.command("create-category")
@click.argument("name")
def create_category(name):
    """Utwórz nową kategorię."""
    from app.models import Category

    if Category.query.filter_by(name=name).first():
        click.echo(f"⚠️  Kategoria '{name}' już istnieje.")
        return

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    click.echo(f"✅ Kategoria '{name}' została utworzona.")

