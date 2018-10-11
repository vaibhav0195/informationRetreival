"""
	This file contains APIs for PUT, GET image details and processMenuItems
"""

import json
import logging
import os
from flask import Blueprint, request, json, render_template
from werkzeug import secure_filename
import pandas as pd
import pika
from databaseAndQueue import mongoDb
from informationRetreval import getTheColmnNames
# Creating a Blueprint which will be registered while creating Flask application context in app.py
appAPIs = Blueprint('appAPIs', __name__, template_folder='templates', static_folder='static',url_prefix='/analyse')
logger = logging.getLogger(__name__)
currentName = ''
currentFolder = 'videoRender'

def getQueueObj():
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='informationRetreival', durable=True)
	return channel

@appAPIs.route('/', methods=['GET'])
def newDemoScreen():
	return render_template('index.html')

@appAPIs.route('/', methods=['POST'])
def upload_file_browse():
	logger.info('got the request')
	folder = os.path.abspath("static/csv/")
	if request.method == 'POST':
		file = request.files['file']
		if file:
			try:
				filename = secure_filename(file.filename)
				file.save(os.path.join(folder, filename))
				pathOfSavedFile = os.path.join(folder, filename)
				logger.info('downloaded the file')

				dataFrameObj = pd.read_csv(pathOfSavedFile)
				dtypesOfColumns = dataFrameObj.dtypes
				mapOfNameToDtype = dict(dtypesOfColumns)
				mapOfNameToDtype = [(str(nameOfColumn),str(mapOfNameToDtype[nameOfColumn])) for nameOfColumn in mapOfNameToDtype]
				#publishing data to queue
				# dataToPublish = {'filePath':pathOfSavedFile,'fileName':filename}
				# collectionDb = mongoDb.getMongoCollectionClient(host='localhost',
				# 												port=27017,
				# 												dbName='informationRetreival',
				# 												collectionName='csv')
				# channel = getQueueObj()
				# channel.basic_publish(exchange='',
				# 					  routing_key='informationRetreival',
				# 					  body=json.dumps(dataToPublish),
				# 					  properties=pika.BasicProperties(
				# 						  delivery_mode=2,  # make message persistent
				# 					  ))
				# dataToStoreInMongo = {'_id':filename,'filePath':pathOfSavedFile}
				# collectionDb.insert_one(dataToStoreInMongo)
				jsonToReturn = {'status':'ok','fileName':filename,'csvHeaders':mapOfNameToDtype}
			except Exception,e:
				jsonToReturn = {'status': 'error','errorMessage': e}
			logger.info('returing the data {}'.format(mapOfNameToDtype))
			return json.dumps(jsonToReturn)


@appAPIs.route('/getTheJsonResponse', methods=['POST'])
def getTheParsedDataFromDb():
	logger.info('got the request')
	folder = os.path.abspath("static/csv/")
	if request.method == 'POST':
		data = json.loads(request.data)
		fileName = data['nameOfFile']
		columnName = data['columnToAnalyse']
		return True