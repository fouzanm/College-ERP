odoo.define('college.website_admission', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var publicWidget = require('web.public.widget');
    publicWidget.registry.WebsiteAdmissionWidget = publicWidget.Widget.extend({
        selector: '#admitted-table',
        events: {
            'click .btn-confirm': 'onClickButton',
        },
        onClickButton: function(ev){
            var recordId = $(ev.currentTarget).data('record-id');
            rpc.query({
                route: '/admitted-list/confirm',
                params: {
                    'record' : recordId
                },
            }).then(function(){
                location.reload()
            });
        },
    })
});