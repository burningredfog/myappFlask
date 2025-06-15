from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, EqualTo, Email, ValidationError
from flask_wtf.file import FileField, FileAllowed

from app.models import User


class PostForm(FlaskForm):
    title = StringField(
        "Tytuł",
        validators=[
            DataRequired(message="Tytuł jest wymagany."),
            Length(max=100)
        ]
    )

    image = FileField('Obrazek', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Tylko obrazki!')
    ])

    # Ukryte pole na dane z Quill.js
    content = HiddenField(
        "Treść",
        validators=[DataRequired(message="Treść jest wymagana.")],
        render_kw={"id": "content-hidden"}  # musi odpowiadać input w HTML
    )

    category_id = SelectField(
        "Kategoria",
        coerce=int,
        validators=[Optional()]
    )

    submit = SubmitField("Zapisz")


class LoginForm(FlaskForm):
    username = StringField(
        "Nazwa użytkownika",
        validators=[
            DataRequired(message="To pole jest wymagane."),
            Length(min=3, max=64, message="Nazwa musi mieć od 3 do 64 znaków."),
        ],
    )
    password = PasswordField(
        "Hasło", validators=[DataRequired(message="To pole jest wymagane.")]
    )
    submit = SubmitField("Zaloguj")


class RegisterForm(FlaskForm):
    username = StringField(
        "Nazwa użytkownika",
        validators=[
            DataRequired(message="To pole jest wymagane."),
            Length(min=3, max=64, message="Nazwa musi mieć od 3 do 64 znaków."),
        ],
    )
    email = StringField(
        "Adres e-mail",
        validators=[
            DataRequired(message="To pole jest wymagane."),
            Email(message="Wprowadź poprawny adres e-mail."),
        ],
    )
    password = PasswordField(
        "Hasło", validators=[DataRequired(message="To pole jest wymagane.")]
    )
    confirm = PasswordField(
        "Potwierdź hasło",
        validators=[
            DataRequired(message="To pole jest wymagane."),
            EqualTo("password", message="Hasła muszą się zgadzać."),
        ],
    )
    submit = SubmitField("Zarejestruj się")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Obecne hasło", validators=[DataRequired()])
    new_password = PasswordField(
        "Nowe hasło", validators=[DataRequired(), Length(min=6)]
    )
    confirm_new_password = PasswordField(
        "Potwierdź nowe hasło",
        validators=[
            DataRequired(),
            EqualTo("new_password", message="Hasła muszą się zgadzać."),
        ],
    )
    submit = SubmitField("Zmień hasło")


class EditProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField("O mnie", validators=[Optional(), Length(max=300)])
    submit = SubmitField("Zapisz zmiany")

    def __init__(self, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Ten adres e-mail jest już zajęty.')


class CategoryForm(FlaskForm):
    name = StringField(
        "Nazwa kategorii",
        validators=[
            DataRequired(message="Nazwa jest wymagana."),
            Length(min=2, max=50),
        ],
    )
    submit = SubmitField("Dodaj kategorię")


class AddUserForm(FlaskForm):
    username = StringField(
        "Nazwa użytkownika", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField("Adres e-mail", validators=[DataRequired(), Email()])
    password = PasswordField("Hasło", validators=[DataRequired(), Length(min=6)])
    is_admin = SelectField(
        "Uprawnienia admina",
        choices=[("0", "Nie"), ("1", "Tak")],
        validators=[DataRequired()],
    )
    submit = SubmitField("Dodaj użytkownika")



class EditUserForm(FlaskForm):
    username = StringField('Nazwa użytkownika', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Administrator')
    submit = SubmitField('Zapisz zmiany')

class ContactForm(FlaskForm):
    name = StringField("Imię i nazwisko", validators=[DataRequired(), Length(max=100)])
    email = StringField("Adres e-mail", validators=[DataRequired(), Email(), Length(max=120)])
    message = TextAreaField("Wiadomość", validators=[DataRequired(), Length(max=2000)])
    submit = SubmitField("Wyślij")

class DeleteImageForm(FlaskForm):
    """Formularz do usuwania zdjęcia z galerii (ochrona CSRF)."""
    submit = SubmitField("Usuń")
