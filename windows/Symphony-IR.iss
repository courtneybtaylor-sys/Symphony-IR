; Symphony-IR Windows Installer Script
; Created with Inno Setup
; 
; This script builds a professional Windows installer for Symphony-IR
; It requires:
;   1. PyInstaller executable already built (dist/Symphony-IR.exe)
;   2. Inno Setup 6.0+ installed
;
; Usage:
;   1. Build executable: python windows/build_pyinstaller.py
;   2. Run this script with Inno Setup
;   3. Installer will be created in Output\ folder
;

#define MyAppName "Symphony-IR"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Symphony-IR Contributors"
#define MyAppURL "https://github.com/courtneybtaylor-sys/Symphony-IR"
#define MyAppExeName "Symphony-IR.exe"
#define MyAppSourceDir "dist"
#define MyAppOutputDir "installer_output"

[Setup]
; Application metadata
AppId={{3E4A5E7F-8B9D-4C2E-A1B6-7D8E9F0A1B2C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Installer UI
AllowNoIcons=yes
AllowRootDirectory=no
Compression=lzma
SolidCompression=yes
WizardStyle=modern
WizardSizePercent=100
VersionInfoVersion={#MyAppVersion}

; Windows compatibility
MinVersion=10.0.14393
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64

; Output configuration
OutputDir={#MyAppOutputDir}
OutputBaseFilename=Symphony-IR-Setup-{#MyAppVersion}-x64
SetupIconFile=windows\symphony_icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}

; User interface
ShowLanguageDialog=no
PrivilegesRequired=none
ChangesAssociations=no
DisableProgramGroupPage=no

; Startup
UsePreviousAppDir=yes
UsePreviousTasks=yes
UsePreviousSetupType=no
AllowUNCPath=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Main executable and data
Source: "{#MyAppSourceDir}\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSourceDir}\README.txt"; DestDir: "{app}"; Flags: isreadme
Source: "{#MyAppSourceDir}\run.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSourceDir}\SHORTCUTS.txt"; DestDir: "{app}"; Flags: ignoreversion

; Documentation
Source: "{#MyAppSourceDir}\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#MyAppSourceDir}\ai-orchestrator\*"; DestDir: "{app}\ai-orchestrator"; Flags: ignoreversion recursesubdirs createallsubdirs

; GUI assets (if any)
Source: "{#MyAppSourceDir}\gui\*"; DestDir: "{app}\gui"; Flags: ignoreversion recursesubdirs createallsubdirs

; All other required files from dist
Source: "{#MyAppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "*.pyc,__pycache__"

[Icons]
; Start Menu icon
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFileName: "{app}\{#MyAppExeName}"; Comment: "Deterministic Multi-Agent Orchestration Engine"

; Additional Start Menu items
Name: "{group}\Documentation"; Filename: "{app}\README.txt"
Name: "{group}\{cm:ProgramOnTheWeb,{#MyAppName}}"; Filename: "{#MyAppURL}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop icon
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFileName: "{app}\{#MyAppExeName}"; Tasks: desktopicon; Comment: "Deterministic Multi-Agent Orchestration Engine"

; Quick Launch icon (Windows XP/7/8 only)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; Comment: "Deterministic Multi-Agent Orchestration Engine"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Remove cached files on uninstall
Type: dirifempty; Name: "{app}"
Type: files; Name: "{userappdata}\Symphony-IR\*"

[Code]
{ Custom code for enhanced installation experience }

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    { Optional: Add Symphony-IR to Windows PATH }
    { This allows running 'Symphony-IR' from command line }
    { Uncomment to enable }
    {
    RegWriteStringValue(HKEY_CURRENT_USER,
      'Environment', 'Path',
      GetEnv('Path') + ';' + ExpandConstant('{app}'));
    }
  end;
end;

procedure DeinitializeSetup();
begin
  { Show completion message }
  if not Canceled then
  begin
    MsgBox('Symphony-IR has been successfully installed.' + #13 +
           'Launch from Start Menu or Desktop shortcut.' + #13 +
           'Go to Settings tab to configure your AI provider.', mbInformation, MB_OK);
  end;
end;

{ Verify system requirements }
function CheckSystemRequirements(): Boolean;
begin
  Result := True;
  
  { Windows version check }
  if CompareVersions(GetWindowsVersionString(), '10.0.14393') < 0 then
  begin
    MsgBox('Windows 10 or later is required.', mbError, MB_OK);
    Result := False;
  end;
  
  { Additional checks can be added here }
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  
  if CurPageID = wpSelectDir then
  begin
    if not CheckSystemRequirements() then
      Result := False;
  end;
end;

{ Preserve user configuration on upgrade }
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    { Optional: Ask user if they want to keep their configuration }
    { Uncomment to enable }
    {
    if MsgBox('Keep Symphony-IR configuration files?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      DelTree(ExpandConstant('{userappdata}\Symphony-IR'), True, True, True);
    end;
    }
  end;
end;
