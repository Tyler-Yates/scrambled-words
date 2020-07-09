let expireTimeMillis = null;

$(document).ready(function () {
    const socket = io.connect('https://' + document.domain + ':' + location.port);

    const roomName = document.getElementById('game-name').innerHTML;

    socket.on('connect', function () {
        console.log('Webhook initiated');
        socket.emit('join', {'room': roomName});
    });

    socket.on('guess_reply', function (data) {
        console.log(data);

        if (data.valid) {
            add_valid_guess(data.guess);
        }
    });

    socket.on('reload_page', function (data) {
        console.log(data);

        window.location.reload(true);
    });

    socket.on("game_state", function (data) {
        console.log(data);

        // Update tiles
        data.tiles.forEach(function (item, index) {
            const tileElement = document.getElementById(`tile-${index}`);
            tileElement.innerHTML = item;
        });

        // Update countdown
        expireTimeMillis = data.expire_time;

        // Update player's list of valid guesses
        const validWordsDiv = document.getElementById("valid-words-div");
        validWordsDiv.innerHTML = "";
        data.player_guesses.forEach(function (item, index) {
            add_valid_guess(item);
        });
    });

    add_button_event_listeners(socket, roomName);

    window.setInterval(function () {

        if (expireTimeMillis == null) {
            return;
        }

        // Get today's date and time
        const now = new Date().getTime();

        // Find the distance between now and the count down date
        const timeRemaining = expireTimeMillis - now;

        let minutesRemaining;
        let secondsRemaining;
        if (timeRemaining > 0) {
            minutesRemaining = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            secondsRemaining = Math.floor((timeRemaining % (1000 * 60)) / 1000);
        } else {
            minutesRemaining = 0;
            secondsRemaining = 0;
        }

        minutesRemaining = String(minutesRemaining).padStart(2, '0');
        secondsRemaining = String(secondsRemaining).padStart(2, '0');

        // Display the result in the element with id="demo"
        document.getElementById("time-remaining-div").innerHTML = `${minutesRemaining}:${secondsRemaining}`;
    }, 1000);
});

function add_valid_guess(valid_guess) {
    const paragraphNode = document.createElement("P");
    const textNode = document.createTextNode(valid_guess.toUpperCase());
    paragraphNode.appendChild(textNode);
    document.getElementById("valid-words-div").appendChild(paragraphNode);
}

// Function that sets up the logic for emitting a socket message when clicking on a button.
function add_button_event_listeners(socket, roomName) {
    // Add event listener to guess buttons and input text box
    const guessWordSubmitElement = document.getElementById("guessWordSubmit");
    const guessWordInputElement = document.getElementById("guessWordInput");

    guessWordSubmitElement.addEventListener('click', (event) => {
        const guessWordInputElement = document.getElementById("guessWordInput");
        const guess = guessWordInputElement.value;
        socket.emit('guess', {'room': roomName, 'guess': guess});
        guessWordInputElement.value = "";
        guessWordInputElement.focus();
    });

    guessWordInputElement.addEventListener("keyup", event => {
        if (event.key === "Enter") {
            guessWordSubmitElement.click();
        }
    });

    // Add event listener to new game button
    document.getElementById("new-game-button").addEventListener('click', (event) => {
        confirmAndStartNewGame(socket, roomName);
    });

    // Give the input text box default focus once the page loads.
    guessWordInputElement.focus();
}

function confirmAndStartNewGame(socket, roomName) {
    const confirmation = confirm("Do you want to start a new game? The current board will be cleared.");
    if (confirmation === true) {
        console.info("Starting new game...");
        socket.emit('new_game', {'room': roomName});
    }
}
