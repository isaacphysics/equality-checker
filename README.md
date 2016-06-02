# equality-checker
Not quite so tiny any more server for testing equivalence of two symbolic expressions.

## Installation / Setup instructions
### Dev Project setup (Windows)
1. [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. [Install Vagrant](http://docs.vagrantup.com/v2/installation/)
3. Clone this repository
4. Execute `vagrant up` in a terminal from the cloned project directory
5. Execute `vagrant ssh` to login to the newly created vagrant vm.
6. Then go to equality-checker directory `cd /equality-checker`
7. Run `./run-docker.sh` to launch the server

Your server should be running on port `http://localhost:5000/check`

### Production
Deploy to dockerhub: `docker push ucamcldtg/equality-checker`

The Docker container is available from [dockerhub](https://registry.hub.docker.com/u/ucamcldtg/equality-checker/) by running: docker pull ucamcldtg/equality-checker . This is useful for production use.

### isaac-dev

The following commands (as root) got it working. The `PYTHONUNBUFFERED` stuff is to make sure stdout is captured properly in logs.

```
docker pull ucamcldtg/equality-checker
docker run -d -p 5000:5000 -e PYTHONUNBUFFERED=0 --name equality-checker ucamcldtg/equality-checker
```

To see live output:

```
docker logs -f equality-checker
```

Before pulling new version:

```
docker rm equality-checker
```
