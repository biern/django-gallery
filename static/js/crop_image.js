jQuery(function($) {
    function saveCoords(c) {
        $('input[name=coords]').val(c.x + ',' + c.y + ',' + c.w + ',' + c.h);
    };

    $('#photo-edit').Jcrop({
        onChange: saveCoords
    });
});
