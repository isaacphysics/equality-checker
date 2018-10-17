# equality-checker
A not-quite-so-tiny-any-more server for testing the equivalence of two algebraic expressions using [SymPy](http://www.sympy.org/en/index.html).

### Development Setup Instructions
#### Simple Setup
1. Install [Python 2.7](https://www.python.org/)
2. Clone this repository
3. Run `pip install -r requirements.txt`
4. Run `python server\api.py`

Your server should be running at `http://localhost:5000/check`.
Now make JSON-based POST requests with target and test expression strings, e.g.
```
{
    "target": "x + 3",
    "test": "3 + x",
    "description": "An optional description for the logs!"
}
```

which will get a response like:
```
{
    "equal": "true",
    "equality_type": "exact",
    "parsed_target": "x + 3",
    "parsed_test": "x + 3",
    "target": "x + 3",
    "test": "3 + x"
}
```
or, if something went wrong, an error like:
```
{
    "error": "Some error message here",
    ...
}
```

#### Docker Setup
To develop the Docker container as well:

5. Install [Docker](https://www.docker.com/)
7. Run `docker build -t ucamcldtg/equality-checker .`
8. Test using `docker run -p 5000:5000 -it ucamcldtg/equality-checker` rather than running Python locally
9. Optionally deploy to dockerhub: `docker push ucamcldtg/equality-checker` (requires authentication)

### Production Use

The Docker container is available from [dockerhub](https://registry.hub.docker.com/u/ucamcldtg/equality-checker/) by running: `docker pull ucamcldtg/equality-checker` or by listing it as an image in a Docker Compose file. Port 5000 of the container will need to be mapped to the port the checker is expected to listen on.

For instance, run:
```
docker run -d -p 5000:5000 --name equality-checker ucamcldtg/equality-checker
```

To see live output:

```
docker logs -f equality-checker
```
