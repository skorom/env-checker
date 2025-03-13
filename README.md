# Introduction

A python application to run an environment check on a target cluster.

Currently the application is capable of doing 3 things:

1. Checks if the given+host ports are open for TCP communication
2. Expose Prometheus metrics for a while
3. Logging

## The application scans the given host+ports

1. If it is reachable, it will be logged in INFO level: `2024-09-27,14:14:45 - INFO - kafka:9092 check succeed`
2. If it is not reachable, it will be logged in WARN level: `2024-09-27,14:14:46 - WARNING - kafka:9092 check failed`

At the end of every group, you will see in the logs if the total amount of accessible endpoints are at least the given value. Example logs:

```Log
2024-09-27,14:14:45 - INFO - Enough port check succeed for gwb group.
2024-09-27,14:39:33 - ERROR - Not enough port check. 4 instead of 10 for kafka group.
```

## The application expose Prometheus metrics

The application expose prometheus metric for a while in the following endpoint: [Metrics endpoint](http://localhost:8080/backend/metrics). The reason why it is not for eternity is because we do not need it. We just run and check in central Grafana that we are able to read metrics from services. We do not want to waist our resources.

## Configuration

The application can be configured through environment variables and through a YAML file.

### Environment variables

| Variable name | Default value | Description |
|---------------|---------------|-------------|
| METRIC_EXPOSE_FOR_SECONDS | 300 | The total number of seconds the service should expose the prometheus metrics. |
| HOSTS_YAML | <config_dir_path>/local.host_ports.yaml | The path of the input configuration YAML. |

### Input yaml

In the YAMl file, you can define the host names (with ports) that the application will scan. You can also define the amount of endpoints you would like to reach from the given group. Why is it useful? Because some of the services are running on multiple nodes but not all the time.

```Yaml
oracle-db:
  host:
    - oracle-db-domain:1521
    - oracle-db-domain:2484
    - oracle-db-domain:6200
  min: 3
rabbitmq:
  host:
    - rabbit:5673
  min: 1
kafka:
  host:
    - kafka-node-1:9092
    - kafka-node-2:9092
    - kafka-node-3:9092
    - kafka-node-4:9092
  min: 2
```
