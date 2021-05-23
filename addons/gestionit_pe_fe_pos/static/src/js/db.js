odoo.define("gestionit_pe_fe_pos.DB",[
    "point_of_sale.DB"
],function(require){
    "use strict";
    var PosDB = require("point_of_sale.DB")
    var PosDBSuper = PosDB.prototype

    
    PosDB = PosDB.extend({
        init: function(options) {
            this.journal_ids = []
            this.journal_by_id = {};
            this.sequence_by_id = {};
            this.journal_sequence_by_id = {};
            this.invoice_numbers=[];
            return PosDBSuper.init.apply(this, arguments);
        },
        add_invoice_numbers: function(number) {
            if (number) {
                var invoice_numbers = this.load('invoice_numbers') || [];
                invoice_numbers.push(number);
                this.save('invoice_numbers', invoice_numbers || null);
            }
        },
        get_invoice_numbers: function() {
            return this.load('invoice_numbers') || [];
        },
        add_journals: function(journals) {
            if (!journals instanceof Array) {
                journals = [journals];
            }
            for (var i = 0, len = journals.length; i < len; i++) {
                this.journal_ids = journals
                this.journal_by_id[journals[i].id] = journals[i];
                this.journal_sequence_by_id[journals[i].id] = journals[i].sequence_id[0];
            }
        },
        add_sequences: function(sequences) {
            if (!sequences instanceof Array) {
                sequences = [sequences];
            }
            for (var i = 0, len = sequences.length; i < len; i++) {
                this.sequence_by_id[sequences[i].id] = sequences[i];
            }
        },
        get_journal_sequence_id: function(journal_id) {
            var sequence_id = this.journal_sequence_by_id[journal_id]
            return this.sequence_by_id[sequence_id] || {};
        },
        get_journal_by_id: function(journal_id) {
            return this.journal_by_id[journal_id];
        },
        set_sequence_next: function(id, number_increment) {
            var sequences = this.load('sequences') || {};
            sequences[id] = number_increment + 1;
            this.save('sequences', sequences || null);
        },
        get_sequence_next: function(journal_id) {
            var sequence_id = this.journal_sequence_by_id[journal_id];

            var sequences = this.load('sequences') || {};
            if (sequences[sequence_id]) {
                if (this.sequence_by_id[sequence_id].all_number_increment > sequences[sequence_id]) {
                    return this.sequence_by_id[sequence_id].all_number_increment;
                } else {
                    return sequences[sequence_id];
                }
            } else {
                return this.sequence_by_id[sequence_id].all_number_increment;
            }
        },
        set_credit_note_types:function(credit_note_types){
            this.credit_note_types = credit_note_types
        },
        get_credit_note_types:function(){
            return this.credit_note_types
        },
        get_credit_note_type_by_code:function(code){
            return _.find(this.credit_note_types,function(el){return el.code == code})
        },
        get_credit_note_type_by_id:function(id){
            return _.find(this.credit_note_types,function(el){return el.id == id})
        }
    });

    return PosDB


})