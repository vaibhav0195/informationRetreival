import pandas as pd
import json
import math
import numpy as np

def getTheDataFrame(filePath):
    return pd.read_csv(filePath)

def getTheColmnNames(dataFrameObj,blackList=['Unnamed: 0']):
    '''

    :param dataFrameObj: dataframe to process
    :param blacklist : col Not to process
    :return: 1) the unique names of col in dataframe
             2) the dictionar {dtypePresent:[col1,col2]}
    '''
    dtypesOfColumns = dataFrameObj.dtypes
    mapOfNameToDtype = dict(dtypesOfColumns)
    nameOfHeaders = list(dataFrameObj)
    mapOfDtypeToCol = {}
    for colName in mapOfNameToDtype:
        if colName in blackList:
            continue
        dtype = str(mapOfNameToDtype[colName])
        if mapOfDtypeToCol.has_key(dtype):
            mapOfDtypeToCol[dtype].append(colName)
        else:
            mapOfDtypeToCol[dtype] = [colName]

    return nameOfHeaders,mapOfDtypeToCol

def doBasicCalulation(dataFrameObj):
    meanOfAllColumns    = dataFrameObj.mean()
    medianOfAllColumns  = dataFrameObj.median()
    stdDevOfAllColumns  = dataFrameObj.std()
    maxOfAllColumns     = dataFrameObj.max()
    minDevOfAllColumns  = dataFrameObj.min()
    return [meanOfAllColumns,medianOfAllColumns,
            stdDevOfAllColumns,
            maxOfAllColumns,minDevOfAllColumns]

def getMappingOfHeaderAndDataFrame(dataFrameObj,columnNameToAnalyise,blackList=['Unnamed: 0']):
    '''

    :param dataFrameObj: data frame to analyse
    :param columnNameToAnalyise: the column name along which the analysis is based
    :return: a hash map as
    {
    key[unique name of the values in the columnname] =
    {
    mean,median,stdDev,maxVal,minVal,rows-of-the-dataframeObj-containing-the-columnname-equal-to-key
    }
    }
    '''
    mapNameToDf = {}
    uniqueValuesForTheColumnName = dataFrameObj[columnNameToAnalyise].unique()
    for colName in uniqueValuesForTheColumnName:
        if colName in blackList:
            continue
        if type(colName)== float:
            if math.isnan(colName):
                continue
        filterReview = dataFrameObj[columnNameToAnalyise]==colName
        filtered_reviews = dataFrameObj[filterReview]
        mean,median,stdDev,maxVal,minVal = doBasicCalulation(filtered_reviews)
        infoMap = {'mean':mean,'median':median,'stdDev':stdDev
                    ,'maxVal':maxVal,'minVal':minVal,'dataFrame':filtered_reviews}
        mapNameToDf[colName] = infoMap

    return mapNameToDf

def calculateTheModeDataForStringObject(mapColNameToFrame,columnNameToAnalyise,blackListColmn):
    '''
    this function calculate the most occuring object for every column in the dataframe.
    if the mode is not there we set it as NONE
    :param mapColNameToFrame: dictioanry {
    key[unique name of the values in the columnname] =
    {
    mean,median,stdDev,maxVal,minVal,rows-of-the-dataframeObj-containing-the-columnname-equal-to-key
    }
    }
    :param columnNameToAnalyise: the name of column to do analysis
    :return:
    {
    key[unique name of the values in the columnname] =
    {
    mean,median,stdDev,maxVal,minVal,rows-of-the-dataframeObj-containing-the-columnname-equal-to-key,col1:{'mode','title}...
    }
    }
    '''

    for uniquecolumnNameValue in mapColNameToFrame:
        modeDictionary = {}
        dataFrameForCol = mapColNameToFrame[uniquecolumnNameValue]['dataFrame']
        for columnName in dataFrameForCol:
            if columnName == columnNameToAnalyise or columnName in blackListColmn:
                continue
            if dataFrameForCol[columnName].dtype == 'object':
                dataFrameForCol[columnName].fillna('nan')
            else:
                dataFrameForCol[columnName].fillna(-1)
            mostUsedValForCol = dataFrameForCol[columnName].mode()
            if mostUsedValForCol.shape[0] == dataFrameForCol.shape[0]:
                modeDictionary[columnName] = {'mode':None}
                #no mode value if the length of mode is equal to dataframe
            else:
                #get the general answer
                filterRows = dataFrameForCol[columnName] == mostUsedValForCol[0]
                filteredRowsWithTheMode = dataFrameForCol[filterRows]
                seriesToSet = filteredRowsWithTheMode['title']
                if seriesToSet.shape[0] <= 0:
                    seriesToSet=None
                innerData = {'mode':mostUsedValForCol,'title_satisfying':seriesToSet}
                modeDictionary[columnName] = innerData
        mapColNameToFrame[uniquecolumnNameValue]['mode'] = modeDictionary

    return mapColNameToFrame

def doInterColumnAnalysis(mapColNameToFrame,uniqueColNames):

    for uniqueValuePresent in mapColNameToFrame:
        dataFrameForCol = mapColNameToFrame[uniqueValuePresent]['dataFrame']
        modesOfdictionaryColmn = mapColNameToFrame[uniqueValuePresent]['mode']
        colmnWithModes = [key for key in modesOfdictionaryColmn if modesOfdictionaryColmn[key]['mode'] is not None]
        crossColmnAnalysis = {}
        for idx in range(len(colmnWithModes)):
            for jdx in range(len(colmnWithModes)):
                frstColmnToAnalysis = colmnWithModes[idx]
                scndColmnToAnalysis = colmnWithModes[jdx]
                modeFrstColmn = dict(modesOfdictionaryColmn[frstColmnToAnalysis]['mode']).values()[0]
                modeScndColmn = dict(modesOfdictionaryColmn[scndColmnToAnalysis]['mode']).values()[0]
                filterRows = (dataFrameForCol[frstColmnToAnalysis] == modeFrstColmn) & (dataFrameForCol[scndColmnToAnalysis] == modeScndColmn)
                filteredRowsWithTheMode = dataFrameForCol[filterRows]
                seriesToSet = filteredRowsWithTheMode['title']
                if not crossColmnAnalysis.has_key(frstColmnToAnalysis):
                    crossColmnAnalysis[frstColmnToAnalysis] = {}
                crossColmnAnalysis[frstColmnToAnalysis][scndColmnToAnalysis] = {'data': seriesToSet}
                if not crossColmnAnalysis.has_key(scndColmnToAnalysis):
                    crossColmnAnalysis[scndColmnToAnalysis] = {}
                crossColmnAnalysis[frstColmnToAnalysis][scndColmnToAnalysis] = {'data': seriesToSet}
        mapColNameToFrame[uniqueValuePresent]['crossColumnAnalysis'] = crossColmnAnalysis
        # print 'got the colmnWithModes'

    return mapColNameToFrame

def analyiseTheFrame(dataFrameObj,columnNameToAnalyise='platform',blackList=['Unnamed: 0']):
    # dataFrameObj.fillna(0)
    jsonPath = saveDir+columnNameToAnalyise+'.json'
    headerNames,mapOfDtypetoCol = getTheColmnNames(dataFrameObj,blackList)
    headerNames = list(set(headerNames)-set(blackList))
    mapColNameToFrame = getMappingOfHeaderAndDataFrame(dataFrameObj,columnNameToAnalyise,blackList)
    # numHeaders = len(headerNames)
    mapColNameToFrame = calculateTheModeDataForStringObject(mapColNameToFrame,columnNameToAnalyise,blackList)
    mapColNameToFrame = doInterColumnAnalysis(mapColNameToFrame,headerNames)
    print 'done with the basic analysis'
    return mapColNameToFrame
if __name__=='__main__':
    csvPath = '/home/yoda/ign_subset.csv'
    reviews = pd.read_csv(csvPath)
    saveDir = '/home/gabbar/mlocr_data/informationretreival/jsonFolder'
    analyiseTheFrame(reviews,'platform')
# nameOfColumns = getTheColmnNames(reviews)
# print nameOfColumns
