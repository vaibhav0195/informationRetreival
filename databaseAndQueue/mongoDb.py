from pymongo import MongoClient

mongo_object = None
collection_object = None

def getMongoClient(host,port):
    global mongo_object
    if mongo_object is None:
        mongo_object = MongoClient(host,port)
    return mongo_object


def getMongoCollectionClient(host,port,dbName,collectionName):
    global mongo_object
    global collection_object
    if collection_object is None:
        if mongo_object is None:
            mongo_object = getMongoClient(host,port)
        collection_object = mongo_object[dbName][collectionName]
    return collection_object