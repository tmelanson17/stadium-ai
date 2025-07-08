"""
ImageUpdate Serialization Module

This module provides serialization/deserialization functionality for ImageUpdate objects
used in the Pokemon Stadium AI system. The main purpose is to convert ImageUpdate
instances to/from JSON-compatible dictionaries for storage, transmission, or caching.

Key Features:
- Converts numpy image arrays to indices for use with SharedImageList
- Preserves all ImageUpdate metadata (ROI, message type, player ID)
- Supports both convenience functions and class-based approach
- Handles cases where SharedImageList is not available

Usage:
    # Quick serialization
    data = serialize_image_update(image_update, shared_image_list)
    restored = deserialize_image_update(data, shared_image_list)
    
    # Advanced usage with persistent serializer
    serializer = ImageUpdateSerializer(shared_image_list)
    data = serializer.to_dict(image_update)
    restored = serializer.from_dict(data)

Example:
    See examples/serialization_example.py for detailed usage examples.
"""

from typing import Dict, Optional
import numpy as np

from ..state.pokestate_defs import ImageUpdate, Rectangle, MessageType, PlayerID
from .shared_image_list import SharedImageList


class ImageUpdateSerializer:
    """
    Serializes ImageUpdate objects to/from JSON format.
    The image is converted to an index for use with SharedImageList.
    """
    def __init__(self, shared_image_list: SharedImageList):
        """
        Initialize the serializer with a SharedImageList instance.
        
        Args:
            shared_image_list: SharedImageList instance for image storage/retrieval
        """
        self.shared_image_list = shared_image_list
    
    def to_dict(self, image_update: ImageUpdate) -> Dict[str, str]:
        """
        Convert ImageUpdate to JSON-serializable dictionary.
        
        Args:
            image_update: ImageUpdate instance to serialize
            store_image: Whether to store the image in SharedImageList (if available)
                        If False, only returns the current image index counter
        
        Returns:
            Dictionary containing serialized ImageUpdate data
        """
        image_index = None
        
        if self.shared_image_list is not None:
            # Store image in SharedImageList and get index
            frame = self.shared_image_list.get_new_frame()
            frame[:] = image_update.image
            image_index = self.shared_image_list.current_index
        else:
            # If no SharedImageList is available, we'll store minimal image metadata
            image_index = -1  # Indicates image is not stored in shared memory
        
        return {
            "image_index": str(image_index),
            "image_dtype": str(image_update.image.dtype) if image_update.image is not None else "",
            "x1": str(image_update.roi.x1),
            "y1": str(image_update.roi.y1),
            "x2": str(image_update.roi.x2),
            "y2": str(image_update.roi.y2),
            "message_type": str(image_update.message_type.value),
            "player_id": str(image_update.player_id.value)
        }
    
    def from_dict(self, data: Dict[str, str]) -> ImageUpdate:
        """
        Convert dictionary back to ImageUpdate instance.
        
        Args:
            data: Dictionary containing serialized ImageUpdate data
            
        Returns:
            ImageUpdate instance with image retrieved from SharedImageList
            
        Raises:
            ValueError: If SharedImageList is not available or image index is invalid
        """
        image_index = int(data["image_index"])
        
        # Retrieve image from SharedImageList
        try:
            image = self.shared_image_list.at(image_index)
        except (IndexError, ValueError) as e:
            raise ValueError(f"Failed to retrieve image at index {image_index}: {e}")
        
        # Reconstruct Rectangle
        roi = Rectangle(
            x1=int(data["x1"]),
            y1=int(data["y1"]),
            x2=int(data["x2"]),
            y2=int(data["y2"])
        )
        
        # Reconstruct enums
        message_type = MessageType(int(data["message_type"]))
        player_id = PlayerID(int(data["player_id"]))
        
        return ImageUpdate(
            image=image,
            roi=roi,
            message_type=message_type,
            player_id=player_id
        )
    
    def set_shared_image_list(self, shared_image_list: SharedImageList):
        """
        Set or update the SharedImageList instance.
        
        Args:
            shared_image_list: SharedImageList instance for image storage/retrieval
        """
        self.shared_image_list = shared_image_list


def serialize_image_update(image_update: ImageUpdate, shared_image_list: SharedImageList) -> Dict[str, str]:
    """
    Convenience function to serialize an ImageUpdate to a dictionary.
    
    Args:
        image_update: ImageUpdate instance to serialize
        shared_image_list: Optional SharedImageList for image storage
        
    Returns:
        Dictionary containing serialized ImageUpdate data
    """
    serializer = ImageUpdateSerializer(shared_image_list)
    return serializer.to_dict(image_update)


def deserialize_image_update(data: Dict[str, str], shared_image_list: SharedImageList) -> ImageUpdate:
    """
    Convenience function to deserialize a dictionary to an ImageUpdate.
    
    Args:
        data: Dictionary containing serialized ImageUpdate data
        shared_image_list: Optional SharedImageList for image retrieval
        
    Returns:
        ImageUpdate instance
    """
    serializer = ImageUpdateSerializer(shared_image_list)
    return serializer.from_dict(data)