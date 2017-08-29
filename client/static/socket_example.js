var socket;
//var nickname = 'mortimerjunior';  // nickname doesn't exist
var nickname = 'rICK';  // nickname exists
//var room_name = 'not_existing_room';  // room doesn't exist
//var room_name = $("#room_name").html();
var room_name = 'room1';

$(document).ready(function () {

        console.log('socket init');
        // Endpoint is the same for every message. Dynamic endpoints weren't supported.
        //socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');
        socket = io.connect('http://localhost:5000/chat');

        socket.on('connect', function () {
            // socket.emit('foo', {key: value}) sends an foo event to connected route.
            socket.emit('joined', {room_name: room_name, nickname: nickname});
        });
        socket.on('status', function (data) {
       //     $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
         //   $('#chat').scrollTop($('#chat')[0].scrollHeight);
            var message = ('<li class="chat_bubble sender_name" style="float: left; font-size: smaller">' + data.msg + '</li>');
            $("#messages_list").append(message);

        });
        socket.on('message', function (data) {
          //  $('#chat').val($('#chat').val() + data.msg + '\n');
          //  $('#chat').scrollTop($('#chat')[0].scrollHeight);

            var msg = data.msg.split(":");

            var message = ('<li class="chat_bubble chat_bubble-sent">' + msg[1] + '</li>');
            $("#messages_list").append(message);

        });
        $('#text').keypress(function (e) {
            var code = e.keyCode || e.which;
            if (code == 13) {
                text = $('#text').val();
                $('#text').val('');
                socket.emit('text', {msg: text, room_name: room_name, nickname: nickname});
            }
        });
    });

function leave_room() {
    console.log(room_name, nickname);
    socket.emit('left', {room_name: room_name, nickname: nickname}, function () {
        socket.disconnect();
        // redirect somewhere else or close the chat window
        // window.location.replace('some_other_file.html');

    });
}