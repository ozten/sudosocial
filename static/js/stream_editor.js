/*jslint browser: true, plusplus: false*/
/*global window: false, require: false, $: false */

/**
 * @depend lib/jquery-1.4.1.min.js
 * @depend lib/require.js
 * @depend widgets/add_feed_panel.js
 */
require.def('', ['widgets/stream_editor_stream_panel', 'widgets/add_feed_panel'], function (stream_panel, add_feed_panel) {
    stream_panel.resizeStreamsPanel();
    add_feed_panel.initialize();
    $('.add-url-form').each(function (index, form) {
        add_feed_panel.initializeForm(form);
    });
    
});
	



$('.tab a').click(function () {
    var other = $('.tab.active-tab').attr('id'),
    newActive = $(this).parent().attr('id');
    
    if (other !== newActive) {
        $('#' + other).removeClass('active-tab');
        $('.tab').each(function (i, li) {
                if ($(li).attr('id') !== newActive) {
                    $('#' + $(li).attr('id') + '-panel').hide();
                } 
            });
        $('#' + newActive).addClass('active-tab');
        $('#' + newActive + '-panel').show();
    }
    return false;
});

$('.tab a:first').trigger('click');

/* auth confirm page */
$('#profile-image button').click(function (event) {
    event.preventDefault();
    $(this).attr('disabled', true);
    var button = $(this),
        img = $(this).parents('div').find('img');
    $.get('gravatar/' + $('#email').val(), function (data) {
        img.attr('src', data);
        button.attr('disabled', false);
    });
    return false;
});


/**
 * @depend widgets/streams/show_hide.js
 * @depend widgets/add_stream_button.js
 * @depend widgets/delete_stream_panel.js
 * @depend effects/checkbox_disable_panel.js
 */
$(document).ready(function () {
    $('.optional-widget').each(function (i, div) {
            var linkActive = $('.add-widget', $(div)).hasClass('active');
            if (linkActive) {
                $('.field', $(div)).hide();
            } else {
                $('.add-widget', $(div)).hide();
            }
            $('.add-widget', $(div)).click(function () {
                window.art = $(this);
                $(this).removeClass('active').hide('slow');
                $(this).parent().find('.field').show('slow');
                return false;
            });
        });

    require.def('app', 
                ['effects/checkbox_disable_panel',
                 'widgets/streams/show_hide', 
                 'widgets/add_stream_button',
                 'widgets/delete_stream_panel'
                 ], 
                function (checkbox_disable, show_hide, add_stream, delete_stream) {
        show_hide.prepareShowHideEntries();
        add_stream.registerAddStreamHandler();
        checkbox_disable.initialize();
        delete_stream.initialize();
    });

    /* Show/Hide panel based on checkbox or radio input */
    $('.multi-choice-input-parent-panel .multi-choice-input-panel').hide();
    var disableCheckboxPanels,
        multi = ['#css_type_widget', '#js_type_widget'],    
        makeMulti = function (multiPanel) {
        return function () {
            var id = $(this).attr('id');            
            $('.multi-choice-input-panel:visible', $(multiPanel)).hide('fast');            
            $('#' + id + '_panel', $(multiPanel)).show('fast');
        };
    };
    
    
    $('input[name=css_type].multi-choice-input-selector').bind('click', makeMulti('#css_type_widget'));
    $('input[name=js_type].multi-choice-input-selector').bind('click', makeMulti('#js_type_widget'));
    $('.multi-choice-input-selector[checked=checked]').trigger('click');

    /* Started creating Flickr style edits... Not in use currently. */
    $('.editable').hover(function () {
        $(this).data('old-background-color', $(this).css('background-color'));
        $(this).css('background-color', 'yellow');
    }, function () {
        $(this).css('background-color', $(this).data('old-background-color'));
    }).attr('title', "Click to Edit").click(function () {
        $(this).hide();
        var id = $(this).attr('id'),
            input;
        $(this).data('old-value', $('#' + id + '_field input').val());
        input = $('#' + id + '_field').show()
            .find('.editable-cancel').click(function () {
                $('#' + id + '_field').hide();
                $('#' + id).show();
                $('#' + id + '_field input').val($('#' + id).data('old-value'));
                // Revert the value of the input field
                return false;
            });
        return false;
    });

    /* generic checkbox support */
    disableCheckboxPanels = function () {
        var id = $(this).attr('id');
        if ($(this).attr('checked')) {
            $('.' + id + '_panel').removeClass('checkbox-disabled')
                .find('input, textarea, select, button')
                    .removeAttr('disabled')
                    .focus();
        } else {
            $('.' + id + '_panel').addClass('checkbox-disabled')
                .find('input, textarea, select, button')
                    .attr('disabled', 'true');
        }
    };
    $('input[type=checkbox]').each(disableCheckboxPanels);
    $('input[type=checkbox]').click(disableCheckboxPanels);



});

$('#username').bind('focus, blur', function () {
    $(this).val($(this).val().toLowerCase());
});
$('#username').trigger('change');

