FROM nginx

ADD ./docker/nginx/includes /etc/nginx/includes
ADD ./docker/nginx/templates /etc/nginx/templates

COPY byceps/static/ /var/www/byceps/byceps/static/

EXPOSE 80
EXPOSE 443
