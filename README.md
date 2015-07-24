# equality-checker
Tiny server for testing equivalence of two symbolic expressions.

## Installation / Setup instructions
### Dev Project setup (Windows)
1. [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads)
2. [Install Vagrant](http://docs.vagrantup.com/v2/installation/)
3. Clone this repository
4. Execute vagrant up in a terminal from the cloned project directory
5. Execute vagrant ssh to login to the newly created vagrant vm.
6. Run /equality-checker/run-docker.sh to launch the server

Your server should be running on port http://localhost:9090/check

### Production
Note: The Docker container is available from [dockerhub](https://registry.hub.docker.com/u/ucamcldtg/equality-checker/) by running: docker pull ucamcldtg/equality-checker . This is useful for production use.
