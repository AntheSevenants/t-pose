import os
import argparse
from app import create_app

parser = argparse.ArgumentParser(description='Run t-pose frontend')
parser.add_argument('-debug', '--debug', nargs='?', type=bool, default=False, help='output file, in JSON format')

args = parser.parse_args()

debug = args.debug

environment_variables = [ "CACHE_DIR" ]

for environment_variable in environment_variables:
 	if not environment_variable in os.environ:
 		raise Exception(f"Environment variable '{environment_variable}' missing")


app = create_app(debug=debug)

if debug:
	app.jinja_env.auto_reload = True
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.run(host='0.0.0.0', debug=debug)
else:
	from waitress import serve
	print("t-pose started")
	serve(app, host='0.0.0.0', port=8080)