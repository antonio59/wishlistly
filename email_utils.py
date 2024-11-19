from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_password_reset_email(user_email, token):
    send_email(
        'Reset Your Password',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user_email],
        text_body=render_template('email/reset_password.txt',
                                token=token),
        html_body=render_template('email/reset_password.html',
                                token=token)
    )

def send_verification_email(user_email, token):
    send_email(
        'Verify Your Email',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user_email],
        text_body=render_template('email/verify_email.txt',
                                token=token),
        html_body=render_template('email/verify_email.html',
                                token=token)
    )

def send_wishlist_shared_notification(user_email, sharer_name, wishlist_title, wishlist_url):
    send_email(
        f'{sharer_name} shared a wishlist with you!',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user_email],
        text_body=render_template('email/wishlist_shared.txt',
                                sharer_name=sharer_name,
                                wishlist_title=wishlist_title,
                                wishlist_url=wishlist_url),
        html_body=render_template('email/wishlist_shared.html',
                                sharer_name=sharer_name,
                                wishlist_title=wishlist_title,
                                wishlist_url=wishlist_url)
    )

def send_item_purchased_notification(user_email, purchaser_name, item_name, wishlist_title):
    send_email(
        'An item from your wishlist was purchased!',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user_email],
        text_body=render_template('email/item_purchased.txt',
                                purchaser_name=purchaser_name,
                                item_name=item_name,
                                wishlist_title=wishlist_title),
        html_body=render_template('email/item_purchased.html',
                                purchaser_name=purchaser_name,
                                item_name=item_name,
                                wishlist_title=wishlist_title)
    )

def send_price_alert(user_email, item_name, old_price, new_price, store_name, item_url):
    send_email(
        f'Price Drop Alert: {item_name}',
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[user_email],
        text_body=render_template('email/price_alert.txt',
                                item_name=item_name,
                                old_price=old_price,
                                new_price=new_price,
                                store_name=store_name,
                                item_url=item_url),
        html_body=render_template('email/price_alert.html',
                                item_name=item_name,
                                old_price=old_price,
                                new_price=new_price,
                                store_name=store_name,
                                item_url=item_url)
    )
