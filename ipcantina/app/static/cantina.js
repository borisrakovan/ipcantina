$(document).ready(function() {

    $('.inactive input').attr('disabled', 'disabled');

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
//    $('.incrementor input').change(function () {
//        var $price = $(this).parent().siblings('.price-tag').first().find('span');
//
//        var unit = parseFloat($(this).parent().siblings('.unit-price').first().text());
//        var newPrice = unit * ($(this).val() <= 0 ? 1 : $(this).val())
//        $price.text(newPrice.toFixed(2));
//    });
//
//    $('.take-away').change(function() {
//        if ($(this).is(':checked')) {
//            var $price = $(this).siblings('.price-tag').first().find('span');
//            console.log($price);
//            var amount = parseInt($(this).siblings('.incrementor').first().children('input').first().val());
//            console.log(amount);
//            var newPrice = parseFloat($price.text()) + amount * 0.3;
//            $price.text(newPrice.toFixed(2));
//        }
//
//    });


});
