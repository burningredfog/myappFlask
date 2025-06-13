import os
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse, urljoin

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, \
    current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from werkzeug.utils import secure_filename

from app import db, mail
from app.forms import (
    PostForm, LoginForm, RegisterForm,
    ChangePasswordForm, EditProfileForm,
    AddUserForm, CategoryForm, ContactForm, EditUserForm
)
from app.models import Post, User, Category
from app.pagination import Pagination
from app.utils import log_template, render_logged, allowed_file

main = Blueprint("main", __name__)


@main.context_processor
def inject_current_year():
    return {"current_year": datetime.now().year}


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


### --- STRONA GŁÓWNA + KATEGORIE --- ###

@main.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    per_page = 6

    categories = Category.query.order_by(Category.name).all()
    all_posts = Post.query.order_by(Post.created_at.desc()).all()
    total = len(all_posts)
    start = (page - 1) * per_page
    end = start + per_page
    items = all_posts[start:end]

    pagination = Pagination(page=page, per_page=per_page, total=total, items=items)
    pagination.endpoint = "main.index"

    return render_template(
        "index.html",
        posts=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=None
    )


@main.route("/category/<int:category_id>")
def category(category_id):
    page = request.args.get("page", 1, type=int)
    per_page = 6

    categories = Category.query.order_by(Category.name).all()
    selected_category = Category.query.get_or_404(category_id)
    posts_query = Post.query.filter_by(category_id=category_id).order_by(
        Post.created_at.desc())
    all_posts = posts_query.all()
    total = len(all_posts)
    start = (page - 1) * per_page
    end = start + per_page
    items = all_posts[start:end]

    pagination = Pagination(page=page, per_page=per_page, total=total, items=items)
    pagination.endpoint = "main.category"

    return render_template(
        "index.html",
        posts=pagination.items,
        pagination=pagination,
        categories=categories,
        selected_category=selected_category
    )


### --- STRONY INFORMACYJNE --- ###

@main.route("/about")
def about():
    return render_template("about.html")


### --- AUTH --- ###

@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.admin_panel"))

    form = LoginForm()
    show_modal_login = False

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            return redirect(url_for("main.admin_panel"))
        flash("Nieprawidłowa nazwa użytkownika lub hasło.", "danger")
        show_modal_login = True
    elif request.method == "POST":
        show_modal_login = True

    return render_template(
        "base2.html",
        login_form=form,
        register_form=RegisterForm(),
        show_modal_login=show_modal_login
    )


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    show_modal_register = False

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Użytkownik już istnieje.", "danger")
            show_modal_register = True
        elif User.query.filter_by(email=form.email.data).first():
            flash("Adres e-mail jest już zajęty.", "danger")
            show_modal_register = True
        else:
            user = User(username=form.username.data)
            user.email = form.email.data
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Rejestracja zakończona pomyślnie. Możesz się teraz zalogować.",
                  "success")
            return redirect(url_for("main.index"))

    elif request.method == "POST":
        show_modal_register = True

    return render_template(
        "base2.html",
        register_form=form,
        login_form=LoginForm(),
        show_modal_register=show_modal_register
    )


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Wylogowano.", "info")
    return redirect(url_for("main.index"))


### --- PANEL ADMINA --- ###

@main.route("/admin")
@login_required
def admin_panel():
    return render_template("admin.html")


@main.route("/admin/posts")
@login_required
def posts_panel():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("posts_panel.html", posts=posts)


### --- POSTY --- ###

@main.route("/post/add", methods=["GET", "POST"])
@login_required
def add_post():
    form = PostForm()
    form.category_id.choices = [(0, "— brak —")] + [(c.id, c.name) for c in
                                                    Category.query.all()]

    if form.validate_on_submit():
        image_filename = None
        image_file = form.image.data
        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            if allowed_file(filename):
                upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                           filename)
                image_file.save(upload_path)
                image_filename = filename
            else:
                flash("Nieprawidłowy format pliku!", "danger")
                return render_template("add_post.html", form=form, quill_enabled=True)

        new_post = Post(
            title=form.title.data,
            content=request.form.get("content"),
            category_id=form.category_id.data or None,
            author_id=current_user.id,
            image_filename=image_filename
        )
        db.session.add(new_post)
        db.session.commit()
        flash("Post został dodany!", "success")
        return redirect(url_for("main.posts_panel"))

    return render_template("add_post.html", form=form, quill_enabled=True)


@main.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", post=post)


@main.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = PostForm(obj=post)
    form.category_id.choices = [(0, "— brak —")] + [(c.id, c.name) for c in
                                                    Category.query.all()]

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = request.form.get("content")
        post.category_id = form.category_id.data or None
        db.session.commit()
        flash("Post został zaktualizowany.", "success")
        return redirect(url_for("main.posts_panel"))

    return render_template("edit_post.html", form=form, post=post, quill_enabled=True)


@main.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post został usunięty.", "success")
    return redirect(url_for("main.posts_panel"))


### --- PROFIL --- ###
@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_email=current_user.email)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        try:
            db.session.commit()
            flash('Zmiany zostały zapisane.', 'success')
            return redirect(url_for('main.profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Wystąpił błąd podczas zapisywania zmian: {e}', 'danger')
    elif request.method == 'GET':
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    return render_template('edit_profile.html', form=form, quill_enabled=True)


@main.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash("Nieprawidłowe aktualne hasło.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Hasło zostało zmienione.", "success")
            return redirect(url_for("main.index"))
    return render_template("change_password.html", form=form)


### --- KATEGORIE --- ###
@main.route("/category/add", methods=["GET", "POST"])
@login_required
def add_category():
    if not current_user.is_admin:
        abort(403)
    form = CategoryForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        existing = Category.query.filter_by(name=name).first()
        if existing:
            flash("Taka kategoria już istnieje.", "error")
        else:
            new_cat = Category(name=name)
            db.session.add(new_cat)
            db.session.commit()
            flash(f'Kategoria "{name}" została dodana.', "success")
            return redirect(url_for("main.admin_panel"))
    return render_template("add_category.html", form=form)


### --- UŻYTKOWNICY (ADMIN) --- ###

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@main.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template("user_list.html", users=users)


@main.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.is_admin = form.is_admin.data
        db.session.commit()
        flash('Dane użytkownika zostały zaktualizowane.', 'success')
        return redirect(url_for('main.admin_users'))
    return render_template('edit_user.html', form=form)


@main.route("/admin/users/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Nie możesz usunąć samego siebie!", "error")
        return redirect(url_for("main.admin_users"))
    db.session.delete(user)
    db.session.commit()
    flash(f"Użytkownik {user.username} został usunięty.", "success")
    return redirect(url_for("main.admin_users"))


@main.route("/admin/add_user", methods=["GET", "POST"])
@login_required
def add_user():
    if not current_user.is_admin:
        abort(403)

    current_app.logger.info("🔍 Szablon: add_user.html")

    form = AddUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            is_admin=bool(int(form.is_admin.data)),
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Użytkownik został dodany", "success")
        return redirect(url_for("main.admin_panel"))

    return render_template("add_user.html", form=form)


# --- PANEL KATEGORII (ADMIN) ---

@main.route("/admin/categories")
@login_required
def admin_categories():
    if not current_user.is_admin:
        abort(403)
    categories = Category.query.order_by(Category.name).all()
    return render_template("admin_categories.html", categories=categories)


@main.route("/admin/categories/edit/<int:category_id>", methods=["GET", "POST"])
@login_required
def edit_category(category_id):
    if not current_user.is_admin:
        abort(403)
    selected_category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=selected_category)
    if form.validate_on_submit():
        name = form.name.data.strip()
        if Category.query.filter(Category.id != selected_category.id,
                                 Category.name == name).first():
            flash("Kategoria o takiej nazwie już istnieje.", "error")
        else:
            selected_category.name = name
            db.session.commit()
            flash("Nazwa kategorii została zmieniona.", "success")
            return redirect(url_for("main.admin_categories"))
    elif request.method == "GET":
        form.name.data = selected_category.name
    return render_template("edit_category.html", form=form, category=selected_category)


@main.route("/admin/categories/delete/<int:category_id>", methods=["POST"])
@login_required
def delete_category(category_id):
    if not current_user.is_admin:
        abort(403)
    selected_category = Category.query.get_or_404(category_id)
    if selected_category.posts.count() > 0:
        flash("Nie można usunąć kategorii, która zawiera posty.", "error")
        return redirect(url_for("main.admin_categories"))
    db.session.delete(selected_category)
    db.session.commit()
    flash("Kategoria została usunięta.", "success")
    return redirect(url_for("main.admin_categories"))


### --- KONTAKT --- ###
@main.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    recipient = current_app.config["MAIL_RECIPIENT"]
    if form.validate_on_submit():
        msg = Message(
            subject=f"Nowa wiadomość z formularza kontaktowego od {form.name.data}",
            sender=form.email.data,
            recipients=[recipient],
            body=(
                f"Imię i nazwisko: {form.name.data}\n"
                f"Email: {form.email.data}\n\n"
                f"Wiadomość:\n{form.message.data}"
            )
        )
        try:
            mail.send(msg)
            flash("Wiadomość została wysłana!", "success")
        except Exception as e:
            flash(f"Błąd podczas wysyłki: {e}", "danger")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)


### --- TESTY/DEV --- ###
@main.route("/test")
def test_layout():
    return render_template("test.html")


@main.route("/test2")
@log_template("test.html")
def test_view():
    return {"some_data": "Hello from decorated view!"}


@main.route("/test3")
@render_logged()
def test_dynamic():
    context = {"msg": "Cześć!"}
    return "test.html", context
