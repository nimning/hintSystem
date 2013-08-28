## ProblemView.js 
*(last updated on March 2013)*   
from ```https://github.com/openwebwork/webwork2/blob/develop/htdocs/js/lib/views/ProblemView.js```   
       
       
Backbone.View object for the problem is defined. The problem is rendered:    

1.	If ```viewObj.model.data``` evaluates to true, problem is rendered directly via MathJax using 
viewObj.allAttrs on the pre-compiled template obtained from ```$(#problem-template).html()```    
2.	If ```viewObj.model.data``` evaluates to false (undefined or empty string e.g.), data is 
fetched from the server using ```viewObj.model.fetch()``` and render is automatically fired again  
with ```viewObj.model.data``` is now available (using MathJax again).   

 --------------------------------------------

## library_browser.js (Library Browser 3) 
*(last updated in 2012)*   
from ```https://github.com/openwebwork/webwork2/tree/master/htdocs/js/apps/LibraryBrowser```   
      
      
There is currently no code for reaching Webwork API in this js file. ```model``` or ```collection``` 
attributes of views can include ```url``` or ```urlRoot``` and they can be passed as arguments to view 
constructors to be able to use the webservice. However, there is a more recent code in the develop branch at:      
```https://github.com/openwebwork/webwork2/tree/develop/htdocs/js/apps/LibraryBrowser```   
I will also examine this developing code.   


 
 