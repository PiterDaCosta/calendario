#!/usr/bin/env python3
"""
Task Calendar Application
Run this file to start the development server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # Run in debug mode for development
    app.run(debug=True, host='0.0.0.0', port=5000)
