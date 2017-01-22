
function getParameterByName(name, url) {
  if (!url) {
    url = window.location.href;
  }
  name = name.replace(/[\[\]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
  results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return null;
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

$(document).ready(function() {
  $('.sidebar-header').append('<div class="h3 song-text" style="display:block">'  + localStorage.song + ', ' + localStorage.artist + '</div>');
  $.ajax({
    type: 'GET',
    url: 'http://localhost:5000/songSearch',
    data: {
      artist: localStorage.artist,
      song: localStorage.song,
      access_token: getParameterByName('access_token')
    },
    success: function(ret_data) {
      $('#songChart').show();
      $('.spinner').hide();
      var ctx = document.getElementById('songChart').getContext('2d');
      var song_dict = JSON.parse(ret_data);
      var data = {
        labels: ["danceability", "acousticness", "energy", "microsoft_happiness", "google_happiness"],
        datasets: [
        {
          backgroundColor: "rgba(179,181,198,0.2)",
          borderColor: "rgba(179,181,198,1)",
          pointBackgroundColor: "rgba(179,181,198,1)",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "rgba(179,181,198,1)",
          data: [
            song_dict['danceability'], 
            song_dict['acousticness'],
            song_dict['energy'], 
            song_dict["microsoft_score"],
            song_dict["google_score"]
          ]
        },
        ]
      };
      console.log('done');
      var myRadarChart = new Chart(ctx, {
        type: 'radar',
        data: data,
        options: {
          legend: {
            display: false
          },
          scales: {
            xAxes: [{
              display: false
            }],
            yAxes: [{
              display: false
            }],
          }
        },
      });
    }
  });

});
