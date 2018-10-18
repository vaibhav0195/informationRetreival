import pandas as pd
import json
import math,logging
import numpy as np


logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
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
            nameOfHeaders.remove(colName)
            continue
        dtype = str(mapOfNameToDtype[colName])
        if mapOfDtypeToCol.has_key(dtype):
            mapOfDtypeToCol[dtype].append(colName)
        else:
            mapOfDtypeToCol[dtype] = [colName]

    return nameOfHeaders,mapOfDtypeToCol

def findTheIndexOfSubString(arrayOfIndex=[0,1,3,4]):

    listOfIndexes = []
    prevIndexValue=-1 #value of the character
    prevIndexInString = -1 # value of the index to slice
    newSubString = False
    substringIndexList = []
    for index,indexValueOfString in enumerate(arrayOfIndex):
        if index==0:
            prevIndexValue =indexValueOfString
            prevIndexInString=index
        elif index >=1:
            if indexValueOfString-prevIndexValue == 1:
                #same occuerence of words
                if newSubString:
                    if len(substringIndexList) >0:
                        listOfIndexes.append(substringIndexList)
                    substringIndexList =[]
                    newSubString = False
                substringIndexList.append(prevIndexValue)
                prevIndexValue = indexValueOfString
                prevIndexInString = index
            else:
                substringIndexList.append(prevIndexValue)
                prevIndexValue = indexValueOfString
                prevIndexInString = index
                newSubString=True
        if index == arrayOfIndex.shape[0]-1:
            # if indexValueOfString - prevIndexValue ==0 :
            substringIndexList.append(indexValueOfString)
            listOfIndexes.append(substringIndexList)

    return listOfIndexes

def findTheStringsforColumn(listOfStrings):
    '''
    this function returns the all the posible substrings for the given numbers of strings in listOfstrings
    :param listOfStrings: [list of strings]
    :return: {name of substring:its freqvalue}
    '''
    # listofSubStrings = []
    bagOfCharacters = {}
    charctersIndex = {}
    charactorIndex = 1

    mapOfStringToItsCode = {}
    substringfreqcounter = {}
    for stringToUse in listOfStrings:
        charPresent = list(stringToUse)
        for charconsider in charPresent:
            if charconsider in bagOfCharacters:
                bagOfCharacters[charconsider] +=bagOfCharacters[charconsider]
            else:
                charctersIndex[charconsider] = charactorIndex
                charactorIndex +=1
                bagOfCharacters[charconsider] = 1

        charcterCodes = np.asarray([charctersIndex[idx] for idx in charPresent])

        if len(mapOfStringToItsCode.keys()) > 0:
            #do the minusthing
            for prevString in mapOfStringToItsCode:
                charcterCodesPrevious = mapOfStringToItsCode[prevString]
                subtractionPrev = charcterCodes-charcterCodesPrevious
                subtractionPresent = charcterCodesPrevious-charcterCodes
                locationPrev = np.where(subtractionPrev==0)[0]
                listOfIndexes = findTheIndexOfSubString(locationPrev)
                for listOfIndex in listOfIndexes:
                    startingIndex = listOfIndex[0]
                    endingIndex = listOfIndex[-1]
                    substring = prevString[startingIndex:endingIndex+1]
                    # listofSubStrings.append(substring)
                    if substringfreqcounter.has_key(substring):
                        substringfreqcounter[substring] = substringfreqcounter[substring]+1
                    else:
                        substringfreqcounter[substring] = 1
                print 'got the values'
                # locationNext = np.where(subtractionPresent==0)

            print
        mapOfStringToItsCode[stringToUse] = charcterCodes

    # listofSubStrings = list(set(listofSubStrings))
    uniqueValuesDescending = sorted(substringfreqcounter, key=substringfreqcounter.get, reverse=True)
    return substringfreqcounter,uniqueValuesDescending[0]

def doBasicCalulation(dataFrameObj):
    meanOfAllColumns    = dataFrameObj.mean()
    medianOfAllColumns  = dataFrameObj.median()
    stdDevOfAllColumns  = dataFrameObj.std()
    maxOfAllColumns     = dataFrameObj.max()
    minDevOfAllColumns  = dataFrameObj.min()
    return [dict(meanOfAllColumns),dict(medianOfAllColumns),
            dict(stdDevOfAllColumns),
            dict(maxOfAllColumns),dict(minDevOfAllColumns)]

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
    uniqueValuesforThecolumn = dict(dataFrameObj[columnNameToAnalyise].value_counts())
    # uniqueValuesforThecolumn = {str(k).replace('.', ':;:'): int(v) for k, v in uniqueValuesforThecolumn.iteritems()}
    # uniqueValuesForTheColumnName = uniqueValuesforThecolumn.keys()
    for colName in uniqueValuesForTheColumnName:
        if colName in blackList:
            continue
        if type(colName)== float:
            if math.isnan(colName):
                continue
        filterReview = dataFrameObj[columnNameToAnalyise]==colName
        filtered_reviews = dataFrameObj[filterReview]
        mean,median,stdDev,maxVal,minVal = doBasicCalulation(filtered_reviews)
        try:
            infoMap = {'totalNumValues':uniqueValuesforThecolumn[colName],'mean':mean,'median':median,'stdDev':stdDev
                        ,'maxVal':maxVal,'minVal':minVal,'dataFrame':filtered_reviews}
            mapNameToDf[str(colName).replace('.', ':;:')] = infoMap
        except Exception,e:
            logger.exception(e)


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
            try:
                if columnName == columnNameToAnalyise or columnName in blackListColmn:
                    continue
                if dataFrameForCol[columnName].dtype == 'object':
                    dataFrameForCol[columnName].fillna('nan')
                else:
                    dataFrameForCol[columnName].fillna(-1)
                mostUsedValForCol = dataFrameForCol[columnName].mode()
                if mostUsedValForCol.shape[0] == dataFrameForCol.shape[0] or mostUsedValForCol.shape[0] == 0:
                    modeDictionary[columnName] = {'mode':None}
                    #no mode value if the length of mode is equal to dataframe
                else:
                    #get the general answer
                    # filterRows = dataFrameForCol[columnName] == mostUsedValForCol[0]
                    # filteredRowsWithTheMode = dataFrameForCol[filterRows]
                    # seriesToSet = filteredRowsWithTheMode['title']
                    # if seriesToSet.shape[0] <= 0:
                    #     seriesToSet=None
                    #     innerData = {'mode': list(set(list(mostUsedValForCol))), 'title_satisfying': seriesToSet}
                    # else:
                    innerData = {'mode': list(set(list(mostUsedValForCol)))}
                    modeDictionary[columnName] = innerData
            except Exception,e:
                logger.exception(e)
        mapColNameToFrame[str(uniquecolumnNameValue)]['mode'] = modeDictionary

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
                modeFrstColmn = modesOfdictionaryColmn[frstColmnToAnalysis]['mode'][0]
                modeScndColmn = modesOfdictionaryColmn[scndColmnToAnalysis]['mode'][0]
                filterRows = (dataFrameForCol[frstColmnToAnalysis] == modeFrstColmn) & (dataFrameForCol[scndColmnToAnalysis] == modeScndColmn)
                filteredRowsWithTheMode = dataFrameForCol[filterRows]
                seriesToSet = filteredRowsWithTheMode['title']

                if not crossColmnAnalysis.has_key(str(frstColmnToAnalysis).replace('.','_-_')):
                    crossColmnAnalysis[str(frstColmnToAnalysis).replace('.','_-_')] = {}
                crossColmnAnalysis[str(frstColmnToAnalysis).replace('.','_-_')][str(scndColmnToAnalysis).replace('.','_-_')] = {'data': list(set(list(seriesToSet)))}

                if not crossColmnAnalysis.has_key(str(scndColmnToAnalysis).replace('.','_-_')):
                    crossColmnAnalysis[str(scndColmnToAnalysis).replace('.','_-_')] = {}
                crossColmnAnalysis[str(scndColmnToAnalysis).replace('.','_-_')][str(frstColmnToAnalysis).replace('.','_-_')] = {'data': list(set(list(seriesToSet)))}
        mapColNameToFrame[str(uniqueValuePresent)]['crossColumnAnalysis'] = crossColmnAnalysis
        # print 'got the colmnWithModes'

    return mapColNameToFrame

def calculateDistributionOfDatadataFrame(mapColumnNameToFrame,columnNameToAnalyse,blackList):

    mapUniqueColData = {}
    for uniqueValuesOfColumn in mapColumnNameToFrame:
        dataFrameForColumn = mapColumnNameToFrame[uniqueValuesOfColumn]['dataFrame']
        dtypesOfColumns = dataFrameForColumn.dtypes
        mapOfNameToDtype = dict(dtypesOfColumns)
        distributionDataForColumn = {}
        for columnName in dataFrameForColumn:
            if columnName not in blackList and columnName not in columnNameToAnalyse:
                distributionDataForColumn[columnName] = {}
                uniqueValuesforThecolumn = dict(dataFrameForColumn[columnName].value_counts())
                uniqueValuesforThecolumn = {str(k).replace('.',':;:'): int(v) for k, v in uniqueValuesforThecolumn.iteritems()}
                # uniqueValuesforThecolumn = dict(dataFrameForColumn.groupby([columnName]).count())
                logger.info('found {} number of unique information'.format(len(uniqueValuesforThecolumn)))
                if 'int' in str(mapOfNameToDtype[columnName]) or 'float' in str(mapOfNameToDtype[columnName]):

                    logger.debug('the type of column is {} so also adding max,min,median,mean,mode of column'.format(len(uniqueValuesforThecolumn)))
                    distributionDataForColumn[columnName] = {'distribution':uniqueValuesforThecolumn,
                                                             'min':mapColumnNameToFrame[uniqueValuesOfColumn]['minVal'][columnName],
                                                             'max':mapColumnNameToFrame[uniqueValuesOfColumn]['maxVal'][columnName],
                                                             'median':mapColumnNameToFrame[uniqueValuesOfColumn]['median'][columnName]}
                else:
                    distributionDataForColumn[columnName] = {'distribution': uniqueValuesforThecolumn,
                                                             'min':None,
                                                             'max':None,
                                                             'median':None}

                modeValuesForcolumn = mapColumnNameToFrame[uniqueValuesOfColumn]['mode'][columnName]['mode']
                if modeValuesForcolumn is None:
                    distributionDataForColumn[columnName]['mode'] = None
                elif len(modeValuesForcolumn) == 0:
                    distributionDataForColumn[columnName]['mode'] = None
                else:
                    distributionDataForColumn[columnName]['mode'] = modeValuesForcolumn[0]
        mapUniqueColData[str(uniqueValuesOfColumn)] = {'dataAlongDifferentColumn':distributionDataForColumn,
                                                       'totalNumValues':mapColumnNameToFrame[uniqueValuesOfColumn]['totalNumValues']}


    return mapUniqueColData

def analyiseTheFrame(dataFrameObj,columnNameToAnalyise='platform',blackList=['Unnamed: 0']):
    # dataFrameObj.fillna(0)
    # jsonPath = saveDir+columnNameToAnalyise+'.json'
    print 'doing with the basic analysis for {}'.format(columnNameToAnalyise)
    headerNames,mapOfDtypetoCol = getTheColmnNames(dataFrameObj,blackList)
    headerNames = list(set(headerNames)-set(blackList))
    mapColNameToFrame = getMappingOfHeaderAndDataFrame(dataFrameObj,columnNameToAnalyise,blackList)
    # numHeaders = len(headerNames)
    mapColNameToFrame = calculateTheModeDataForStringObject(mapColNameToFrame,columnNameToAnalyise,blackList)
    mapColNameToFrame = calculateDistributionOfDatadataFrame(mapColNameToFrame,columnNameToAnalyise,blackList)
    # mapColNameToFrame = doInterColumnAnalysis(mapColNameToFrame,headerNames)
    print 'done with the basic analysis for {}'.format(columnNameToAnalyise)
    return mapColNameToFrame



if __name__=='__main__':
    matchedString = '20802713'
    rollNumbers = []
    for i in range(1,128):
        if i <=9:
            rollNumbers.append('00'+str(i)+matchedString)
        elif i >=10 and i<=99:
            rollNumbers.append('0'+str(i)+matchedString)
        else:
            rollNumbers.append(str(i) + matchedString)
    findTheStringsforColumn(rollNumbers)
    # csvPath = '/home/yoda/ign_subset.csv'
    # reviews = pd.read_csv(csvPath)
    # saveDir = '/home/gabbar/mlocr_data/informationretreival/jsonFolder'
    # analyiseTheFrame(reviews,'release_year')
# nameOfColumns = getTheColmnNames(reviews)
# print nameOfColumns
