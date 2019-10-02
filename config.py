from os import path, environ, curdir
basedir = path.abspath(path.dirname(__file__))


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
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_SLOW_DB_QUERY_TIME = 0.5
    FLASK_MAIL_SENDER = 'Flasky Admin <flask@example.com>'
    FLASK_ADMIN = environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOP_LEVEL_DIR = path.abspath(curdir)
    UPLOADS_DEFAULT_DEST = TOP_LEVEL_DIR + '/app/media/'
    UPLOADED_IMAGES_DEST = TOP_LEVEL_DIR + '/app/media/images/'
    IMAGES_PATH = ['media/images']

    @classmethod
    def init_app(cls, app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URL', 'sqlite:///' + path.join(basedir, 'data-dev.sqlite'))

    @classmethod
    def init_app(cls, app):
        from flask_debugtoolbar import DebugToolbarExtension

        debug = DebugToolbarExtension()
        debug.init_app(app)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL', 'sqlite://' +  path.join(basedir, 'data-test.sqlite'))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL', 'sqlite:///' + path.join(basedir, 'data.sqlite'))
    LOGGING_FILENAME = 'prod.log'

    @classmethod
    def init_app(cls, app):
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(cls.LOGGING_FILENAME, maxBytes=1024 * 1024 * 100, backupCount=20)
        file_handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
