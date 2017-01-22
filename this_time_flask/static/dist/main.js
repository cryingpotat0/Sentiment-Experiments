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

  $('.search_submit').click(function() {
    console.log('moving');
    localStorage.artist = $('.artist').val();
    localStorage.song = $('.song').val();
    window.location.replace("http://localhost:5000/login");
  });

});

var getJsonData = function(attribute1, attribute2) {
  $.ajax({
    type: 'GET',
    url: 'https://triple-s-156413.appspot-preview.com/' + attribute1,
    success: function(data1) {
      //console.log(data1);
      $.ajax({
        type: 'GET',
        url: 'https://triple-s-156413.appspot-preview.com/' + attribute2,
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
  var data = { } 
  var innerData = [];
  for(var label of labels){
    innerData.push({
      data: [{
        x: data1[label],
        y: data2[label],
      }],
      label: label,
      strokeColor: '#FFF'
    });
  }
  innerData.sort(compare);
  console.log(innerData);
    data.datasets = [{
      backgroundColor: "rgba(153, 255, 51, 0.5)",
      data: innerData
    }];
  //console.log(labels)
  //console.log(data);
  $('#myChart').remove();
  $('.append-chart-to').append(' <canvas id="myChart"></canvas>');
  createTwoFeature(innerData, attribute1, attribute2, labels);
}

function compare(a,b) {
  if (a.data.x < b.data.x )
    return -1;
  if (a.data.x > b.data.x)
    return 1;
  return 0;
}


var createTwoFeature = function(innerData, xLabel, yLabel, labels) {
  var ctx = document.getElementById('myChart').getContext('2d');
  /*
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
     yAxes: [{
     display: true,
     ticks: {
     suggestedMin: 0,    
     beginAtZero: true   // minimum value will be 0.
     },
     scaleLabel: {
     display: true,
     labelString: yLabel
     }
     }],
     xAxes: [{
     display: false,
     ticks: {
     suggestedMin: 0,    
     beginAtZero: true   // minimum value will be 0.
     },
     scaleLabel: {
     display: true,
     labelString: xLabel ,
     }
     }],
     }
     }
     });
     */
  console.log(innerData)
  var scatterChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: innerData    },
    options: {
      legend: {
        display: false
      },
      scales: {
        xAxes: [{
          type: 'linear',
          position: 'bottom',
          scaleLabel: {
            display: true,
            labelString: xLabel
          }
        }],
        yAxes: [{
          type: 'linear',
          position: 'left',
          scaleLabel: {
            display: true,
            labelString: yLabel
          }
        }]
      }
    }
  });
}
