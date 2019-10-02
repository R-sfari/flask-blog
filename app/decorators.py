from flask_login import current_user
from flask import abort
from .models import Permission
from functools import wraps


def permission_required_eq(perm):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            _check_perm(perm)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def permission_required_in(*perms):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            _check_perm(perms)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        _check_perm(Permission.ADMIN)
        return func(*args, **kwargs)
    return decorated_function


def _check_perm(perms):
    if isinstance(perms, list) or isinstance(perms, tuple):
        for perm in perms:
            if not current_user.can(perm):
                abort(403)
    else:
        if not current_user.can(perms):
            abort(403)