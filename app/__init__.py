from flask import Flask
from datetime import datetime
from dotenv import load_dotenv
import os

def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except Exception:
            return value
    return value.strftime(format)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'

    load_dotenv()

    # ثبت blueprintها
    from .routes import bp
    app.register_blueprint(bp)

    # ثبت فیلتر datetimeformat
    app.jinja_env.filters['datetimeformat'] = datetimeformat

    return app
