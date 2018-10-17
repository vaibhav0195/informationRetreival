import pika,logging,json
import informationRetreval
from databaseAndQueue import mongoDb

logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
collectionDb = mongoDb.getMongoCollectionClient(host='localhost',port=27017,
                                                dbName='informationRetreival',collectionName='dataframeAnalysis')

collectionDbHeaderInfo = mongoDb.getMongoCollectionClient(host='localhost',port=27017,
													dbName='informationRetreival',collectionName='dataframeHeadAndDtype')


def removeTheKey(mapOfInfo,keyToRemove):
    mapOfInfoWithoutdataFrame = {}
    for key in mapOfInfo:
        innerDict = mapOfInfo[key]
        value = innerDict.pop(keyToRemove,None)
        mapOfInfoWithoutdataFrame[key] = innerDict

    return mapOfInfoWithoutdataFrame

def informationRetrieval(ch, method, properties, body):
    dataFromQueue = json.loads(body)
    fileName = dataFromQueue['fileName']
    filePath = dataFromQueue['filePath']
    dataFrameObj = informationRetreval.getTheDataFrame(filePath)
    dataDb = collectionDbHeaderInfo.find_one({"fileName": fileName})
    columnUsefullMap = {}
    blackListColumns = []
    for dataOfColumn in dataDb['headers']:
        columnUsefullMap[dataOfColumn[0]] = dataOfColumn[2]
        if not dataOfColumn[2]:
            blackListColumns.append(dataOfColumn[0])
    columnNames,dtypMap = informationRetreval.getTheColmnNames(dataFrameObj,blackList=blackListColumns)
    analysisAlongTheKeys = {} #information according to the key of the dict
    dbUpdateObj = {'_id':fileName,'filePath':filePath}
    for columnName in columnNames:
        if columnName not in blackListColumns:
            mapOfInfo = informationRetreval.analyiseTheFrame(dataFrameObj,columnName,blackListColumns)
            mapOfInfo = removeTheKey(mapOfInfo,'dataFrame')
            analysisAlongTheKeys[columnName] = {'analysis':mapOfInfo}
    dbUpdateObj['analysedData'] = analysisAlongTheKeys
    mongoObj = collectionDb.update_many(
        {'_id': fileName},
        {
            "$set": {'processed':dbUpdateObj}
        }
    )
    logger.info('got the {} file from queue.'.format(body))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    return

if __name__ =='__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    startTime = None

    channel.queue_declare(queue='informationRetreival', durable=True)
    channel.basic_qos(prefetch_count=1) #send one file to worker
    channel.basic_consume(informationRetrieval,
                          queue='informationRetreival')

    channel.start_consuming()