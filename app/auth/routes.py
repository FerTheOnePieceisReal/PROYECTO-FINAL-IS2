from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
MAIN_INDEX_ENDPOINT = 'main.index'
AUTH_LOGIN_ENDPOINT = 'auth.login'

def _has_valid_credentials(user, password):
    return user is not None and user.check_password(password)


def _get_safe_next_page(next_page):
    if not next_page or urlsplit(next_page).netloc != '':
        return url_for(MAIN_INDEX_ENDPOINT)
    return next_page


def _find_user_by_email(email):
    return db.session.scalar(
        sa.select(User).where(User.email == email)
    )


def _create_user_from_form(form):
    user = User(
        username=form.username.data,
        email=form.email.data
    )
    user.set_password(form.password.data)

    db.session.add(user)
    db.session.commit()

    return user


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))

    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        if not _has_valid_credentials(user, form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for(AUTH_LOGIN_ENDPOINT))

        login_user(user, remember=form.remember_me.data)

        next_page = _get_safe_next_page(request.args.get('next'))
        return redirect(next_page)

    return render_template(
        'auth/login.html',
        title=_('Sign In'),
        form=form
    )


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for(MAIN_INDEX_ENDPOINT))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))

    form = RegistrationForm()

    if not form.validate_on_submit():
        return render_template(
            'auth/register.html',
            title=_('Register'),
            form=form
        )

    _create_user_from_form(form)

    flash(_('Congratulations, you are now a registered user!'))
    return redirect(url_for(AUTH_LOGIN_ENDPOINT))


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))

    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = _find_user_by_email(form.email.data)

        if user is not None:
            send_password_reset_email(user)

        flash(
            _('Check your email for the instructions to reset your password')
        )
        return redirect(url_for(AUTH_LOGIN_ENDPOINT))

    return render_template(
        'auth/reset_password_request.html',
        title=_('Reset Password'),
        form=form
    )


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))

    user = User.verify_reset_password_token(token)

    if user is None:
        return redirect(url_for(MAIN_INDEX_ENDPOINT))

    form = ResetPasswordForm()

    if not form.validate_on_submit():
        return render_template(
            'auth/reset_password.html',
            form=form
        )

    user.set_password(form.password.data)
    db.session.commit()

    flash(_('Your password has been reset.'))
    return redirect(url_for(AUTH_LOGIN_ENDPOINT))
