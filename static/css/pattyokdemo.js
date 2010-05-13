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
        var tagWidth = $('.tag-area', div).width();
        $(div).css('padding-right', tagWidth);
    });
    // Fixup Twitter html
    $('.feed-twitter').find('a:last').addClass('permalink');
    
    //Give props to Robert Podgórski
    $('.powered_by').prepend('<h5>Firefoxzilla protects the city</h5><div>Background imagery By <a href="http://creative.mozilla.org/people/blackmoondev">Blackmoondev</a></div>');
    
    // Shift the background by the height of the profile
    var pos = $('#viewport').css('background-position'),
        parts = pos.split(' '),
        blurb = $('.profile_blurb'),
        profileHeight = blurb.outerHeight() + blurb.offset().top + 10;
        $('#viewport').css('background-position', parts[0] + ' ' + profileHeight + 'px');
});