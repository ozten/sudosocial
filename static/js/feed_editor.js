/*jslint browser: true*/
/*global window: false, require: false, $: false */

/**
 * @depend lib/require.js
 * @depend lib/jquery-1.4.1.min.js
 * @depend widgets/stream_preview.js
 * @depend widgets/feed_editor_delete_feed.js
 * @depend effects/checkbox_disable_panel.js
 */
require.def('app', 
	    ['widgets/stream_preview', 'widgets/feed_editor_delete_feed', 'effects/checkbox_disable_panel'], 
	    function (stream_preview, delete_feed, checkbox_panel) {
    stream_preview.registerRetryClickHandler();
    stream_preview.reloadFeedPreview();
    checkbox_panel.initialize();
    return {};
});



