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

        // Ensure buttons and input are in the right state
        const guessButtonElement = document.getElementById("guessWordSubmit");
        if (guessButtonElement.hasAttribute("disabled")) {
            guessButtonElement.removeAttribute("disabled");
        }

        const guessWordInputElement = document.getElementById("guessWordInput");
        guessWordInputElement.value = "";
        guessWordInputElement.focus();

        const newGameButton = document.getElementById("new-game-button");
        newGameButton.style.display = "none";
        const disabledAttribute = document.createAttribute("disabled");
        newGameButton.setAttributeNode(disabledAttribute);
    });

    socket.on("game_over", function (data) {
        console.log(data);

        let totalScore = 0;

        data.scored_words.forEach(function (item, index) {
            const score = get_score_for_word(item);
            totalScore += score;

            const validGuessElement = document.getElementById(`valid-guess-${item}`);
            validGuessElement.innerHTML = `${item.toUpperCase()} +${score}`;
            validGuessElement.classList.add("scored-word");
        });

        data.unscored_words.forEach(function (item, index) {
            const validGuessElement = document.getElementById(`valid-guess-${item}`);
            validGuessElement.classList.add("unscored-word");
        });

        const scoreDiv = document.getElementById("score-div");
        scoreDiv.innerHTML = String(totalScore);
    });

    // Add event listeners to the buttons
    add_button_event_listeners(socket, roomName);

    // Update the remaining time counter each second
    window.setInterval(function () {
        // Don't waste calculations if the game is over
        if (expireTimeMillis == null) {
            return;
        }

        const now = new Date().getTime();
        const timeRemaining = expireTimeMillis - now;

        let minutesRemaining;
        let secondsRemaining;
        if (timeRemaining > 0) {
            minutesRemaining = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
            secondsRemaining = Math.floor((timeRemaining % (1000 * 60)) / 1000);
        } else {
            minutesRemaining = 0;
            secondsRemaining = 0;
            socket.emit('timer_expired', {'room': roomName});
            // Set variables to indicate game is over
            expireTimeMillis = null;
            end_game();
        }

        minutesRemaining = String(minutesRemaining).padStart(2, '0');
        secondsRemaining = String(secondsRemaining).padStart(2, '0');

        document.getElementById("time-remaining-div").innerHTML = `${minutesRemaining}:${secondsRemaining}`;
    }, 1000);
});

function get_score_for_word(word) {
    if(word.length <= 4) {
        return 1;
    } else if (word.length === 5) {
        return 2;
    } else if (word.length === 6) {
        return 3;
    } else if (word.length === 7) {
        return 5;
    } else if (word.length >= 8) {
        return 8;
    }
}

function end_game() {
    const guessButtonElement = document.getElementById("guessWordSubmit");
    const disabledAttribute = document.createAttribute("disabled");
    guessButtonElement.setAttributeNode(disabledAttribute);

    const newGameButton = document.getElementById("new-game-button");
    newGameButton.style.display = "";
    if (newGameButton.hasAttribute("disabled")) {
        newGameButton.removeAttribute("disabled");
    }
}

function add_valid_guess(valid_guess) {
    const paragraphNode = document.createElement("P");
    paragraphNode.id = `valid-guess-${valid_guess.toLowerCase()}`;
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
