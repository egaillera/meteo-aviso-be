from app import app

@app.route('/')
def homepage():
	app.logger.info('Home page visited')
	return 'Home page'
	
