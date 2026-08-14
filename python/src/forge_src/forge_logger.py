#!/usr/bin/env python3
"""Centralized logging for Explorer-d334"""

import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)

def log_info(message):
    """Log info message"""
    logging.info(message)

def log_error(message):
    """Log error message"""
    logging.error(message)

def log_warning(message):
    """Log warning message"""
    logging.warning(message)

def log_debug(message):
    """Log debug message"""
    logging.debug(message)
