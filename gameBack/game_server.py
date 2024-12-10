# # to check

# import asyncio
# import json
# from game_logic import Game

# connected_clients = set()
# game = Game()

# async def handle_client(websocket):
#     connected_clients.add(websocket)
#     try:
#         async for message in websocket:
#             data = json.loads(message)
#             if data['action'] == 'move':
#                 direction = data['direction']
#                 game.update_paddle("player", direction)
#     finally:
#         connected_clients.remove(websocket)

# async def game_loop():
#     while True:
#         game.update_ball()
#         state = game.get_state()
#         if connected_clients:
#             await asyncio.wait([client.send(json.dumps(state)) for client in connected_clients])
#         await asyncio.sleep(1 / 60)  # 60 FPS

# async def main():
#     async with websockets.serve(handle_client, "localhost", 8000):
#         await game_loop()




import asyncio
import json
import websockets
from game_logic import Game

# Dictionary to keep track of active games (keyed by game_id)
games = {}
players = {}

async def handle_connection(websocket, path):
    try:
        # Assign a unique player ID
        player_id = id(websocket)
        players[player_id] = websocket
        print(f"Player {player_id} connected.")

        async for message in websocket:
            data = json.loads(message)
            action = data.get("action")
            game_id = data.get("game_id")

            if action == "start":
                # Create a new game instance
                mode = data.get("mode")
                game_id = f"game_{player_id}"  # Example game ID
                games[game_id] = Game(mode)
                await websocket.send(json.dumps({"type": "started", "game_id": game_id}))

            elif action == "move":
                direction = data["data"]["direction"]
                if game_id in games:
                    game = games[game_id]
                    game.move_player(player_id, direction)
                    # Update all connected players
                    await broadcast_game_state(game_id)

            elif action == "disconnect":
                del players[player_id]
                await websocket.close()

    except websockets.exceptions.ConnectionClosed:
        print(f"Player {player_id} disconnected.")
        if player_id in players:
            del players[player_id]

async def broadcast_game_state(game_id):
    if game_id in games:
        game_state = games[game_id].get_state()
        message = json.dumps({"type": "update", "data": game_state})
        # Broadcast state to all players in the game
        for player in players.values():
            await player.send(message)

start_server = websockets.serve(handle_connection, "0.0.0.0", 8765)

if __name__ == "__main__":
    print("Game server running on ws://0.0.0.0:8765")
    asyncio.run(start_server)
