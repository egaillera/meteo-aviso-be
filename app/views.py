from app import app
from models import Station,Measurement

@app.route('/')
def homepage():
	app.logger.info('Home page visited')
	return 'Home page'

	
@app.route('/stations')	
def stations():
	st = Station.query.all()
	return jsonify(st)
	
