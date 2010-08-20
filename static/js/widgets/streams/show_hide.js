/*global window: false, self: false, require: false, $: false */

require.def('widgets/streams/show_hide', {     
    prepareShowHideEntries: function () {
        var that = this,
            panels = $('.stream-preview-panel'),
	    feed_panel,
	    feed_panel_offset;
        $('a.display_entry').click(function () {
            var entryIsVisible = $(this).hasClass('entry-visible');
            if (entryIsVisible) {
                that.changeVisibility($(this), false, 'entry-visible', 'entry-hidden', 'Show Entry');
                $(this).parent().addClass('entry-hidden');
            } else {
                that.changeVisibility($(this), true, 'entry-hidden', 'entry-visible', 'Hide Entry');
                $(this).parent().removeClass('entry-hidden');
            }
            return false;
        });
        $('a.display_entry.entry-hidden').parent().addClass('entry-hidden');
    
        
        if (panels.length > 0) {
            panels.css('height', 
                       $(window).height() - panels.offset().top);
        } else {
            feed_panel = $('#stream-preview');
            feed_panel_offset = feed_panel.offset();
            if (feed_panel_offset) {
                feed_panel.css('height', $(window).height() - feed_panel_offset.top);
            }
        }
    },
    /**
     * 
     */
    changeVisibility: function (jQueryElement, newState, oldClass, newClass, newLabel) {
        var that = jQueryElement,
            url = that.attr('href');
        that.removeAttr('href');
        $.post(url, {'change-visibility': newState}, function (data, statusText) {
            that.removeClass(oldClass).addClass(newClass);
            that.attr('href', url);
            that.text(newLabel);
        });    
    }
});