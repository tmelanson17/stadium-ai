import json
import requests

from typing import Dict, Any

from src.rabbitmq.receive import listen
from src.rabbitmq.topics import BATTLE_STATE_UPDATE, CONTROLLER_EXCHANGE


url = "http://100.69.80.141:11434/api/generate"

def summarize_battle_state(state):
    """Convert the battle state dict into a compact readable summary string."""
    """
    Example battle state string:
    Your active Pokémon: NIDOKING (Poison/Ground) HP:45% Moves: Earthquake, Horn Drill, Rage, Substitute
    Opponent’s active Pokémon: SEADRA (Water) HP:100% Moves: Surf, Toxic, Smokescreen, Swift
    Your bench:
    1. ALAKAZAM (Psychic) HP:100% Moves: Psybeam, Disable, Tri Attack
    2. KADABRA (Psychic) HP:100% Moves: Psychic, Counter, Recover, Dig
    3. EEVEE (Normal) HP:100% Moves: Body Slam, Swift, Sand-attack, Toxic
    4. GRIMER (Poison) HP:100% Moves: Sludge, Body Slam, Explosion, Screech
    5. VENUSAUR (Grass/Poison) HP:100% Moves: Leech Seed, Poisonpowder, Solarbeam, Take Down
    Opponent’s revealed bench:
    - DODRIO (Normal/Flying) HP:133 charging Moves: Fly, Tri Attack, Agility, Reflect
    - DRATINI (Dragon) HP:120 Moves: Hyper Beam, Body Slam, Thunderbolt, Thunder Wave
    """

    def mon_summary(mon):
        if not mon["in_play"]:
            return None
        status = []
        if mon["status"] != 0:
            status.append(f"status={mon['status']}")
        if mon["confused"]:
            status.append("confused")
        if mon["sleep_turns"] > 0:
            status.append(f"sleep({mon['sleep_turns']})")
        if mon["two_turn_move"]:
            status.append("charging")

        hp = f"{mon['hp']}%"
        moves = []
        for i in range(1, 5):
            move = mon.get(f"move{i}")
            if move and move["known"]:
                moves.append(move["name"])
        return f"{mon['name']} ({mon['type1']}{'/' + mon['type2'] if mon['type2'] else ''}) HP:{hp} " \
               f"{' '.join(status) if status else ''} Moves: {', '.join(moves)}"

    # Player team summary
    player_active_idx = state["player_active_mon"]
    player_team = state["player_team"]["pk_list"]
    player_active = mon_summary(player_team[player_active_idx])

    # Opponent team summary
    opponent_active_idx = state["opponent_active_mon"]
    opponent_team = state["opponent_team"]["pk_list"]
    opponent_active = mon_summary(opponent_team[opponent_active_idx])

    summary_lines = []
    summary_lines.append(f"Your active Pokémon: {player_active}")
    summary_lines.append(f"Opponent’s active Pokémon: {opponent_active}")
    summary_lines.append("Your bench:")
    for i, mon in enumerate(player_team):
        if i != player_active_idx:
            bench_line = mon_summary(mon)
            if bench_line:
                summary_lines.append(f"  {i+1}. {bench_line}")

    summary_lines.append("Opponent’s revealed bench:")
    for i, mon in enumerate(opponent_team):
        if i != opponent_active_idx and i in state["opponent_team"]["in_play"]:
            bench_line = mon_summary(mon)
            if bench_line:
                summary_lines.append(f"  - {bench_line}")

    return "\n".join(summary_lines)

def feed_battle_state_to_llm(battle_state: Dict[str, Any]) -> None:
    battle_state_string = summarize_battle_state(battle_state)
    prompt = f"""
    You are an expert Pokémon Stadium battle strategist. You have the option of choosing an attacking move or switching to a different Pokémon on your bench.

    Here is the current battle summary:
    {battle_state_string}

    Please output the best move for Player 1 in the format:
    "use [1-4]" or "switch [1-5]".
    where the number index for use is the index of the move in the active Pokémon's move list, and the number index for switch is the index of the Pokémon in the bench.
    """

    payload = {
            "model": "qwen3:4b",
            "prompt": prompt,
            "stream": False
    }

    headers = {}

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code != 200:
            raise Exception(f"Request failed with status code {res.status_code}: {res.text}")

    think_start = "\u003cthink\u003e"
    think_end = "\u003c/think\u003e"

    response = json.loads(res.text)["response"]
    # Find the start and end of the thought process
    think_delim = response.find(think_start)
    if think_delim != -1:
        think_delim_end = response.find(think_end, think_delim)
        if think_delim_end != -1:
            # Extract the thought process
            thought_process = response[think_delim + len(think_start):think_delim_end]
            print("Thought Process:", thought_process)

            short_answer = response[think_delim_end + len(think_end):].strip()
        else:
            raise ValueError("End of thought process not found.")
    else:
        print("No thought process found.")
        short_answer = response
    print(short_answer)


if __name__ == "__main__":
        listener = listen(CONTROLLER_EXCHANGE, {
            BATTLE_STATE_UPDATE: feed_battle_state_to_llm
        })