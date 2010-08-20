/*jslint browser: true*/
/*global window: false, require: false, $: false */

/**
 * @depend ../lib/require.js
 * @depend ../lib/jquery-1.4.1.min.js
 */
require.def('widgets/feed_editor_delete_feed', [], function () {
    $('a.feed-delete').live('click', function () {
        var that = $(this),
            url_hash = that.attr('href'),
            deleteSuccessFn = function () {
                that.parent().remove();
                window.location = $('#back').attr('href');
            };
        $.ajax({url: '/manage/url/' + $('#auth-username').text() + '/' + url_hash, type: 'DELETE', success: deleteSuccessFn, dataType: 'json'});
        return false;
    });
    return {};
});