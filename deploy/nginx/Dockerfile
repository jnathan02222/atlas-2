FROM nginx:trixie-perl
COPY default.conf.template /etc/nginx/templates/default.conf.template
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-venv libaugeas-dev gcc
RUN apt-get remove certbot
RUN python3 -m venv /opt/certbot/
RUN /opt/certbot/bin/pip install --upgrade pip
RUN /opt/certbot/bin/pip install certbot certbot-nginx
RUN ln -s /opt/certbot/bin/certbot /usr/bin/certbot