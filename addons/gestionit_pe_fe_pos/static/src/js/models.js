odoo.define("gestionit_pe_fe_pos.models",[
    "gestionit_pe_fe_pos.DB",
    "point_of_sale.models"
],function(require){
    "use strict";
    var models = require("point_of_sale.models")
    var PosDB = require("gestionit_pe_fe_pos.DB")
    var PosModelSuper = models.PosModel;
    var OrderSuper = models.Order
    var exports = {}

    _.find(PosModelSuper.prototype.models,function(el){return el.model == 'res.partner'}).fields.push('l10n_latam_identification_type_id');
    _.find(PosModelSuper.prototype.models,function(el){return el.model == 'res.company'}).fields.push('logo','street','phone');
    _.find(PosModelSuper.prototype.models,function(el){return el.model == 'account.tax'}).fields.push('tax_group_id')

    PosModelSuper.prototype.models.push({
        model: 'account.journal',
        fields: ['id','name','code','invoice_type_code_id','sequence_id'],
        domain: function(self) {
            return [
                ['id', 'in', self.config.invoice_journal_ids]
            ];
        },
        loaded: function(self, journals) {
            self.db.sequence_ids = _.map(journals,function(journal){return journal.sequence_id[0]});
            self.db.add_journals(journals);
        },
    },{
        model: 'ir.sequence',
        fields: ['id', 'prefix', 'suffix', 'padding', 'number_next_actual'],
        domain: function(self) {
            return [
                ['id', 'in', self.db.sequence_ids]
            ];
        },
        loaded: function(self, sequences) {
            self.db.add_sequences(sequences);
        },
    },{
        model: 'account.tax.group',
        fields: ['id','codigo','tipo_afectacion'],
        loaded:function(self,account_tax_groups){
            self.taxes = _.map(self.taxes,function(tax){
                tax["tax_group_id"] = _.find(account_tax_groups,function(atg){atg.id == tax["tax_group_id"]})
                return tax
            })
        }
    });


    models.PosModel = models.PosModel.extend({
        initialize: function(session, attributes) {
            var res = PosModelSuper.prototype.initialize.apply(this, arguments);
            this.db = new PosDB(); // a local database used to search trough products and categories & store pending orders
            return res;
        },
        generate_order_number: function(journal_id) {
            var sequence = this.db.get_journal_sequence_id(journal_id);
            var num = "%0" + sequence.padding + "d";
            var prefix = sequence.interpolated_prefix || "";
            var suffix = sequence.interpolated_suffix || "";
            var increment = this.db.get_sequence_next(journal_id);
            var number = prefix + num.sprintf(parseInt(increment)) + suffix;
            return { 'number': number, 'sequence_number': increment };
        },
        get_order_number: function(journal_id) {
            var numbers = this.generate_order_number(journal_id);
            if (this.db.get_invoice_numbers().indexOf(numbers.number) != -1) {
                var numbers = this.get_order_number(journal_id);
                var sequence = this.db.get_journal_sequence_id(journal_id);
                this.db.set_sequence_next(sequence.id, numbers.sequence_number);
            }
            return numbers;
        },
        set_sequence: function(journal_id, number, number_increment) {
            var sequence = this.db.get_journal_sequence_id(journal_id);
            this.db.set_sequence_next(sequence.id, number_increment);
            this.db.add_invoice_numbers(number);

        },
        _save_to_server: function(orders, options) {
            if (!orders || !orders.length) {
                var result = $.Deferred();
                result.resolve([]);
                return result;
            }
            options = options || {};
            var self = this;
            var order_ids_to_sync = _.pluck(orders, 'id');
            
            return rpc.query({
                model: "pos.order",
                method: "create_from_ui",
                args: [_.map(orders, function(order) {
                    order.to_invoice = order.data.invoice_type_code_id?true:false
                    return order;
                })]
            }).then(function(server_ids) {
                _.each(order_ids_to_sync, function(order_id) {
                    self.db.remove_order(order_id);
                });
                self.set('failed', false);
                return server_ids;
            }).fail(function(error, event) {
                if (error.code === 200) { // Business Logic Error, not a connection problem
                    //if warning do not need to display traceback!!
                    if (error.data.exception_type == 'warning') {
                        delete error.data.debug;
                    }

                    // Hide error if already shown before ...
                    if ((!self.get('failed') || options.show_error) && !options.to_invoice) {
                        self.gui.show_popup('error-traceback', {
                            'title': error.data.message,
                            'body': error.data.debug
                        });
                    }
                    self.set('failed', error)
                }
                // prevent an error popup creation by the rpc failure
                // we want the failure to be silent as we send the orders in the background
                event.preventDefault();
                console.error('Failed to send orders:', orders);
            });
        }
    });
    
    models.Order = models.Order.extend({
        initialize: function(attributes, options) {
            this.sale_type = "sale"
            var res = OrderSuper.prototype.initialize.apply(this, arguments);
            this.number = false;
            this.invoice_journal_id = undefined;
            this.sequence_number = 0;
            this.set("credit_note_type",undefined)
            this.save_to_db(); 
        },
        set_sale_type: function(sale_type){
            var self = this;
            this.assert_editable();
            if(['sale','refund'].indexOf(sale_type)){
                self.sale_type = sale_type
            }else{
                self.gui.show_popup('error', {
                    'title': "Error",
                    'body': "El tipo de venta no esta permitido. Tipos de ventas permitidas 'sale', 'refund'",
                });
            }
        },
        get_sale_type: function(){
            return this.sale_type
        },
        set_invoice_journal_id: function(invoice_journal_id) {
            this.assert_editable();
            this.to_invoice = invoice_journal_id?true:false
            this.invoice_journal_id = invoice_journal_id;
        },
        get_invoice_journal_id: function() {
            return this.invoice_journal_id;
        },
        
        export_as_JSON: function() {
            var res = OrderSuper.prototype.export_as_JSON.apply(this, arguments);
            var journal = this.pos.db.get_journal_by_id(this.invoice_journal_id);
            res['invoice_journal_id'] = this.invoice_journal_id;
            res['number'] = this.number;
            res['sequence_number'] = this.sequence_number;
            res['invoice_type_code_id'] = (typeof journal === 'undefined') ? journal : journal.invoice_type_code_id;
            res['invoice_type'] = this.invoice_type
            res['credit_note_type'] = this.credit_note_type
            res['credit_note_comment'] = this.credit_note_comment
            res['refund_invoice'] = this.refund_invoice
            res['refund_invoice_type_code'] = this.refund_invoice_type_code
            return res;
        },
        init_from_JSON: function(json) {
            OrderSuper.prototype.init_from_JSON.apply(this, arguments);
            this.sale_type = json.sale_type || "sale"
            this.credit_note_type = json.credit_note_type
            this.invoice_journal_id = json.invoice_journal_id
            this.refund_invoice = json.refund_invoice
            this.refund_invoice_type_code = json.refund_invoice_type_code
            this.credit_note_comment = json.credit_note_comment
            this.invoice_type_code_id = json.invoice_type_code_id
        },
        set_number: function(number) {
            this.assert_editable();
            this.number = number;
        },
        get_number: function() {
            return this.number;
        },
        set_sequence_number: function(number) {
            this.assert_editable();
            this.sequence_number = number;
        },
        get_sequence_number: function() {
            return this.sequence_number;
        },
        set_credit_note_type:function(credit_note_type){
            this.assert_editable();
            if(credit_note_type){
                this.credit_note_type = parseInt(credit_note_type)
                this.set("credit_note_type",credit_note_type)
            }
        },
        get_credit_note_type:function(){
            return this.credit_note_type
        },
        get_credit_note_type_name:function(){
            return this.pos.db.get_credit_note_type_by_id(this.credit_note_type).name
        },
        set_credit_note_comment:function(comment){
            this.assert_editable();
            this.credit_note_comment = comment
        },
        get_credit_note_comment:function(){
            return this.credit_note_comment
        },
        set_refund_invoice_type_code:function(refund_invoice_type_code){
            this.assert_editable();
            var self = this;
            if(["01","03"].indexOf(refund_invoice_type_code)>=0){
                this.refund_invoice_type_code = refund_invoice_type_code
            }else{
                self.pos.gui.show_popup('error', {
                    'title': "Error",
                    'body': "El tipo de comprobante a rectificar no esta permitido. Solo se acepta 01-Factura y 03-Boleta",
                });
                throw new TypeError("El tipo de comprobante a rectificar no existe");
            }
        },
        set_refund_invoice:function(invoice){
            this.assert_editable();
            this.refund_invoice = invoice
        },
        get_refund_invoice_type_code:function(){
            return this.refund_invoice_type_code
        },
        get_refund_invoice:function(){
            return {id:this.refund_invoice[0],name:this.refund_invoice[1]}
        },
        set_invoice_type_code_id:function(invoice_type_code_id){
            this.invoice_type_code_id = invoice_type_code_id
        },
        get_invoice_type_code_id:function(){
            return this.invoice_type_code_id
        }
    });

    exports.models =models

})