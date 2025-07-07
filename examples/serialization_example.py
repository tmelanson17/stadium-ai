"""
Example usage of ImageUpdate serialization methods.

This demonstrates how to use the ImageUpdateSerializer to convert
ImageUpdate objects to/from JSON format for storage or transmission.
"""

import json
import numpy as np
from src.utils.serialization import ImageUpdateSerializer, serialize_image_update, deserialize_image_update
from src.state.pokestate_defs import ImageUpdate, Rectangle, MessageType, PlayerID
from src.utils.shared_image_list import SharedImageList


def example_usage():
    """
    Example demonstrating ImageUpdate serialization/deserialization.
    """
    
    # Create a sample ImageUpdate
    sample_image = np.random.randint(0, 255, (100, 150, 3), dtype=np.uint8)
    sample_roi = Rectangle(x1=10, y1=20, x2=110, y2=170)
    
    image_update = ImageUpdate(
        image=sample_image,
        roi=sample_roi,
        message_type=MessageType.HP,
        player_id=PlayerID.P1
    )
    
    print("Original ImageUpdate:")
    print(f"  Image shape: {image_update.image.shape}")
    print(f"  ROI: {image_update.roi}")
    print(f"  Message type: {image_update.message_type}")
    print(f"  Player ID: {image_update.player_id}")
    
    # Method 1: Using convenience functions
    print("\n=== Using convenience functions ===")
    
    # Serialize to dictionary
    serialized_dict = serialize_image_update(image_update)
    print(f"Serialized dict: {serialized_dict}")
    
    # Convert to JSON string
    json_string = json.dumps(serialized_dict, indent=2)
    print(f"JSON string:\n{json_string}")
    
    # Deserialize back to ImageUpdate
    deserialized_update = deserialize_image_update(serialized_dict)
    print(f"\nDeserialized ImageUpdate:")
    print(f"  Image shape: {deserialized_update.image.shape}")
    print(f"  ROI: {deserialized_update.roi}")
    print(f"  Message type: {deserialized_update.message_type}")
    print(f"  Player ID: {deserialized_update.player_id}")
    
    # Method 2: Using the serializer class with SharedImageList
    print("\n=== Using serializer class ===")
    
    # Create a mock config for SharedImageList (this would normally come from your system)
    mock_config = {
        'name': 'test_shared_memory',
        'n_shmem_frames': '10',
        'height': '480',
        'width': '640', 
        'channel': '3',
        'dtype': 'uint8'
    }
    
    try:
        # Try to create SharedImageList (may fail if shared memory doesn't exist)
        shared_image_list = SharedImageList(mock_config, create=False)
        
        # Create serializer with SharedImageList
        serializer = ImageUpdateSerializer(shared_image_list)
        
        # Serialize
        serialized_with_shm = serializer.to_dict(image_update, store_image=True)
        print(f"Serialized with SharedImageList: {serialized_with_shm}")
        
        # Deserialize
        deserialized_with_shm = serializer.from_dict(serialized_with_shm)
        print(f"Deserialized with SharedImageList:")
        print(f"  Image shape: {deserialized_with_shm.image.shape}")
        print(f"  ROI: {deserialized_with_shm.roi}")
        
    except (ValueError, FileNotFoundError) as e:
        print(f"SharedImageList not available: {e}")
        print("This is expected if shared memory is not set up.")
    
    # Method 3: Batch processing multiple ImageUpdates
    print("\n=== Batch processing ===")
    
    # Create multiple ImageUpdates
    image_updates = []
    for i in range(3):
        img = np.random.randint(0, 255, (50, 75, 3), dtype=np.uint8)
        roi = Rectangle(x1=i*10, y1=i*10, x2=i*10+50, y2=i*10+75)
        message_type = MessageType.HP if i % 2 == 0 else MessageType.CONDITION
        player_id = PlayerID.P1 if i % 2 == 0 else PlayerID.P2
        
        image_updates.append(ImageUpdate(
            image=img,
            roi=roi,
            message_type=message_type,
            player_id=player_id
        ))
    
    # Serialize all updates
    serializer = ImageUpdateSerializer()
    serialized_batch = [serializer.to_dict(update, store_image=False) for update in image_updates]
    
    print(f"Serialized {len(serialized_batch)} ImageUpdates")
    
    # Convert to JSON
    batch_json = json.dumps(serialized_batch, indent=2)
    print(f"Batch JSON (first 200 chars): {batch_json[:200]}...")
    
    # Deserialize all updates
    deserialized_batch = [serializer.from_dict(data) for data in serialized_batch]
    print(f"Deserialized {len(deserialized_batch)} ImageUpdates")
    
    # Verify data integrity
    for i, (original, deserialized) in enumerate(zip(image_updates, deserialized_batch)):
        assert original.roi.x1 == deserialized.roi.x1, f"ROI mismatch at index {i}"
        assert original.message_type == deserialized.message_type, f"Message type mismatch at index {i}"
        assert original.player_id == deserialized.player_id, f"Player ID mismatch at index {i}"
        print(f"  Update {i}: Data integrity verified ✓")


if __name__ == "__main__":
    example_usage()
