$(document).ready(function() {
    $('.inactive input').attr('disabled', 'disabled');
    $('.inactive input').siblings('.plus, .minus').css("opacity", 0.6)

    $('.minus').click(function () {
        var $input = $(this).parent().find('input');
        if ($input.attr('disabled') == 'disabled') {
            return;
        }

        var cur = (parseInt($input.val(), 10) || 0);
        var count = cur - 1;
        count = count < 0 ? 0 : count;
        $input.val(count);
        $input.change();

        return false;
    });
    $('.plus').click(function () {
        var $input = $(this).parent().find('input');
        if ($input.attr('disabled') == 'disabled') {
            return;
        }
        var num = parseInt($input.val(), 10) || 0;
        $input.val(num + 1);
        $input.change();

        return false;
    });

    $('.incrementor input').change(function () {
        var $wrapper = $(this).parent().parent()
        var $price = $wrapper.siblings('.price-tag').first().find('span');

        var unit = parseFloat($wrapper.siblings('.unit-price').first().text());
        var takeAway = $wrapper.siblings('.take-away').first();

        var surcharge = 0.0;
        if (takeAway.is(':checked')) {
            surcharge = 0.3;
        }

        var newPrice = (unit + surcharge) * ($(this).val() <= 0 ? 1 : $(this).val());
        $price.text(newPrice.toFixed(2));
    });

    $('.take-away').change(function() {
        $input = $(this).siblings('div').first().children('.incrementor').first().children('input').first();

        $input.change();

    });

    // temporary: implicitly checked
    $('.take-away').prop('readonly', true);
    $('.incrementor input').each(function() {
        $(this).change();
    });

});
