odoo.define('gestionit_pe_fe_pos.screens',[
    'point_of_sale.screens',
    'web.core',
    'web.rpc'
],function(require){
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var rpc = require("web.rpc")
    var QWeb = core.qweb;
    var exports = {}
    // var DomCache = screens.DomCache
    
    screens.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            self = this;
            this._super(force_validation);
        },
        renderElement: function() {
            var self = this;
            this._super();
            self.render_sale_journals().appendTo(this.$('.payment-buttons'));
            self.$('.js_sale_journal').click(function() {
                self.click_sale_journals($(this).data('id'));
            });
        },
        render_sale_journals: function() {
            var self = this;
            return  $(QWeb.render('SaleInvoiceJournal', { widget: self}));
        },
        click_sale_journals: function(journal_id) {
            var order = this.pos.get_order();
            var journal = this.pos.db.get_journal_by_id(journal_id);

            if (order.get_invoice_journal_id() != journal_id) {
                order.set_invoice_journal_id(journal_id);
                order.set_invoice_type_code_id(journal.invoice_type_code_id)
                this.$('.js_sale_journal').removeClass('highlight');
                this.$('div[data-id="' + journal_id + '"]').addClass('highlight');
            } else {
                order.set_invoice_journal_id(undefined);
                order.set_invoice_type_code_id(undefined);
                this.$('.js_sale_journal').removeClass('highlight');
            }
            order.trigger('change',order);
        },
        customer_changed: function() {
            var client = this.pos.get_client();
            // console.log(this.pos.get_client_display_name())
            this.$('.js_customer_name').text( client ? this.pos.get_client_display_name() : "Cliente" );
        },
        order_is_valid: function(force_validation) {
            var self = this;
            var order = self.pos.get_order();
            var client = order.get_client();
            var identification_type = undefined;
            var client_identification_type_code = undefined;
            if(client){
                if(client.l10n_latam_identification_type_id){
                    identification_type = this.pos.db.identification_type_by_id[client.l10n_latam_identification_type_id[0]]
                    var client_identification_type_code = identification_type.l10n_pe_vat_code
                }
            }
            var journal = order.get_invoice_journal_id()?self.pos.db.journal_by_id[order.get_invoice_journal_id()]:undefined;
            
            var total = 0;
            var error_msg_subtotal = ""
            order.get_orderlines().forEach(function(orderline,index) {
                var subtotal = orderline.get_quantity() * orderline.get_unit_price() * (1-orderline.get_discount()/100.0)
                total += subtotal
                if(subtotal<=0){
                    error_msg_subtotal +=" * item ("+(index+1).toString()+") - ["+orderline["product"]["default_code"]+"]"+orderline["product"]["display_name"]
                }
            })

            // if (!order.get_client() && this.pos.config.anonymous_id) {
            //     var new_client = this.pos.db.get_partner_by_id(this.pos.config.anonymous_id[0]);
            //     if (new_client) {
            //         order.set_client(new_client);
            //     }
            // }

            if (journal) {
                if (client) {
                    if ( ["1","6","0"].indexOf(String(client_identification_type_code)) == -1 || identification_type.available_in_pos == false) {
                        self.gui.show_popup('confirm', {
                            'title': 'Datos del Cliente Incorrectos',
                            'body': 'El cliente seleccionado tiene un tipo de documento de identidad inválido o no permitido. Tipos de documentos de identidad válidos: DNI, RUC y "Sin Documento" para ventas Menores a S/.700.00. Configuración de Documentos de Identidad permitidos en Contactos -> Configuración -> Tipo de Identificación.',
                            confirm: function() {
                                self.gui.show_screen('clientlist');
                            },
                        });
                        return false
                    }
                    if(journal.invoice_type_code_id == '03' || journal.invoice_type_code_id == '01'){
                        if(error_msg_subtotal.length>0){
                            self.gui.show_popup('confirm', {
                                'title': 'Error: Cantidad y precio de uno o más productos deben ser mayores a cero.',
                                'body': $('<div>Revise los siguientes productos de la lista de pedido:'+error_msg_subtotal+"</div>").html(),
                                confirm: function() {
                                    self.gui.show_screen('products');
                                },
                            });
                            return false
                        }
                    }
                    if (journal.invoice_type_code_id == '03') {
                        if (client) {
                            if (total >= 700) {
                                if (!client.vat) {
                                    self.gui.show_popup('confirm', {
                                        'title': 'Datos del Cliente Incorrectos',
                                        'body': 'El número de documento de identidad del cliente es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 el detalle de DNI es obligatorio ',
                                        confirm: function() {
                                            self.gui.show_screen('clientlist');
                                        },
                                    });
                                    return false
                                }
                                if (!client_identification_type_code) {
                                    self.gui.show_popup('confirm', {
                                        'title': 'Datos del Cliente Incorrectos',
                                        'body': 'El tipo de documento de identidad es obligatorio',
                                        confirm: function() {
                                            self.gui.show_screen('clientlist');
                                        },
                                    });
                                    return false
                                }
                                if (client_identification_type_code != "1") {
                                    self.gui.show_popup('confirm', {
                                        'title': 'Datos del Cliente Incorrectos',
                                        'body': 'El tipo de documento de identidad (DNI) es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 de detalle el DNI es obligatorio',
                                        confirm: function() {
                                            self.gui.show_screen('clientlist');
                                        },
                                    });
                                    return false
                                }
                                if (!self.pos.dniValido(client.vat)) {
                                    self.gui.show_popup('confirm', {
                                        'title': 'Error',
                                        'body': 'El DNI del cliente tiene un formato incorrecto.',
                                        confirm: function() {
                                            self.gui.show_screen('clientlist');
                                        },
                                    });
                                    return false
                                }
                            }
                        } else {
                            self.gui.show_popup('confirm', {
                                'title': 'No ha seleccionado un cliente',
                                'body': 'Seleccione un cliente',
                                confirm: function() {
                                    self.gui.show_screen('clientlist');
                                },
                            });
                            return false
                        }
                    } else if (journal.invoice_type_code_id == '01') {
                        if (client) {
                            if (!client.vat) {
                                self.gui.show_popup('confirm', {
                                    'title': 'Datos del Cliente Incorrectos',
                                    'body': 'El número de documento de identidad del cliente es obligatorio',
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return false
                            }
                            if (!client_identification_type_code) {
                                self.gui.show_popup('confirm', {
                                    'title': 'Datos del Cliente Incorrectos',
                                    'body': 'El tipo de documento de identidad es obligatorio',
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return false
                            }
                            if (client_identification_type_code != "6") {
                                self.gui.show_popup('confirm', {
                                    'title': 'Datos del Cliente Incorrectos',
                                    'body': 'Para emitir una Factura el cliente seleccionada debe tener RUC',
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return false
                            }
                            if (!self.pos.rucValido(client.vat)) {
                                self.gui.show_popup('confirm', {
                                    'title': 'Datos del Cliente Incorrectos',
                                    'body': 'El Número de documento de identidad del cliente (RUC) no es válido.',
                                    confirm: function() {
                                        self.gui.show_screen('clientlist');
                                    },
                                });
                                return false
                            }
                        } else {
                            self.gui.show_popup('confirm', {
                                'title': 'No ha seleccionado un cliente',
                                'body': 'Seleccione un cliente. Recuerde que para una factura el cliente asociado debe poseer RUC y debe estar Activo.',
                                confirm: function() {
                                    self.gui.show_screen('clientlist');
                                },
                            });
                            return false
                        }
                    }
                }
            }
            return self._super(force_validation);
        },
        finalize_validation:function(){
            var order = this.pos.get_order();
            if (order.get_invoice_journal_id()) {
                var numbers = this.pos.get_order_number(order.get_invoice_journal_id());
                order.set_number(numbers.number);
                order.set_sequence_number(numbers.sequence_number);
            }
            if (order.get_number() && !order.get_invoice_journal_id()) {
                order.set_number(false);
                order.set_sequence_number(0);
            }
            if (order.get_number()) {
                this.pos.set_sequence(order.get_invoice_journal_id(), order.get_number(), order.get_sequence_number())
            }
            this._super()
        },
        post_push_order_resolve: function (order, server_ids) {
            // if (this.pos.is_french_country()) {
                var _super = this._super;
                var args = arguments;
                var self = this;
                var get_hash_prom = new Promise (function (resolve, reject) {
                    rpc.query({
                            model: 'pos.order',
                            method: 'get_current_invoice',
                            args: [server_ids],
                            kwargs: {}
                        }).then(function (res) {
                            order.set_digest_value(res.digest_value || false);
                            order.set_number(res.name);
                            order.set_sequence_number(res.name);
                            order.set_invoice_portal_url(res.invoice_portal_url || false);
                        }).finally(function () {
                            _super.apply(self, args).then(function () {
                                resolve();
                            }).catch(function (error) {
                                reject(error);
                            });
                        });
                });
                return get_hash_prom;
            // }
            // else {
            //     return this._super(order, server_ids);
            // }
        },
    });

    screens.ClientListScreenWidget.include({
        events:_.extend({},screens.ClientListScreenWidget.prototype.events,{
            'change input[name="radio_l10n_latam_identification_type_id"]':"change_l10n_latam_identification_type_id",
            'click .btn_get_datos':'get_datos',
        }),
        init: function(parent, options){
            this._super(parent, options);
            this.integer_client_details.push("l10n_latam_identification_type_id")
        },
        change_l10n_latam_identification_type_id:function(ev){
            var l10n_latam_identification_type_id = $(ev.currentTarget).val()
            this.set_l10n_latam_identification_type_id(l10n_latam_identification_type_id)
        },
        set_l10n_latam_identification_type_id:function(l10n_latam_identification_type_id){
            $(this.$el).find("input[name='l10n_latam_identification_type_id']").val(l10n_latam_identification_type_id)
            var vat = $(this.$el).find("input[name='vat']").val()
            var identification_code = this.pos.db.identification_type_by_id[parseInt(l10n_latam_identification_type_id)].l10n_pe_vat_code

            if(vat == undefined || vat == '' && identification_code == '0'){
                $(this.$el).find("input[name='vat']").val('0')
                $(this.$el).find("div.btn_get_datos").css("display","none")
            }else if(identification_code == '0'){
                $(this.$el).find("div.btn_get_datos").css("display","none")
            }else if(identification_code != '0'){
                $(this.$el).find("div.btn_get_datos").css("display","block")
            }
        },
        get_datos:function(ev){
            var self = this;
            var numero_document = $(this.$el).find("input[name='vat']").val()
            var l10n_latam_identification_type_id = $(this.$el).find("input[name='l10n_latam_identification_type_id']").val()
            if( l10n_latam_identification_type_id  == undefined){
                return false
            }
            var identification_code = this.pos.db.identification_type_by_id[parseInt(l10n_latam_identification_type_id)].l10n_pe_vat_code

            this._rpc({
                model:"res.company",
                method:"request_number_identificacion_partner",
                args:[],
                kwargs:{
                    tipo_doc:identification_code,
                    num_doc:numero_document
                }
            }).then(function(result){
                for(const att in result){
                    $(self.$el).find(`input[name='${att}']`).val(result[att])
                }
            })
        }
    })

    screens.ReceiptScreenWidget.include({
        get_receipt_render_env:function(){
            var res = this._super()
            // console.log(res)
            return res 
        }
    })
    exports.screens = screens

    return screens;
})