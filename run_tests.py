#!/usr/bin/env python
"""
Test runner script for AI-Med-Agent framework
"""

import sys
import os
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Discover and run tests
if __name__ == '__main__':
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
