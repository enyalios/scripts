function toggle_add_channel() {
    if(document.getElementById("addchannel1").style.display == "none") {
        document.getElementById("addchannel1").style.display = "block";
        document.getElementById("addchannel2").style.display = "none";
    } else {
        document.getElementById("addchannel1").style.display = "none";
        document.getElementById("addchannel2").style.display = "block";
    }
}

function toggle_section(x) {
    var el = document.getElementById("section" + x);
    var arrow = document.getElementById("arrow" + x);
    if(el.style.display == "block") {
        el.style.display = "none";
        arrow.className = "fa fa-fw fa-chevron-right";
    } else {
        el.style.display = "block";
        arrow.className = "fa fa-fw fa-chevron-down";
    }
}

function resume(x) {
    document.getElementById('pod').play();
    document.getElementById('pod').currentTime = x;
}

function toggle_watched(channel, episode) {
    var args = "toggle=1&channel=" + channel + "&episode=" + episode;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4) {
            document.getElementById("toggle").innerHTML=xmlhttp.responseText;
        }
    }
    xmlhttp.open("POST", "worker.cgi", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send(args);
    document.getElementById("toggle").innerHTML="Toggling...";
}

function seek(x) {
    document.getElementById('pod').currentTime = parseInt(document.getElementById('pod').currentTime) + x;
}

function save_time(channel, episode, length) {
    if(document.getElementById('pod').paused) { return; }
    var time = parseInt(document.getElementById('pod').currentTime);
    if(time < 60) { return; }
    var args = "channel=" + channel + "&episode=" + episode + "&time=" + time + "&length=" + length;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4) {
            document.getElementById("status").innerHTML=xmlhttp.responseText;
        }
    }
    xmlhttp.open("POST", "worker.cgi", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send(args);
    document.getElementById("status").innerHTML="Saving at " + time + " seconds...";
    if(length - time < 30) { document.getElementById("toggle").innerHTML="<i class=\"fa fa-lg fa-eye\"></i> Mark Unwatched"; }
}

function subscribe(channel, toggle) {
    var args = "action=sub&channel=" + channel + "&toggle=" + toggle;
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
        if(xmlhttp.readyState == 4) {
            document.getElementById("sub" + channel).innerHTML=xmlhttp.responseText;
        }
    }
    xmlhttp.open("POST", "worker.cgi", true);
    xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    xmlhttp.send(args);
    document.getElementById("sub" + channel).innerHTML="<img class=\"subspin\" src=\"img/spin.gif\">";
}
