$(document).ready(function () {
    const socket = io.connect('https://' + document.domain + ':' + location.port);

    const roomName = document.getElementById('game-name').innerHTML;

    socket.on('connect', function () {
        console.log('Webhook initiated');
        socket.emit('join', {'room': roomName});
    });

    socket.on('game_update', function (data) {
        console.log(data);

        update_team_information(data.game_state);

        data.game_state.tiles.forEach(function (item, index) {
            update_tile(item.word, item.hidden_value, item.guessed);
        });
    });

    socket.on('reload_page', function (data) {
        console.log(data);

        window.location.reload(true);
    });

    add_button_event_listeners(socket, roomName);
});

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {

    // Add event listener to new game button
    document.getElementById("new-game-button").addEventListener('click', (event) => {
        confirmAndStartNewGame(socket, roomName);
    });
}

function confirmAndStartNewGame(socket, roomName) {
    const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
    if (confirmation === true) {
        console.info("Starting new game...");
        socket.emit('new_game', {'room': roomName});
    }
}
