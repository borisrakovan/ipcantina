$(document).ready(function() {
    var activeId = 1;

    $('#' + activeId).addClass('active').show();

    handleHeader(activeId);

    $('.prev-button').click(function() {
        var activeId = getActiveId();

        $('.week-order-list').removeClass('active').hide();
        $('#' + (activeId + 1)).addClass('active').show();
        handleHeader(activeId + 1);
    });
    $('.next-button').click(function() {
        var activeId = getActiveId();

        $('.week-order-list').removeClass('active').hide();
        $('#' + (activeId - 1)).addClass('active').show();
        handleHeader(activeId - 1);
    });

});

function handleHeader(activeId) {
    var lists = $('.week-order-list');
    var numWeeks = lists.size();
    $('.btn').removeClass('disabled')
    if (activeId == 1) {
        $('.next-button').addClass('disabled');
    }
    if (activeId == numWeeks) {
        $('.prev-button').addClass('disabled');
    }
    var dateString = $('#' + activeId + ' .week-date-string').text();
    $('.order-list-header .week-date-string').text(dateString);

}

function getActiveId() {
    return parseInt($('.week-order-list.active').first().attr('id'));
}
