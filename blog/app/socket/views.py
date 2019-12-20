from . import socket
from flask import render_template, request, current_app, flash, redirect, url_for, abort
from flask_login import current_user, login_required
from ..models import db, User, Room, RoomUserAssociation
from datetime import datetime, timedelta
from .forms import RoomForm


@socket.route('/rooms')
@login_required
def rooms():
    page = request.args.get('page', type=int, default=1)
    paginator = Room.query.paginate(page, per_page=current_app.config['FLASKY_USER_PER_PAGE'])
    return render_template('socket/rooms-page.html', rooms=paginator.items, paginator=paginator)


@socket.route('/new/room', methods=['GET', 'POST'])
@login_required
def create_room():
    print(request.form)
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(name=form.name.data, author=current_user)
        room.room_users = [RoomUserAssociation(user=user, room=room) for user in [*form.users.data, current_user]]
        db.session.add(room)
        db.session.commit()
        flash('Your room has been created')
    return render_template('socket/create-room-page.html', form=form)


@socket.route('/show/room/<int:room_id>')
@login_required
def show_room(room_id):
    room = Room.query.get_or_404(room_id) if room_id is not None else None
    return render_template('socket/chat-page.html', current_room=room)


@socket.route('/delete/room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.filter_by(id=room_id).first_or_404()
    if room.is_author(current_user) or current_user.is_administrator():

        db.session.delete(room)
        db.session.commit()

        flash('The room has been deleted')
        return redirect(url_for('.rooms', _external=True))

    abort(401)


@socket.route('/online/users')
@login_required
def online_users():
    page = request.args.get('page', type=int, default=1)
    paginator = User.query.filter(User.last_seen > datetime.utcnow() - timedelta(minutes=10)) \
        .paginate(page, per_page=current_app.config['FLASKY_USER_PER_PAGE'])
    return render_template('socket/online-users-page.html', users=paginator.items, paginator=paginator)
