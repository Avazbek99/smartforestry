#!/usr/bin/env python
"""
Simple compilation script for Flask-Babel translations
"""

import os
import subprocess

def compile_translations():
    """Compile translations using pybabel"""
    print("🔨 Compiling translations...")
    
    # Compile translations
    result = subprocess.run([
        'pybabel', 'compile', '-d', 'translations'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Translations compiled successfully!")
        print(result.stdout)
    else:
        print("❌ Compilation failed:")
        print(result.stderr)
    
    return result.returncode == 0

if __name__ == '__main__':
    compile_translations()
