from os import path, environ, curdir


class Config:
    SECRET_KEY = environ.get('SECRET_KEY', 'hard to guess string')

    MAIL_SERVER = environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')

    FLASKY_POSTS_PER_PAGE = 9
    FLASKY_FOLLOWER_PER_PAGE = 10
    FLASKY_FOLLOWED_PER_PAGE = 10
    FLASKY_COMMENT_PER_PAGE = 10
    FLASKY_USER_PER_PAGE = 9

    FLASK_MAIL_SENDER = environ.get('FLASK_MAIL_SENDER', 'Flask Admin <flask@example.com>')
    FLASK_ADMIN = environ.get('FLASK_ADMIN')

    TOP_LEVEL_DIR = environ.get('MEDIA_DIR', path.abspath(path.dirname(path.dirname(__file__))))
    UPLOADS_DEFAULT_DEST = path.join(TOP_LEVEL_DIR, 'media')
    UPLOADED_IMAGES_DEST = path.join(TOP_LEVEL_DIR, 'media', 'uploads')
    IMAGES_PATH = ['media/uploads']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URL', 'sqlite:///' +  path.join(Config.TOP_LEVEL_DIR, 'db', 'data-dev.sqlite'))
    SQLALCHEMY_SLOW_DB_QUERY_TIME = 0.5

    @classmethod
    def init_app(cls, app):
        from flask_debugtoolbar import DebugToolbarExtension

        debug = DebugToolbarExtension()
        debug.init_app(app)

        @app.after_app_request
        def after_request(response):
            for query in get_debug_queries():
                if query.duration >= current_app.config['FLASK_SLOW_DB_QUERY_TIME']:
                    current_app.logger.warning('Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n' % (query.statement, query.parameters, query.duration, query.context))
            return response


class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL', 'sqlite:///' +  path.join(Config.TOP_LEVEL_DIR, 'db', 'data-test.sqlite'))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL', 'sqlite:///' +  path.join(Config.TOP_LEVEL_DIR, 'db', 'data.sqlite'))

    @classmethod
    def init_app(cls, app):
        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'DEV': DevelopmentConfig,
    'TEST': TestingConfig,
    'PROD': ProductionConfig,
    'DEFAULT': DevelopmentConfig
}
