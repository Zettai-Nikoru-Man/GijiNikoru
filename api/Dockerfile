FROM python:3

WORKDIR /usr/src/app

# Setup basic tools
RUN apt-get update && \
	apt-get install -y git vim cron mysql-client

# Set files
ADD .bashrc .
RUN cp .bashrc ~/

# Install pip libs
ADD src/app/requirements.txt /usr/src/app
RUN pip install -r requirements.txt

# Set timezone
RUN cp /etc/localtime /etc/localtime.org && \
    ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# Set cron
ADD src/app/config/cron_gijinikoru /etc/cron.d/

# Set uwsgi
ADD src/app/uwsgi/uwsgi.ini /usr/src/app/uwsgi/

# Run app
ENV FLASK_APP /usr/src/app/app.py
CMD uwsgi --ini /usr/src/app/uwsgi/uwsgi.ini
