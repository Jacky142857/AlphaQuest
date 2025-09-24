#!/usr/bin/env python
"""
Render deployment startup script for Django AlphaQuest backend.
This script ensures the Django server binds to the correct host and port for Render.
"""
import os
import sys
from django.core.management import execute_from_command_line

def main():
    """Start Django server with Render-compatible settings."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_signals.settings')

    # Get port from environment variable (Render sets this)
    port = os.environ.get('PORT', '10000')

    # Prepare Django runserver command with correct host and port
    # Render requires binding to 0.0.0.0
    sys.argv = [
        'start.py',
        'runserver',
        f'0.0.0.0:{port}'
    ]

    try:
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__ == '__main__':
    main()