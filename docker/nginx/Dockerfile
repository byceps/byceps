FROM nginx

ADD ./docker/nginx/includes /etc/nginx/include
ADD ./docker/nginx/templates /etc/nginx/templates

COPY byceps/static/ /var/www/byceps/byceps/static/

EXPOSE 80
EXPOSE 443
