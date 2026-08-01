# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

app_name = "Ziro.ai"
version = "2.0.0"
author = "Aref Daei"

# -----------------------------
# Data files
# -----------------------------
datas = []
datas += [("src/assets", "assets")]
datas += collect_data_files("whisper")

# -----------------------------
# Excludes
# -----------------------------
excludes = [
    "PySide6.Qt3DCore", "PySide6.Qt3DExtras",
    "PySide6.QtBluetooth", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtDesigner",
    "PySide6.QtHelp", "PySide6.QtLocation",
    "PySide6.QtNetworkAuth", "PySide6.QtPdf",
    "PySide6.QtPositioning", "PySide6.QtQml",
    "PySide6.QtQuick", "PySide6.QtQuickControls2",
    "PySide6.QtQuick3D", "PySide6.QtRemoteObjects",
    "PySide6.QtScxml", "PySide6.QtSensors",
    "PySide6.QtSerialBus", "PySide6.QtSerialPort",
    "PySide6.QtSql", "PySide6.QtTest",
    "PySide6.QtTextToSpeech", "PySide6.QtWebChannel",
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebSockets",
]

# -----------------------------
# Analysis
# -----------------------------
a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
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
    icon="src/assets/icons/Ziro.ico" if sys.platform == "win32" else "src/assets/icons/Ziro.png",
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
    icon="src/assets/icons/Ziro.icns",
    bundle_identifier="ir.ardastudio.ziro",
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
