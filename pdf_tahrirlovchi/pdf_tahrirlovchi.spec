# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for PDF Tahrirlovchi application."""

import os
import sys
from PyInstaller.utils.hooks import collect_all, collect_data_files, copy_metadata

block_cipher = None

# Collect streamlit data
streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all('streamlit')
streamlit_meta = copy_metadata('streamlit')

# Collect PyMuPDF data
fitz_datas, fitz_binaries, fitz_hiddenimports = collect_all('fitz')

# Collect python-docx data
docx_datas, docx_binaries, docx_hiddenimports = collect_all('docx')

all_datas = streamlit_datas + streamlit_meta + fitz_datas + docx_datas
all_binaries = streamlit_binaries + fitz_binaries + docx_binaries
all_hiddenimports = streamlit_hiddenimports + fitz_hiddenimports + docx_hiddenimports + [
    'streamlit',
    'streamlit.runtime',
    'streamlit.runtime.scriptrunner',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.web',
    'streamlit.web.server',
    'streamlit.web.server.server',
    'fitz',
    'pymupdf',
    'docx',
    'docx.shared',
    'docx.oxml',
    'docx.oxml.ns',
]

# Add source files as data
all_datas += [
    ('app.py', '.'),
    ('pdf_engine.py', '.'),
    ('exporters.py', '.'),
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PDF_Tahrirlovchi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PDF_Tahrirlovchi',
)
