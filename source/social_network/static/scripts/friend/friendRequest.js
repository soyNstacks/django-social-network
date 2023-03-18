 /** Function to accept friend request*/ 
function acceptFriendRequest(request_id, loadUrl, csrftoken) { 

    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "request_id": request_id,
    }

    $.ajax({
        type: "POST",
        dataType: "json",
        url: loadUrl,
        timeout: 5000,
        data: payload,
        success: function(data){
            console.log('Success: ' + data.response)
        },
        error: function(data){
            console.log('Error: ' + data.response)
            alert("Error occured. Please try again.")
        },
        complete: function(data){
            onUpdateRequest()
        },
    })
}

/** Function to reject friend request*/ 
function rejectFriendRequest(request_id, loadUrl, csrftoken) {

    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "request_id": request_id,
    }

    $.ajax({
        type: "POST",
        dataType: "json",
        url: loadUrl,
        timeout: 5000,
        data: payload,
        success: function(data){
            console.log('Success: ' + data.response)
        },
        error: function(data){
            console.log('Error: ' + data.response)
            alert("Error occured. Please try again.")
        },
        complete: function(data){
            onUpdateRequest()
        },
    })
}

/** Function to cancel friend request*/ 
function cancelFriendRequest(request_id, loadUrl, csrftoken) {

    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "request_id": request_id,
    }

    $.ajax({
        type: "POST",
        dataType: "json",
        url: loadUrl,
        timeout: 5000,
        data: payload,
        success: function(data){
            console.log('Success: ' + data.response)
        },
        error: function(data){
            console.log('Error: ' + data.response)
        },
        complete: function(data){
            onUpdateRequest()
        },
    })
}

/** Function to send friend request*/ 
function sendFriendRequest(username, loadUrl, csrftoken) {

    payload = {
        "csrfmiddlewaretoken": csrftoken,
        "receiver_username": username,
    }

    $.ajax({
        type: "POST",
        dataType: "json",
        url: loadUrl,
        timeout: 5000,
        data: payload,
        success: function(data){
            console.log('Success: ' + data.response)
        },
        error: function(payload){
            // console.log('Error: ' + data.error)
            alert("Error occured. Please try again.")
        },
        complete: function(data){
            onUpdateRequest()
        },
    })
}

/** Function to reload page to update responses */
function onUpdateRequest(){ 
    location.reload();
}