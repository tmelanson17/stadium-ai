import unittest
from src.utils.box_average_filter import BoxAverageFilter
from src.state.pokestate_defs import Rectangle


class TestBoxAverageFilter(unittest.TestCase):
    
    def test_first_five_entries_not_outliers(self):
        """Test that the first 5 entries aren't considered outliers"""
        # Create filter with window size of 6
        filter = BoxAverageFilter(window_size=6)
        
        # Add 5 different rectangles
        rectangles = [
            Rectangle(10, 20, 30, 40),
            Rectangle(12, 22, 32, 42),
            Rectangle(8, 18, 28, 38),
            Rectangle(11, 21, 31, 41),
            Rectangle(9, 19, 29, 39)
        ]
        
        # Test that each rectangle is not considered an outlier as it's added
        for i, rect in enumerate(rectangles):
            filter.add(rect)
            # Should not be outlier since we don't have enough data points yet
            # or we just reached the window size
            self.assertFalse(filter.is_outlier(rect), 
                           f"Rectangle {i+1} should not be considered an outlier")
    
    def test_outlier_detection_with_specific_average(self):
        """Test outlier detection when average bounding box is (1,2,3,4)"""
        # Create filter with window size of 5
        filter = BoxAverageFilter(window_size=5)
        
        # Add 5 rectangles that will average to (1,2,3,4)
        # Average: x1=1, y1=2, x2=3, y2=4
        rectangles = [
            Rectangle(1, 2, 3, 4),  # Exact average
            Rectangle(1, 2, 3, 4),  # Exact average
            Rectangle(1, 2, 3, 4),  # Exact average
            Rectangle(1, 2, 3, 4),  # Exact average
            Rectangle(1, 2, 3, 4)   # Exact average
        ]
        
        for rect in rectangles:
            filter.add(rect)
        
        # Verify the average is indeed (1,2,3,4)
        avg = filter.get_average()
        self.assertEqual(avg.x1, 1)
        self.assertEqual(avg.y1, 2)
        self.assertEqual(avg.x2, 3)
        self.assertEqual(avg.y2, 4)
        
        # Test the outlier case: (3,2,3,4)
        # This has x1=3 which differs from average x1=1 by 2
        # Width = avg.x2 - avg.x1 = 3 - 1 = 2
        # Difference / width = 2 / 2 = 1.0 which > 0.5 threshold
        outlier_rect = Rectangle(3, 2, 3, 4)
        self.assertTrue(filter.is_outlier(outlier_rect), 
                       "Rectangle (3,2,3,4) should be considered an outlier when average is (1,2,3,4)")
    
    def test_outlier_detection_with_threshold(self):
        """Test outlier detection with custom threshold"""
        filter = BoxAverageFilter(window_size=3)
        
        # Add rectangles to establish a baseline
        base_rect = Rectangle(10, 10, 20, 20)  # Width=10, Height=10
        for _ in range(3):
            filter.add(base_rect)
        
        # Test with default threshold (0.5)
        # A rectangle that differs by MORE than 50% of width/height should be an outlier
        outlier_rect = Rectangle(16, 10, 20, 20)  # x1 differs by 6, which is > 50% of width (10)
        self.assertTrue(filter.is_outlier(outlier_rect))
        
        # Test with higher threshold (0.6)
        # Same rectangle should not be an outlier with higher threshold
        self.assertFalse(filter.is_outlier(outlier_rect, threshold=0.7))
    
    def test_not_outlier_when_within_threshold(self):
        """Test that rectangles within threshold are not considered outliers"""
        filter = BoxAverageFilter(window_size=3)
        
        # Establish baseline
        rectangles = [
            Rectangle(10, 10, 20, 20),
            Rectangle(9, 11, 21, 19),
            Rectangle(11, 9, 19, 21)
        ]
        
        for rect in rectangles:
            filter.add(rect)
        
        # Test rectangle that's close to average (should not be outlier)
        close_rect = Rectangle(10, 10, 21, 20)  # Only x2 differs by 1, well within threshold
        self.assertFalse(filter.is_outlier(close_rect))
    
    def test_empty_filter_no_outliers(self):
        """Test that empty filter doesn't consider anything an outlier"""
        filter = BoxAverageFilter(window_size=5)
        
        test_rect = Rectangle(100, 200, 300, 400)
        self.assertFalse(filter.is_outlier(test_rect))
    
    def test_insufficient_data_no_outliers(self):
        """Test that filter with insufficient data doesn't consider anything an outlier"""
        filter = BoxAverageFilter(window_size=5)
        
        # Add only 3 rectangles (less than window size)
        for i in range(3):
            filter.add(Rectangle(i, i, i+10, i+10))
        
        test_rect = Rectangle(1000, 1000, 2000, 2000)
        self.assertFalse(filter.is_outlier(test_rect))


if __name__ == '__main__':
    unittest.main()