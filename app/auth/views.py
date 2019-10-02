from . import auth
from flask import render_template, request, flash, redirect, url_for, current_app
from .forms import LoginForm, RegistrationForm, ResetPasswordForm, ForgotPasswordForm, EditProfileForm, EditUserForm
from ..models import User, Post
from app import db
from ..utils import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from ..decorators import admin_required
from datetime import datetime


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        db.session.commit()


@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.username == form.username.data, User.email == form.username.data)).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            redirect_url = request.args.get('next')
            if redirect_url is None or not redirect_url.startswith('/'):
                redirect_url = url_for('blog.index_posts')
            return redirect(redirect_url)

        flash('Invalid username or password.')
    return render_template('auth/login-page.html', form=form)


@auth.route('/account/recover', methods=['GET', 'POST'])
def account_recover():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter(or_(User.username == form.email.data, User.email == form.email.data)).first()
        if user is not None:
            token = user.generate_token(3600)
            send_mail(user.email, 'Resetting Password', 'auth/email/resetting.html', user=user, token=token)

        flash('An email has been sent. It contains a link you must click to reset your password.'
              'If you don\'t get an email check your spam folder or try again.')

    return render_template('auth/account-recover-page.html', form=form)


@auth.route('/account/reset/<string:token>', methods=['GET', 'POST'])
def account_reset(token):
    user_id = User.extract_token(token)
    user = User.query.get(int(user_id)) if user_id is not None else None
    if user is None:
        return redirect(url_for('.account_recover'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data
        db.session.commit()
        login_user(user, False)
        flash('The password has been reset successfully')
        return redirect(url_for('blog.index'))

    return render_template('auth/reset-password-page.html', form=form, user=user)


@auth.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data,
                    first_name=form.first_name.data, last_name=form.last_name.data, news_letter=form.news_letter.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_token()
        send_mail(user.email, 'Confirm your account', 'auth/email/confirm.html', user=user, token=token)
        flash('An email has been sent to {0}. It contains an activation link you must click to activate your account.'.format(user.email))
        return redirect(url_for('.login'))

    return render_template('auth/registration-page.html', form=form)


@auth.route('/resend/confirmation', methods=['GET'])
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    send_mail(current_user.email, 'Confirm your account', 'auth/email/confirm.html', user=current_user, token=token)
    flash('An email has been sent to {0}. It contains an activation link you must click to activate your account.'.format(current_user.email))
    return redirect(url_for('main.index'))


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.login'))


@auth.route('/confirm/<string:token>', methods=['GET'])
@login_required
def confirm(token):
    if not current_user.confirmed and current_user.check_token(token):
        current_user.confirmed = True
        db.session.commit()
        flash('You have confirmed your account. Thanks!')

    if current_user.confirmed:
        return redirect(url_for('.confirmed'))

    flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('blog.index'))


@auth.route('/confirmed')
@login_required
def confirmed():
    return render_template('auth/confirmed-page.html')


@auth.route('/profile/<string:username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('auth/profile-page.html', user=user)


@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def setting():
    form = EditProfileForm()
    if form.validate_on_submit() and current_user.check_password(form.current_password.data):
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.about_me = form.about_me.data
        current_user.phone = form.phone.data
        current_user.birthday = form.birthday.data
        current_user.address = form.address.data
        db.session.add(current_user._get_current_object())
        db.session.commit()

    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.about_me.data = current_user.about_me
    form.phone.data = current_user.phone
    form.birthday.data = current_user.birthday
    form.address.data = current_user.address

    return render_template('auth/edit-profile-page.html', user=current_user, form=form)


@auth.route('/edit-profile/<int:identifier>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(identifier):
    user = User.query.get_or_404(identifier)
    form = EditUserForm()
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.about_me = form.about_me.data
        user.phone = form.phone.data
        user.birthday = form.birthday.data
        user.address = form.address.data
        user.role = form.role.data
        user.email = form.email.data
        user.username = form.username.data
        if form.password.data:
            user.password = form.password.data
        db.session.add(user)
        db.session.commit()

    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.about_me.data = user.about_me
    form.phone.data = user.phone
    form.birthday.data = user.birthday
    form.address.data = user.address
    form.role.data = user.role
    form.email.data = user.email
    form.username.data = user.username

    return render_template('auth/edit-user-page.html', user=user, form=form)


@auth.route('/delete-user/<int:identifier>', methods=['POST'])
@login_required
def delete_user(identifier):
    user = User.query.get_or_404(identifier)
    if not user.is_administrator():
        user.deleted_at = datetime.utcnow()
        db.session.commit()
        flash('The given user is deleted successfully')
    else:
        flash('You can not delete an administrator')

    return redirect(url_for('.index_users'))


@auth.route('/undelete-user/<int:identifier>', methods=['POST'])
@login_required
def undelete_user(identifier):
    user = User.query.get_or_404(identifier)
    if not user.is_administrator():
        user.deleted_at = None
        db.session.commit()
        flash('The given user is un deleted successfully')
    else:
        flash('You can not delete an administrator')

    return redirect(url_for('.index_users'))


@auth.route('/users')
@login_required
@admin_required
def index_users():
    page = request.args.get('page', 1, type=int)
    paginator = User.query.paginate(page, per_page=current_app.config['FLASKY_USER_PER_PAGE'], error_out=True)
    return render_template('auth/users-page.html', users=paginator.items, paginator=paginator)