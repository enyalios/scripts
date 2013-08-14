// ==UserScript==
// @name        Imgur Toggle
// @namespace   enyalios.net
// @description Toggle between the imgur page with comments and just the image.  Also on truncated galleries, it displays the rest of the images rather than going to just one.
// @include     http://*imgur.com/*
// @version     1.0
// @run-at      document-start
// ==/UserScript==
(function(){
    document.addEventListener('keydown', function(e) {
        // pressed F1
        if(e.keyCode == 112 && !e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
            url = window.location.href;
            if(matches = url.match(/^http:\/\/imgur\.com\/gallery\/(.*)$/)) {
                div = document.getElementById("album-truncated");
                if(div) {
                    div.getElementsByTagName("a")[0].click();
                } else {
                    //alert(document.getElementById("image").getElementsByClassName("album-title").length)
                    window.location = document.querySelector("[rel='image_src']").href
                }
            } else if(matches = url.match(/^http:\/\/i.imgur\.com\/(.*)\.(jpg|gif|png)$/)) {
                window.location = "http://imgur.com/gallery/" + matches[1];
            }
        }
    }, false);
})();
