odoo.define('bo_backend_sale_invoice_ticket.SaleInvoiceTicket', function(require) {
    "use strict";
    
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var _t = core._t;
    var QWeb = core.qweb;
    
    var InvoiceTicket = AbstractAction.extend({
        hasControlPanel: true,
        contentTemplate: 'InvoiceTicketMain',
        events: {
            // "click .o_hr_attendance_sign_in_out_icon": function() {
            //     this.$('.o_hr_attendance_sign_in_out_icon').attr("disabled", "disabled");
            //     this.update_attendance();
            // },
        },
    
        init: function(parent, context) {
            // debugger;
            this._super(parent, context);
            // console.log(parent);
            // console.log(context);
            this.invoice_id = context.params.invoice_id
            this.dashboards_templates = ['OrderReceipt'];
            // console.log("invoice_id : " + this.invoice_id);
        },
    
        willStart: function() {
            console.log("WILL START FUNCTION");
            var self = this;
                return self.fetch_data();
        },
    
        start: function() {
            console.log("START FUNCTION");
            var self = this;
            this.set("title", 'Dashboard');
            return this._super().then(function() {
                self.update_cp();
                self.render_dashboards();
                self.render_graphs();
                //self.clear_data()
                self.$el.parent().addClass('oe_background_grey');
            });
        },
        fetch_data: function() {
            var self = this;
            var def0 = self._rpc({
                model: 'account.move',
                method: 'check_user_group'
            }).then(function(result) {
                if (result == true) {
                    self.is_manager = true;
                } else {
                    self.is_manager = false;
                }
            });
            // var def1 = self._rpc({
            //     model: 'account.move',
            //     method: 'invoice_data',
            //     args: [self.invoice_id]
            // }).then(function(result) {
            //     if (result == true){
            //         self.is_report = true;
            //     }else {
            //         self.is_report = false;
            //     }
            //     // self.report_id = result['report_id'];
            //     // self.fecha_inicio = result['date_start'];
            //     // self.fecha_fin = result['date_end'];
            // });
            return $.when(def0);
        },
    
        render_dashboards: function() {
            console.log('render_dashboards')
            var self = this;
            // console.log(self.get_receipt_env())
            var templates = []
            if (self.is_manager == true) { templates = ['ReceiptScreenWidget']; } else { templates = ['ReceiptScreenWidget']; }
            _.each(templates, function(template) {
                self.$('.screens').append(QWeb.render(template, { widget: self }));
            });
            
        },
    
        render_graphs: function() {
            console.log("RENDER_GRAPHS")
            var self = this;
            self.render_ticket();
            //self.$('.o_invoice_ticket').append(QWeb.render(template, self.get_receipt_env()));
        },
    
        on_reverse_breadcrumb: function() {
            console.log("ON_REVERSE_BREADCRUMB")
            var self = this;
            web_client.do_push_state({});
            this.update_cp();
            this.fetch_data().then(function() {
                self.$('.o_indicador_dashboard').empty();
                // self.render_dashboards();
                self.render_graphs();
            });
        },
    
        update_cp: function() {
            var self = this;
            console.log("UPDATE_CP")
        },
        destroy: function(){
            console.log("DESTROY");
        },
        render_ticket: function() {
            var self = this;
            //console.log("invoice_id: " + self.invoice_id);
            // var receipt = {}
            // debugger;
            rpc.query({
                model: 'account.move',
                method: 'invoice_data',
                args: [self.invoice_id]
            }).then(function(result) {
                // receipt = result;
                console.log("invoice_data");
                console.log(result);
                self.$('.pos-receipt-container').append(QWeb.render('OrderReceipt', result));
            });
        },
    });
    
    core.action_registry.add('invoice_ticket', InvoiceTicket);
    
    return InvoiceTicket;
    });