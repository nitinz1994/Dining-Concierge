var $messages = $('.messages-content'),
    d, h, m,
    i = 0;

var apigClient = apigClientFactory.newClient();

var humanMessage = '';
var botMessage = '';
var greetMessage = 'Welcome to Dining Concierge Virtual Assistant!'

$(window).load(function() {
    $messages.mCustomScrollbar();
    setTimeout(function() {
        initialMessage();
        // getChatbotMessage();
    }, 50);
});

function updateScrollbar() {
    $messages.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
        scrollInertia: 10,
        timeout: 0
    });
}

function setDate() {
    d = new Date()
    if (m != d.getMinutes()) {
        m = d.getMinutes();
        if (m < 10) m = "0" + m;
        $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
    }
}

function insertMessage() {
    msg = $('.message-input').val();
    if ($.trim(msg) == '') {
        return false;
    }
    msg = msg.charAt(0).toUpperCase() + msg.slice(1);
    $('<div class="message message-personal">' + msg + '<figure class="avatar"><img src="img/human.png" /></figure></div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    humanMessage = msg;
    $('.message-input').val(null);
    updateScrollbar();
    getChatbotMessage();
    setTimeout(function() {
        insertBotMessage();
    }, 500 + (Math.random() * 20) * 10);
}

$('.message-submit').click(function() {
    insertMessage();
});

$(window).on('keydown', function(e) {
    if (e.which == 13) {
        insertMessage();
        return false;
    }
})

var body = {
  "messages": [
    {
      "type": "string",
      "unstructured": {
        "id": "string",
        "text": "hello",
        "timestamp": "string"
      }
    }
  ]
};

var params = {
    //This is where any header, path, or querystring request params go. The key is the parameter named as defined in the API
};

var additionalParams = {
    //If there are any unmodeled query parameters or headers that need to be sent with the request you can add them here
};

function getChatbotMessage() {
    // insert human entered message into the body of request
    body['messages'][0]['unstructured']['text'] = humanMessage;
    console.log('humanMessage = ' + body['messages'][0]['unstructured']['text']);

    apigClient.chatbotPost(params, body, additionalParams)
    .then(function(result){
        // console.log(result);
        // This is where you would put a success callback
        botMessage = result['data']['messages'][0]['unstructured']['text'];
        console.log('botMessage = ' + botMessage);
    }).catch(function(result){
        console.log('ERROR: Response failed - ' + result['status_code']);
        // This is where you would put an error callback
    });
}

function initialMessage() {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="img/chatbot.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
        $('.message.loading').remove();
        $('<div class="message new"><figure class="avatar"><img src="img/chatbot.png" /></figure>' + greetMessage + '</div>').appendTo($('.mCSB_container')).addClass('new');
        // setDate();
        updateScrollbar();
    }, 500 + (Math.random() * 20) * 10);

}

function insertBotMessage() {
    if ($('.message-input').val() != '') {
        return false;
    }
    $('<div class="message loading new"><figure class="avatar"><img src="img/chatbot.png" /></figure><span></span></div>').appendTo($('.mCSB_container'));
    updateScrollbar();

    setTimeout(function() {
        $('.message.loading').remove();
        $('<div class="message new"><figure class="avatar"><img src="img/chatbot.png" /></figure>' + botMessage + '</div>').appendTo($('.mCSB_container')).addClass('new');
        setDate();
        updateScrollbar();
    }, 500 + (Math.random() * 20) * 10);

}
