// Global variables to manage the components: the canvas, the timeline and the video
var timelineData = new TAFFY(); // we manage the client data with TAFFY database: http://taffydb.com/
var colors = ['red', 'green', 'yellow', 'blue', 'white', 'purple', 'cyan'];
var objectCount = 0;
var endpoints = {
  "submission": "/submission/",
};

/**
 * Events happen while loading the window.
 */
window.onload = function() {
  setupCanvas();
  setupTimeline();
};

/**
 * Managing the canvas.
 * We use FABRICJS to manage the canvas events.
 */
function setupCanvas() {
  // find the canvas by ID
  var canvas = new fabric.Canvas('canvas');
  // the canvas will be managed by keys
  fabric.util.addListener(document.body, 'keydown', function(options) {
    var currentActiveObjects = canvas.getActiveObjects();
    var key = options.which || options.keyCode; // key detection
    if (String.fromCharCode(key) == 'N') { // add a new rectangle
      window.player.pause(); // stop the video for a while
      var currentTime = window.player.currentTime();
      var baseRect = new fabric.Rect({
        top: 100,
        left: 100,
        width: 100,
        height: 100,
        fill: 'transparent',
        stroke: colors[objectCount % colors.length],
      });
      canvas.add(baseRect);
      objectCount++;
    } else if (String.fromCharCode(key) == 'D') { // remove selected rectangles
      for (var i = 0; i < currentActiveObjects.length; ++i)
        canvas.remove(currentActiveObjects[i]);
    } else if (String.fromCharCode(key) == 'C') { // continue playing the video
      window.player.play();
    } else if (String.fromCharCode(key) == 'S') { // stop the video
      window.player.pause();
    }
  });
}

/**
 * Managing the timeline bar.
 * Timeline module is created and managed using D3-timeline plugin.
 */
function setupTimeline() {
  $('#my-timeline').html(''); // clear the content of the timeline
  var chartWidth = $('#my-timeline').width();
  // create a new content for the timeline
  var chart = d3.timelines();
  chart.stack();
  var svg = d3.select('#my-timeline').append('svg');
  svg.attr('width', chartWidth).datum(timelineData).call(chart);
}

window.addEventListener('resize', setupTimeline);

/**
 * Communications with servers
 */
function sendTimelineData() {
  timelineData.yid = $("#hidden1").value(); // get the video identifier
  // send the data to server
  $.ajax({
    url: endpoints.submission,
    type: "POST",
    dataType: "json",
    async: true,
    crossDomain: false,
    crossOrigin: false,
    data: timelineData
  }).done(function(data) {
    //alert("Finished sending! Reported with data: " + data);
  }).fail(function(e) {
    alert("Failed to send timeline data with error: " + e + "\nPlease try again later.");
  });
}

/**
 * TAFFYDB management tools
 */
function insertRecordToTimeline(currentTime, objectId, rect, ) {

}