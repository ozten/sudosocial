/*global window: false, self: false, require: false, $: false */
/*jslint plusplus: false */
/**
* @depend ../lib/jquery-1.4.1.min.js
* @depend ../lib/require.js
*/
require.def('widgets/delete_stream_panel', ['widgets/stream_editor_stream_panel'], function (stream_panel) {
    var that = {
        initialize: function () {
            $('.stream-delete').live('click', function () {
                var that = $(this),
                    stream_id,
                    deleteSuccessFn;
                if (window.confirm("Are you sure you want to delete this entire stream?")) {

                    stream_id = that.attr('href');
                    deleteSuccessFn = function () {
                        that.parents('.streams-panel').remove();
                        stream_panel.resizeStreamsPanel();
                    };
                    $.ajax({url: '/manage/stream/' + $('#auth-username').text() + '/sid/' + stream_id, type: 'DELETE', success: deleteSuccessFn, dataType: 'json'});

                }
                return false;
            });
        }
    };
    return that;
});
