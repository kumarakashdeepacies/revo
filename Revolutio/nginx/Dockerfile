ARG VERSION=stable-alpine
FROM nginx:${VERSION} as builder

ENV MORE_HEADERS_VERSION=0.34
ENV MORE_HEADERS_GITREPO=openresty/headers-more-nginx-module

# Download sources
RUN wget "http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz" -O nginx.tar.gz && \
    wget "https://github.com/${MORE_HEADERS_GITREPO}/archive/v${MORE_HEADERS_VERSION}.tar.gz" -O extra_module.tar.gz

# For latest build deps, see https://github.com/nginxinc/docker-nginx/blob/master/mainline/alpine/Dockerfile
RUN  apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    make \
    openssl-dev \
    pcre-dev \
    zlib-dev \
    linux-headers \
    libxslt-dev \
    gd-dev \
    geoip-dev \
    perl-dev \
    libedit-dev \
    mercurial \
    bash \
    alpine-sdk \
    findutils

SHELL ["/bin/ash", "-eo", "pipefail", "-c"]

RUN rm -rf /usr/src/nginx /usr/src/extra_module && mkdir -p /usr/src/nginx /usr/src/extra_module && \
    tar -zxC /usr/src/nginx -f nginx.tar.gz && \
    tar -xzC /usr/src/extra_module -f extra_module.tar.gz

WORKDIR /usr/src/nginx/nginx-${NGINX_VERSION}

# Reuse same cli arguments as the nginx:alpine image used to build
RUN CONFARGS=$(nginx -V 2>&1 | sed -n -e 's/^.*arguments: //p') && \
    sh -c "./configure --with-compat $CONFARGS --add-dynamic-module=/usr/src/extra_module/*" && make modules


# Production container starts here
FROM nginx:${VERSION}

COPY --from=builder /usr/src/nginx/nginx-${NGINX_VERSION}/objs/*_module.so /etc/nginx/modules/

ARG UID=101
ARG GID=101
RUN apk del libcurl curl

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx_dev.conf /etc/nginx/
COPY blockuseragents.rules /etc/nginx/conf.d

RUN chown -R nginx:nginx /var/cache/nginx && \
        chown -R nginx:nginx /var/log/nginx && \
        chown -R nginx:nginx /etc/nginx/conf.d && \
        chown -R nginx:nginx /etc/ssl/

RUN chmod 755 -R /var/cache/nginx && \
        chmod 755 -R /var/log/nginx && \
        chmod 755 -R /etc/ssl/

RUN touch /var/run/nginx.pid && \
        chown -R nginx:nginx /var/run/nginx.pid

USER nginx
HEALTHCHECK NONE