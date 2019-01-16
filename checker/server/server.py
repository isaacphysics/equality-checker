import signal

from flask import Flask, request, jsonify, abort
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

from checker import maths, logic


__all__ = ["app"]

MAX_REQUEST_COMPUTATION_TIME = 5  # How long should we spend on a single request?


app = Flask(__name__)


class TimeoutException(Exception):
    """An exception to be raised if simplification takes too long to finish."""
    pass


class TimeoutProtection(object):
    """A custom class to abort long-running code.

       The timeout cannot interrupt libraries running external C code, and so
       care must be taken. See http://stackoverflow.com/a/22348885 for source.
       On platforms which do not support SIGALRM (notably Windows), the code will
       run without timeout protection and merely print a warning to the console.
        - 'duration' is the number of seconds to allow the code to run for before
          raising a TimeoutException.
    """
    def __init__(self, duration=10):
        self.duration = duration
        self.timeout_allowed = True
        try:
            signal.SIGALRM
        except AttributeError:
            self.timeout_allowed = False

    @staticmethod
    def handle_timeout(signal_number, frame):
        """The callback function to handle the signal being raised."""
        raise TimeoutException()

    def __enter__(self):
        """Allows a 'with' block. If can set an alarm, do so."""
        if self.timeout_allowed:
            signal.signal(signal.SIGALRM, TimeoutProtection.handle_timeout)
            signal.alarm(self.duration)
        else:
            # We can't use SIGALRM
            print("WARN: Timeout Unsupported!")

    def __exit__(self, _type, value, traceback):
        """Cancels alarm after 'with' block exits."""
        if self.timeout_allowed:
            signal.alarm(0)


def _make_json_error(ex):
    """Return JSON error pages, not HTML!

       Using a method suggested in http://flask.pocoo.org/snippets/83/, convert
       all outgoing errors into JSON format.
    """
    status_code = ex.code if isinstance(ex, HTTPException) else 500
    response = jsonify(message=str(ex), code=status_code, error=type(ex).__name__)
    response.status_code = status_code
    return response


@app.route('/check', methods=["POST"])
@app.route('/check/maths', methods=["POST"])
def check_maths():
    """Check the equivalence of two mathematical expressions."""
    body = request.get_json(force=True)

    if not (("test" in body) and ("target" in body)):
        print("=" * 50)
        print("ERROR: Ill-formed request!")
        print(body)
        print("=" * 50)
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    target_str = body.get("target")
    test_str = body.get("test")
    description = body.get("description")

    if (target_str == "") or (test_str == ""):
        print("=" * 50)
        if description is not None:
            print(description)
            print("=" * 50)
        print("ERROR: Empty string in request!")
        print("Target: '{0}'\nTest: '{1}'".format(target_str, test_str))
        print("=" * 50)
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    symbols = body.get("symbols")
    check_symbols = str(body.get("check_symbols", "true")).lower() == "true"

    # To reduce computation issues on single-threaded server, institute a timeout
    # for requests. If it takes longer than this to process, return an error.
    # This cannot interrupt numpy's computation, so care must be taken in selecting
    # a value for MAX_REQUEST_COMPUTATION_TIME.
    try:
        with TimeoutProtection(MAX_REQUEST_COMPUTATION_TIME):
            response_dict = maths.check(test_str, target_str, symbols=symbols, check_symbols=check_symbols, description=description)
            return jsonify(**response_dict)
    except TimeoutException as e:
        print("ERROR: {} - Request took too long to process, aborting!".format(type(e).__name__))
        print("=" * 50)
        error_dict = dict(
            target=target_str,
            test=test_str,
            error="Request took too long to process!",
            )
        return jsonify(**error_dict)


@app.route('/check/logic', methods=["POST"])
def check_endpoint():
    """Check the equivalence of two boolean logic expressions."""
    body = request.get_json(force=True)

    if not (("test" in body) and ("target" in body)):
        print("=" * 50)
        print("ERROR: Ill-formed request!")
        print(body)
        print("=" * 50)
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    target_str = body.get("target")
    test_str = body.get("test")
    description = body.get("description")

    if (target_str == "") or (test_str == ""):
        print("=" * 50)
        if description is not None:
            print(description)
            print("=" * 50)
        print("ERROR: Empty string in request!")
        print("Target: '{0}'\nTest: '{1}'".format(target_str, test_str))
        print("=" * 50)
        abort(400)  # Probably want to just abort with a '400 BAD REQUEST'

    check_symbols = str(body.get("check_symbols", "true")).lower() == "true"

    # To reduce computation issues on single-threaded server, institute a timeout
    # for requests. If it takes longer than this to process, return an error.
    # This cannot interrupt numpy's computation, so care must be taken in selecting
    # a value for MAX_REQUEST_COMPUTATION_TIME.
    try:
        with TimeoutProtection(MAX_REQUEST_COMPUTATION_TIME):
            response_dict = logic.check(test_str, target_str, check_symbols=check_symbols, description=description)
            return jsonify(**response_dict)
    except TimeoutException as e:
        print("ERROR: {} - Request took too long to process, aborting!".format(type(e).__name__))
        print("=" * 50)
        error_dict = dict(
            target=target_str,
            test=test_str,
            error="Request took too long to process!",
            )
        return jsonify(**error_dict)


@app.route('/', methods=["GET"])
def ping():
    """Allow monitoring Flask status.

       This is for production monitoring of the application's status. Under no
       circumstances should it be running in debug mode in production!"""
    if app.debug:
        abort(500)
    return jsonify(code=200)


# Make sure all outgoing error messages are in JSON format.
# This will only work provided debug=False - otherwise the debugger hijacks them!
for code in default_exceptions.keys():
    app.register_error_handler(code, _make_json_error)

if __name__ == '__main__':
    # Run the app:
    app.run(port=5000, host="0.0.0.0", debug=False)
