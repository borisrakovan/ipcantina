$(document).ready(function() {
    $('.minus').click(function () {
        var $input = $(this).parent().find('input');
        if ($input.attr('disabled') == 'disabled') {
            return;
        }
        var count = (parseInt($input.val(), 10) || 0) - 1;
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
});

$(document).ready(function() {
    $('.readonly input').prop('readonly', true);
});

$(document).ready(function() {
    $('.inactive input').attr('disabled', 'disabled');
});
