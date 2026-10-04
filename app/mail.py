from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)
import sib_api_v3_sdk

from app.db import get_db


bp = Blueprint('mail', __name__, url_prefix="/")

@bp.route('/', methods=['GET'])
def index():
    db, c = get_db()

    c.execute("SELECT * FROM email")
    mails = c.fetchall()
    
    return render_template('mails/index.html', mails=mails)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        email = request.form.get('email')
        subject = request.form.get('subject')
        content = request.form.get('content')
        errors = []
        if not email:
            errors.append("El campo 'Correo Electrónico' es obligatorio.")
        if not subject:
            errors.append("El campo 'Asunto' es obligatorio.")
        if not content:
            errors.append("El campo 'Contenido' es obligatorio.")

        if len(errors) == 0:
            required_config = (
                current_app.config.get("BREVO_API_KEY"),
                current_app.config.get("BREVO_SENDER_EMAIL"),
                current_app.config.get("BREVO_SENDER_NAME"),
            )
            if not all(required_config):
                flash("Falta configurar las credenciales o el remitente de Brevo.")
            else:
                try:
                    send(email, subject, content)
                except Exception:
                    current_app.logger.exception("Error al enviar correo con Brevo")
                    flash("No se pudo enviar el correo. Revisa la configuración de Brevo e inténtalo de nuevo.")
                else:
                    db, c = get_db()
                    c.execute(
                        "INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)",
                        (email, subject, content),
                    )
                    db.commit()
                    flash("Correo enviado correctamente.")
                    return redirect(url_for('mail.index'))
        else:
            for error in errors:
                flash(error)
    return render_template('mails/create.html')

@bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    db, c = get_db()
    
    if query:
        # Buscamos coincidencias en el correo, el asunto o el contenido
        c.execute(
            "SELECT * FROM email WHERE email LIKE %s OR subject LIKE %s OR content LIKE %s",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
    else:
        c.execute("SELECT * FROM email")
        
    mails = c.fetchall()
    return render_template('mails/_list.html', mails=mails, query=query)


def send(to, subject, content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = current_app.config["BREVO_API_KEY"]

    api = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    message = sib_api_v3_sdk.SendSmtpEmail(
        sender={
            "name": current_app.config["BREVO_SENDER_NAME"],
            "email": current_app.config["BREVO_SENDER_EMAIL"],
        },
        to=[{"email": to}],
        subject=subject,
        text_content=content,
    )
    return api.send_transac_email(message)