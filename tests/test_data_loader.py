"""
Tests for data_loader.py module.
"""

import os
import unittest
from unittest.mock import patch, mock_open, MagicMock
import json
import tempfile
from pathlib import Path

from db import load_json_data, import_categories, import_products, load_sample_data, DatabaseRegistry, Category, Product


class TestDataLoader(unittest.TestCase):
    """Test cases for the data loader module."""

    def setUp(self):
        """Set up for tests: Create mock database and session."""
        # Mock database setup
        self.patcher_session = patch('db.data_loader.DatabaseRegistry.session')
        self.mock_session = self.patcher_session.start()
        self.mock_query = self.mock_session.return_value.query
        
        # Default response: No existing data
        self.mock_query.return_value.count.return_value = 0
    
    def tearDown(self):
        """Clean up after tests."""
        self.patcher_session.stop()

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"test": "data"}]')
    def test_load_json_data_docker_path(self, mock_file, mock_exists):
        """Test loading JSON data from Docker path."""
        # Setup
        mock_exists.side_effect = lambda path: str(path).endswith("/code/data/test.json")
        
        # Execute
        data = load_json_data("test.json")
        
        # Assert
        mock_exists.assert_any_call(Path("/code/data/test.json"))
        mock_file.assert_called_once()
        self.assertEqual(data, [{"test": "data"}])

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='[{"test": "local_data"}]')
    def test_load_json_data_local_path(self, mock_file, mock_exists):
        """Test loading JSON data from local path."""
        # Setup
        mock_exists.side_effect = lambda path: not str(path).endswith("/code/data/test.json")
        
        # Execute
        data = load_json_data("test.json")
        
        # Assert
        mock_exists.assert_any_call(Path("/code/data/test.json"))
        mock_file.assert_called_once()
        self.assertEqual(data, [{"test": "local_data"}])

    @patch('os.path.exists')
    def test_load_json_data_file_not_found(self, mock_exists):
        """Test loading JSON data when file doesn't exist."""
        # Setup
        mock_exists.return_value = False
        
        # Execute
        data = load_json_data("nonexistent.json")
        
        # Assert
        self.assertEqual(data, [])

    @patch('db.data_loader.load_json_data')
    def test_import_categories_success(self, mock_load_json_data):
        """Test successful import of categories."""
        # Setup
        mock_categories_data = [
            {"id": 1, "name": "Category 1", "description": "Description 1"},
            {"id": 2, "name": "Category 2", "description": "Description 2"}
        ]
        mock_load_json_data.return_value = mock_categories_data
        
        # Execute
        import_categories()
        
        # Assert
        mock_load_json_data.assert_called_once_with("categories.json")
        mock_session = self.mock_session.return_value
        self.assertEqual(mock_session.add.call_count, 2)
        mock_session.commit.assert_called_once()

    def test_import_categories_skip_existing(self):
        """Test that category import is skipped when categories already exist."""
        # Setup
        self.mock_query.return_value.count.return_value = 5  # 5 existing categories
        
        # Execute
        import_categories()
        
        # Assert
        mock_session = self.mock_session.return_value
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch('db.data_loader.load_json_data')
    def test_import_products_success(self, mock_load_json_data):
        """Test successful import of products."""
        # Setup
        mock_products_data = [
            {"id": 1, "name": "Product 1", "description": "Description 1", "price": 10.0, "stock": 100, "category_id": 1},
            {"id": 2, "name": "Product 2", "description": "Description 2", "price": 20.0, "stock": 200, "category_id": 2}
        ]
        mock_load_json_data.return_value = mock_products_data
        
        # Execute
        import_products()
        
        # Assert
        mock_load_json_data.assert_called_once_with("products.json")
        mock_session = self.mock_session.return_value
        self.assertEqual(mock_session.add.call_count, 2)
        mock_session.commit.assert_called_once()

    def test_import_products_skip_existing(self):
        """Test that product import is skipped when products already exist."""
        # Setup
        self.mock_query.return_value.count.return_value = 10  # 10 existing products
        
        # Execute
        import_products()
        
        # Assert
        mock_session = self.mock_session.return_value
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    @patch('db.data_loader.import_categories')
    @patch('db.data_loader.import_products')
    def test_load_sample_data_success(self, mock_import_products, mock_import_categories):
        """Test successful load of all sample data."""
        # Execute
        load_sample_data()
        
        # Assert
        mock_import_categories.assert_called_once()
        mock_import_products.assert_called_once()

    @patch('db.data_loader.import_categories')
    @patch('db.data_loader.import_products')
    def test_load_sample_data_with_exception(self, mock_import_products, mock_import_categories):
        """Test load sample data when an exception occurs."""
        # Setup
        mock_import_categories.side_effect = Exception("Test error")
        
        # Execute
        load_sample_data()
        
        # Assert
        mock_import_categories.assert_called_once()
        mock_import_products.assert_not_called()  # Should not be called after exception


if __name__ == '__main__':
    unittest.main()
