juicer merge -s --force  static/js/stream_editor.js 
juicer merge -s --force  static/js/feed_editor.js 

juicer merge -d .  -e data_uri -f  static/css/editor-stylo.css
juicer merge -d .  -e data_uri -f  static/css/general-site.css