
function jumpTo (time) {
    var audio = document.querySelector("audio");
    audio.currentTime = time;
    audio.play();
}

function httpGetAsync(theUrl, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous
    xmlHttp.send(null);
}

function parseResponse(response, callback) {
    callback(JSON.parse(response));
}

httpGetAsync("https://magic-meeting.appspot.com/magic/meeting/summary",function(response){
   parseResponse(response, function(data) {
       var audio = document.querySelector("Audio");
       var audioSrc = document.createElement("Source");
       audioSrc.src = data.url;
       audio.appendChild(audioSrc);
       audio.currentTime = 0;

       var note_list = document.getElementById('note_list');

       for(var i=0; i < data.notes.length; ++i) {
           (function() {
               var li = document.createElement("Li");
               li.className="mdl-list__item";
               var btn = document.createElement("Button");
               btn.className = "mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect mdl-button--accent";
               var note = data.notes[i];
               var hours = Math.floor(note.time / 3600), minutes = Math.floor(note.time / 60);
               var seconds = Math.floor(note.time - hours*3600 - minutes*60);
               var time = (hours ? (hours > 9 ? hours : "0" + hours) : "00") + ":" + (minutes ? (minutes > 9 ? minutes : "0" + minutes) : "00") + ":" + (seconds > 9 ? seconds : "0" + seconds);
               btn.innerText = "" + note.type + " - " + time ;
               btn.onclick = function () {
                   jumpTo(note.time - 3)
               };
               li.appendChild(btn);
               note_list.appendChild(li);
           })();
       }
   })
});
