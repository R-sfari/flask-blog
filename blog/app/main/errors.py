from flask import render_template
from . import main


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('errors/404-page.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('errors/500-page.html'), 500


@main.app_errorhandler(403)
def internal_server_error(e):
    return render_template('errors/403-page.html'), 403


@main.app_errorhandler(401)
def internal_server_error(e):
    return render_template('errors/401-page.html'), 401
