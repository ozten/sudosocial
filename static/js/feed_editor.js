$(document).ready(function(){
    var reloadFeedPreview = function() {
        var url = $('#feed_preview_source').attr('href');
        $.ajax({url: url, dataType: 'html',
                success: function(data, status, xhr){
                    $('#feed_preview').html(data);
                    prepareShowHideEntries();
             }});
        
    }
    window.reloadFeedPreview = reloadFeedPreview;
    $('#feed_disabled_retry').click(function(){
        var oldText = $(this).text(),
            that = this;
        $(this).text('Loading');
        $.ajax({url:$(this).attr('href'),
               type: "GET",
               dataType: 'json',
               complete: function(xhr, status) {
                  alert('call complete');
               },
               success: function(data, status, xhr) {
                alert('call success');
                    window.data = data;
                    if (Boolean(data.enabled)) {
                        $('#feed-disabled_panel').hide();
                    }
                    reloadFeedPreview();
                    
                   $(that).text(oldText);
               },
               error: function(xhr, status, err) {
                  alert('call error');
                  $(that).text("Error, " + oldText);
               }
        });
        return false;
        });
    reloadFeedPreview();    
});