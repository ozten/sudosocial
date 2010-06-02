$(document).ready(function(){
    // Blow up Flickr by 200%
    $('.feed-flickr a img').each(function(i, img){
        var w = parseInt($(img).attr('width'));
        if (w * 2 < 600) {
            var h = parseInt($(img).attr('height'));
            
            $(img).attr('width', w * 2)
                  .attr('height', h * 2);            
        }
    });
    
    // Tags shouldn't overlap content
    $('.feed-entry').each(function(i, div){
        var tagArea = $('.tag-area', div);
        var tagWidth = tagArea.width();
        if (tagWidth < 120) {
            $(div).css('padding-right', tagWidth);
        } else {
            var tagHeight = $('.tag-area', div).height;
            $(div).css('padding-bottom', tagHeight)
        }
        var maxWidth = 0;
        $('li', tagArea).each(function(i, li){
            console.info(li);
            if ($(li).outerWidth() > maxWidth) {
                maxWidth = $(li).outerWidth();
            }
            });
        // TODO use geometry 30 degrees
        tagArea.css('height', (maxWidth * 0.6) + 'px');
    });
    // Fixup Twitter html
    $('.feed-twitter').find('a:last').addClass('permalink');
    
    //Give props to Robert Podgórski
    $('.powered_by').prepend('<h5>Firefoxzilla protects the city</h5><div>Background imagery By <a href="http://creative.mozilla.org/people/blackmoondev">Blackmoondev</a></div>');
    
    // Shift the background by the height of the profile
    /*var pos = $('#viewport').css('background-position'),
        parts = pos.split(' '),
        blurb = $('.profile_blurb'),
        profileHeight = blurb.outerHeight() + blurb.offset().top + 10;
        $('#viewport').css('background-position', parts[0] + ' ' + profileHeight + 'px');*/
});


$(document).ready(function(){
    var processingScript = $('script[type=application/processing]').text();
    if (window.console) { console.info("Sending Processing", processingScript); }
    Processing( $('#processing-canvas').get(0), processingScript );
});