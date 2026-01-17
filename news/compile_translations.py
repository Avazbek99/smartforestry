#!/usr/bin/env python
"""
Compile translations script for Flask-Babel
Run this script after adding new translations
"""

import os
import sys
from flask_babel import Babel

def compile_translations():
    """Compile translations using pybabel"""
    os.system('pybabel compile -d translations')
    print("✅ Translations compiled successfully!")

if __name__ == '__main__':
    compile_translations()
