//get the dependencies (RequireJS)
define(['Backbone', 'underscore', 'config', 'jquery-imagesloaded'], function (Backbone, _, config) {
	//##The problem View

    //A view defined for the browser app for the webwork Problem model.
    //There's no reason this same view couldn't be used in other pages almost as is.
    //Extend Backbone.View with the following attributes
    var ProblemView = Backbone.View.extend({
        //We want the problem to render in a `li` since it will be included in a list
        tagName:"li",
        //Add the 'problem' class to every problem
        className: "problem",                
        //This is the template for a problem, the html is defined in SetMaker3.pm
        template: _.template($('#problem-template').html()),

    
        //In most model views, initialize is used to set up listeners
        //on the views model.        
        initialize: function () {
            //this = new ProblemView object in the following 3 methods
            _.bindAll(this,"render","updateProblem","clear");
            // this.options.viewAttrs will determine which tools are shown on the problem
            this.allAttrs = {};                      
            //There are several special options that, if passed, will be attached directly to the view: 
            //model, collection, el, id, className, tagName and attributes.
            //the remaining options passed to the constructor are stored in options attribute of the view
            //------------
            //**options available for this implementation: viewAttrs(draggable), type, model(path, data, place, updateM, add-to-targetE, problemSeed), 
            //collection, el, jQuery(style, data-path, data-source)**
            //------------
            //extend allAttrs with the remaining objects in the argument list 
            _.extend(this.allAttrs,this.options.viewAttrs,{type: this.options.type});

            //get the part of the path in the model of this view
            var thePath = this.model.get("path").split("templates/")[1];
            //***create the query string***
            var probURL = "?effectiveUser=" + config.requestObject.user + "&editMode=SetMaker&displayMode=images&key=" 
                + config.requestObject.session_key 
                + "&sourceFilePath=" + thePath + "&user=" + config.requestObject.user + "&problemSeed=1234";
            //add editURL and viewURL to allAttrs 
            _.extend(this.allAttrs, { editUrl: "../pgProblemEditor/Undefined_Set/1/" + probURL, viewUrl: "../../Undefined_Set/1/" + probURL });
            //when data changes, fire off the render method with this = new ProblemView object
            this.model.on('change:data', this.render, this);
            //when a model is destroyed, fire off the remove method with this = new ProblemView object
            this.model.on('destroy', this.remove, this);
        },

        render:function () {
            var self = this;
            //if data is defined/not empty string
            if(this.model.get('data')){
                _.extend(this.allAttrs, this.model.attributes);
                //set the html using allAttrs on the template 
                this.$el.html(this.template(this.allAttrs));
                //view bg-color is lightgray
                this.$el.css("background-color", "lightgray");
                //manipulate the elements of class problem in the view
                this.$(".problem").css("opacity", "0.5");
                //assign handler for change event of elements of class .prob-value                
                this.$(".prob-value").on("change", this.updateProblem);
                //trigger the handler with the additional argument: place attribute
                this.model.collection.trigger("problemRendered",this.model.get("place"));
                
                // if images  mode is used
                var dfd = this.$el.imagesLoaded();
                //when images are loaded sucessfully
                dfd.done( function( $images ){
                    self.$el.removeAttr("style");
                    self.$(".problem").removeAttr("style");
                    self.$(".loading").remove();
                });

                if (this.options.viewAttrs.draggable) {
                    this.$el.draggable({
                        helper:'clone',
                        revert:true,
                        handle:'.drag-handle',
                        appendTo:'body',
                        //cursorAt:{top:0,left:0}, 
                        //opacity:0.65
                    }); 

                } 
                //if displayMode = "MathJax", use MathJax API
                if(this.model.get("displayMode")==="MathJax"){
                    MathJax.Hub.Queue(["Typeset",MathJax.Hub,this.el]);
                }                
            }
            //**if data is not defined, go to server and GET it**
            else {
                this.$el.html("<img src='/webwork2_files/images/ajax-loader-small.gif' alt='loading'/>");
                this.model.fetch(); //**NO success/failure CALLBACKS**
                //if successful render is fired automatically (change:data event)
            }
            //id = client-id
            //**NOT SURE IF IT IS GOOD IDEA. HOW TO FETCH AGAIN?**
            this.el.id = this.model.cid;
            this.$el.attr('data-path', this.model.get('path'));
            this.$el.attr('data-source', this.allAttrs.type);

            return this;
        },

        events: {"click .hide-problem": "hideProblem",
            "click .remove": 'clear',
            "click .refresh-problem": 'reloadWithRandomSeed',
            "click .add-problem": "addProblem"},

        reloadWithRandomSeed: function () {
            //choose a seed b/w 0 and 10000
            var seed = Math.floor((Math.random() * 10000));
            //set in silent mode 
            this.model.set({data:"", problemSeed: seed},{silent: true});
            //since data:"", model is fetched from the server
            this.render();
        },

        addProblem: function (evt){
            this.model.collection.trigger("add-to-target",this.model);
        },

        hideProblem: function (evt) {
            //$(this) can bed used instead of $(evt.target)
            $(evt.target).parent().parent().css("display","none")
        },

        updateProblem: function(evt)
        {
            this.model.update({value: $(evt.target).val()});
        },

        clear: function(){
            console.log("removing problem");
            this.model.collection.remove(this.model);
            //remove all attributes from the model which automatically fires this.render()
            this.model.clear();
            // update the number of problems shown
        }
    });

	return ProblemView;
});