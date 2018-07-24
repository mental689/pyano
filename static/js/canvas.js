// Global variables to manage the components: the canvas, the timeline and the video
var timelineData = new TAFFY(); // we manage the client data with TAFFY database: http://taffydb.com/
var colors = ['red', 'green', 'yellow', 'blue', 'white', 'purple', 'cyan'];
var objectCount = 0;
var canvas = null;

/**
 * Events happen while loading the window.
 */
window.onload = function() {
  setupCanvas();
  if ($("#yid") != null) {
    alert("You are annotating a video from external source. " +
        "Therefore the source video can be editted after you annotate. " +
        "We recommend to use PYANO resources! " +
        "If you still want to use external source, we recommend to download video right after finishing your annotations." +
        "We still let you submit and we will review your work at our best.");
  }
};

/**
 * Managing the canvas.
 * We use FABRICJS to manage the canvas events.
 */
function setupCanvas() {
  // find the canvas by ID
  canvas = new fabric.Canvas('canvas');
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
        id: objectCount,
        hasRotatingPoint: false, // whether to obtain orientation information or not
      });
      canvas.add(baseRect);
      canvas.setActiveObject(baseRect);
      insertRecordToTimeline(currentTime, baseRect);
      objectCount++;
    } else if (String.fromCharCode(key) == 'D') { // remove selected rectangles
      for (var i = 0; i < currentActiveObjects.length; ++i)
        canvas.remove(currentActiveObjects[i]);
    } else if (String.fromCharCode(key) == 'C') { // continue playing the video
      window.player.play();
    } else if (String.fromCharCode(key) == 'S') { // S key to pause the video
      window.player.pause();
    }
  });
  canvas.on({
    'object:modified': function(e) {
      var modifiedObject = e.target;
      e.target.set('opacity', 0.3);
      //console.log(modifiedObject);
      window.player.pause();
      var currentTime = window.player.currentTime();
      insertRecordToTimeline(currentTime, modifiedObject);
      displayObjectInfo(e.target.id);
    },
  });
  canvas.on('mouse:over', function(e) {
    e.target.set('fill', 'red');
    e.target.set('opacity', 0.3);
    canvas.renderAll();
    displayObjectInfo(e.target.id);
  });
  canvas.on('mouse:out', function(e) {
    e.target.set('fill', 'transparent');
    e.target.set('opacity', 1.0);
    canvas.renderAll();
    //$("#object").html("");
  });

  window.player.on('timeupdate', function(e) {
    var currentTime = window.player.currentTime();
    //console.log("Moved to timestamp " + currentTime);
    var objects = retrieveObjectByTimestamp(currentTime);
    canvas.clear();
    for (var i = 0; i < objects.length; ++i) {
      var object = objects[i];
      var o = baseObject(object['id']);
      o.top = object['top'];
      o.left = object['left'];
      o.width = object['width'];
      o.height = object['height'];
      canvas.add(o);
      //insertRecordToTimeline(currentTime, o);
    }
  });
}

function displayObjectInfo(id) {
  $("#object").html("")
  var history = timelineData({"id": id}).order("timestamp").get(0);
  for (var i = 0; i < history.length; ++i) {
    var record =  history[i];
    var timestamp =  record["timestamp"];
    $("#timestamp").html(timestamp)
    $("#object").append('<button onmouseover="gotoTime();return false;" class="genric-btn primary-border" disabled>' +  String(i+1) + '</button> ')
  }
}

/**
 * Managing the timeline bar.
 * Timeline module is created and managed using D3-timeline plugin.
 */
// function setupTimeline() {
//   $('#my-timeline').html(''); // clear the content of the timeline
//   var chartWidth = $('#my-timeline').width();
//   // create a new content for the timeline
//   var chart = d3.timelines();
//   chart.stack();
//   var svg = d3.select('#my-timeline').append('svg');
//   svg.attr('width', chartWidth).datum(timelineData).call(chart);
// }

// window.addEventListener('resize', setupTimeline);

/**
 * TAFFYDB management tools
 */
function insertRecordToTimeline(currentTime, rect) {
  var count = timelineData({'id': rect.id, 'timestamp': currentTime}).count();
  if (count == 0) {
    timelineData.insert({
      'timestamp': currentTime,
      'id': rect.id,
      'top': rect.top,
      'left': rect.left,
      'width': rect.width * rect.scaleX,
      'height': rect.height * rect.scaleY,
    });
    //console.log("Inserted a record of object " + rect.id);
  } else {
    timelineData({'id': rect.id, 'timestamp': currentTime}).update({
      'top': rect.top,
      'left': rect.left,
      'width': rect.width * rect.scaleX,
      'height': rect.height * rect.scaleY,
    });
    //console.log("Updated a record of object " + rect.id);
  }
  $('#hidden2').val(timelineData().stringify());
}

function retrieveObjectByTimestamp(timestamp) {
  var ids = timelineData().distinct('id');
  var objects = new Array();
  for (var i = 0; i < ids.length; ++i) {
    var o = linearObjectBBoxInterpolation(timestamp, ids[i]);
    if (o != null) {
      objects.push(o);
    }
  }
  //console.log("Found " + objects.length + " records at " + timestamp);
  return objects;
}

function linearInterpolation(t1, t, t2, x1, x2) {
  return x1 + (t - t1) * (x2 - x1) / (t2 - t1);
}

function linearObjectBBoxInterpolation(timestamp, id) {
  var beforeTimestamp = timelineData(
      {'timestamp': {'<=': timestamp}, 'id': id}).order('timestamp');
  var afterTimestamp = timelineData({'timestamp': {'>': timestamp}, 'id': id}).
      order('timestamp');
  if (beforeTimestamp.count() < 1) {
    //console.log("No history at " + timestamp + " for object ID " + id);
    return null;
  } else {
    if (afterTimestamp.count() < 1) {
      return beforeTimestamp.last();
    } else {
      var begin = beforeTimestamp.last();
      var end = afterTimestamp.first();
      // do interpolation
      var o = baseObject(begin.id);
      var t1 = begin['timestamp'];
      var t2 = end['timestamp'];
      o.top = linearInterpolation(t1, timestamp, t2, begin.top, end.top);
      o.left = linearInterpolation(t1, timestamp, t2, begin.left, end.left);
      o.width = linearInterpolation(t1, timestamp, t2, begin.width, end.width);
      o.height = linearInterpolation(t1, timestamp, t2, begin.height,
          end.height);
      return o;
    }
  }
}

function baseObject(id) {
  var o = new fabric.Rect({
    top: 100,
    left: 100,
    width: 100,
    height: 100,
    fill: 'transparent',
    stroke: colors[id % colors.length],
    id: id,
    hasRotatingPoint: false, // whether to obtain orientation information or not
  });
  return o;
}

function gotoTime() {
  var timestamp = $("#timestamp").value;
  window.player.play();
  window.player.currentTime(timestamp);
}
