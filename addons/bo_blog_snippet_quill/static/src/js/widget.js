odoo.define("bo_blog_snippet_quill.widget", function(require){
    var widget = require("web.public.widget")
    // var core = require("web.core")
    // var ImageResize = require("quill-image-resize-module")
    // Quill.import('core/module');

    // Quill.register({'modules/imageResize': ImageResize});
    Quill.register("modules/imageUploader", ImageUploader);

    hljs.configure({
        languages: ['shell', 'javascript', 'python','html']
    });

    widget.registry.QuillTextEditor = widget.Widget.extend({
        selector:".quill_text_editor",
        events:{
            "click .btn_blog_save":"save"
        },
        start:function(){
            var self = this;
            $(this.$el).find(".btn_blog_save").removeClass("d-none")

            const fullToolbarOptions = [
                [{ header: [1, 2, 3, false]},'align','direction','code-block'],
                ['background','bold', 'italic', 'underline', 'strike','underline'],
                ["clean"],
                ["image"],
            ];
            var options = {
                // debug: 'info',
                theme: 'snow',
                modules:{
                    syntax: true,
                    toolbar: {
                        container: fullToolbarOptions,
                    },
                    imageResize:{
                        displaySize: true,
                    },
                    imageUploader:{
                        upload: (file) => {
                            return new Promise((resolve, reject) => {
                                var reader = new FileReader();
                                reader.onloadend = function () {
                                    self._rpc({
                                        model:"ir.attachment",
                                        method:"create",
                                        args:[{
                                            type:"binary",
                                            public:true,
                                            name:file.name,
                                            mimetype:file.type,
                                            file_size:file.size,
                                            datas:reader.result.replace(/^data:.+;base64,/, '')
                                        }]
                                    }).then(function(res){
                                        if(res){
                                            resolve(window.location.origin+"/web/content/"+String(res))
                                        }else{
                                            reject("Error al cargar la imagen")
                                        }
                                    })
                                }
                                reader.readAsDataURL(file);
                            })
                            // return new Promise((resolve, reject) => {
                            //   setTimeout(() => {
                            //     resolve(
                            //       "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/JavaScript-logo.png/480px-JavaScript-logo.png"
                            //     );
                            //   }, 3500);
                            // });
                        },
                    }
                },
                // readOnly: true,
                
            };
            this.quill = new Quill(".blog_post_content",options); 
            this._super()
        },
        save:function(ev){
            var blog_id = $(this.$el).data("blog-id");
            var content = this.quill.root.innerHTML.trim();

            $(ev.currentTarget).attr("disabled", true);
            $(".blog_msg").text("Guardando ... ")
            this._rpc({
                model:"blog.post",
                method:"write",
                args:[[blog_id],{content}]
            }).then(function(res){
                setTimeout(function(){
                    $(ev.currentTarget).attr("disabled", false);
                    $(".blog_msg").text("");
                },1000)
            }).catch(function(res){
                $(ev.currentTarget).attr("disabled", false);
                $(".blog_msg").text("Se ha producido un error, vuelva a intentarlo.");
            })
        }
    })
})