import asyncio
import cv2
import numpy as np
import os

from src.state_reader.state_reader import (
    PlayerID,
    StadiumMode,
    Rectangle,
    ImageUpdate,
    UpdateQueue
)
from src.state.pokestate import (
    BattleState
)
from test.state_reader.test_utils import create_example_battle_state

async def main():
    battle_state = create_example_battle_state(active_p1_name="BULBY")
    battle_state.player_team.pk_list[battle_state.player_active_mon].confused = False
    battle_state.player_team.pk_list[battle_state.player_active_mon].hp = 100
    battle_state.opponent_team.pk_list[battle_state.opponent_active_mon].hp = 100

    queue = UpdateQueue(battle_state)
    STATUS_ROI = Rectangle(76, 230, 406, 296)  # Status condition area
    P1_HP = Rectangle(30, 20, 138, 78)
    P2_HP = Rectangle(340, 20, 448, 78)
    i=0
    for img_path in os.listdir(os.path.join("test", "data")):
        if not img_path.endswith(".png"):
            continue
        full_path = os.path.join("test", "data", img_path)
        print(f"Testing with image: {full_path}")
        image = cv2.imread(full_path)
        id = PlayerID.P1 if i % 2 == 0 else PlayerID.P2
        input_update_condition = ImageUpdate(
            image=image,
            roi=STATUS_ROI,
            stadium_mode=StadiumMode.EXECUTE,
            player_id=id
        )
        await queue.put(input_update_condition)
        input_update_health = ImageUpdate(
            image=image,
            roi=P1_HP if id == PlayerID.P1 else P2_HP,
            stadium_mode=StadiumMode.CHOOSE_MOVE,
            player_id=id
        )
        await queue.put(input_update_health)
        i += 1

    print("All updates have been put into the queue.")
    state = await queue.get_state()
    assert isinstance(state, BattleState), "Expected BattleState instance"
    # Check that active pokemon is confused
    # TODO: Make a utility function for getting the active mon
    p1_mon = state.player_team.pk_list[state.player_active_mon]
    p2_mon = state.opponent_team.pk_list[state.opponent_active_mon]
    assert p1_mon.confused, "Player 1's active Pokemon should be confused"
    print("New HP: ")
    print(f"P1: {p1_mon.hp}")
    print(f"P2: {p2_mon.hp}")
    assert p1_mon.hp != 100, "Health was not updated"
    

    await queue.close()
    assert queue.queue.empty(), "Queue should be closed and empty"


if __name__ == "__main__":
    asyncio.run(main())