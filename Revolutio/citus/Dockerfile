FROM debian:bullseye-slim
WORKDIR /var/lib/postgresql

ARG VERSION=11.2.0
ENV CITUS_VERSION ${VERSION}.citus-1

# Volume mounts should happen on /var/lib/postgresql and /var/run/postgresql
#
# We don't use VOLUME declarations like in the offical image as
# it just causes file permission issues and slow start times if we try
# to fix permissions during boot.
#
# And they won't work well with pg_upgrade and the --link argument,
# which greatly improves the upgrade speed of major versions.
ADD ./scripts /scripts
RUN /scripts/postgres-install && rm /scripts/postgres-install

USER postgres
ENV PG_MAJOR=15
ENV PGUSER=postgres
ENV PGHOST /var/run/postgresql
ENV PGPORT 5432
ENV PGDATA /var/lib/postgresql/data
ENV PAGER 'pspg -s 0'
ENV PATH="$PATH:/usr/lib/postgresql/15/bin:/scripts"
ENV WALG_CONFIG_FILE=/var/lib/postgresql/.walg.json
ENV LANG en_US.utf8

COPY --from=postgres:15 /usr/local/bin/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

ADD ./scripts /scripts

# add health check script
COPY pg_healthcheck /

# add scripts to run after initdb
COPY ./scripts/001-create-citus-extension.sql /docker-entrypoint-initdb.d/

# entry point unsets PGPASSWORD, but we need it to connect to workers
# https://github.com/docker-library/postgres/blob/33bccfcaddd0679f55ee1028c012d26cd196537d/12/docker-entrypoint.sh#L303

HEALTHCHECK --interval=4s --start-period=6s CMD ./pg_healthcheck

STOPSIGNAL SIGINT
ENTRYPOINT ["/scripts/entrypoint"]
CMD ["postgres"]