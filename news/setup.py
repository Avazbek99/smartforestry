#!/usr/bin/env python
"""
Setup script for Flask-Babel translations
"""

import os
import subprocess
import sys

def setup_translations():
    """Setup and compile translations"""
    print("🔧 Setting up translations...")
    
    # Create translations directory if not exists
    if not os.path.exists('translations'):
        os.makedirs('translations')
        print("✅ Created translations directory")
    
    # Extract messages from templates
    print("📝 Extracting messages from templates...")
    os.system('pybabel extract -F babel.cfg -o translations/messages.pot .')
    
    # Compile translations
    print("🔨 Compiling translations...")
    os.system('pybabel compile -d translations')
    
    print("✅ Translations setup completed!")

if __name__ == '__main__':
    setup_translations()
