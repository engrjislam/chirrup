var socket;
//var nickname = 'mortimerjunior';  // nickname doesn't exist
var nickname = 'rICK';  // nickname exists
//var room_name = 'not_existing_room';  // room doesn't exist
var room_name = 'room1'; // room exists


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
            $('#chat').val($('#chat').val() + '<' + data.msg + '>\n');
            $('#chat').scrollTop($('#chat')[0].scrollHeight);
        });
        socket.on('message', function (data) {
            $('#chat').val($('#chat').val() + data.msg + '\n');
            $('#chat').scrollTop($('#chat')[0].scrollHeight);
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