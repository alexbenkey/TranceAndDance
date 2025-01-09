//import { handleServerMessage } from "./statics/script.js";

//const serverUrl = "ws://localhost:8000/ws/game_server/";
//const serverUrl = "ws://localhost/ws/game_server/";
const wsUrl = `ws://${window.location.host}/ws/game_server/`;

//const serverUrl = `ws://${window.location.host}/ws/game_server/`;

let socket;

function connectWebSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
        console.log("WebSocket already connected.");
        return;
    }

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("Connected to the game server.");
        //initializeGame(); // Perform any necessary setup
        if (gameState) {
            socket.send(JSON.stringify({action: "start", mode: gameState.mode}));
        }
    };

    socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        handleServerMessage(message);
    };

    socket.onclose = () => {
        console.log("Disconnected from the game server.");
        alert("Connection to the game server lost.");
    };

    socket.onerror = (error) => {
        console.error("WebSocket error:", error);
        alert(`WebSocket error: ${error.message}`);  // More detailed error message
    };
}

function sendPlayerAction(action, data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ action, data }));
    } else {
        console.warn("WebSocket is not open. Unable to send data.");
    }
}

function handleServerMessage(message) {
    switch (message.type) {
        case "update":
            updateGameState(message.data);
            break;
        case "end":
            alert(`Game Over: ${message.reason}`);
            break;
        default:
            console.warn("Unknown message type received:", message.type);
    }
}

//export { connectWebSocket, sendPlayerAction };