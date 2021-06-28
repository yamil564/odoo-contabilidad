odoo.define("bo_blog_snippet_quill.snippet",function(require){
    var options = require("web_editor.snippets.options")
    var core = require("web.core")
    var qweb = core.qweb
    var Dialog = require("web.Dialog")

    options.registry.QuillTextEditor = options.Class.extend({
        start:function(ev){
            this._super()
        },
        edit:function(ev){
            console.log("edit")
        }
    })
})