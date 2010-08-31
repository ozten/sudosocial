/*global window: false, self: false, require: false, $: false */

/**
 * @depend ../lib/jquery-1.4.1.min.js
 * @depend ../lib/require.js
 */
require.def('effects/checkbox_disable_panel', [], function () {                    
    var that = {
        initialize: function () {
            $('input[type=checkbox]').each(function (i, input) {                
                that.disableCheckboxPanels.call(input);
            });
            $('input[type=checkbox]').click(that.disableCheckboxPanels);
        },
        disableCheckboxPanels: function () {
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
        }
    };
    return that;
});

    