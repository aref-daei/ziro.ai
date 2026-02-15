[Setup]
AppName=Ziro
AppVersion=1.4.1
AppVerName=Ziro 1.4.1
AppPublisher=Aref Daei
AppPublisherURL=https://github.com/aref-daei/ziro.ai
AppSupportURL=https://github.com/aref-daei/ziro.ai/issues
AppUpdatesURL=https://github.com/aref-daei/ziro.ai/releases
AppCopyright=Copyright (C) 2025-2026  Aref Daei - AGPL-3.0

VersionInfoVersion=1.4.1.0
VersionInfoCompany=Aref Daei
VersionInfoDescription=Automated Subtitle Generation Application
VersionInfoCopyright=Copyright (C) 2025-2026  Aref Daei - AGPL-3.0

DefaultDirName={commonpf}\Ziro
DefaultGroupName=Ziro
SetupIconFile=src\assets\Ziro.ico
UninstallDisplayIcon={app}\Ziro.exe
LicenseFile=LICENSE

Compression=lzma2/ultra64
LZMAUseSeparateProcess=yes
InternalCompressLevel=ultra
SolidCompression=yes

ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

OutputBaseFilename=ZiroSetup-x64-1.4.1
OutputDir=Releases
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

CloseApplications=yes

[Files]
Source: "dist\Ziro\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Ziro"; Filename: "{app}\Ziro.exe"
Name: "{commondesktop}\Ziro"; Filename: "{app}\Ziro.exe"

[Run]
Filename: "{app}\Ziro.exe"; Description: "Launch Ziro"; Flags: nowait postinstall skipifsilent
