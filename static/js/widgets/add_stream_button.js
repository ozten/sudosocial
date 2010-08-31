/*global window: false, self: false, require: false, $: false */

/**
 * @depend ../lib/require.js
 * @depend stream_editor_stream_panel.js
 */
require.def('widgets/add_stream_button', ['widgets/stream_editor_stream_panel'], function (stream_panel) {
    var that = this;
    return {
        registerAddStreamHandler: function () {
            $('a.add-stream').click(function () {                 
                var panel = $(this).parents('.add-stream-panel'),
                    link = $(this),
                    options;
                $('.add-stream', panel).hide();
                $('.creating', panel).show();
                options = {
                    url: link.attr('href'),
                    type: 'POST',
                    dataType: 'json',
                    error: function (xhr, status, error) {
                        $('.add-stream', panel).show();
                        $('.creating', panel).hide();
                        panel.append('<p>Error creating new stream <code>;(</code>');
                    },
                    success: function (data, status, xhr) {
                        $('.add-stream', panel).show();
                        $('.creating', panel).hide();
                        stream_panel.addStream({id: data.new_stream_id});
                    }
                };
                $.ajax(options);
                return false;
            });
        }
    };
});