#!/usr/bin/env python
"""
Setup and compile translations for Flask-Babel
"""

import os
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
    result = os.system('pybabel extract -F babel.cfg -o translations/messages.pot .')
    if result != 0:
        print("⚠️ Warning: pybabel extract failed")
    else:
        print("✅ Messages extracted successfully")
    
    # Compile translations
    print("🔨 Compiling translations...")
    result = os.system('pybabel compile -d translations')
    if result != 0:
        print("⚠️ Warning: pybabel compile failed")
    else:
        print("✅ Translations compiled successfully!")
    
    print("🎉 Translation setup completed!")

if __name__ == '__main__':
    setup_translations()
