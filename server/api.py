from flask import Flask, request, jsonify
app = Flask(__name__)

from sympy.parsing.sympy_parser import parse_expr, implicit_multiplication, standard_transformations
from sympy.printing.latex import latex
import sympy
import numpy

@app.route('/check', methods=["POST"])
def check():
	body = request.get_json(force=True)

	target_expr = parse_expr(body["target"],transformations=standard_transformations+(implicit_multiplication,))
	test_expr = parse_expr(body["test"],transformations=standard_transformations+(implicit_multiplication,))

	print "Parsed target: %s\nParsed to check: %s" % (target_expr, test_expr)

	equal = sympy.simplify(test_expr - target_expr)==0

	if not equal:
		domain = numpy.arange(10)
		f_target = sympy.lambdify(target_expr.free_symbols, target_expr, "numpy")
		f_test = sympy.lambdify(test_expr.free_symbols, test_expr, "numpy")
		print f_target(domain)
		print f_test(domain)
		diff = numpy.abs(numpy.sum(f_test(domain) - f_target(domain)))
		print "Diff of %.6E" % diff
		equal = diff <= (1E-10 * numpy.max(f_target(domain)))
	
	return jsonify(
		target=body["target"],
		test=body["test"],
		parsedTarget=latex(target_expr),
		parsedTest=latex(test_expr),
		equal=str(equal)
	)

if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0", debug=True)