import os
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates')
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("Falta SECRET_KEY. Configúrala en .env antes de iniciar Flask.")

    app.config.from_mapping(
        BREVO_API_KEY=os.environ.get("BREVO_API_KEY"),
        BREVO_SENDER_EMAIL=os.environ.get("BREVO_SENDER_EMAIL"),
        BREVO_SENDER_NAME=os.environ.get("BREVO_SENDER_NAME", "MailerApp"),
        SECRET_KEY=secret_key, 
        DATABASE_HOST=os.environ.get("FLASK_DATABASE_HOST"),
        DATABASE_PASSWORD=os.environ.get("FLASK_DATABASE_PASSWORD"),
        DATABASE_USER=os.environ.get("FLASK_DATABASE_USER"),
        DATABASE=os.environ.get("FLASK_DATABASE"),
    )
    from . import db

    db.init_app(app)

    from . import mail
    app.register_blueprint(mail.bp)
    


    return app
