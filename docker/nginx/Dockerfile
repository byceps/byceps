FROM nginx

COPY docker/nginx/include/ /etc/nginx/include/
COPY docker/nginx/templates/ /etc/nginx/templates/

COPY byceps/static/ /var/www/byceps/byceps/static/

EXPOSE 80
EXPOSE 443
