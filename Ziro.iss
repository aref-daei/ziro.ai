[Setup]
AppName=Ziro
AppVersion=1.2.0
AppPublisher=Aref Daei
DefaultDirName={autopf}\Ziro
DefaultGroupName=Ziro
SetupIconFile=src\assets\Ziro.ico
UninstallDisplayIcon={app}\Ziro.exe
LicenseFile=LICENSE
Compression=lzma2/ultra64
LZMAUseSeparateProcess=yes
LZMADictionarySize=65536
LZMANumFastBytes=273
LZMANumBlockThreads=2
InternalCompressLevel=ultra
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64compatible
OutputBaseFilename=ZiroSetup
OutputDir=Releases
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Files]
Source: "dist\Ziro\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Ziro"; Filename: "{app}\Ziro.exe"
Name: "{commondesktop}\Ziro"; Filename: "{app}\Ziro.exe"

[Run]
Filename: "{app}\Ziro.exe"; Description: "Launch Ziro"; Flags: nowait postinstall skipifsilent
