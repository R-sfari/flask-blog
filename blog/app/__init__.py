from flask import Flask, render_template
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_datepicker import datepicker
from flask_wtf.csrf import CSRFProtect
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_images import Images
from flask_socketio import SocketIO


images = Images()
uploads = UploadSet('images', IMAGES)
mail = Mail()
moment = Moment()
db = SQLAlchemy(session_options={"autoflush": False})
login_manager = LoginManager()
csrf = CSRFProtect()
socket_io = SocketIO()
migrate = Migrate()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    datepicker(app)
    configure_uploads(app, uploads)
    db.init_app(app)
    migrate.init_app(app, db)
    images.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socket_io.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint, url_prefix='/blog')

    from .socket import socket as socket_blueprint
    app.register_blueprint(socket_blueprint, url_prefix='/socket')

    return app
