/*global window: false, self: false, require: false, $: false */

/**
 * @depend streams/show_hide.js
 */
require.def('widgets/stream_preview', ['widgets/streams/show_hide'], function (show_hide) {
    var that = {
        /**
         * @depend streams/show_hide.js
         */
        reloadFeedPreview: function () {
            var url = $('#feed_preview_source').attr('href'),
                ajaxOptions = {
                    url: url, 
                    dataType: 'html',
                    success: function (data, status, xhr) {
                        $('#feed_preview').html(data);
                        show_hide.prepareShowHideEntries();
		            }
	            };
            $.ajax(ajaxOptions);
        },
        registerRetryClickHandler: function () {
            $('#feed_disabled_retry').click(function () {
                var oldText = $(this).text(),
                    target = this;
                $(this).text('Loading');
                $.ajax({url: $(this).attr('href'),
                       type: "GET",
                       dataType: 'json',
                       complete: function (xhr, status) {},
                       success: function (data, status, xhr) {
                            if ('enabled' in data && Boolean(data.enabled)) {
                                $('#feed-disabled_panel').hide();
                            }
                            that.reloadFeedPreview();
                    
                            $(target).text(oldText);
                        },
                       error: function (xhr, status, err) {
                            $(target).text("Error, " + oldText);
                        }
                 });
                return false;

            });
        }
    };
    return that;
});