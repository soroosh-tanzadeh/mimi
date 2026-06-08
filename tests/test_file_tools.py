import pytest
import os
import json
import tempfile
from tools.file_tools import read_file, list_files, write_to_file


class TestFileTools:
    """Test cases for file tools"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """Clean up test environment"""
        # Remove temporary directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_read_file_success(self):
        """Test successful file reading"""
        # Create a test file
        test_file = os.path.join(self.test_dir, "test.txt")
        test_content = "Hello, World!"
        
        with open(test_file, "w") as f:
            f.write(test_content)
            
        # Test reading the file
        result = read_file.func(test_file)
        assert result == test_content
        
    def test_read_file_not_found(self):
        """Test reading non-existent file"""
        non_existent_file = os.path.join(self.test_dir, "non_existent.txt")
        result = read_file.func(non_existent_file)
        assert "Error reading file" in result
        assert non_existent_file in result
        
    def test_list_files_success(self):
        """Test successful directory listing"""
        # Create some test files
        for i in range(3):
            with open(os.path.join(self.test_dir, f"file{i}.txt"), "w") as f:
                f.write(f"Content {i}")
                
        # Test listing files
        result = list_files.func(self.test_dir)
        result_dict = json.loads(result)
        
        assert result_dict["success"] == True
        assert result_dict["directory"] == self.test_dir
        assert len(result_dict["files"]) >= 3  # May include other files
        
    def test_list_files_not_found(self):
        """Test listing files in non-existent directory"""
        non_existent_dir = os.path.join(self.test_dir, "non_existent")
        result = list_files.func(non_existent_dir)
        result_dict = json.loads(result)
        
        assert result_dict["success"] == False
        assert non_existent_dir in result_dict["error"]
        
    def test_write_to_file_success(self):
        """Test successful file writing"""
        # Use a relative path for testing to avoid absolute path restrictions
        test_file = "output.txt"
        test_content = "Test content"
        
        # Test writing to file
        result = write_to_file.func(test_file, test_content)
        result_dict = json.loads(result)
        
        assert result_dict["success"] == True
        assert result_dict["filename"] == test_file
        
        # Verify file was created with correct content
        with open(test_file, "r") as f:
            assert f.read() == test_content
        
        # Clean up test file
        os.remove(test_file)
            
    def test_write_to_file_forbidden_path(self):
        """Test writing to forbidden path"""
        # Test with absolute path
        result = write_to_file.func("/forbidden.txt", "content")
        result_dict = json.loads(result)
        
        assert result_dict["success"] == False
        assert "Forbidden" in result_dict["error"]
        
        # Test with parent directory traversal
        result = write_to_file.func("../forbidden.txt", "content")
        result_dict = json.loads(result)
        
        assert result_dict["success"] == False
        assert "Forbidden" in result_dict["error"]
        
    def test_write_to_file_overwrite(self):
        """Test file overwriting"""
        test_file = "overwrite.txt"
        
        # Create initial file
        with open(test_file, "w") as f:
            f.write("Initial content")
            
        # Overwrite file
        new_content = "New content"
        result = write_to_file.func(test_file, new_content, overwrite=True)
        result_dict = json.loads(result)
        
        assert result_dict["success"] == True
        
        # Verify file was overwritten
        with open(test_file, "r") as f:
            assert f.read() == new_content
            
        # Clean up test file
        os.remove(test_file)


if __name__ == "__main__":
    pytest.main([__file__])
