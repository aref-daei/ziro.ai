[Setup]
AppName=Ziro.ai
AppId={{B30C851B-3D88-477D-AED9-9D5476BB7051}}
AppVersion=2.0.0
AppVerName=Ziro.ai 2.0.0
AppPublisher=Aref Daei
AppPublisherURL=https://github.com/aref-daei/ziro.ai
AppSupportURL=https://github.com/aref-daei/ziro.ai/issues
AppUpdatesURL=https://github.com/aref-daei/ziro.ai/releases
AppCopyright=Copyright (C) 2025-2026  Aref Daei - AGPL-3.0

VersionInfoVersion=2.0.0.0
VersionInfoCompany=Aref Daei
VersionInfoDescription=AI-Powered Video Transcription, Translation & Subtitle Generation
VersionInfoCopyright=Copyright (C) 2025-2026  Aref Daei - AGPL-3.0

DefaultDirName={commonpf}\Ziro.ai
DefaultGroupName=Ziro.ai
SetupIconFile=src\assets\icons\Ziro.ico
UninstallDisplayIcon={app}\Ziro.ai.exe
LicenseFile=LICENSE

Compression=lzma2/ultra64
LZMAUseSeparateProcess=yes
InternalCompressLevel=ultra
SolidCompression=yes

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputBaseFilename=ZiroSetup-x64-2.0.0
OutputDir=Releases
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

CloseApplications=yes

[Files]
Source: "dist\Ziro.ai\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Ziro.ai"; Filename: "{app}\Ziro.ai.exe"
Name: "{commondesktop}\Ziro.ai"; Filename: "{app}\Ziro.ai.exe"

[Run]
Filename: "{app}\Ziro.ai.exe"; Description: "Launch Ziro.ai"; Flags: nowait postinstall skipifsilent
