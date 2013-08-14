// ==UserScript==
// @name        Find Related Links
// @namespace   enyalios.net
// @description Find links for next and previous pages.
// @include     *
// @version     1.0
// ==/UserScript==
//function OuterHTML(object) {
//    var element;
//    if (!object) return null;
//    element = document.createElement("div");
//    element.appendChild(object.cloneNode(true));
//    return element.innerHTML;
//}
(function(){
    document.addEventListener('keydown', function(e) {
        // bail if they dont have just the control modifier key held
        if(e.shiftKey || !e.ctrlKey || e.altKey || e.metaKey) { return; }
        // some sites have the next and previous button reversed
        var invert = 0;
        if(window.location.href.search(/www\.fmylife\.com/) > -1) { invert = 1; }
        if((e.keyCode == 222 && !invert) || (e.keyCode == 188 && invert)) {
            // pressed ctrl + '
            var el = document.querySelector("[rel='prev']");
            if(el) { // Wow a developer that knows what he or she is doing!
                document.location = el.href;
            } else { // Search from the bottom of the page up for a previous link.
                var els = document.getElementsByTagName("a");
                var i = els.length;
                while(el = els[--i]) {
                    if(el.innerHTML.search(/\b((sub)?prev|older|(sub)?back\b|id="pvs?" class="nav_ro")/i) > -1) {
                        window.location = el.href;
                        break;
                    }
                }
            }
        } else if((e.keyCode == 188 && !invert) || (e.keyCode == 222 && invert)) {
            // pressed ctrl + ,
            var el = document.querySelector("[rel='next']");
            if(el) {
                document.location = el.href;
            } else {
                var els = document.getElementsByTagName("a");
                var i = els.length;
                while(el = els[--i]) {
                    if(el.innerHTML.search(/\b((sub)?next|newer|id="nx" class="nav_ro)\b/i) > -1) {
                        window.location = el.href;
                        break;
                    }
                }
            }
        }
    }, false);
})();
