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
                    addRow(tableIdToUse,nameOfColumn,dTypeOfColumn,nameOfFile)
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
            $("#imageResponse").css('visibility',"visible");
//            $(".DocumentItem1").append("<div class=\"textcont\"></div>");
            parsedData = JSON.parse(data)
            status = parsedData.status
            if (status == 'ok')
            {
                uniqueValuesOfColumn = parsedData.columnModeData
                mapOfValuesOfColumn = parsedData.columnValues
                otherColumnAlongwhichAnalysis = parsedData.columnHeaders
                //tableID,columnData,idofTableValues,headerValues
                //datatowrite,elementType,classListString,idToAssign,data-[name],valueofit,typeOfelement
                var tableID = 'uniqueValuesAndMode';
                var columnData = [[]]
                fileName = parsedData.fileName
                var numRows = uniqueValuesOfColumn.length;
                var numColumns = otherColumnAlongwhichAnalysis.length;

                for (var i = 0; i < arrayLength; i++)
                    {

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

function addRowProtoType(tableID,columnData,idofTableValues,headerValues)
{   /*
    this function adds the row to a table specified by the tableID
    tableId : id of table to fill the values
    columnData : data about each column in the row
    ifofTablevalues : values to set to the each element
    headerValue : weather its a header element or not.(if 1 then it is header else no)
    */
    if (headervalues ==1)
    {
        var tableBody = document.getElementById(tableID).getElementsByTagName('thead')[0];
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
        var cell = row.insertCell(i);
        var currentDatatowrite = columnData[i]
        var dataToWrite = currentDatatowrite[0];
        var elementType = currentDatatowrite[1];
        var classList = currentDatatowrite[2].split('::');
        var numClasses = classList.length;
        var idForElement = currentDatatowrite[3];
        var dataElementName = currentDatatowrite[4];
        var dataElementValue = currentDatatowrite[5];
        var typeOfElement = currentDatatowrite[6];
        var element1 = document.createElement(elementType);
        element1.innerHTML=dataToWrite;
        element1.setAttribute(dataElementName,dataElementValue);
        element1.setAttribute('id',idForElement);
        if typeOfElement == null
        {
            console.log('type is null so not setting it')
        }
        else
        {
            element1.setAttribute("type",typeOfElement);
        }
        for (var j = 0; j < numClasses; j++)
        {
            element1.classList.add(classList[j]);
        }
        cell1.appendChild(element1);

    }
}