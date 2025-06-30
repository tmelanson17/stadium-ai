import asyncio
import cv2
import numpy as np
import os

from src.state_reader.state_reader import (
    PlayerID,
    StadiumMode,
    Rectangle,
    ImageUpdate,
    BattleState,
    UpdateQueue
)

async def main():
    queue = UpdateQueue()
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
    # assert state.p1_hp is not None, "P1 HP not updated."
    assert state.p1_condition is not None, "P1 Condition not updated."
    # assert state.p2_hp is not None, "P2 HP not updated."
    assert state.p2_condition is not None, "P1 Condition not updated."

    await queue.close()
    assert queue.queue.empty(), "Queue should be closed and empty"


if __name__ == "__main__":
    asyncio.run(main())