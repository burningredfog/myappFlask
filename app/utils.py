from functools import wraps

import bleach
from flask import render_template, current_app
from markdown import markdown


def truncate_html(text, length=100):
    if not text:
        return ""
    truncated = bleach.clean(
        text,
        tags=[],
        attributes={},
        strip=True
    )
    if len(truncated) > length:
        return truncated[:length].rstrip() + "..."
    return truncated



def log_template(template_name):
    """
    Dekorator do logowania użycia danego szablonu
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            current_app.logger.info(f"🔍 Szablon: {template_name}")
            context = view_func(*args, **kwargs)
            return render_template(template_name, **context)

        return wrapper

    return decorator


def render_logged():
    """
    Dekorator: oczekuje, że widok zwróci (template_name, context_dict)
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            result = view_func(*args, **kwargs)

            if not isinstance(result, tuple) or len(result) != 2:
                raise ValueError("Funkcja musi zwracać (template_name, context_dict)")

            template_name, context = result

            if not isinstance(template_name, str):
                raise TypeError("Pierwszy element musi być nazwą szablonu (str)")
            if not isinstance(context, dict):
                raise TypeError("Drugi element musi być dict-em z kontekstem")

            current_app.logger.info(f"🔍 Szablon dynamicznie: {template_name}")
            return render_template(template_name, **context)

        return wrapper

    return decorator


def markdown_filter(text):
    return markdown(text, output_format="html5")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
