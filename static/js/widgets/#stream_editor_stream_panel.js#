/*global window: false, self: false, require: false, $: false */
/**
 * Duplicates a stream.
 * 
 * @depend ../lib/require.js
 * @depend add_feed_panel.js
 */
require.def('widgets/stream_editor_stream_panel', ['widgets/add_feed_panel'], function (add_feed_panel) {
    return {
        addStream: function (newStream) {
            var newStreamPanel = $('.streams-panel:first').clone();
            $('input[name=streams]', newStreamPanel).val(newStream.id);
            $('.stream-delete', newStreamPanel).attr('href', newStream.id);
            $('.user_streams li:not(:first)', newStreamPanel).remove();
            $('.user_streams li a.button', newStreamPanel).addClass('feed-edit');
            $('.user_streams li strong').text('');
            $('.user_streams li', newStreamPanel).addClass('base-stream-feed-link').hide();

            $('#edit-stream-panel').append(newStreamPanel);
            $('.feed-entry', newStreamPanel).remove();
            add_feed_panel.initializeForm($('form', newStreamPanel).get(0));

            this.resizeStreamsPanel();
        },
        resizeStreamsPanel: function () {
            var numberStreamPanels = $('.streams-panel').length;
            $('#edit-stream-panel').css('width', numberStreamPanels * 818 + 'px');
        }
    };
});