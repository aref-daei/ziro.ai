# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

app_name = "Ziro"
version = "1.2.0"
author = "Aref Daei"

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
    icon="src/assets/Ziro.ico" if sys.platform == "win32" else "src/assets/Ziro.png",
)

# -----------------------------
# macOS App Bundle
# -----------------------------
app = BUNDLE(
    exe,
    name=f"{app_name}.app",
    icon="src/assets/Ziro.icns",
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
