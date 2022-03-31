function runFunc(){
  var row = SpreadsheetApp.getActiveSheet().getRange("A2:GY2").getValues()[0];
  for (i = 0; i < row.length; i++) {
    if (row[i].length < 1){
      row[i] = NaN;
    }
  } 
  Logger.log(row);
  
  var data = {
  'password':'REDACTED',
  'raw' : row
  };
  var url = "ENDPOINT URL FOR CLOUD FUNC";
  var options = {
    'method' : 'post',
    'contentType': 'application/json',
    'payload' : JSON.stringify(data)
  };
  res = UrlFetchApp.fetch(url, options);
  Logger.log(res);
  sets = SpreadsheetApp.getActiveSheet().getRange("A4:A4").setValue(res);
}
