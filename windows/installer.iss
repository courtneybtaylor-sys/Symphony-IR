; ============================================================
;  Symphony-IR — Inno Setup Installer Script
;  Compiler : Inno Setup 6.3+   (https://jrsoftware.org/isinfo.php)
;  Target   : Windows 10 / 11  — x64 only
;  Build    : Run windows/build.py first to produce dist\Symphony-IR.exe
; ============================================================

; --------------- Application constants ----------------------
#define MyAppName        "Symphony-IR"
#define MyAppVersion     "1.0.0"
#define MyAppPublisher   "Kheper LLC"
#define MyAppURL         "https://github.com/courtneybtaylor-sys/Symphony-IR"
#define MyAppSupportURL  "https://github.com/courtneybtaylor-sys/Symphony-IR/issues"
#define MyAppUpdatesURL  "https://github.com/courtneybtaylor-sys/Symphony-IR/releases"
#define MyAppExeName     "Symphony-IR.exe"
#define MyAppDescription "Deterministic Multi-Agent AI Orchestration Engine"

; Session-file association (.sir = Symphony-IR session)
#define MyAssocExt       ".sir"
#define MyAssocProgID    "SymphonyIR.SessionFile"
#define MyAssocName      "Symphony-IR Session"

; Source paths (relative to this .iss file — lives in windows/)
#define SrcRoot          ".."
#define SrcDist          "..\dist"
#define SrcExe           "..\dist\Symphony-IR.exe"

; ============================================================
[Setup]
; -------- Identity ------------------------------------------
AppId={{135D100C-6789-4A2B-99B7-B8FD51A80CD4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppSupportURL}
AppUpdatesURL={#MyAppUpdatesURL}
AppCopyright=Copyright (C) 2024 Kheper LLC

; -------- Installation paths --------------------------------
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}

; -------- Output --------------------------------------------
OutputDir={#SrcDist}\installer
OutputBaseFilename=Symphony-IR-{#MyAppVersion}-Setup

; -------- Wizard appearance ---------------------------------
; Modern style automatically respects Windows 10/11 dark mode.
WizardStyle=modern
WizardResizable=no
WizardSizePercent=115,115

; Branding images — place 164x314 px (banner) and 55x58 px (small) PNGs here.
; Inno Setup will fall back to its built-in images if these files are absent.
; WizardImageFile=wizard-banner.bmp
; WizardSmallImageFile=wizard-small.bmp

; -------- Platform ------------------------------------------
; Require 64-bit Windows 10 or later
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0

; -------- Privileges ----------------------------------------
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; -------- Features ------------------------------------------
ChangesAssociations=yes
ChangesEnvironment=yes
SolidCompression=yes
Compression=lzma2/ultra64

; -------- License -------------------------------------------
LicenseFile={#SrcRoot}\LICENSE.txt

; -------- Version stamping on the setup EXE ----------------
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright=Copyright (C) 2024 Kheper LLC

; ============================================================
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; ============================================================
[Messages]
; --- Wizard window title ---
SetupAppTitle=Symphony-IR Setup
SetupWindowTitle=Symphony-IR {#MyAppVersion} Setup

; --- Welcome page ---
WelcomeLabel1=Welcome to the[nl][nl]{#MyAppName} {#MyAppVersion} Setup Wizard
WelcomeLabel2=This wizard will guide you through installing [name/ver] on your computer.[nl][nl]Symphony-IR is a deterministic, multi-agent AI orchestration engine for Windows.[nl][nl]Click Next to continue, or Cancel to exit.

; --- Finish page ---
FinishHeadingLabel=Symphony-IR is ready.
FinishLabel=[name] has been installed successfully.[nl][nl]Click Finish to close this wizard.

; --- Buttons (these are always visible) ---
ButtonNext=Next  >
ButtonBack=<  Back
ButtonInstall=Install
ButtonFinish=Launch Symphony-IR
ButtonCancel=Cancel

; ============================================================
[CustomMessages]
; --- Task descriptions ---
TaskDesktopIcon=Create a &Desktop shortcut
TaskStartup=Launch Symphony-IR when Windows starts

; --- Ready-to-install summary ---
ReadyLabel1=Setup is ready to install {#MyAppName} {#MyAppVersion} on your computer.
ReadyLabel2a=Click Install to proceed, or click Back to review your selections.
ReadyLabel2b=Click Install to proceed.
ReadyMemoDir=Installation folder:
ReadyMemoType=Installation type:
ReadyMemoTasks=Additional tasks:

; --- Installing ---
InstallingLabel=Please wait while {#MyAppName} is being installed...

; ============================================================
[Tasks]
Name: "desktopicon"; \
  Description: "{cm:TaskDesktopIcon}"; \
  GroupDescription: "{cm:AdditionalIcons}"; \
  Flags: unchecked

; ============================================================
[Files]
; -------- Main application ---------------------------------
; Build with:  python windows/build.py
; Then compile this script with Inno Setup.
Source: "{#SrcExe}"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

; -------- Documentation ------------------------------------
Source: "{#SrcRoot}\README.md"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

Source: "{#SrcRoot}\LICENSE.txt"; \
  DestDir: "{app}"; \
  Flags: ignoreversion

Source: "{#SrcRoot}\docs\*"; \
  DestDir: "{app}\docs"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

; -------- Orchestrator config templates --------------------
Source: "{#SrcRoot}\ai-orchestrator\config\*"; \
  DestDir: "{app}\config"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

; -------- Symphony Flow templates --------------------------
Source: "{#SrcRoot}\ai-orchestrator\flow\templates\*"; \
  DestDir: "{app}\templates\flow"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

; ============================================================
[Icons]
; Start Menu shortcut
Name: "{autoprograms}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  Comment: "{#MyAppDescription}"

; Desktop shortcut (optional task)
Name: "{autodesktop}\{#MyAppName}"; \
  Filename: "{app}\{#MyAppExeName}"; \
  Comment: "{#MyAppDescription}"; \
  Tasks: desktopicon

; Uninstall shortcut in Start Menu
Name: "{autoprograms}\{#MyAppName}\Uninstall {#MyAppName}"; \
  Filename: "{uninstallexe}"

; ============================================================
[Registry]
; -------- .sir file-type association -----------------------
; Register extension
Root: HKA; \
  Subkey: "Software\Classes\{#MyAssocExt}\OpenWithProgids"; \
  ValueType: string; ValueName: "{#MyAssocProgID}"; ValueData: ""; \
  Flags: uninsdeletevalue

; ProgID
Root: HKA; \
  Subkey: "Software\Classes\{#MyAssocProgID}"; \
  ValueType: string; ValueName: ""; ValueData: "{#MyAssocName}"; \
  Flags: uninsdeletekey

Root: HKA; \
  Subkey: "Software\Classes\{#MyAssocProgID}\DefaultIcon"; \
  ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"

Root: HKA; \
  Subkey: "Software\Classes\{#MyAssocProgID}\shell\open\command"; \
  ValueType: string; ValueName: ""; \
  ValueData: """{app}\{#MyAppExeName}"" ""%1"""

; -------- Add install dir to user PATH ---------------------
Root: HKA; \
  Subkey: "Environment"; \
  ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}"; \
  Check: NeedsAddPath('{app}'); \
  Flags: preservestringtype

; -------- Add to Windows Apps & Features ------------------
Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{135D100C-6789-4A2B-99B7-B8FD51A80CD4}_is1"; \
  ValueType: string; ValueName: "DisplayIcon"; \
  ValueData: "{app}\{#MyAppExeName}"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{135D100C-6789-4A2B-99B7-B8FD51A80CD4}_is1"; \
  ValueType: string; ValueName: "HelpLink"; \
  ValueData: "{#MyAppSupportURL}"

Root: HKLM; \
  Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{135D100C-6789-4A2B-99B7-B8FD51A80CD4}_is1"; \
  ValueType: string; ValueName: "URLUpdateInfo"; \
  ValueData: "{#MyAppUpdatesURL}"

; ============================================================
[Run]
; Launch after install — optional, shown on Finish page
Filename: "{app}\{#MyAppExeName}"; \
  Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; \
  Flags: nowait postinstall skipifsilent

; ============================================================
[UninstallRun]
; Remove any .orchestrator working directory on silent uninstall
; (per-user data preserved unless user opts in via Add/Remove Programs)

; ============================================================
[Code]
(* =========================================================
   Helper: Check whether a directory is already in PATH.
   Used by the [Registry] PATH entry above.
   ========================================================= *)
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(
    HKA,
    'Environment',
    'Path',
    OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Uppercase(Param) + ';',
                ';' + Uppercase(OrigPath) + ';') = 0;
end;

(* =========================================================
   Windows 10 / 11 dark-mode awareness.

   Inno Setup 6.3+ already renders the installer UI respecting
   the system theme via the modern WizardStyle.  The code below
   additionally sets the DWMWA_USE_IMMERSIVE_DARK_MODE attribute
   on the wizard window so the title-bar chrome also flips dark.
   This is purely cosmetic and fails silently on older Windows.
   ========================================================= *)
const
  DWMWA_USE_IMMERSIVE_DARK_MODE = 20;

procedure ApplyDarkTitleBar(Handle: HWND);
var
  DarkMode: DWORD;
begin
  DarkMode := 1;
  DwmSetWindowAttribute(Handle, DWMWA_USE_IMMERSIVE_DARK_MODE,
                         DarkMode, SizeOf(DarkMode));
end;

procedure InitializeWizard();
begin
  { Apply dark title bar if the user's system is in dark mode }
  try
    ApplyDarkTitleBar(WizardForm.Handle);
  except
    { Silently ignore — not all Windows versions support this API }
  end;
end;

(* =========================================================
   Pre-install check: warn if the machine is not 64-bit
   (should never trigger because of ArchitecturesAllowed, but
   kept here as a belt-and-suspenders guard).
   ========================================================= *)
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not Is64BitInstallMode then begin
    MsgBox(
      'Symphony-IR requires a 64-bit version of Windows 10 or later.'#13#10 +
      'Setup will now exit.',
      mbError, MB_OK);
    Result := False;
  end;
end;

(* =========================================================
   Post-install: create the per-user .orchestrator working
   directory so the first launch does not need to init.
   ========================================================= *)
procedure CurStepChanged(CurStep: TSetupStep);
var
  OrchestratorDir: string;
begin
  if CurStep = ssPostInstall then begin
    OrchestratorDir := ExpandConstant('{localappdata}\Symphony-IR\.orchestrator');
    if not DirExists(OrchestratorDir) then
      ForceDirectories(OrchestratorDir);
  end;
end;
