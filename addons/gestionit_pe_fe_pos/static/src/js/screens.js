odoo.define('gestionit_pe_fe_pos.screens',[
    'point_of_sale.screens',
    'web.core'
],function(require){
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var QWeb = core.qweb;
    var exports = {}

    
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
        validate_journal_invoice: function() {
            var res = false;
            var order = this.pos.get_order();

            if (!order.get_client() && this.pos.config.anonymous_id) {
                var new_client = this.pos.db.get_partner_by_id(this.pos.config.anonymous_id[0]);
                if (new_client) {
                    order.fiscal_position = _.find(this.pos.fiscal_positions, function(fp) {
                        return fp.id === new_client.property_account_position_id[0];
                    });
                } else {
                    order.fiscal_position = undefined;
                }
                if (new_client) {
                    order.set_client(new_client);
                }
            }
            if (!order.get_client() && order.get_sale_journal()) {

                self.gui.show_popup('confirm', {
                    'title': _t('An anonymous order cannot be invoiced'),
                    'body': _t('You need to select the customer before you can invoice an order.'),
                    confirm: function() {
                        self.gui.show_screen('clientlist');
                    },
                });
                return true;
            }
            return res;
        },
        order_is_valid: function(force_validation) {
            var res = this._super(force_validation);
            if (!res) {
                return res;
            }
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
            return res;
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
        // validate_order: function(force_validation) {
        //     self = this;
        //     var order = this.pos.get_order();
        //     var client = order.get_client();

        //     var journal = _.filter(order.pos.journal_ids, function(j_id) {
        //         return j_id["id"] == order.journal_id
        //     })[0]
        //     var total = 0;
        //     var error_msg_subtotal = ""
        //     order["orderlines"]["models"].forEach(function(orderline,index) {
        //         var subtotal = orderline["quantity"] * orderline["price"] * (1-orderline["discount"]/100.0)
        //         total += subtotal
        //         if(subtotal<=0){
        //             error_msg_subtotal +=" * item ("+(index+1).toString()+") - ["+orderline["product"]["default_code"]+"]"+orderline["product"]["display_name"]
        //         }
        //     })
            

        //     if (journal) {
        //         if (client) {
        //             let tipo_documento = client["tipo_documento"];
        //             if (!tipo_documento) {
        //                 self.gui.show_popup('confirm', {
        //                     'title': _t('Datos del Cliente Incorrectos'),
        //                     'body': _t('El cliente seleccionado no tiene un tipo de documento identidad. Tipos de Documento: 1 - DNI, 6 - RUC y "-" (guión) para ventas Menores a S/.700.00 '),
        //                     confirm: function() {
        //                         self.gui.show_screen('clientlist');
        //                     },
        //                 });
        //                 return true
        //             }
        //         }
        //         if(journal["invoice_type_code_id"] == '03' || journal["invoice_type_code_id"] == '01'){
        //             if(error_msg_subtotal.length>0){
        //                 self.gui.show_popup('confirm', {
        //                     'title': 'Error: Cantidad y precio de uno o más productos deben ser mayores a cero.',
        //                     'body': $('<div>Revise los siguientes productos de la lista de pedido:'+error_msg_subtotal+"</div>").html(),
        //                     confirm: function() {
        //                         self.gui.show_screen('products');
        //                     },
        //                 });
        //                 return true
        //             }
        //         }
        //         if (journal["invoice_type_code_id"] == '03') {
        //             if (client) {
        //                 let name = client["name"];
        //                 let dni = client["vat"];
        //                 let tipo_documento = client["tipo_documento"];

        //                 if (total >= 700) {
        //                     if (!dni) {
        //                         self.gui.show_popup('confirm', {
        //                             'title': _t('Datos del Cliente Incorrectos'),
        //                             'body': _t('El número de documento de identidad del cliente es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 el detalle de DNI es obligatorio '),
        //                             confirm: function() {
        //                                 self.gui.show_screen('clientlist');
        //                             },
        //                         });
        //                         return true
        //                     }
        //                     if (!tipo_documento) {
        //                         self.gui.show_popup('confirm', {
        //                             'title': _t('Datos del Cliente Incorrectos'),
        //                             'body': _t('El tipo de documento de identidad es obligatorio'),
        //                             confirm: function() {
        //                                 self.gui.show_screen('clientlist');
        //                             },
        //                         });
        //                         return true
        //                     }
        //                     if (tipo_documento != "1") {
        //                         self.gui.show_popup('confirm', {
        //                             'title': _t('Datos del Cliente Incorrectos'),
        //                             'body': _t('El tipo de documento de identidad (DNI) es obligatorio.\n Recuerda que para montos mayores a S/. 700.00 de detalle el DNI es obligatorio'),
        //                             confirm: function() {
        //                                 self.gui.show_screen('clientlist');
        //                             },
        //                         });
        //                         return true
        //                     }
        //                     if (!self.dniValido(dni)) {
        //                         self.gui.show_popup('confirm', {
        //                             'title': _t('Error'),
        //                             'body': _t('El DNI del cliente tiene un formato incorrecto.'),
        //                             confirm: function() {
        //                                 self.gui.show_screen('clientlist');
        //                             },
        //                         });
        //                         return true
        //                     }
        //                 }
        //             } else {
        //                 self.gui.show_popup('confirm', {
        //                     'title': _t('No ha seleccionado un cliente'),
        //                     'body': _t('Seleccione un cliente'),
        //                     confirm: function() {
        //                         self.gui.show_screen('clientlist');
        //                     },
        //                 });
        //                 return true
        //             }
        //         } else if (journal["invoice_type_code_id"] == '01') {
        //             if (client) {
        //                 let name = client["name"];
        //                 let ruc = client["vat"];
        //                 let street = client["street"];
        //                 let tipo_documento = client["tipo_documento"]
        //                 let email = client["email"]
        //                 if (!ruc) {
        //                     self.gui.show_popup('confirm', {
        //                         'title': _t('Datos del Cliente Incorrectos'),
        //                         'body': _t('El número de documento de identidad del cliente es obligatorio'),
        //                         confirm: function() {
        //                             self.gui.show_screen('clientlist');
        //                         },
        //                     });
        //                     return true
        //                 }
        //                 if (!tipo_documento) {
        //                     self.gui.show_popup('confirm', {
        //                         'title': _t('Datos del Cliente Incorrectos'),
        //                         'body': _t('El tipo de documento de identidad es obligatorio'),
        //                         confirm: function() {
        //                             self.gui.show_screen('clientlist');
        //                         },
        //                     });
        //                     return true
        //                 }
        //                 if (tipo_documento != "6") {
        //                     self.gui.show_popup('confirm', {
        //                         'title': _t('Datos del Cliente Incorrectos'),
        //                         'body': _t('Para emitir una Factura el cliente seleccionada debe tener RUC'),
        //                         confirm: function() {
        //                             self.gui.show_screen('clientlist');
        //                         },
        //                     });
        //                     return true
        //                 }
        //                 if (!self.rucValido(ruc)) {
        //                     self.gui.show_popup('confirm', {
        //                         'title': _t('Datos del Cliente Incorrectos'),
        //                         'body': _t('El Número de documento de identidad del cliente (RUC) no es válido.'),
        //                         confirm: function() {
        //                             self.gui.show_screen('clientlist');
        //                         },
        //                     });
        //                     return true
        //                 }
        //             } else {
        //                 self.gui.show_popup('confirm', {
        //                     'title': _t('No ha seleccionado un cliente'),
        //                     'body': _t('Seleccione un cliente. Recuerde que para una factura el cliente asociado debe poseer RUC y debe estar Activo.'),
        //                     confirm: function() {
        //                         self.gui.show_screen('clientlist');
        //                     },
        //                 });
        //                 return true
        //             }
        //         }
        //     }

        //     if (this.validate_journal_invoice()) {
        //         return;
        //     }
        //     this._super(force_validation);

        // },
    });

    exports.screens = screens

    return screens;
})