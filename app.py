"""
	This file contains details of application server. Things like initialising database connections, creating Flask application and running tornado server are done here.
	For production deployment, it picks configuration from 'mlocrappci/config/server/config.txt' which is symlinked from '/var/mlocrappci/config/config.txt'
"""

import logging
import os
import os
from flask import Flask, Blueprint
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from apis import appApi

logging.basicConfig(format='[%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s] - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
	'''
	<tbody>
                        {% for metaData in mapData %}
                        {% set count = count + 1 %}
                        {% set columnName = metaData[0] %}
                        {% set columnDtype = metaData[1] %}
                        <tr>
                            <td>{{columnName}}</td>
                            <td >{{columnDtype}}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                    '''

	logger.info('Creating Flask application context')
	# Creating Flask application object

	app = Flask(__name__) # Initialize the Flask application
	app.config['RESTPLUS_JSON'] = {'indent': 5, 'separators': (',', ':')}
	app.secret_key = os.urandom(12)

	# Registering different APIs
	# logger.info('Registering core APIs blueprints')
	# app.register_blueprint(coreAPIs.coreAPIs)
	logger.info('Registering application APIs blueprints')
	app.register_blueprint(appApi.appAPIs)

	# @app.before_request
	# def _db_connect():
	# 	# logger.debug('Connect DB')
	# 	database.connect()
    #
	# @app.teardown_request
	# def _db_close(exc): #don't remove the parameter - it is required
	# 	if not database.is_closed():
	# 		# logger.debug('Close DB')
	# 		database.close()

	#why CORS allowed?
	@app.after_request
	def setHeaders(response):
		response.headers["Access-Control-Allow-Origin"] = '*'
		response.headers["Access-Control-Allow-Headers"] = '*'
		# logger.debug('After Request')
		return response

	port = 1112
	# if config.get(config.APP_MODE) == constants.APP_DEBUG_MODE:
	# 	port=config.get(config.DEBUG_PORT)
	# if (config.get(config.CLUSTER_MODE) and config.get(config.MASTER_NODE)) or not config.get(config.CLUSTER_MODE):
		# Following line processes all pending requests on server startup
		# appAPI.checkUnprocessedFiles()
		# nextDay = datetime.datetime.now() + datetime.timedelta(days=1)
		# dateString = nextDay.strftime('%d-%m-%Y') + " 07-00-00"
		# newDate = nextDay.strptime(dateString,'%d-%m-%Y %H-%M-%S')
		# delay = (newDate - datetime.datetime.now()).total_seconds()
		# Timer(delay, coreAPIs.generateAndSendReports, ()).start()
		# pass


	logger.debug("Setting Flask application context logger as same as this server's logger")
	# app.logger.addHandler(file_handler)
	app.logger_name = 'server' #TODO: see if it works

	# Wrapping Flask application in WSGI container of tornado
	logger.info('Creating WSGI wrapper around Flask application context')
	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(port)

	# Starting tornado server
	logger.info("Web application server started on port - {}".format(port))
	IOLoop.instance().start()
