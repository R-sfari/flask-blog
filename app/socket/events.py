from flask_socketio import emit, join_room, leave_room, send, rooms
from .. import socket_io
from flask_login import current_user, login_required


@socket_io.on('join')
@login_required
def on_join(data):
    room = data['room']
    join_room(room)
    emit('status', '{} has joined the room.'.format(current_user.full_name()), room=room)


@socket_io.on('message')
@login_required
def handle_message(data):
    message = data['message']
    room = data['room']
    emit('text', {'username': current_user.username, 'user_full_name': current_user.full_name(), 'message': message}, room=room)


@socket_io.on('leave')
@login_required
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('status', '{} has left the room.'.format(current_user.full_name()), room=room)