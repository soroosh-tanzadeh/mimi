#!/usr/bin/env python3
"""
Test runner for MiMi agent.
"""
import sys
import subprocess
import os


def run_tests():
    """Run all tests for the MiMi agent."""
    print("Running tests for MiMi agent...")
    
    # Run tests using pytest
    try:
        # Run pytest with coverage
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        # Print output
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        # Return exit code
        return result.returncode
        
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest:")
        print("pip install pytest")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)