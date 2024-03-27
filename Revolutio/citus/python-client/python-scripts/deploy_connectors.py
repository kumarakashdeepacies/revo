"""
script for deploying kafka connect connectors on existing kafka connect cluster with the default port (8083)
expected inputs: connectors.json ---->>>>>>> json file comprising of connectors that need to be deployed
"""

import json
import os

from dotenv import load_dotenv


def deploy_connectors(url, connectors, kafka_connect_port):

    for connector in connectors:
        print(connector)
        fileName = "{}.json".format(connector["name"])
        with open(fileName, "w+") as outfile:
            json.dump(connector, outfile)
        os.system(
            'curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -d @{} {}:{}/connectors'.format(
                fileName, url, kafka_connect_port
            )
        )


if __name__ == "__main__":
    load_dotenv()

    KAFKA_CONNECT_HOST = os.getenv("KAFKA_CONNECT_HOST")
    KAFKA_CONNECT_PORT = os.getenv("KAFKA_CONNECT_PORT")
    print(KAFKA_CONNECT_HOST)
    connect_url = KAFKA_CONNECT_HOST
    connectors = json.loads(open("connectors.json").read())
    deploy_connectors(connect_url, connectors, KAFKA_CONNECT_PORT)
