import os

PROMETHEUS_METRICS_ENDPOINT = "/metrics"
"""Endpoint to expose Prometheus metrics."""
EXPOSE_METRICS_FOR_SECONDS = os.environ.get("METRIC_EXPOSE_FOR_SECONDS", 300)
"""The total number of seconds the service should expose the prometheus metrics."""
HOSTS_CHECK_YAML_PATH = os.environ.get(
    "HOSTS_YAML", os.path.join(os.path.dirname(__file__), "local.host_ports.yaml")
)
"""The path of the input configuration YAML."""
