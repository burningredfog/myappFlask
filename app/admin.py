from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request
from wtforms import PasswordField
from wtforms.validators import DataRequired, Length
from flask_admin.form import SecureForm


class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for("main.login", next=request.url))


class UserAdmin(SecureModelView):
    form_base_class = SecureForm
    form_columns = ["username", "email", "is_admin"]
    column_searchable_list = ["username", "email"]
    column_filters = ["is_admin"]

    def scaffold_form(self):
        base_form = super().scaffold_form()

        class ExtendedForm(base_form):
            password = PasswordField(
                "Hasło",
                validators=[
                    DataRequired(),
                    Length(min=6, message="Hasło musi mieć co najmniej 6 znaków.")
                ]
            )

        return ExtendedForm

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)


class CategoryAdmin(SecureModelView):
    form_columns = ["name"]
