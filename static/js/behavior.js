/*jslint browser: true, plusplus: false, newcap: false */
/*global window: false, require: false, $: false, Processing: false */
$(document).ready(function () { 
    // Blow up Flickr by 200%
    $('.feed-flickr a img').each(function (i, img) {
        var w = parseInt($(img).attr('width'), 10),
            h;
        if (w * 2 < 600) {
            h = parseInt($(img).attr('height'), 10);
            
            $(img).attr('width', w * 2)
                  .attr('height', h * 2);            
        }
    });
    
    // Tags shouldn't overlap content
    $('.feed-entry').each(function (i, div) {
        var tagArea = $('.tag-area', div),
            tagWidth = tagArea.width(),
            tagHeight,
            maxWidth;
        if (tagWidth < 120) {
            $(div).css('padding-right', tagWidth);
        } else {
            tagHeight = $('.tag-area', div).height;
            $(div).css('padding-bottom', tagHeight);
        }
        maxWidth = 0;
        $('li', tagArea).each(function (i, li) {
            if ($(li).outerWidth() > maxWidth) {
                maxWidth = $(li).outerWidth();
            }
        });
        // TODO use geometry 30 degrees
        tagArea.css('height', (maxWidth * 0.6) + 'px');
    });
    // Fixup Twitter html
    $('.feed-twitter').find('a:last').addClass('permalink');        
});


$(document).ready(function () {
    var processingScript = $('script[type=application/processing]').text();
    Processing($('#processing-canvas').get(0), processingScript);
});