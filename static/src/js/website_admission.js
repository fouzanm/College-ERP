odoo.define('college.website_admission', function (require) {
    "use strict";
    var core = require('web.core');
    var rpc = require('web.rpc');
    $('.btn-confirm').click(function(){
        var record = $(this).data('record-id')
        rpc.query({
            route: '/admitted-list/confirm',
            params: {
                'record' : record
            },
        }).then(function(){
            location.reload()
        });
    });
});