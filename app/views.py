from app import app
import models

@app.route('/')
def homepage():
	app.logger.info('Home page visited')
	return 'Home page'

	
@app.route('/stations')	
def stations():
	st = Station.query.all()
	return jsonify(st)
	
