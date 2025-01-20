import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from game_server.game_logic import Game

games = {}  # active games by game_id -- laura might need??
players = {}  # active players by player_id -- laura??

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.player_id = self.channel_name
        players[self.player_id] = self
        print(f"Player {self.player_id} connected.")
        
        game_id = f"game_{self.player_id}"
        if game_id in games:
            game = games[game_id]
            if not game.running:
                game.reset_game("One Player")  # Ensure 'mode' is defined
        else:
            # Create a new game for this player
            game = Game("One Player")  # Default mode
            games[game_id] = game

        if self.player_id not in game.players:
            game.add_player(self.player_id)

        #self.scope["player_id"] = self.player_id # is this still needed??
        await self.accept()  # accept socket connection

    async def disconnect(self, close_code):
        print(f"Player {self.player_id} disconnected.")
        if self.player_id in players:
            del players[self.player_id]
        
        # Remove the player from any active games
        for game_id, game in games.items():
            if self.player_id in game.players:
                game.remove_player(self.player_id)
                if not game.players:
                    game.stop_game("No players")
                    del games[game_id]
        await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        game_id = data.get("game_id")
        #player_id = self.player_id

        if action == "reset":
            mode = data.get("mode")
            if game_id in games:
                games[game_id].reset_game(mode)
                await self.send(json.dumps({
                    "type": "reset",
                    "data": games[game_id].get_state(),
                }))
            else:
                await self.send(json.dumps({
                    "type": "error",
                    "message": "Game ID not found for reset.",
                }))
        
        elif action == "start":
            mode = data.get("mode")
            game_id = f"game_{self.player_id}"
            if game_id in games:
                game = games[game_id]
                game.start_game()  # Start the game, if not already started
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": game_id,
                }))
                asyncio.create_task(self.broadcast_game_state(game_id))  # Broadcast only after starting
            else:
                games[game_id] = Game(mode)
                await self.send(text_data=json.dumps({
                    "type": "started",
                    "game_id": game_id,
                }))

        elif action == "move":
            direction = data.get("direction")  # Get direction directly from the message
            print(f"Data: {data}")
            print(f"player_id: {self.player_id}")
            if not direction or not game_id in games:
                print(f"Invalid move action: Missing 'direction' or 'game_id'. Data: {data}")
                return
            if game_id in games:
                game = games[game_id]
                if self.player_id in game.players:
                    print(f"player_id: {self.player_id} SENDING TO MOVE_PLAYER")
                    game.move_player(self.player_id, direction)
                    await self.broadcast_game_state(game_id)
            else:
                print(f"Game {game_id} not found.")

        elif action == "stop":
            if game_id in games:
                del games[game_id]
                await self.broadcast_game_state(game_id)
                await self.send(text_data=json.dumps({
                    "type": "end",
                    "reason": "Game stopped by player.",  # change this to something dynamic to see who won
                }))

        elif action == "disconnect":
            del players[self.player_id]
            await self.close()
            print(f"WebSocket disconnected: {close_code}")
            await self.channel_layer.group_discard(
                "game_group",
                self.channel_name
            )

    async def broadcast_game_state(self, game_id):
        if game_id in games:
            game = games[game_id]
            while game.running:
                game.update_state()
                game_state = game.get_state()
                message = json.dumps({"type": "update", "data": game_state})
                
                if not game.running:
                    winner = "Player" if game.score["player"] >= 10 else "Opponent"
                    message = json.dumps({"type": "end", "reason": f"Game Over: {winner} wins"})
                    break
                    # socket.close() ???
                
                send_operations = [
                    player.send(text_data=message)
                    for player_id, player in players.items()
                    if player_id in game.players
                ]
                await asyncio.gather(*send_operations)
                await asyncio.sleep(0.05)  # Adjust frequency as needed
