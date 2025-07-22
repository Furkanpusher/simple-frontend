set -euo pipefail
IFS=$'\n\t'
trap "exit 1" HUP INT QUIT ABRT SEGV

DOCKER_BUILDKIT=1 docker build --pull --tag fastapi-celery:local .

docker run --user root --rm -it -p 8000:8000 fastapi-celery:local bash
