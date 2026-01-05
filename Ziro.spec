# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

app_name = "Ziro"
version = "1.3.0-RC"
author = "Aref Daei"

# -----------------------------
# Data files
# -----------------------------
datas = []
datas += [("src/assets", "assets")]
datas += collect_data_files("whisper")

# -----------------------------
# Hidden imports
# -----------------------------
hiddenimports = []
hiddenimports += collect_submodules("customtkinter")

# -----------------------------
# Analysis
# -----------------------------
a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
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
# EXE (The Loader)
# -----------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="src/assets/Ziro.ico" if sys.platform == "win32" else "src/assets/Ziro.png",
)

# -----------------------------
# COLLECT (Folder Generation)
# -----------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

# -----------------------------
# BUNDLE (macOS App Bundle)
# -----------------------------
app = BUNDLE(
    coll,
    name=f"{app_name}.app",
    icon="src/assets/Ziro.icns",
    bundle_identifier="com.arefdaei.ziro",
    info_plist={
        "CFBundleName": app_name,
        "CFBundleDisplayName": app_name,
        "CFBundleShortVersionString": version,
        "CFBundleVersion": version,
        "NSHighResolutionCapable": "True",
        "NSAppTransportSecurity": {
            "NSAllowsArbitraryLoads": True
        },
    },
)
