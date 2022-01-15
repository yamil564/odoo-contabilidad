odoo.define("gestionit_pe_fe_pos.models",[
    "gestionit_pe_fe_pos.DB",
    "point_of_sale.models",
    "web.rpc",
    "web.session"
],function(require){
    "use strict";
    var models = require("point_of_sale.models")
    var PosDB = require("gestionit_pe_fe_pos.DB")
    var session = require('web.session');
    var PosModelSuper = models.PosModel;
    var OrderSuper = models.Order
    var exports = {}

    _.find(PosModelSuper.prototype.models,function(el){return el.model == 'res.partner'}).fields.push('l10n_latam_identification_type_id','mobile');
    _.find(PosModelSuper.prototype.models,function(el){return el.model == 'res.company'}).fields.push('logo','street','phone','website_invoice_search');
    _.find(PosModelSuper.prototype.models,function(el){return el.model == 'account.tax'}).fields.push('tax_group_id')
    _.find(PosModelSuper.prototype.models,function(el){return el.label == 'pictures'}).loaded = function (self) {
        self.company_logo = new Image();
        return new Promise(function (resolve, reject) {
            self.company_logo.onload = function () {
                var img = self.company_logo;
                var ratio = 1;
                var targetwidth = 300;
                var maxheight = 150;
                if( img.width !== targetwidth ){
                    ratio = targetwidth / img.width;
                }
                if( img.height * ratio > maxheight ){
                    ratio = maxheight / img.height;
                }
                var width  = Math.floor(img.width * ratio);
                var height = Math.floor(img.height * ratio);
                var c = document.createElement('canvas');
                c.width  = width;
                c.height = height;
                var ctx = c.getContext('2d');
                ctx.drawImage(self.company_logo,0,0, width, height);

                self.company_logo_base64 = c.toDataURL();
                resolve();
            };
            self.company_logo.onerror = function () {
                reject();
            };
            self.company_logo.crossOrigin = "anonymous";
            self.company_logo.src = '/web/image?model=res.company&id='+self.company.id+'&field=logo'+ '&dbname=' + session.db + '&_' + Math.random();
        });
    }

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
    },{
        model:'l10n_latam.identification.type',
        fields: ['id','name','l10n_pe_vat_code','available_in_pos'],
        domain:['|',['active','=',true],['active','=',false]],
        loaded:function(self,identification_types){
            self.identification_types = identification_types
            self.db.add_identification_types(identification_types)
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
            var prefix = sequence.prefix || "";
            var suffix = sequence.suffix || "";
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
        get_client_identification_type_code:function(){
            var client = this.get_client()
            var identification_type = undefined
            if(client.l10n_latam_identification_type_id){
                identification_type = this.db.identification_type_by_id[client.l10n_latam_identification_type_id[0]]
                var client_identification_type_code = identification_type.l10n_pe_vat_code
            }else{
                var client_identification_type_code = undefined
            }
            return client_identification_type_code
        },
        get_client_display_name:function(){
            var client = this.get_client()
            if(client){
                var client_name = client.name
            }else{
                return false
            }
            var identification_type = undefined;
            if(client.l10n_latam_identification_type_id){
                identification_type = this.db.identification_type_by_id[client.l10n_latam_identification_type_id[0]]
                var client_identification_type_code = identification_type.l10n_pe_vat_code
            }else{
                var client_identification_type_code = undefined
            }
            if(['1','6'].indexOf(client_identification_type_code) >=0 && Boolean(client.vat)){
                client_name += " [" +identification_type.name+"-"+client.vat+"]" 
            }else if(['1','6'].indexOf(client_identification_type_code) >=0 && Boolean(~client.vat) ){
                client_name += " [" +identification_type.name+"- N/A]" 
            }else{
                client_name += " [N/A]"
            }
            return client_name
        },
        set_sequence: function(journal_id, number, number_increment) {
            var sequence = this.db.get_journal_sequence_id(journal_id);
            this.db.set_sequence_next(sequence.id, number_increment);
            this.db.add_invoice_numbers(number);

        },
        rucValido: function(ruc) {
            var ex_regular_ruc;
            ex_regular_ruc = /^\d{11}(?:[-\s]\d{4})?$/;
            if (ex_regular_ruc.test(ruc)) {
                return true
            }
            return false;
        },
        dniValido: function(dni) {
            var ex_regular_dni;
            ex_regular_dni = /^\d{8}(?:[-\s]\d{4})?$/;
            if (ex_regular_dni.test(dni)) {
                return true
            }
            return false;
        },
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
        export_for_printing:function(){
            var res = OrderSuper.prototype.export_for_printing.apply(this, arguments);
            var self = this;
            var client = self.pos.get_client()
            var client_identification_type_code = undefined;
            var identification_type = undefined;
            // var company = this.pos.company;
            if(client){
                if(client.l10n_latam_identification_type_id){
                    identification_type = self.pos.db.identification_type_by_id[client.l10n_latam_identification_type_id[0]]
                    var client_identification_type_code = identification_type.l10n_pe_vat_code
                }
            } 
            var journal = self.get_invoice_journal_id()?self.pos.db.journal_by_id[self.get_invoice_journal_id()]:undefined;
            if(client && journal){
                res["qr_string"] = [res.company.vat, //RUC de emisor
                                    journal.invoice_type_code_id, //Tipo de comprobante electrónico
                                    journal.code, //Serie de comprobante
                                    self.sequence_number,//Número correlativo
                                    res.total_tax,//Total IGV
                                    res.total_with_tax,//Monto Totales
                                    res.date.localestring.substr(0,10),//Fecha de Emisión
                                    client_identification_type_code,//Tipo de documento de identidad de Receptor
                                    client.vat, //Número de documento de identidad de Receptor
                                    this.get_digest_value()
                                    ].join("|")
            }
            return res
        },
        set_digest_value:function(digest_value){
            this.digest_value = digest_value
        },
        get_digest_value:function(){
            return this.digest_value || "*"
        },
        set_invoice_portal_url:function(invoice_portal_url){
            this.invoice_portal_url = invoice_portal_url
        },
        get_invoice_portal_url:function(){
            return this.invoice_portal_url
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
            res['sale_type'] = this.sale_type || "sale"
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
            // this.assert_editable();
            this.number = number;
        },
        get_number: function() {
            return this.number;
        },
        set_sequence_number: function(number) {
            // this.assert_editable();
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