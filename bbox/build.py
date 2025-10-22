#!/usr/bin/env python3
"""Build script for BBox executable"""

import PyInstaller.__main__
import os
import platform

# Determine separator based on OS
separator = ';' if platform.system() == 'Windows' else ':'

# Build command
args = [
    'bbox.py',
    '--onefile',
    '--name=bbox',
    f'--add-data=config.yaml{separator}.',
    '--hidden-import=pypdf',
    '--hidden-import=reportlab',
    '--hidden-import=yaml',
    '--hidden-import=fitz',
    '--console',
]

# Add icon if it exists
if os.path.exists('bbox.ico'):
    args.append('--icon=bbox.ico')

# Run PyInstaller
PyInstaller.__main__.run(args)