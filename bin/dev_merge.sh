juicer merge -s --force -m '' static/js/stream_editor.js 
juicer merge -s --force -m '' static/js/feed_editor.js 

juicer merge -d .  -e data_uri -f -m '' static/css/editor-stylo.css
juicer merge -d .  -e data_uri -f -m '' static/css/general-site.css