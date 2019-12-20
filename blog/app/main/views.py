from . import main
from .forms import ContactForm
from ..utils import send_contact_mail
from flask import redirect, url_for, flash, render_template


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        send_contact_mail(form.email.data, '{0} from {1}'.format(form.subject.data, form.name.data), form.message.data)
        flash('Your message has been sent, thank you.')
        return redirect(url_for('.contact', _external=True))

    return render_template('main/contact-page.html', form=form)


@main.route('/')
def index():
    return render_template('main/index-page.html')
