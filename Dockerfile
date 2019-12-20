FROM python:3.6

LABEL MAINTAINER="Rami sfari <rami2sfari@gmail.com>"

# Flask env variables
ENV FLASK_APP manage:app

# Copy the project
COPY ./blog /blog

WORKDIR /blog

# Install dependencies
RUN ["pip", "install", "-r", "requirements/docker.txt"]

# Create New user & group
RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
USER uwsgi

EXPOSE 5000 9191

# Runtime configuration
COPY ./entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
