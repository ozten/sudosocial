/*global window: false, self: false, require: false, $: false */
/*jslint plusplus: false */
/**
* @depend ../lib/jquery-1.4.1.min.js
* @depend ../lib/require.js
*/
require.def('widgets/add_feed_panel', [], function () {
    var that = {
        patchouliUsername: function () {
            return $('#auth-username').text();
        },
        initialize: function () {
            $('#auth-username').text($('#auth-username').text().toLowerCase());
        },
        initializeForm: function (form) {
            $(form).submit(function () {
                var panel = $(form).parents('.streams-panel'),
                    successFn,
                    completeFn;
                successFn = function (data, status, xhr) {
                    var stream_id = $('.id_streams', panel).val(),
                    i,
                    feed,
                    newFeedLi;
                    $('.no-stream-feed-blurb', panel).hide();
                    $('input[name=url]', panel).val('');
                    for (i = 0; i < data.feeds.length; i++) {
                        feed = data.feeds[i];
                        newFeedLi = $('.base-stream-feed-link', panel).clone();
                        newFeedLi.attr('id', null);
                        $('a.stream-feed-source', newFeedLi).attr('href', feed.url)
                            .text(feed.title);
                        $('a.feed-edit', newFeedLi).attr('href', that.patchouliUsername() + '/stream/' + stream_id + '/feed/' + feed.url_hash);
                        newFeedLi.show();
                        $('.user_streams', panel).append(newFeedLi);
                    }
                };
                completeFn = function (xhr, status) {
                    $('input', panel).attr('disabled', null);
                };
                $('input', panel).attr('disabled', 'disabled');
                $.ajax({
                    url: '/manage/urls/' + $('#auth-username').text(), 
                    type: 'POST', 
                    data: { url: $('input[name=url]', panel).val(), streams: [$('input[name=streams]', panel).val()] }, 
                    success: successFn, 
                    complete: completeFn, 
                    dataType: 'json'
                });

                return false;
            });
        }
    };
    return that;
});
