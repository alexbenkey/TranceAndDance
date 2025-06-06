import json
import random
import math
import asyncio
from channels.layers import get_channel_layer
import msgspec

class TournamentLogic:
    def __init__(self, mode):
        self.mode = mode
        self.num_players = int(mode)
        self.players = []  # player IDs and usernames -> list of dict, check line 22 to see the format
        self.matches = []  # ongoing matches
        self.bracket = {}
        self.current_round = 1
        self.running = False
        self.winners = []  # players who won their matches
        self.final_winner = None

    def add_player(self, player_id, username):
        if len(self.players) < self.num_players:
            self.players.append({"id": player_id, "username": username})
            print(f"Player {username} joined the tournament. Total players: {len(self.players)}", flush=True)
        else:
            print(f"Tournament is full. Player {username} cannot join.", flush=True)

    async def start_tournament(self):
        if len(self.players) != self.num_players:
            print("Not enough players to start the tournament.", flush=True)
            return

        self.running = True
        self._create_bracket()
        await self.cache_update()
        await self._start_next_round()

    async def cache_update(self):
        channel_layer = get_channel_layer()
        state = self.get_tournament_state()
        serialized = msgspec.json.encode(state).decode("utf-8")
        await channel_layer.group_send(
            "tournament_lobby",
            {
                "type": "force.cache.update",
                "state": serialized,

            }
        )
        await asyncio.sleep(5)

    def _create_bracket(self):
        if self.current_round not in self.bracket:
            self.bracket[self.current_round] = []

        self.bracket[self.current_round] = [
            ({"player": self.players[i], "winner": False}, 
            {"player": self.players[i + 1], "winner": False}) 
            for i in range(0, len(self.players), 2)
        ]

        print(f"tournament bracket created: {self.bracket}", flush=True)

    async def _start_next_round(self):
        print(f"NEW ROUND IN START NEXT ROUND", flush=True)
        if self.final_winner:
            print(f"tournament already ended. Winner: {self.final_winner}", flush=True)
            return

        self.matches = []
        self.winners = []
        channel_layer = get_channel_layer()

        for player1, player2 in self.bracket[self.current_round]:
            match_exists = any(match["player1"] == player1["player"]["id"] and match["player2"] == player2["player"]["id"] for match in self.matches)
            
            if not match_exists:
                await channel_layer.group_send(
                    "tournament_lobby",
                    {
                        "type": "create.game.tournament",
                        "player1": player1["player"]["id"],
                        "player2": player2["player"]["id"],
                    }
                )
                print(f"Sent create.game.tournament message for {player1['player']['username']} vs {player2['player']['username']}", flush=True)

        print(f"Round {self.current_round} started.", flush=True)
        asyncio.create_task(self._round_timeout_handler(self.current_round, timeout_seconds=300))  # 5 min timeout

    async def register_match_result(self, game_id, winner_username):
        print(f"Registering match result: Game {game_id}, Winner {winner_username}", flush=True)
        
        if not any(m[0] == game_id for m in self.matches):
            print(f"Game {game_id} already processed or not in active matches list.")
            return

        match_indices = [i for i, (g_id, p1, p2) in enumerate(self.matches) if g_id == game_id]
        if not match_indices:
            print(f"Game {game_id} not found in matches", flush=True)
            return
        
        match_index = match_indices[0]
        game_id, player1, player2 = self.matches[match_index]
        
        winner_player = next((player for player in self.players if player["username"] == winner_username), None)
        if not winner_player:
            print(f"Player {winner_username} not found in players list", flush=True)
            return
        if not any(winner["id"] == winner_player["id"] and winner["username"] == winner_player["username"] 
                for winner in self.winners):
            self.winners.append(winner_player)
            print(f"✅ Added {winner_username} to winners list", flush=True)
        else:
            print(f"Player {winner_username} already in winners list", flush=True)
        
        # update bool with the winner of the match
        if self.current_round in self.bracket:
            bracket_updated = False
            for i, match in enumerate(self.bracket[self.current_round]):
                match = list(match)
                if (match[0]["player"]["username"] == player1 and match[1]["player"]["username"] == player2) or \
                (match[0]["player"]["username"] == player2 and match[1]["player"]["username"] == player1):
                    match[0]["winner"] = (match[0]["player"]["username"] == winner_username)
                    match[1]["winner"] = (match[1]["player"]["username"] == winner_username)
                    self.bracket[self.current_round][i] = tuple(match)
                    bracket_updated = True
                    print(f"Updated bracket for round {self.current_round}, match between {player1} and {player2}", flush=True)
                    break
            
            if not bracket_updated:
                print(f"Could not find match in bracket for {player1} vs {player2}", flush=True)
        
        # rm previous matches 
        self.matches = [(g_id, p1, p2) for g_id, p1, p2 in self.matches if g_id != game_id]
         
        if len(self.matches) == 0:
            await self._advance_to_next_round()

    async def _advance_to_next_round(self):
        print(f"WINNERS BEFORE ADVANCE: {self.winners}", flush=True)

        # share with frontend 
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "tournament_lobby",
            {
                "type": "tournament.winners",
                "winners": self.winners,
                "round": self.current_round
            }
        )

        if len(self.winners) == 1:
            self.final_winner = self.winners[0]
            self.running = False
            print(f"Tournament ended. Winner: {self.final_winner['username']}", flush=True)
            return

        if len(self.matches) == 0 and len(self.winners) >= 2:
            self.current_round += 1
            self.bracket[self.current_round] = []
            round_participants = self.winners.copy()

            while len(round_participants) >= 2:
                player1 = round_participants.pop(0)
                player2 = round_participants.pop(0)
                
                self.bracket[self.current_round].append(
                    ({"player": player1, "winner": False}, {"player": player2, "winner": False})
                )
            
            print(f"Round {self.current_round} created with {len(self.bracket[self.current_round])} matches.", flush=True)
            await self._start_next_round()

    async def _round_timeout_handler(self, round_number, timeout_seconds):
        await asyncio.sleep(timeout_seconds)
        if self.current_round == round_number and self.running:
            print(f"⚠️ Round {round_number} timeout reached.", flush=True)
            if self.matches:
                print(f"Unresolved matches: {self.matches}", flush=True)
                self.running = False
                channel_layer = get_channel_layer()
                await channel_layer.group_send(
                    "tournament_lobby",
                    {
                        "type": "tournament.timeout",
                        "round": round_number,
                        "unresolved_matches": self.matches
                    }
                )

    def get_tournament_state(self):
        return {
            "mode": self.mode,
            "num_players": self.num_players,
            "players": self.players,
            "bracket": self.bracket,
            "current_round": self.current_round,
            "tournament_active": self.running,
            "running": self.running,
            "final_winner": self.final_winner,
            "matches": self.matches,
            "winners": self.winners,
            "players_in": len(self.players),
            "remaining_spots": self.num_players - len(self.players),
        }

    def set_tournament_state(self, state: dict):
        if "mode" in state:
            self.mode = state["mode"]
        if "num_players" in state:
            self.num_players = state["num_players"]
        if "players" in state:
            self.players = state["players"]
        if "bracket" in state:
            self.bracket = state["bracket"]
        if "current_round" in state:
            self.current_round = state["current_round"]
        if "running" in state:
            self.running = state["running"]
        if "tournament_active" in state:
            self.running = state["tournament_active"]
        if "final_winner" in state:
            self.final_winner = state["final_winner"]
        if "matches" in state:
            self.matches = state["matches"]
        if "winners" in state:
            self.winners = state["winners"]
