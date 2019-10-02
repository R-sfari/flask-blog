import os
from app import socket_io, create_app

app = create_app(os.getenv('FLASK_CONFIG', 'default'))

if __name__ == '__main__':
    socket_io.run(app)
