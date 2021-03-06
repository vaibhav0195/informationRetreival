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
import informationRetreval
# Creating a Blueprint which will be registered while creating Flask application context in app.py
appAPIs = Blueprint('appAPIs', __name__, template_folder='templates', static_folder='static',url_prefix='/analyse')
logger = logging.getLogger(__name__)
currentName = ''
currentFolder = 'videoRender'

def Convert(tup, di):
    di = dict(tup)
    return di

def getQueueObj():
	connection = pika.BlockingConnection(
		pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='informationRetreival', durable=True)
	return channel

def getTheModeOfHeaders(dataFrameObj):
	columnNameToUse = []
	for columnName in dataFrameObj:
		mostUsedValForCol = dataFrameObj[columnName].mode()
		if mostUsedValForCol.shape[0] == dataFrameObj[columnName].shape[0] or mostUsedValForCol.shape[0] ==0:
			continue
		else:
			columnNameToUse.append(columnName)

	return columnNameToUse

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
				columnNameToUse = getTheModeOfHeaders(dataFrameObj)
				mapOfNameToDtype = dict(dtypesOfColumns)
				mapOfNameToDtype = [(str(nameOfColumn),str(mapOfNameToDtype[nameOfColumn]),nameOfColumn in columnNameToUse) for nameOfColumn in mapOfNameToDtype]
				#publishing data to queue
				dataToPublish = {'filePath':pathOfSavedFile,'fileName':filename}
				collectionDbAnalysis = mongoDb.getMongoCollectionClient(host='localhost',
																port=27017,
																dbName='informationRetreival',
																collectionName='dataframeAnalysis')

				collectionDbHeaderAndType = mongoDb.getMongoCollectionClient(host='localhost',
																port=27017,
																dbName='informationRetreival',
																collectionName='dataframeHeadAndDtype')
				dataDb = collectionDbAnalysis.find_one({"_id": filename})
				if dataDb is None:

					channel = getQueueObj()
					channel.basic_publish(exchange='',
										  routing_key='informationRetreival',
										  body=json.dumps(dataToPublish),
										  properties=pika.BasicProperties(
											  delivery_mode=2,  # make message persistent
										  ))
					dataToStoreInMongo = {'_id':filename,'filePath':pathOfSavedFile}
					dataToStoreInMongoHeadersIndType = {'fileName':filename,'headers':mapOfNameToDtype}
					collectionDbAnalysis.insert_one(dataToStoreInMongo)
					collectionDbHeaderAndType.insert_one(dataToStoreInMongoHeadersIndType)
				jsonToReturn = {'status':'ok','fileName':filename,'csvHeaders':mapOfNameToDtype}
			except Exception,e:
				logger.exception(e)
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
		#.find_one({"author": "Mike"})
		collectionDb = mongoDb.getMongoCollectionClient(host='localhost',port=27017,
								dbName='informationRetreival',collectionName='dataframeAnalysis')
		collectionDbHeaderAndType = mongoDb.getMongoCollectionClient(host='localhost',
													 port=27017,
													 dbName='informationRetreival',
													 collectionName='dataframeHeadAndDtype')
		dataDb = collectionDb.find_one({"_id": fileName})
		headerTypeForFile =  collectionDbHeaderAndType.find_one({"fileName": fileName})
		headerListValues = headerTypeForFile['headers']
		headerType = [(f[0],f[1]) for f in headerListValues if ('int' in f[1]  or 'float' in f[1] ) and (f[0] !=columnName) and (f[2] ==True)]
		mapOfHeaderAndType = {}
		if len(headerType) >0:
			mapOfHeaderAndType = Convert(headerType, mapOfHeaderAndType)
		if len(mapOfHeaderAndType.keys()) > 0:
			useRange=True
		else:
			useRange =False
		uniqueValueNameMApToMode = {}
		columnDistributionData = {}
		if useRange:
			for numericColumnName in mapOfHeaderAndType.keys():
				dataForTheNumericColumn = dataDb['processed']['analysedData'][numericColumnName]['analysis']
				numericvalues = [float(k.replace(':;:','.')) for k in dataForTheNumericColumn.keys()]
				numericvalues.sort()
				mapOfHeaderAndType[numericColumnName] = numericvalues
		if columnName in dataDb['processed']['analysedData']:
			dataForTheColumnName = dataDb['processed']['analysedData'][columnName]['analysis']
			# if 'int' in headerType or 'float' in headerType:
			# 	numericvalues = [float(k) for k in dataForTheColumnName.keys()]
			# 	numericvalues.sort()
			# 	useRange=True
			# else:
			# 	numericvalues=[]
			for uniqueColumnVal in dataForTheColumnName:
				uniqueValueNameMApToMode[uniqueColumnVal] = {}
				modeDataOfColumn = dataForTheColumnName[uniqueColumnVal]
				# dataForColumn = dataForTheColumnName[uniqueColumnVal]
				columnHeaders = modeDataOfColumn['dataAlongDifferentColumn'].keys()
				for columnValueToAnalyse in modeDataOfColumn['dataAlongDifferentColumn']:
					modeData = modeDataOfColumn['dataAlongDifferentColumn'][columnValueToAnalyse]['mode']
					columnDistributionData[uniqueColumnVal] = modeDataOfColumn['totalNumValues']
					valueToSetForColumn = {'mode':None,'samples':None,'relevant':False}
					if modeData is not None:
						# if len(modeData) == 1:
						# titleSatisfying = modeDataOfColumn[columnValueToAnalyse]['title_satisfying']
						valueToSetForColumn['mode'] = modeData
						valueToSetForColumn['samples'] = []
						valueToSetForColumn['relevant'] = True
					uniqueValueNameMApToMode[uniqueColumnVal][columnValueToAnalyse] = valueToSetForColumn
			logger.info('got the data from mongo db for {}'.format(fileName))
			columnHeaders.insert(0, columnName)
			return json.dumps(
			{
			'status':'ok',
			'columnModeData':  uniqueValueNameMApToMode,
			'columnValues':uniqueValueNameMApToMode.keys(),
			'columnHeaders': columnHeaders,
			'fileName':fileName,
			'distribution':columnDistributionData,
			'numericValue':useRange,
			'rangeValue':mapOfHeaderAndType
			}
				)

@appAPIs.route('/getTheAnalysisData', methods=['POST'])
def getTheAnalysedData():
	logger.info('got the request')

	if request.method == 'POST':
		data = json.loads(request.data)
		dataAboutThecell = data['columnToAnalyse']
		dataList = dataAboutThecell.split(':;:')
		columnvalue,columnName,rowValue,rowName,fileName = dataList[0],dataList[1],dataList[2],dataList[3],dataList[4]
		# columnName = data['columnToAnalyse']
		#.find_one({"author": "Mike"})
		collectionDb = mongoDb.getMongoCollectionClient(host='localhost',port=27017,
													dbName='informationRetreival',collectionName='dataframeAnalysis')
		dataDb = collectionDb.find_one({"_id": fileName})
		# uniqueValueNameMApToMode = {}
		if rowName in dataDb['processed']['analysedData']:
			dataForTheColumnName = dataDb['processed']['analysedData'][rowName]['analysis']
			modeDataOfCellRow = dataForTheColumnName[rowValue]['dataAlongDifferentColumn'][columnName]
		if columnName in dataDb['processed']['analysedData']:
			dataForTheColumnName = dataDb['processed']['analysedData'][columnName]['analysis']
			modeDataOfCellColumn = dataForTheColumnName[columnvalue]['dataAlongDifferentColumn'][rowName]
		return json.dumps(
			{
				'status':'ok',
				'columnData':modeDataOfCellColumn,
				'rowData':modeDataOfCellRow,
				'rowHeader':rowName,
				'columnHeader':columnName
			}


							)

@appAPIs.route('/doRangeAnalysis', methods=['POST'])
def doingRangeAnalysis():
	logger.info('got the request')
	if request.method == 'POST':
		folder = os.path.abspath("static/csv/")
		data = json.loads(request.data)
		fileName = data['fileName']
		rangeData = data['columnRangeData']
		columnNameToAnalyse = data['columnNametoAnalyse']
		pandasQuery = ''
		pathOfSavedFile = os.path.join(folder, fileName)
		logger.info('downloaded the file')

		dataFrameObj = pd.read_csv(pathOfSavedFile)
		for columnNameInRangeData in rangeData:
			minimumvalue = rangeData[columnNameInRangeData]['min']
			maximumvalue = rangeData[columnNameInRangeData]['max']
			queryForColumn = '{} <= {} <= {}'.format(minimumvalue,columnNameInRangeData,maximumvalue)
			pandasQuery += queryForColumn+'&'
		pandasQuery = pandasQuery.strip('&')
		mapOfInfo = informationRetreval.doRangeAnalysis(dataFrameObj,pandasQuery,columnNameToAnalyse,[])

		collectionDb = mongoDb.getMongoCollectionClient(host='localhost', port=27017,
														dbName='informationRetreival',
														collectionName='dataframeAnalysis')
		collectionDbHeaderAndType = mongoDb.getMongoCollectionClient(host='localhost',
																	 port=27017,
																	 dbName='informationRetreival',
																	 collectionName='dataframeHeadAndDtype')

		dataDb = collectionDb.find_one({"_id": fileName})
		headerTypeForFile = collectionDbHeaderAndType.find_one({"fileName": fileName})
		headerListValues = headerTypeForFile['headers']
		headerType = [(f[0], f[1]) for f in headerListValues if
					  ('int' in f[1] or 'float' in f[1]) and (f[0] != columnNameToAnalyse) and (f[2] == True)]
		mapOfHeaderAndType = {}
		if len(headerType) > 0:
			mapOfHeaderAndType = Convert(headerType, mapOfHeaderAndType)
		if len(mapOfHeaderAndType.keys()) > 0:
			useRange = True
		else:
			useRange = False
		columnDistributionData = {}
		if useRange:
			for numericColumnName in mapOfHeaderAndType.keys():
				dataForTheNumericColumn = dataDb['processed']['analysedData'][numericColumnName]['analysis']
				numericvalues = [float(k.replace(':;:','.')) for k in dataForTheNumericColumn.keys()]
				numericvalues.sort()
				mapOfHeaderAndType[numericColumnName] = numericvalues

		uniqueValueNameMApToMode = {}
		for uniqueColumnVal in mapOfInfo:
			uniqueValueNameMApToMode[uniqueColumnVal] = {}
			modeDataOfColumn = mapOfInfo[uniqueColumnVal]
			# dataForColumn = dataForTheColumnName[uniqueColumnVal]
			columnHeaders = modeDataOfColumn['dataAlongDifferentColumn'].keys()
			for columnValueToAnalyse in modeDataOfColumn['dataAlongDifferentColumn']:
				modeData = modeDataOfColumn['dataAlongDifferentColumn'][columnValueToAnalyse]['mode']
				columnDistributionData[uniqueColumnVal] = modeDataOfColumn['totalNumValues']
				valueToSetForColumn = {'mode': None, 'samples': None, 'relevant': False}
				if modeData is not None:
					# if len(modeData) == 1:
					# titleSatisfying = modeDataOfColumn[columnValueToAnalyse]['title_satisfying']
					valueToSetForColumn['mode'] = modeData
					valueToSetForColumn['samples'] = []
					valueToSetForColumn['relevant'] = True
				uniqueValueNameMApToMode[uniqueColumnVal][columnValueToAnalyse] = valueToSetForColumn
		logger.info('got the data from mongo db for {}'.format(fileName))
		columnHeaders.insert(0, columnNameToAnalyse)
		return json.dumps(
			{
				'status': 'ok',
				'columnModeData': uniqueValueNameMApToMode,
				'columnValues': uniqueValueNameMApToMode.keys(),
				'columnHeaders': columnHeaders,
				'fileName': fileName,
				'distribution': columnDistributionData,
				'numericValue': useRange,
				'rangeValue': mapOfHeaderAndType
			}
		)