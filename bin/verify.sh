find static/js/ -name '[a-zA-Z]*.js' | grep -v "/lib/" | grep -v "min.js" | xargs juicer verify

