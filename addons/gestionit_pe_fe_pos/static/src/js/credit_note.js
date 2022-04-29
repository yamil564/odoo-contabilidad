odoo.define("gestionit_pe_fe_pos.credit_note",function(require){
    "use strict";
    var pos_order_mgmt = require('pos_order_mgmt.widgets')
    var screens = require("point_of_sale.screens")
    var gui = require("point_of_sale.gui")
    var popups = require("point_of_sale.popups")
    var DB = require('point_of_sale.DB');
    var models = require('point_of_sale.models')
    var chrome = require('point_of_sale.chrome')
    var BaseWidget = require('point_of_sale.BaseWidget')
    var PosModelSuper = models.PosModel


    chrome.OrderSelectorWidget.include({
        order_click_handler: function(event,$el) {
            this._super(event,$el)
            // console.log(this.pos.get_order())
            if(this.pos.get_order().get_invoice_type() == 'out_refund'){
                this.gui.show_screen("screen_credit_note")
            }
        },
    })

    var CreateCreditNoteModal = popups.extend({
        template:"CreateCreditNoteModal",
        events:{
            "click .create_credit_note":"create",
            'click .button.cancel': 'click_cancel'
        },
        show:function(options){
            this._super(options)
            this.order_id = options.order_id
            this.partner_id = options.partner_id[0]
            $(this.$el).find("#invoice_name").text(options.invoice_id[1]) 
            $(this.$el).find("#partner_name").text(options.partner_id[1])
        },
        create:function(ev){
            var self = this
            var credit_note_comment = $(this.$el).find("textarea[name='credit_note_comment']").val()
            var credit_note_type = $(this.$el).find("input[name='credit_note_type']:checked").val()
            if(credit_note_comment == "" || credit_note_type == ""){
                self.gui.show_popup('error', {
                    'title': "Error",
                    'body': "El sustento y el tipo de la nota de crédito son obligatorios",
                });
                return;
            }
            this._rpc({
                model:"pos.order",
                method:"get_order",
                args:[[self.order_id]],
                kwargs:{}
            }).then(function(res){
                var new_order = new models.Order({},{pos:self.pos});
                self.pos.get('orders').add(new_order);

                var client = self.pos.db.get_partner_by_id(self.partner_id)
                new_order.set_client(client);
                new_order.set_invoice_type('out_refund');
                new_order.set_credit_note_comment(credit_note_comment);
                new_order.set_refund_order_id(self.order_id);
                new_order.set_refund_order_name(res.order_name);
                new_order.set_refund_order_date(res.date)
                new_order.set_credit_note_type(credit_note_type);
                if(res.has_invoice){
                    new_order.set_refund_invoice(res.invoice_id);
                    new_order.set_refund_invoice_type_code(res.invoice_type_code);
                }
                new_order.trigger('change',new_order);
                self.pos.set('selectedOrder', new_order);
                self.gui.show_screen("screen_credit_note")
            })
        }
    })

    gui.define_popup({
        name:"create_credit_note_modal",
        widget:CreateCreditNoteModal
    })

});