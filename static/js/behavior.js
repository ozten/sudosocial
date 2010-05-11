
$(document).ready(function(){
    var processingScript = $('script[type=application/processing]').text();
    if (window.console) { console.info("Sending Processing", processingScript); }
    Processing( $('#processing-canvas').get(0), processingScript );
});