var playerName = document.getElementById("game_board").getAttribute("player_name");
var char_choice = document.getElementById("game_board").getAttribute("char_choice");

var gameSocket = new WebSocket('ws://' + window.location.host + '/ws/game/' + playerName + '/');
var gameBoard = [
    -1, -1, -1,
    -1, -1, -1,
    -1, -1, -1,
];
winIndices = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
]
let moveCounter = 0;
let isRequestedUserTurn = true;

let elementArray = document.getElementsByClassName('square');
for (var i = 0; i < elementArray.length; i++){
    elementArray[i].addEventListener("click", event=>{
        var path = event.composedPath ? event.composedPath() : event.path;
        if (path) {
            const index = path[0].getAttribute('data-index');
            if(gameBoard[index] == -1){
                if(!isRequestedUserTurn){
                    alert("Wait for" +  playerName + " to place a move");
                }  
                else{
                    isRequestedUserTurn = false;
                    document.getElementById("alert_move").style.display = 'none';      
                    make_move(index, char_choice);
                }
            }
        }
        else {
            window.location.reload()
        }
        
        
    })
}

function make_move(index, player){
    index = parseInt(index);
    let data = {
        "event": "MOVE",
        "message": {
            "index": index,
            "player": player
        }
    }
    
    if(gameBoard[index] == -1){
        moveCounter++;
        if(player == 'X')
            gameBoard[index] = 1;
        else if(player == 'O')
            gameBoard[index] = 0;
        else{
            alert("Invalid character choice");
            return false;
        }
        gameSocket.send(JSON.stringify(data))
    }

    elementArray[index].innerHTML = player;
    const hasWon = getWinner();
    if(isRequestedUserTurn){
        if(hasWon){
            data = {
                "event": "END",
                "message": `Congratulations to the Winner: ${player}. Would you like to play again?`
            }
            gameSocket.send(JSON.stringify(data))
        }
        else if(!hasWon && moveCounter == 9){
            data = {
                "event": "END",
                "message": "Draw! Would you like to play again?"
            }
            gameSocket.send(JSON.stringify(data))
        }
    }
}

function resetMoves(){
    gameBoard = [
        -1, -1, -1,
        -1, -1, -1,
        -1, -1, -1,
    ]; 
    moveCounter = 0;
    isRequestedUserTurn = true;
    document.getElementById("alert_move").style.display = 'inline';        
    for (var i = 0; i < elementArray.length; i++){
        elementArray[i].innerHTML = "";
    }
}

const check = (winIndex) => {
    if (
    gameBoard[winIndex[0]] !== -1 &&
    gameBoard[winIndex[0]] === gameBoard[winIndex[1]] &&
    gameBoard[winIndex[0]] === gameBoard[winIndex[2]]
    )   return true;
    return false;
};

function getWinner(){
    let hasWon = false;
    if (moveCounter >= 5) {
    winIndices.forEach((w) => {
        if (check(w)) {
        hasWon = true;
        windex = w;
        }
    });
    }
    return hasWon;
}

function wsConnect() {
    gameSocket.onopen = function open() {
        console.log('WebSockets connection created.');
        gameSocket.send(JSON.stringify({
            "event": "START",
            "message": ""
        }));
    };

    gameSocket.onclose = function (e) {
        console.log('Socket is closed. Reconnect will be attempted in 1 second.', e.reason);
        setTimeout(function () {
            wsConnect();
        }, 1000);
    };
    
    // Sending info about the player
    gameSocket.onmessage = function (e) {
        let data = JSON.parse(e.data);
        data = data["payload"];
        let message = data['message'];
        let event = data["event"];
        switch (event) {
            case "START":
                resetMoves();
                break;
            case "END":
                alert(message);
                resetMoves();
                break;
            case "MOVE":
                if(message["player"] != char_choice){
                    make_move(message["index"], message["player"])
                    isRequestedUserTurn = true;
                    document.getElementById("alert_move").style.display = 'inline';        
                }
                break;
            default:
                console.log("No event")
        }
    };

    if (gameSocket.readyState == WebSocket.OPEN) {
        gameSocket.onopen();
    }
}

wsConnect();