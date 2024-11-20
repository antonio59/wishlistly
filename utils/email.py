from flask import current_app, render_template, url_for
from flask_mail import Mail, Message
from threading import Thread

mail = Mail()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, template, **kwargs):
    """Send an email using a template"""
    msg = Message(
        subject=subject,
        recipients=recipients,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    msg.html = render_template(template, **kwargs)
    
    # Send email asynchronously
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()

def send_password_reset_email(user, token):
    """Send password reset email to user"""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    send_email(
        subject='Reset Your Wishlistly Password',
        recipients=[user.email],
        template='email/reset_password.html',
        user=user,
        reset_url=reset_url
    )
