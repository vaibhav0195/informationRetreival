google.charts.load('current', {'packages':['corechart']});
function clearTable(tableId)
{
 var tableRef = document.getElementById(tableId);
 while ( tableRef.rows.length > 0 )
 {
  tableRef.deleteRow(0);
 }
}

function changeImage(element){
    $.get('thumb?imageName=' + element.name, function(data){
        try{
            document.getElementById("labelledMatter").style.visibility = "visible";
        }
        catch(err){

        }
        $(".textcont").remove();
        $(".DocumentItem1").append("<div class=\"textcont\"></div>");
        parsedData = JSON.parse(data)
        folder = parsedData.folder
        imageName = parsedData.imageData.name
        postProcessedData = parsedData.postProcessInfo

        basename = imageName.substring(0, imageName.indexOf('.'))
        ext = imageName.substring(imageName.indexOf('.'))
        //document.getElementsByName("originalImage")[0].src = '/static/images/' + folder + '/' + basename + '_boundary' + ext  //since actualimage.jpg is same as actualimage_boundary.jpg
        document.getElementsByName("originalImage")[0].src = '/static/images/' + folder + '/' + imageName  //since actualimage.jpg is same as actualimage_boundary.jpg
//        document.getElementsByName("segmentedImage")[0].src = '/static/images/' + folder + '/segmented.' + basename + ext
        $('.textcont').append((parsedData.text))

        $('.billDate')[0].innerHTML = postProcessedData.billDate;
        $('.billNumber')[0].innerHTML = postProcessedData.billNumber;
        $('.billTime')[0].innerHTML = postProcessedData.billTime;
        $('.billTotal')[0].innerHTML = postProcessedData.billTotal;

   });

}

$(document).on('change', '.btn-file :file', function() {
   var input = $(this),
   numFiles = input.get(0).files ? input.get(0).files.length : 1,
   label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
   $("#button").click();
});

$("#fileUploadForm").submit(function(){
   $("#uploaddiv").hide()

   var formData = new FormData($(this)[0]);
   $.ajax({
       url: window.location.pathname,
       type: 'POST',
       data: formData,
       async: true,
       success: function (data) {
            $("#imageResponse").css('visibility',"visible");
//            $(".DocumentItem1").append("<div class=\"textcont\"></div>");
            parsedData = JSON.parse(data)
            status = parsedData.status
            if (status == 'ok')
            {
                headerData = parsedData.csvHeaders
                tableIdToUse = 'nameAndDtypeOfColumn'
                nameOfFile = parsedData.fileName
                var arrayLength = headerData.length;
                for (var i = 0; i < arrayLength; i++)
                    {
                    nameOfColumn = headerData[i][0]
                    dTypeOfColumn = headerData[i][1]
                    columnToUse = headerData[i][2]
                    if (columnToUse == true)
                        {
                        addRow(tableIdToUse,nameOfColumn,dTypeOfColumn,nameOfFile)
                        }
                    }
                 $("#uploaddiv").show();
            }

            if (status == 'error')
            {
                console.log('error returned from the server')
            }

            }
        ,
        error:function(){
            alert("Error occured while processing the image. Please try again.");
            $('.uploaddivnew').remove();
            $("#uploaddiv").show();
            $("[name='"+firstImage+"']").click();
        },
       cache: false,
       contentType: false,
       processData: false,

   });


   return false;
});

$(document).on("click", "#doAnalysis", function(){
    var nameOfFile      = $(this).attr('data-nameFile');
    var columnToAnalyse  = $(this).attr('data-nameColumn');
    var jsonData = {'nameOfFile':nameOfFile,'columnToAnalyse':columnToAnalyse};
    $.ajax({
       url: 'getTheJsonResponse',
       type: 'POST',
       data: JSON.stringify(jsonData),
       async: true,
       success: function (data) {
            $("#modeDataToUse").css('visibility',"visible");
//            $("#imageResponse").css('visibility',"hidden");
//            $(".DocumentItem1").append("<div class=\"textcont\"></div>");
            parsedData = data
            status = parsedData.status
            if (status == 'ok')
            {
                columnModeData = parsedData.columnModeData
                nameOfuniqueValues = parsedData.columnValues
                fileName = parsedData.fileName
                headerNames = parsedData.columnHeaders
                distributionData = parsedData.distribution
                useRangeData = parsedData.numericValue
                arrayOfRangeData = parsedData.rangeValue
                //tableID,columnData,idofTableValues,headerValues
                //datatowrite,elementType,classListString,idToAssign,data-[name],valueofit,typeOfelement
                var rowChartData = maketheDataForGoogleChartFormat(distributionData,columnToAnalyse,nameOfFile);
                var elementtype = []
                for (var i =0 ;i<headerNames.length; i++)
                    {
                        elementtype.push('h5')
                    }
                var tableID = 'uniqueValuesAndMode';
                var columnDataHeader = [[headerNames,elementtype,null,null,null,null,null]]
                fileName = parsedData.fileName
                var numRows = nameOfuniqueValues.length;
                var numColumns = headerNames.length;
                addRowProtoType(tableID,columnDataHeader,1)
                for (var uniqueValueForRow in columnModeData)
                {
                    var columnDataBody = [uniqueValueForRow]
                    columnDataBody.fill('-',1,headerNames.length)
                    var columnDataElementType = ['button']
                    columnDataElementType.fill('button',1,headerNames.length)
                    var classListString = ['btn::btn-success']
                    classListString.fill('button',1,headerNames.length)
                    var idToAssign = ['uniqueColumnValue']
                    idToAssign.fill('uniqueColumnValue',1,headerNames.length)
                    var dataVariable = ['data-columnData']
                    dataVariable.fill('data-columnData',1,headerNames.length)
                    var dataValue = [columnDataBody]
                    dataValue.fill('data-columnData',1,headerNames.length)
                    var typeOfValue = ['button']
                    typeOfValue.fill(0,1,headerNames.length)
                    var analysedData = columnModeData[uniqueValueForRow]

                    for (var analysedColName in analysedData)
                        {
                            var innerData = analysedData[analysedColName]
                            var indexVal = headerNames.indexOf(analysedColName)
                            columnDataElementType[indexVal] = 'button'
                            idToAssign[indexVal] = 'uniqueColumnMode';
                            dataVariable[indexVal] = 'data-columnDataMode';
                            if (innerData['relevant'] == true)
                            {

                                var modeData = innerData['mode']
                                columnDataBody[indexVal] = modeData
                                dataValue[indexVal] = modeData +':;:'+analysedColName+':;:'+uniqueValueForRow+':;:'+columnToAnalyse+':;:'+nameOfFile;
                                typeOfValue.push('button')

                            }
                            else
                            {
                                columnDataBody[indexVal] = '-'
                                dataValue[indexVal] = '-'
                                typeOfValue[indexVal] = null

                            }

                        }

                    var rowData = [[columnDataBody,columnDataElementType,classListString,idToAssign,dataVariable,dataValue,typeOfValue]]
                    addRowProtoType(tableID,rowData,0)
                    columnDataHeader.push(rowData)

                }
                if (useRangeData)
                {
                    console.log('got the integer data can set the slider');
                    drawSlider(arrayOfRangeData,fileName,columnToAnalyse);
                }
                drawPiewChart(rowChartData,'pieChartHeader')

                 $("#uploaddiv").show();
            }

            if (status == 'error')
            {
                console.log('error returned from the server')
            }

            }
        ,
        error:function(){
            alert("Error occured while processing the image. Please try again.");
            $('.uploaddivnew').remove();
            $("#uploaddiv").show();
        },
       cache: false,
       contentType: false,
       processData: false,
       dataType: "json",
       contentType : "application/json"
   });
});


$(document).on("click", "#uniqueColumnMode", function(){
    var columnToAnalyse  = $(this).attr('data-columndatamode');
    var jsonData = {'columnToAnalyse':columnToAnalyse};
    $.ajax({
       url: 'getTheAnalysisData',
       type: 'POST',
       data: JSON.stringify(jsonData),
       async: true,
       success: function (data) {
            $("#modeDataToUse").css('visibility',"visible");
//            $("#imageResponse").css('visibility',"hidden");
//            $(".DocumentItem1").append("<div class=\"textcont\"></div>");
            parsedData = data
            status = parsedData.status
            if (status == 'ok')
            {

                dataViewedByRow = parsedData.rowData.distribution;
                dataViewedByCol = parsedData.columnData.distribution;
                rowHeader        = parsedData.rowHeader;
                columnHeader    = parsedData.columnHeader;
                var rowChartData = maketheDataForGoogleChartFormat(dataViewedByRow,rowHeader,columnHeader);
                var columnChartData = maketheDataForGoogleChartFormat(dataViewedByCol,columnHeader,rowHeader);
                drawPiewChart(rowChartData,'pieChartRow')
                drawPiewChart(columnChartData,'pieChartCol')
            }

            if (status == 'error')
            {
                console.log('error returned from the server')
            }

            }
        ,
        error:function(){
            alert("Error occured while processing the image. Please try again.");
            $('.uploaddivnew').remove();
            $("#uploaddiv").show();
        },
       cache: false,
       contentType: false,
       processData: false,
       dataType: "json",
       contentType : "application/json"
   });
});

$(document).on("click", "#rangeselectupload", function(){
//    var minValue  = document.getElementById("minrangevalue");
//    var maxValue  = document.getElementById("maxrangevalue");

    var maxValues = document.getElementsByClassName("sliderClassesMax");
    var minValues = document.getElementsByClassName("sliderClassesMin");


    var fileName  = minValues[0].dataset.filename;
    var columnName  = minValues[0].dataset.columnname;
    var columnToAnalyse  = minValues[0].dataset.analysiscolumnname;
    var jsonDataMin = {}
    for (var i=0;i<minValues.length;i++)
    {
        columnName = minValues[i].dataset.columnname;
        minimumValue = minValues[i].value;
        jsonDataMin[columnName] = minimumValue
    }
    var jsonDataMax = {}
    for (var i=0;i<maxValues.length;i++)
    {
        columnName = maxValues[i].dataset.columnname;
        maxValue = maxValues[i].value;
        jsonDataMax[columnName] = maxValue
    }
    var finalJson = {'fileName':fileName,'columnNametoAnalyse':columnToAnalyse,'columnRangeData':{}}
    for (var key in jsonDataMin)
    {
        minimumValue = jsonDataMin[key]
        maxValue = jsonDataMax[key]
        finalJson['columnRangeData'][key] = {'min':minimumValue,'max':maxValue}

    }
    $.ajax({
       url: 'doRangeAnalysis',
       type: 'POST',
       data: JSON.stringify(finalJson),
       async: true,
       success: function (data) {
            $("#modeDataToUse").css('visibility',"visible");
//            $("#imageResponse").css('visibility',"hidden");
//            $(".DocumentItem1").append("<div class=\"textcont\"></div>");
            parsedData = data
            status = parsedData.status
            if (status == 'ok')
            {
                columnModeData = parsedData.columnModeData
                nameOfuniqueValues = parsedData.columnValues
                fileName = parsedData.fileName
                headerNames = parsedData.columnHeaders
                distributionData = parsedData.distribution
                useRangeData = parsedData.numericValue
                arrayOfRangeData = parsedData.rangeValue
                //tableID,columnData,idofTableValues,headerValues
                //datatowrite,elementType,classListString,idToAssign,data-[name],valueofit,typeOfelement
                var rowChartData = maketheDataForGoogleChartFormat(distributionData,columnToAnalyse,nameOfFile);
                var elementtype = []
                for (var i =0 ;i<headerNames.length; i++)
                    {
                        elementtype.push('h5')
                    }
                var tableID = 'uniqueValuesAndMode';
                var columnDataHeader = [[headerNames,elementtype,null,null,null,null,null]]
                fileName = parsedData.fileName
                var numRows = nameOfuniqueValues.length;
                var numColumns = headerNames.length;
                addRowProtoType(tableID,columnDataHeader,1)
                for (var uniqueValueForRow in columnModeData)
                {
                    var columnDataBody = [uniqueValueForRow]
                    columnDataBody.fill('-',1,headerNames.length)
                    var columnDataElementType = ['button']
                    columnDataElementType.fill('button',1,headerNames.length)
                    var classListString = ['btn::btn-success']
                    classListString.fill('button',1,headerNames.length)
                    var idToAssign = ['uniqueColumnValue']
                    idToAssign.fill('uniqueColumnValue',1,headerNames.length)
                    var dataVariable = ['data-columnData']
                    dataVariable.fill('data-columnData',1,headerNames.length)
                    var dataValue = [columnDataBody]
                    dataValue.fill('data-columnData',1,headerNames.length)
                    var typeOfValue = ['button']
                    typeOfValue.fill(0,1,headerNames.length)
                    var analysedData = columnModeData[uniqueValueForRow]

                    for (var analysedColName in analysedData)
                        {
                            var innerData = analysedData[analysedColName]
                            var indexVal = headerNames.indexOf(analysedColName)
                            columnDataElementType[indexVal] = 'button'
                            idToAssign[indexVal] = 'uniqueColumnMode';
                            dataVariable[indexVal] = 'data-columnDataMode';
                            if (innerData['relevant'] == true)
                            {

                                var modeData = innerData['mode']
                                columnDataBody[indexVal] = modeData
                                dataValue[indexVal] = modeData +':;:'+analysedColName+':;:'+uniqueValueForRow+':;:'+columnToAnalyse+':;:'+nameOfFile;
                                typeOfValue.push('button')

                            }
                            else
                            {
                                columnDataBody[indexVal] = '-'
                                dataValue[indexVal] = '-'
                                typeOfValue[indexVal] = null

                            }

                        }

                    var rowData = [[columnDataBody,columnDataElementType,classListString,idToAssign,dataVariable,dataValue,typeOfValue]]
                    addRowProtoType(tableID,rowData,0)
                    columnDataHeader.push(rowData)

                }
                if (useRangeData)
                {
                    console.log('got the integer data can set the slider');
                    drawSlider(arrayOfRangeData,fileName,columnToAnalyse);
                }
                drawPiewChart(rowChartData,'pieChartHeader')

                 $("#uploaddiv").show();
            }

            if (status == 'error')
            {
                console.log('error returned from the server')
            }

            }
        ,
        error:function(){
            alert("Error occured while processing the image. Please try again.");
            $('.uploaddivnew').remove();
            $("#uploaddiv").show();
        },
       cache: false,
       contentType: false,
       processData: false,
       dataType: "json",
       contentType : "application/json"
   });
});


function addRow(tableID,nameofColumn,dTypeOfColumn,nameOfFile)
{
    var tableBody = document.getElementById(tableID).getElementsByTagName('tbody')[0];
    var rowCount = tableBody.rows.length;
    var row = tableBody.insertRow(rowCount);
    var cell1 = row.insertCell(0);
    var element1 = document.createElement("button");
    var element2 = document.createElement("h5");
    //<button type="button" class="btn btn-success">Success</button>
    element1.classList.add("btn");
    element1.classList.add("btn-success");
    element1.innerHTML=nameofColumn;
    element1.setAttribute("data-nameFile",nameOfFile);
    element1.setAttribute("data-nameColumn",nameofColumn);
    element1.setAttribute("id","doAnalysis");
    element1.setAttribute("type","button");
    element2.innerHTML=dTypeOfColumn
    cell1.appendChild(element1);
    var  cell2= row.insertCell(1);
    cell2.appendChild(element2);
}

function addRowProtoType(tableID,columnData,headerValues)
{   /*
    this function adds the row to a table specified by the tableID
    tableId : id of table to fill the values
    columnData : data about each column in the row
    ifofTablevalues : values to set to the each element
    headerValue : weather its a header element or not.(if 1 then it is header else no)
    */
    if (headerValues ==1)
    {
        var tableBody = document.getElementById(tableID);
    }
    else
    {
        var tableBody = document.getElementById(tableID).getElementsByTagName('tbody')[0];
    }

    var rowCount = tableBody.rows.length;
    var row = tableBody.insertRow(rowCount);

    var numColumns = columnData.length;
    for (var i = 0; i < numColumns; i++)
    {
        //array to write in the column is of format
        //[datatowrite,elementType,classListString,idToAssign,data-[name],valueofit,typeOfelement]

        var currentDatatowrite = columnData[i]
        var dataToWrite = currentDatatowrite[0];
        var numCols = dataToWrite.length;
        var elementType = currentDatatowrite[1];
        var classList = currentDatatowrite[2]
        var idForElement = currentDatatowrite[3];
        var dataElementName = currentDatatowrite[4];
        var dataElementValue = currentDatatowrite[5];
        var typeOfElement = currentDatatowrite[6];
        for (var idx = 0; idx < numCols; idx++)
        {
            var cell = row.insertCell(idx);
            var element1 = document.createElement(elementType[idx]);
            element1.innerHTML=dataToWrite[idx].toString();

            if (idForElement == null)
            {
                console.log('id set to be is null')
            }
            else
            {
                element1.setAttribute('id',idForElement[idx].toString());
            }
            if (dataElementName == null)
            {
                console.log('id set to be is null')
            }
            else
            {
                element1.setAttribute(dataElementName[idx].toString(),dataElementValue[idx].toString());
            }
            if (typeOfElement == null)
            {
                console.log('type is null so not setting it')
            }
            else
            {
                if (typeOfElement[idx] != null)
                {
                    element1.setAttribute("type",typeOfElement[idx].toString());
                }
            }
            if (classList == null)
            {
                console.log('gotnull')
            }
            else
            {
                classList=classList[i].split('::');
                var numClasses = classList.length;
                for (var j = 0; j < numClasses; j++)
                {
                    element1.classList.add(classList[j]);
                }
            }


            cell.appendChild(element1);
        }



    }
}

function maketheDataForGoogleChartFormat(parsedJson,keyHeader,valuesHeader)
{
    var arrayOfValues = [[keyHeader,valuesHeader]]
    for (var key in parsedJson)
    {
        arrayOfValues.push([key,parsedJson[key]])
    }
    return arrayOfValues
}

function drawPiewChart(dataToshow,idOfElement)
{

      google.charts.setOnLoadCallback(drawChart(dataToshow));

      function drawChart(dataToshow) {

        var data = google.visualization.arrayToDataTable(dataToshow);
        var headers = dataToshow[0]
        var options = {
          title: 'data of '+headers[0]+' at different '+headers[1],
          'width':550, 'height':400,
              sliceVisibilityThreshold: 0
        };

        var chart = new google.visualization.PieChart(document.getElementById(idOfElement));
        chart.draw(data, options);
      }

}

function drawSlider(parsedJson,fileName,columnToAnalyse)
{


    var parentForm = document.getElementById("formdataSlider");
    var counterDiv = 0;
    for(var key in parsedJson)
    {
        counterDiv +=1
        var div = document.createElement("div");
        div.setAttribute("id","rangeslider_"+key);
        div.setAttribute("data-role","rangeslider");
        var dataForColumn = parsedJson[key]
        var minimumValue = dataForColumn[0];
        var maxValue = dataForColumn[dataForColumn.length-1];
        var inputvaluemin = document.createElement("input");
        var inputvaluemax = document.createElement("input");
        var labelvaluemin = document.createElement("label");
        var labelvaluemax = document.createElement("label");
        labelvaluemin.setAttribute('id','labelvalueMin_'+key)
        labelvaluemin.setAttribute('for','valueMin_'+key)
        labelvaluemin.innerHTML='Min'
        labelvaluemax.setAttribute('id','labelvalueMax_'+key)
        labelvaluemax.setAttribute('for','valueMax_'+key)
        labelvaluemax.innerHTML='Max'
        inputvaluemin.setAttribute('id','valueMin_'+key)
        inputvaluemin.setAttribute('class','sliderClassesMin')
        inputvaluemin.setAttribute('name','valueMin_'+key)
//        inputvaluemin.setAttribute('type','range')
        inputvaluemin.setAttribute("value",minimumValue);
        inputvaluemin.setAttribute("max",maxValue);
        inputvaluemin.setAttribute("min",minimumValue);
        inputvaluemin.setAttribute("data-columnName",key);
        inputvaluemin.setAttribute("data-fileName",fileName);
        inputvaluemin.setAttribute("data-analysisColumnName",columnToAnalyse);

        inputvaluemax.setAttribute('id','valueMax_'+key)
        inputvaluemax.setAttribute('name','valueMax_'+key)
//        inputvaluemax.setAttribute('type','range')
        inputvaluemax.setAttribute('class','sliderClassesMax')
        inputvaluemax.setAttribute("value",maxValue);
        inputvaluemax.setAttribute("max",maxValue);
        inputvaluemax.setAttribute("min",minimumValue);
        inputvaluemax.setAttribute("data-columnName",key);
        inputvaluemax.setAttribute("data-fileName",fileName);
        div.appendChild(labelvaluemin)
        div.appendChild(inputvaluemin)
        div.appendChild(labelvaluemax)
        div.appendChild(inputvaluemax)

        parentForm.appendChild(div)
    }
    for (var key in parsedJson)
    {
        $( "div#"+"rangeslider_"+key ).rangeslider();
//        $( "div#"+"rangeslider_"+key ).rangeslider("refresh");
    }
//  $( "div#"+"slidervalues"+key ).rangeslider();
  $("#slidervalues").css('visibility',"visible");
}