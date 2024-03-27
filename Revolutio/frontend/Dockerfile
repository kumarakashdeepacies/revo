# Use an official node runtime as a parent image
FROM node:19-alpine3.16

ARG REVOLUTIO_UID="70070"
ARG REVOLUTIO_HOME=/app/

WORKDIR /app/

# Install dependencies
COPY package.json /app/

RUN npm install --legacy-peer-deps

# Add rest of the client code
COPY . /app/

RUN adduser --quiet "revolutio" --uid "${REVOLUTIO_UID}" --gid "0" --home "${REVOLUTIO_HOME}" && \
    chown -R "revolutio:root" "${REVOLUTIO_HOME}"

RUN chown -R revolutio:root /opt/data_store

USER ${REVOLUTIO_UID}

EXPOSE 3000

CMD npm start
