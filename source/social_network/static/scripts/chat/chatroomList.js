document.querySelector('#room-name-input').focus();
document.querySelector('#room-name-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#room-name-submit').click();
    }
};

document.querySelector('#room-name-submit').onclick = function(e) {
    var roomName = document.querySelector('#room-name-input').value;
    validateRoomName(roomName)
};

document.querySelectorAll(".room-name-enter").forEach(btn => {
    btn.addEventListener('click', e => {
        var roomName = btn.value;
        validateRoomName(roomName); 
    }); 
});  

function validateRoomName(roomName) {
    if (roomName === '') {
        alert('Room name field is empty! Please enter a valid room name.')
        location.reload();
    }
    else {  
        window.location.pathname = 'chat/' + roomName + '/';
    }
}

