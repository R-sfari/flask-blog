import os
from app import create_app, db, uploads, socket_io
from app.models import User, Role, Permission
from app import fixtures
from flask_images import resized_img_src
from flask_sqlalchemy import get_debug_queries
from flask import current_app


app = create_app(os.getenv('FLASK_CONFIG', 'default'))


@app.cli.command('load-fixtures')
def load_fixtures():
    fixtures.exec_fixtures()


# @app.after_app_request
# def after_request(response):
#     for query in get_debug_queries():
#         if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
#             current_app.logger.warning('Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % (query.statement, query.parameters, query.duration, query.context))
#     return response


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.shell_context_processor
def shell_context():
    return dict(db=db, Role=Role, User=User, Permission=Permission)


@app.template_global()
def render_uploaded_file_url(filename, **kwargs):
    if filename:
        return resized_img_src(uploads.url(filename), **kwargs)

    return resized_img_src('no-image-icon.png')


if __name__ == '__main__':
    socket_io.run(app, debug=True)
