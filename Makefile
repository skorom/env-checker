IMAGE_NAME="env-checker"
VERSION="1.0-SNAPSHOT"

.PHONY: $(MAKECMDGOALS)

# build python
build:
	podman build \
		--tag ${IMAGE_NAME}:${VERSION} \
		.

# Stop the python app
stop:
	podman kill $(IMAGE_NAME) || true
	podman rm $(IMAGE_NAME) || true

# Start python app
start:
	podman run --name $(IMAGE_NAME) -it --rm -p 8080:8080 \
		-v ./app/config/local.host_ports.yaml:/config/host_ports.yaml\
		-e HOSTS_YAML=/config/host_ports.yaml \
		${IMAGE_NAME}:${VERSION}