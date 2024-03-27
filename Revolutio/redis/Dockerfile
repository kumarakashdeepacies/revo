FROM redis:7.2.4-bookworm

ARG REVOLUTIO_UID="70070"
ARG REVOLUTIO_HOME=/data

RUN adduser --quiet "revolutio" --uid "${REVOLUTIO_UID}" --gid "0" --home "${REVOLUTIO_HOME}" && \
    chown -R "revolutio:root" "${REVOLUTIO_HOME}"

USER ${REVOLUTIO_UID}
HEALTHCHECK NONE