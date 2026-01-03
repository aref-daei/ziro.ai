# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules
from src.core.config import PROJECT_NAME, PROJECT_VERSION, PROJECT_AUTHOR, PROJECT_ICON

block_cipher = None

app_name = PROJECT_NAME
version = PROJECT_VERSION
author = PROJECT_AUTHOR
icon_file = str(PROJECT_ICON)

# -----------------------------
# Hidden imports (CustomTkinter)
# -----------------------------
hiddenimports = collect_submodules("customtkinter")

# -----------------------------
# Analysis
# -----------------------------
a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    datas=[
        ("src/assets", "assets"),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# -----------------------------
# PYZ
# -----------------------------
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# -----------------------------
# EXE (Windows / Linux)
# -----------------------------
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI-only
    icon=icon_file,
)

# -----------------------------
# macOS App Bundle
# -----------------------------
app = BUNDLE(
    exe,
    name=f"{app_name}.app",
    icon=icon_file,
    bundle_identifier="com.arefdaei.ziro",
    info_plist={
        "CFBundleName": app_name,
        "CFBundleDisplayName": app_name,
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "NSHighResolutionCapable": True,
        "NSAppTransportSecurity": {
            "NSAllowsArbitraryLoads": True
        },
    },
)

# -----------------------------
# COLLECT (onedir)
# -----------------------------
coll = COLLECT(
    exe if sys.platform != "darwin" else app,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
