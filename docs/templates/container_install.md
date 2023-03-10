# Install The CANU Container

## Pre-built Image

A pre-built CANU image can be pulled using a container runtime (Docker, Podman, etc.)

```shell
docker pull <registry>/canu:<tag>
```

You will need to [authorize your container runtime](https://www.jfrog.com/confluence/display/JFROG/Docker+Registry#DockerRegistry-PushingandPullingImages) in order to pull from it.

### Wrapper Script 

You may also wish to install the `canuctl` wrapper script to simplify running the container with the correct arguments.  That script is installed with the RPM or is [available in the repo](https://github.com/Cray-HPE/canu/blob/main/canuctl) when building the container image.

```shell
./canuctl -p # run the prouction container
./canuctl -d # run a development container, which has a development environment setup for making changes
```

```shell
./canuctl -h

./canuctl -d(ev) | -p(rod) [-r(ebuild)] [-i(mage) <image>] [args] [-h(elp)]

  -d: run the dev container (editable environment to make changes to the code)
  -p: run the prod container (canu for everyday use)
  -r: rebuild the container (default ${ALPINE_IMAGE}: alpine:3.17)
  -i: specify the image to use (default ${CANU_IMAGE}: artifactory.algol60.net/csm-docker/stable/canu)
  -h: print this help message

```

## Dockerfile

The container image can be built from the `Dockerfile` in the [canu repo](https://github.com/Cray-HPE/canu/blob/main/Dockerfile).

```shell
git clone https://github.com/Cray-HPE/canu.git
cd canu
make prod
```

Note: this pulls from an authenticated Artifactory by default in order to get the base image.  You will need to [authorize your container runtime](https://www.jfrog.com/confluence/display/JFROG/Docker+Registry#DockerRegistry-PushingandPullingImages) in order to pull from it.

Alternatively, you can override the base image to one that is publicly accessible.

```bash
ALPINE_IMAGE=alpine:3.17 make image
```
