from flask_mail import Message
from flask import current_app, render_template
from . import mail
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, templatem, **kwargs):
    app = current_app._get_current_object()
    msg = Message(app.config['IMOVIES_SUBJECT_PERFIX'] + subject, 
                    sender = app.config['IMOVIES_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(templatem + '.txt', **kwargs)
    msg.html = render_template(templatem + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr