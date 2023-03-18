console.log("Sanity check from room.js.");

const roomName = JSON.parse(document.getElementById('room-name').textContent);
const chatLog = document.querySelector('#chat-log');
const messageInputDom = document.querySelector('#chat-message-input');
const audioRecordBtn = document.querySelector('#record-audio');
const onlineMembers = JSON.parse(document.getElementById('online-members').textContent);

const chatSocket = new WebSocket('ws://' 
                                + window.location.host 
                                + '/ws/chat/' 
                                + roomName
                                + '/'  
);

chatSocket.onopen = wsOnOpen;
    
chatSocket.onmessage = wsOnMessage;

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
}; 

chatSocket.onerror = function(err) {
    console.log("Error encountered: " + err.message);
    chatSocket.close();
}

messageInputDom.focus();
messageInputDom.onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};  

const exitBtn = document.querySelector('#room-exit-btn')
exitBtn.onclick = exitRoom;

const returnBtn = document.querySelector('#return-btn')
returnBtn.onclick = function(e) {
    console.log("Return to chatlist");
    window.location.pathname = 'chat/chat_room_list/';
};

const fileUploadResult = handleFileUpload();
document.querySelector('#chat-message-submit').onclick = function(e) {
    const message = messageInputDom.value;

    chatSocket.send(JSON.stringify({
        'message': message,
        'image': fileUploadResult[0]
    }));

    messageInputDom.value = '';
};

if (onlineMembers > 0) { 
    const pmFriendBtn = document.querySelector("#pm-friend-btn");
    
    if (pmFriendBtn != undefined) {
        pmFriendBtn.onclick = function() {
            messageInputDom.value = "/private " + pmFriendBtn.value + " ";
            messageInputDom.focus();
        };
    }
}

function wsOnMessage(e) {
    const data = JSON.parse(e.data);
    populateChatLog(data, chatLog);
}  

function wsOnOpen(e) {
    console.log('Connection is open')
}

function populateChatLog(data, chatLog) {
    if (data.message) {

        const options = { 
            hour: 'numeric',
            minute: 'numeric'
        };
        const timestamp = new Date().toLocaleString('default', options);

        switch (data.type) {
            case "bytes_data":
                document.querySelector('#transcript').textContent += ' ' + data
                break;
            case "chat_message":
                chatLog.innerHTML += ("["
                                        + timestamp 
                                        + "] "
                                        + data.username 
                                        + ": " 
                                        + data.message 
                                        + '\n');

                break;
                
            case "chat_image":
                const imageDiv = document.createElement('div');
                const classLists = ['display-uploaded-image']
                for (var i = 0; i < classLists.length; i++) {
                    imageDiv.classList.add(classLists[i]);
                }

                chatLog.innerHTML += ("["
                                        + timestamp 
                                        + "] "
                                        + data.username 
                                        + ": " 
                                        + data.message 
                                        + '\n');
                
                imageDiv.innerHTML += ('<img src="'
                                    + data.image
                                    + '" class="uploaded-image img-fluid img-thumbnail px-1 border" >');
                
                chatLog.appendChild(imageDiv);

                break;
            // source: https://testdriven.io/blog/django-channels/
            case "user_join":
                chatLog.innerHTML += (data.user 
                                    + " has joined the room. Say hi!\n");
                break;
                
            case "user_leave":
                chatLog.innerHTML += (data.user 
                                    + " has left the room. \n");
                break;

            case "private_message":
                chatLog.innerHTML += ("PM from " + data.username + ": " + data.message + "\n");
                break;

            case "private_message_delivered":
                chatLog.innerHTML += ("PM to " + data.target + ": " + data.message + "\n");
                break;

            default:
                alert("Please try again.")
                break;
        }
    } 
}

function handleFileUpload() {
    const results = [];

    btn = document.querySelector('#image-message-upload');
    // source: https://stackoverflow.com/questions/32556664/getting-byte-array-through-input-type-file
    btn.addEventListener('change', function (e) {
        const file = btn.files[0];
    
        try {
            toBase64(file).then(function (result) {
                results.push(result);
            });
        } catch(error) {
            console.error(error);
            return;
        }
    }, false);

    return results;

}

// source: https://stackoverflow.com/questions/36280818/how-to-convert-file-to-base64-in-javascript
function toBase64(file) {
    const reader = new FileReader();

    return new Promise((resolve, reject) => {
        reader.addEventListener('load', function (e) {
            console.log(reader.result);
            resolve(reader.result);
        }, false);

        reader.addEventListener('error', function (error) {
            reject(error);
        }, false);

        if (file) {
            reader.readAsDataURL(file);
        }

    });
}

function exitRoom(e) {
    const resp = window.confirm("Are you sure you want to leave this group permanently?");
    if (resp) {
        const message = exitBtn.value;
        chatSocket.send(JSON.stringify({
            'message': message
        }));
        window.location.pathname = 'chat/chat_room_list/';
    }
    else {
        location.reload();
    }
}

/** sources:
 * https://blog.deepgram.com/live-transcription-django/
*/


// audioRecordBtn.onclick = openAudioConnection;

function openAudioConnection() {
    console.log("Recording button clicked!");

    navigator.mediaDevices.getUserMedia({ audio: true})
        .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.start();
        const audioChunks = [];
 
        mediaRecorder.addEventListener("dataavailable", event => {
            audioChunks.push(event.data);
        });

        const inputGroup = document.querySelector("#message-controls");   
        inputGroup.innerHTML += ('<input id="stop-audio" class="mr-2 btn btn-outline-success" type="button" value="Stop Recording">')
        const audioStopBtn = document.querySelector("#stop-audio");  
            
        audioStopBtn.onclick = function(e) {
            mediaRecorder.stop();
            audioStopBtn.remove();
        }

        setTimeout(function(){
            mediaRecorder.stop();
            audioStopBtn.remove();
        }, 3000)});

}


 