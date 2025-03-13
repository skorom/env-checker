import logging
import os
import signal
import socket
import sys
import threading
import time

import uvicorn
import yaml
from app.config.application_config import (
    EXPOSE_METRICS_FOR_SECONDS,
    HOSTS_CHECK_YAML_PATH,
)

CHECK_RESULT = 0


def init_handler(signum, frame):
    """Closing the application on SIGINT signal and return with ok or nok."""
    logging.info("Closing application. Result: %d", CHECK_RESULT)
    sys.exit(CHECK_RESULT)


def uvicorn_shutdown():
    """Shutting down the application after the configured seconds"""
    logging.info("Webservice will shut down in %s seconds.", EXPOSE_METRICS_FOR_SECONDS)
    time_left = int(EXPOSE_METRICS_FOR_SECONDS)
    while time_left > 1:
        div = time_left // 2
        time.sleep(div)
        time_left = time_left - div
        logging.info("Webservice will shut down in %d seconds.", time_left)
    os.kill(os.getpid(), signal.SIGINT)


#
def check_port(host: str, port: int) -> bool:
    """Checks if the given host is open for a TCP communication through the given port

    Args:
        host (str): The hostname
        port (int): The port number in string format

    Returns:
        bool: true if the check succeed
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        return result == 0


def main():
    """The entry point of the application.
    It starts the `uvicorn` service and a new thread for all the metrics."""

    signal.signal(signal.SIGINT, init_handler)
    with open(HOSTS_CHECK_YAML_PATH, "r", encoding="utf-8") as file:
        global CHECK_RESULT
        data = yaml.safe_load(file)
        for group, connection in data.items():
            succeed = 0
            for host_port in connection["host"]:
                host = host_port.split(":")[0]
                port = int(host_port.split(":")[1])
                if check_port(host, port):
                    logging.info("%s:%d check succeed", host, port)
                    succeed += 1
                else:
                    logging.warning("%s:%d check failed", host, port)
            expected_succeed = connection["min"]
            if succeed < connection["min"]:
                logging.error(
                    "Not enough port check. %d instead of %d for %s group.",
                    succeed,
                    expected_succeed,
                    group,
                )
                CHECK_RESULT = 1
            else:
                logging.info("Enough port check succeed for %s group.", group)

    if EXPOSE_METRICS_FOR_SECONDS != "-":
        thread = threading.Thread(target=uvicorn_shutdown)
        # Configure the thread as a daemon so it will exit when main thread exists.
        thread.daemon = True
        thread.start()
        uvicorn.run(
            "controller.prometheus_controller:app",
            host="0.0.0.0",
            port=int(8080),
        )
    else:
        logging.info("Skip starting webservice on user request.")


if __name__ == "__main__":
    main()
