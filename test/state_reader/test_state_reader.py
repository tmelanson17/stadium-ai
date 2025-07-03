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

    queue = UpdateQueue(battle_state)
    STATUS_ROI = Rectangle(76, 230, 406, 296)  # Status condition area
    i=0
    for img_path in os.listdir(os.path.join("test", "data")):
        if not img_path.endswith(".png"):
            continue
        full_path = os.path.join("test", "data", img_path)
        print(f"Testing with image: {full_path}")
        image = cv2.imread(full_path)
        id = PlayerID.P1 if i % 2 == 0 else PlayerID.P2
        input_update_p1_hp = ImageUpdate(
            image=image,
            roi=STATUS_ROI,
            stadium_mode=StadiumMode.EXECUTE,
            player_id=id
        )
        i += 1
        await queue.put(input_update_p1_hp)

    print("All updates have been put into the queue.")
    state = await queue.get_state()
    assert isinstance(state, BattleState), "Expected BattleState instance"
    # Check that active pokemon is confused
    p1_mon = state.player_team.pk_list[state.player_active_mon]
    assert p1_mon.confused, "Player 1's active Pokemon should be confused"

    await queue.close()
    assert queue.queue.empty(), "Queue should be closed and empty"


if __name__ == "__main__":
    asyncio.run(main())