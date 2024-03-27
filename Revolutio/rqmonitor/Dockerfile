FROM python:3.10.2-slim-bullseye

ARG REVOLUTIO_UID="70070"
ARG REVOLUTIO_HOME=/app/

RUN apt-get update && apt-get install -y --no-install-recommends \
		gcc \
		libc-dev \
	&& rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN chmod +x /app/start && \
pip install -r requirements.txt

RUN adduser --quiet "revolutio" --uid "${REVOLUTIO_UID}" --gid "0" --home "${REVOLUTIO_HOME}" && \
    chown -R "revolutio:root" "${REVOLUTIO_HOME}"

EXPOSE 8899

ENTRYPOINT ["/bin/sh","-c"]