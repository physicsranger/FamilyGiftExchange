#!/usr/bin/env python

#using script example from pyinstaller website
import PyInstaller.__main__

PyInstaller.__main__.run([
    'FamilyGiftExchange.py',
    '--onefile',
    '--windowed'])