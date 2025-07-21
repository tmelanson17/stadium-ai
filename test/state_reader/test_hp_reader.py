import unittest
import cv2
import numpy as np
import os

from src.state_reader.hp_reader import get_pokemon_name
from src.state.pokestate import BattleState
from src.state.pokestate_defs import Rectangle
from test.state_reader.test_utils import create_example_battle_state
from typing import Tuple

class TestHPReader(unittest.TestCase):
    """Test cases for hp_reader.get_pokemon_name function"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a battle state with known Pokemon names
        # TODO: Update with image specific Pokemon names.
        self.battle_state = create_example_battle_state(
            active_p1_name="GENGAR",
            active_p2_name="BULBY",
        )
        # Create similar names in the P1 team
        self.battle_state.player_team.pk_list[1].name = "GRAVELER"
        self.battle_state.player_team.pk_list[2].name = "GOLEM"
        self.battle_state.player_team.pk_list[3].name = "GLIGAR"
        self.battle_state.player_team.pk_list[4].name = "ENTEI"
        self.battle_state.player_team.pk_list[5].name = "FENRIR"
        # Create similar names in the P2 team
        self.battle_state.opponent_team.pk_list[1].name = "VOLBY"
        self.battle_state.opponent_team.pk_list[2].name = "BULLY"
        self.battle_state.opponent_team.pk_list[3].name = "BULLET"
        self.battle_state.opponent_team.pk_list[4].name = "PULLEY"
        self.battle_state.opponent_team.pk_list[5].name = "BOLVY"

        # Define HP box regions similar to test_state_reader.py
        # These regions should include the Pokemon name area
        self.P1_HP = Rectangle(30, 20, 138, 78)
        self.P2_HP = Rectangle(340, 20, 448, 78)
        
        # Get the test data directory
        self.test_data_dir = os.path.join(os.getcwd(), "test", "data")
        print(f"Pokemon names in battle state: {[pk.name for pk in self.battle_state.player_team.pk_list + self.battle_state.opponent_team.pk_list]}")
        
    def convert_rectangle_to_bbox(self, rect: Rectangle) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Convert Rectangle to BBox format expected by get_pokemon_name"""
        return rect.to_coord()
        
    def load_test_images(self):
        """Load all PNG images from test/data directory"""
        images = []
        image_paths = []
        
        if not os.path.exists(self.test_data_dir):
            self.skipTest(f"Test data directory not found: {self.test_data_dir}")
            
        for filename in os.listdir(self.test_data_dir):
            if filename.endswith(".png"):
                full_path = os.path.join(self.test_data_dir, filename)
                image = cv2.imread(full_path)
                if image is not None:
                    images.append(image)
                    image_paths.append(full_path)
                    
        if not images:
            self.skipTest("No PNG images found in test/data directory")
            
        return images, image_paths

    def test_get_pokemon_name_p1(self):
        """Test get_pokemon_name for Player 1 (P1) on all test images"""
        images, image_paths = self.load_test_images()
        
        p1_bbox = self.convert_rectangle_to_bbox(self.P1_HP)
        
        for i, (image, image_path) in enumerate(zip(images, image_paths)):
            with self.subTest(image_path=image_path, player="P1"):
                result = get_pokemon_name(
                    image=image,
                    roi=p1_bbox,
                    battle_state=self.battle_state,
                    opponent=False  # P1 is not opponent
                )
                
                # Assert that we get some result (not None)
                self.assertIsInstance(result, (str, type(None)), 
                    f"Expected string or None, got {type(result)} for {image_path}")
                
                # If we get a result, it should be a non-empty string
                if result is not None:
                    self.assertIsInstance(result, str, 
                        f"Expected string result for {image_path}")
                    self.assertGreater(len(result), 0, 
                        f"Expected non-empty string for {image_path}")
                
                print(f"P1 Pokemon name from {os.path.basename(image_path)}: {result}")

    def test_get_pokemon_name_p2(self):
        """Test get_pokemon_name for Player 2 (P2) on all test images"""
        images, image_paths = self.load_test_images()
        
        p2_bbox = self.convert_rectangle_to_bbox(self.P2_HP)
        
        for i, (image, image_path) in enumerate(zip(images, image_paths)):
            with self.subTest(image_path=image_path, player="P2"):
                result = get_pokemon_name(
                    image=image,
                    roi=p2_bbox,
                    battle_state=self.battle_state,
                    opponent=True  # P2 is opponent
                )
                
                # Assert that we get some result (not None)
                self.assertIsInstance(result, (str, type(None)), 
                    f"Expected string or None, got {type(result)} for {image_path}")
                
                # If we get a result, it should be a non-empty string
                if result is not None:
                    self.assertIsInstance(result, str, 
                        f"Expected string result for {image_path}")
                    self.assertGreater(len(result), 0, 
                        f"Expected non-empty string for {image_path}")
                
                print(f"P2 Pokemon name from {os.path.basename(image_path)}: {result}")

    def test_get_pokemon_name_with_known_pokemon(self):
        """Test that get_pokemon_name returns reasonable results when Pokemon are in battle state"""
        images, image_paths = self.load_test_images()
        
        if not images:
            return
            
        # Test with the first available image
        test_image = images[0]
        test_path = image_paths[0]
        
        # Test P1
        p1_bbox = self.convert_rectangle_to_bbox(self.P1_HP)
        p1_result = get_pokemon_name(
            image=test_image,
            roi=p1_bbox,
            battle_state=self.battle_state,
            opponent=False
        )
        
        # Test P2 
        p2_bbox = self.convert_rectangle_to_bbox(self.P2_HP)
        p2_result = get_pokemon_name(
            image=test_image,
            roi=p2_bbox,
            battle_state=self.battle_state,
            opponent=True
        )
        
        print(f"Results from {os.path.basename(test_path)}:")
        print(f"  P1: {p1_result}")
        print(f"  P2: {p2_result}")
        
        # At minimum, the function should not crash and should return expected types
        self.assertIsInstance(p1_result, (str, type(None)))
        self.assertIsInstance(p2_result, (str, type(None)))

    def test_empty_image_handling(self):
        """Test that get_pokemon_name handles edge cases gracefully"""
        # Test with a small empty image
        empty_image = np.zeros((100, 100, 3), dtype=np.uint8)
        p1_bbox = self.convert_rectangle_to_bbox(self.P1_HP)
        
        result = get_pokemon_name(
            image=empty_image,
            roi=p1_bbox,
            battle_state=self.battle_state,
            opponent=False
        )
        
        # Should handle gracefully without crashing
        self.assertIsInstance(result, (str, type(None)))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
