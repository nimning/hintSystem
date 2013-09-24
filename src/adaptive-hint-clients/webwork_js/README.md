
Installation
============

1. Update `WeBWorK/ContentGenerator/Problem.pm` with the following patch:    
```
--- a/lib/WeBWorK/ContentGenerator/Problem.pm
+++ b/lib/WeBWorK/ContentGenerator/Problem.pm
@@ -1765,7 +1765,10 @@ sub output_JS{

        # The Base64.js file, which handles base64 encoding and decoding.
        print CGI::start_script({type=>"text/javascript", src=>"$site_url/js/Base64.js"}), CGI::end_script();
-
+
+       # Adaptive Hints
+       print CGI::start_script({type=>"text/javascript", src=>"http://cdn.sockjs.org/sockjs-0.3.min.js"}), CGI::end_script();
+       print CGI::start_script({type=>"text/javascript", src=>"$site_url/js/adaptive_hints.js"}), CGI::end_script();

        return "";
 }
```

2. Place [`adaptive_hints.js`](adaptive_hints.js) in ``/opt/webwork/webwork2/htdocs/js``

