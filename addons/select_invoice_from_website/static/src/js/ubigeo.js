odoo.define('select_invoice_from_website.change_res_ubigeo',function(require){
    'use strict';
    var publicWidget = require("web.public.widget")
    var rpc = require("web.rpc")
    var core = require("web.core")
    var qweb = core.qweb
    var ajax = require("web.ajax")
    var _t = core._t;
    var Widget = require("web.Widget")
    var session = require("web.session")

    publicWidget.registry.ChangeDepartamento = publicWidget.Widget.extend({
        selector: ".oe_cart",
        events:{
            'change #departamento':'loadProvincias',
            'change #provincia':'loadDistritos',
            'change #country':'loadDepartamentos',
        },
        start: function () {
        },
        loadDepartamentos:function(){
            var self = this
            var pais = $(self.$el).find("#country").val()
            console.log(pais)
            ajax.jsonRpc('/get-departamento', 'call',
             {'pais': pais}).then(function (data) {
                    console.log(data);
                    for (let i = 0; i < data.length; i++) {
                        $(self.$el).find("#departamento").append($('<option /}>').val(data[i].id).text(data[i].name));
                    }
            })
        },
        loadProvincias:function(){
            var self = this
            var departamento = $(self.$el).find("#departamento").val()
            //console.log('********DEPARTAMENTO********')
            //console.log(departamento)
            ajax.jsonRpc('/get-provincia', 'call',
             {'departamento': departamento}).then(function (data) {
                    console.log(data);
                    for (let i = 0; i < data.length; i++) {
                        $(self.$el).find("#provincia").append($('<option /}>').val(data[i].id).text(data[i].name));
                    }
            })
        },
        loadDistritos:function(){
            var self = this
            var provincia = $(self.$el).find("#provincia").val()
            //console.log('********PROVINCIA********')
            //console.log(provincia)
            ajax.jsonRpc('/get-distrito', 'call',
             {'provincia': provincia}).then(function (data) {
                    console.log(data);
                    for (let i = 0; i < data.length; i++) {
                        $(self.$el).find("#distrito").append($('<option /}>').val(data[i].id).text(data[i].name));
                    }
            })
        },
    });
});
