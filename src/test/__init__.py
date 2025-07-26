"""
test

"""
# Import preliminary modules
import sys
import os

# Get the project root direcrtory
test_content_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add the project root to the system path if it's not already there
if test_content_dir not in sys.path:
    sys.path.insert(0, test_content_dir)