from flask_mail import Message, Mail
from flask import render_template, current_app

mail = Mail()


def send_mail(recipients, subject, template, **kwargs):
    message = Message(subject=subject, sender=current_app.config['FLASK_MAIL_SENDER'], recipients=[recipients])
    if template.endswith('.txt'):
        message.body = render_template(template, **kwargs)
    else:
        message.html = render_template(template, **kwargs)

    mail.send(message=message)


def send_contact_mail(sender, subject, message):
    message = Message(subject=subject, body=message, sender=sender, recipients=[current_app.config['FLASK_MAIL_SENDER']])
    mail.send(message=message)
