[Setup]
AppName=Ziro
AppVersion=1.2.0
AppPublisher=Aref Daei

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

OutputBaseFilename=ZiroSetup
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
