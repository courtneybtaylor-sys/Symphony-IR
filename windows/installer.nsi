; Symphony-IR Windows Installer
; Built with NSIS (Nullsoft Scriptable Install System)
; Download NSIS from https://nsis.sourceforge.io/

!include "MUI2.nsh"

; Application information
!define APPNAME "Symphony-IR"
!define APPVERSION "1.0.0"
!define APPURL "https://github.com/courtneybtaylor-sys/Symphony-IR"
!define APPEXE "Symphony-IR.exe"

; Installer configuration
Name "${APPNAME} ${APPVERSION}"
OutFile "dist/Symphony-IR-${APPVERSION}-Installer.exe"
InstallDir "$PROGRAMFILES\${APPNAME}"
InstallDirRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation"

; Request admin rights
RequestExecutionLevel admin

; UI Settings
!insertmacro MUI2_PAGE_WELCOME
!insertmacro MUI2_PAGE_DIRECTORY
!insertmacro MUI2_PAGE_INSTFILES
!insertmacro MUI2_PAGE_FINISH
!insertmacro MUI2_LANGUAGE "English"

; Installer sections
Section "Install"
  SetOutPath "$INSTDIR"

  ; Copy application files
  File /r "dist\${APPNAME}\*.*"

  ; Create start menu shortcuts
  CreateDirectory "$SMPROGRAMS\${APPNAME}"
  CreateShortcut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${APPEXE}" "" "$INSTDIR\${APPEXE}" 0
  CreateShortcut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"

  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\${APPEXE}" "" "$INSTDIR\${APPEXE}" 0

  ; Write registry entries for uninstall
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} ${APPVERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${APPVERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${APPURL}"

  ; Create uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Add to PATH
  EnVar::AddValueEx "PATH" "$INSTDIR" "all"
SectionEnd

; Uninstaller section
Section "Uninstall"
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
  Delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
  RMDir "$SMPROGRAMS\${APPNAME}"
  Delete "$DESKTOP\${APPNAME}.lnk"

  ; Remove files
  RMDir /r "$INSTDIR"

  ; Remove registry entries
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"

  ; Remove from PATH
  EnVar::DeleteValue "PATH" "$INSTDIR" "all"
SectionEnd
