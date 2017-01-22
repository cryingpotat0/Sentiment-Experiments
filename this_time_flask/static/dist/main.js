$(document).ready(function() {
  var lastClicked = $('#danceability');
  var secondLastClicked = $('#energy');
  var idOne = lastClicked.attr('id');
  var idTwo = secondLastClicked.attr('id');
  getJsonData(idOne, idTwo);

  $('.nav li').click(function() {
    lastClicked = secondLastClicked;
    secondLastClicked = $(this);
    $('.nav li').removeClass('active');
    lastClicked.addClass('active');
    secondLastClicked.addClass('active');
    idOne = lastClicked.attr('id');
    idTwo = secondLastClicked.attr('id');
    getJsonData(idOne, idTwo);
  });
    

});

var getJsonData = function(attribute1, attribute2) {
  $.ajax({
    type: 'GET',
    url: 'http://localhost:5000/' + attribute1,
    success: function(data1) {
      //console.log(data1);
      $.ajax({
        type: 'GET',
        url: 'http://localhost:5000/' + attribute2,
        success: function(data2) {
          //console.log(data1);
          //console.log(data2);
          populateGraphs(JSON.parse(data1), JSON.parse(data2), attribute1, attribute2);
        }
      });
    }
  });
}

var populateGraphs = function(data1, data2, attribute1, attribute2) {
  var labels = [];
  //console.log(data1);
  for(var label in data1) {
    labels.push(label);
  }
  var data = { labels: labels };
  var innerData = [];
  for(var label of labels){
    innerData.push({
      x: data1[label],
      y: data2[label]
    });
  }
  data.datasets = [{
    backgroundColor: "rgba(153, 255, 51, 0.5)",
    data: innerData
  }];
  //console.log(labels)
  //console.log(data);
  $('#myChart').remove();
  $('.append-chart-to').append(' <canvas id="myChart"></canvas>');
  createTwoFeature(data, attribute1, attribute2, labels);
}

var createTwoFeature = function(data, xLabel, yLabel, labels) {
  var ctx = document.getElementById('myChart').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'line',
    data: data,
    options:
    {
      legend: {
        display: false
      },
      scales:
      {
        xAxes: [{
          display: false
        }]
      }
    }
  });
}
