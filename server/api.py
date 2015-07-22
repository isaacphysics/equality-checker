from flask import Flask, request, jsonify
app = Flask(__name__)

from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.latex import latex

@app.route('/check', methods=["POST"])
def check():
	body = request.get_json(force=True)

	target_expr = parse_expr(body["target"])
	test_expr = parse_expr(body["test"])

	print "Parsed target: %s\nParsed to check: %s" % (target_expr, test_expr)
	
	return jsonify(
		target=body["target"],
		test=body["test"],
		parsedTarget=latex(target_expr),
		parsedTest=latex(test_expr),
		equal=target_expr == test_expr
	)

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)