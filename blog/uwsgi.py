import os
from app import socket_io, create_app, uploads
from flask_images import resized_img_src

app = create_app(os.getenv('FLASK_CONFIG', 'DEFAULT'))

@app.template_global()
def render_uploaded_file_url(filename, **kwargs):
    if filename:
        return resized_img_src(uploads.url(filename), **kwargs)

    return resized_img_src('no-image-icon.png')

if __name__ == '__main__':
    socket_io.run(app, host="0.0.0.0", port="5000", debug=True)
