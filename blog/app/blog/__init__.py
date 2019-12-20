from flask import Blueprint
from ..models import Permission


blog = Blueprint('blog', __name__)
from . import views