FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY index.html /usr/share/nginx/html/index.html
COPY 2026-dashboard.html /usr/share/nginx/html/2026-dashboard.html
COPY .nojekyll /usr/share/nginx/html/.nojekyll

EXPOSE 80
