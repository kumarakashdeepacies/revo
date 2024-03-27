FROM python:3.11.8-slim-bookworm

ARG REVOLUTIO_UID="70070"
ARG REVOLUTIO_HOME=/app/

#COPY  build/bin /usr/local/bin
#RUN  /usr/local/bin/user_setup

RUN mkdir -pv /opt/data_store

COPY requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY arrow-flight-server.py arrow-flight-server.py

RUN adduser --quiet "revolutio" --uid "${REVOLUTIO_UID}" --gid "0" --home "${REVOLUTIO_HOME}" && \
    chown -R "revolutio:root" "${REVOLUTIO_HOME}"

RUN chown -R revolutio:root /app /opt/data_store

EXPOSE 8080

USER ${REVOLUTIO_UID}
HEALTHCHECK NONE
ENTRYPOINT ["python3"]
CMD ["arrow-flight-server.py", "--loglevel", "trace"]