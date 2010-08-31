
Each screen 'foo' will have 
* one or more entries in urls.py
* one Python function foo in views.py
* one HTML template foo.html under templates
* one JavaScript file joo.js that requires all of it's dependencies
* one Minified JavaScript file foo.min.js for deployment
* one CSS file that @import's other CSS files

Any interesting sub-component should have
* one HTML template for inclusion
* one RequireJS style module
* one CSS file

Reusable JavaScript is broken into modules under the js/modules directory.

# Dev versus Production #
If you delete foo.min.js, then require.js will request each dependency one by one.
Otherwise require.min.js will need to be refreshed by running the build commands in

JS Lint
~/.gem/ruby/1.8/bin/juicer verify static/js/modules/streams/show_hide.js
Deploy code
~/.gem/ruby/1.8/bin/juicer merge -i --force -m '' static/js/feed_editor.js

For the least amount of pain use autocompile.py to re-build after a file is modified

Note: Use of the require funciton and the @depend docstring are provided by  RequireJS and Juicer.

RequireJS - provides CommonJS compatible JavaScript modules
Juicer - Used for "loading" source code (at compile time)

RequireJS also *can* provide the code loading piece, but htis isn't used. Maybe we should use this for lazy loaded code... but this is confusing enough as it is. RequireJS has an optimization script that is like Juicer, but it only provides Google Closure compiler and can't do jsmin or YUI Compressor. Also RequireJS is written in Java, which means Oracle will sue your face off.