; Haval LocalAI Benchmarking — NSIS hooks + wizard extras.
; Included at the top of installer.nsi (before pages).
!ifndef HAVAL_WIZARD_NAME
  !define HAVAL_WIZARD_NAME "Haval LocalAI Benchmarking"
!endif
!ifndef HAVAL_OLLAMA_BMP
  !define HAVAL_OLLAMA_BMP "${__FILEDIR__}\..\assets\bmp\ollama.bmp"
!endif
!include nsDialogs.nsh
!include WinMessages.nsh

!ifndef PBM_SETBARCOLOR
  !define PBM_SETBARCOLOR 0x409
!endif
!ifndef PBM_SETBKCOLOR
  !define PBM_SETBKCOLOR 0x2001
!endif
!ifndef PBM_SETMARQUEE
  !define PBM_SETMARQUEE 0x40A
!endif
!ifndef PBS_MARQUEE
  !define PBS_MARQUEE 0x08
!endif

; Cream canvas + charcoal ink (tokens.css)
!define MUI_BGCOLOR F6F1E9
!define MUI_TEXTCOLOR 1A1A1A
!define MUI_INSTFILESPAGE_COLORS "1A1A1A F6F1E9"
!define MUI_LICENSEPAGE_BGCOLOR /windows
!define MUI_PROGRESSBAR_SMOOTH

!define MUI_WELCOMEPAGE_TITLE "Welcome to ${HAVAL_WIZARD_NAME}"
!define MUI_WELCOMEPAGE_TEXT "This wizard installs Haval LocalAI Benchmarking on this PC.$\r$\n$\r$\nIt copies the app plus bundled Python and Node.js so hidden benchmark tests can run on this PC. Doctor then prepares Windows, Ollama, storage, and acceleration the first time you open the app.$\r$\n$\r$\nClick Next to continue."
!define MUI_FINISHPAGE_TITLE "${HAVAL_WIZARD_NAME} is installed"
!define MUI_FINISHPAGE_TEXT "Setup has finished. Open the app to let Doctor complete remaining checks. If Ollama still needs a small internet download, Doctor will walk you through it."
!define MUI_FINISHPAGE_RUN_TEXT "Open Haval LocalAI Benchmarking"
!define MUI_DIRECTORYPAGE_TEXT_TOP "Setup will install Haval LocalAI Benchmarking in the following folder."
!define MUI_INNERTEXT_INSTFILES "Please wait while Haval LocalAI Benchmarking is copied to this PC."
!define MUI_UNCONFIRMPAGE_TEXT_TOP "Haval LocalAI Benchmarking will be removed from the folder below."

Var OllamaFound
Var OllamaDlg
Var OllamaBmpCtl
Var OllamaBmpImage
Var OllamaDownloadRadio
Var OllamaLaterRadio
Var OllamaStatus
Var OllamaProgress

!macro NSIS_HOOK_PREINSTALL
  ${If} $UpdateMode = 1
    DetailPrint "Updating the current install. Reports and settings stay on this PC."
    Call HavalWaitForAppExit
    IfFileExists "$INSTDIR\uninstall.exe" 0 skip_keep_data_uninst
      ExecWait '"$INSTDIR\uninstall.exe" /S /KEEP_DATA /UPDATE _?=$INSTDIR'
    skip_keep_data_uninst:
  ${Else}
    DetailPrint "Preparing Haval LocalAI Benchmarking files..."
  ${EndIf}
!macroend

!macro NSIS_HOOK_POSTINSTALL
  Call HavalWriteInstallJson
  DetailPrint "Haval LocalAI Benchmarking files are in place."
!macroend

!macro NSIS_HOOK_PREUNINSTALL
!macroend

!macro NSIS_HOOK_POSTUNINSTALL
!macroend

Function DetectOllama
  StrCpy $OllamaFound 0
  IfFileExists "$LOCALAPPDATA\Programs\Ollama\ollama.exe" ollama_yes
  IfFileExists "$PROGRAMFILES64\Ollama\ollama.exe" ollama_yes
  IfFileExists "$PROGRAMFILES\Ollama\ollama.exe" ollama_yes
  ReadRegStr $0 HKCU "Software\Microsoft\Windows\CurrentVersion\App Paths\ollama.exe" ""
  StrCmp $0 "" check_hklm
  IfFileExists "$0" ollama_yes
  check_hklm:
  ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\ollama.exe" ""
  StrCmp $0 "" ollama_done
  IfFileExists "$0" ollama_yes ollama_done
  ollama_yes:
  StrCpy $OllamaFound 1
  ollama_done:
FunctionEnd

Function ThemeInstFiles
  FindWindow $0 "#32770" "" $HWNDPARENT
  SetCtlColors $HWNDPARENT 0x1A1A1A 0xF6F1E9
  SetCtlColors $0 0x1A1A1A 0xF6F1E9
  GetDlgItem $1 $0 1004
  ${If} $1 != 0
    System::Call 'uxtheme::SetWindowTheme(p r1, w " ", w " ")i .r2'
    SendMessage $1 ${PBM_SETBKCOLOR} 0 0x00E9F1F6
    SendMessage $1 ${PBM_SETBARCOLOR} 0 0x001B4FDB
  ${EndIf}
  GetDlgItem $1 $0 1006
  ${If} $1 != 0
    SetCtlColors $1 0x1A1A1A 0xF6F1E9
  ${EndIf}
  ${If} $UpdateMode = 1
    Call HavalStyleUpdateWindow
  ${EndIf}
FunctionEnd

Function PageOllama
  ${If} $PassiveMode = 1
  ${OrIf} $UpdateMode = 1
    Abort
  ${EndIf}
  Call DetectOllama
  ${If} $OllamaFound = 1
    Abort
  ${EndIf}

  !insertmacro MUI_HEADER_TEXT "Internet needed for Ollama" "A small, fast download of the latest Ollama service"

  nsDialogs::Create 1018
  Pop $OllamaDlg
  ${If} $OllamaDlg == error
    Abort
  ${EndIf}
  SetCtlColors $OllamaDlg 0x1A1A1A 0xF6F1E9

  ${If} ${FileExists} "$PLUGINSDIR\ollama.bmp"
    ${NSD_CreateBitmap} 0 0 120 72 ""
    Pop $OllamaBmpCtl
    ${NSD_SetImage} $OllamaBmpCtl "$PLUGINSDIR\ollama.bmp" $OllamaBmpImage
  ${EndIf}

  ${NSD_CreateLabel} 128 0 220 72 "This PC does not have Ollama yet. Haval LocalAI Benchmarking uses the official Ollama service to run models here. This step downloads the latest Ollama service. It is a small, fast download. Stay connected until it finishes."
  Pop $0
  SetCtlColors $0 0x40454A 0xF6F1E9

  ${NSD_CreateRadioButton} 0 78 450 14 "Download Ollama"
  Pop $OllamaDownloadRadio
  SetCtlColors $OllamaDownloadRadio 0x1A1A1A 0xF6F1E9
  ${NSD_Check} $OllamaDownloadRadio

  ${NSD_CreateRadioButton} 0 94 450 14 "I'll connect later"
  Pop $OllamaLaterRadio
  SetCtlColors $OllamaLaterRadio 0x1A1A1A 0xF6F1E9

  ${NSD_CreateLabel} 0 112 450 12 ""
  Pop $OllamaStatus
  SetCtlColors $OllamaStatus 0xA83B15 0xF6F1E9

  ${NSD_CreateProgressBar} 0 126 450 8 ""
  Pop $OllamaProgress
  ShowWindow $OllamaProgress ${SW_HIDE}

  nsDialogs::Show
  ${NSD_FreeImage} $OllamaBmpImage
FunctionEnd

Function PageOllamaLeave
  ${NSD_GetState} $OllamaDownloadRadio $0
  ${If} $0 != ${BST_CHECKED}
    Return
  ${EndIf}

  ShowWindow $OllamaProgress ${SW_SHOW}
  Push $0
  StrCpy $0 $OllamaProgress
  System::Call 'user32::GetWindowLong(p r0, i -16) i .r1'
  IntOp $1 $1 | ${PBS_MARQUEE}
  System::Call 'user32::SetWindowLong(p r0, i -16, i r1)'
  Pop $0
  SendMessage $OllamaProgress ${PBM_SETMARQUEE} 1 16
  SendMessage $OllamaStatus ${WM_SETTEXT} 0 "STR:Checking internet for the Ollama download..."

  nsExec::ExecToStack '"$SYSDIR\curl.exe" -I -s -o NUL --max-time 10 https://ollama.com'
  Pop $0
  Pop $1
  ${If} $0 != 0
    SendMessage $OllamaProgress ${PBM_SETMARQUEE} 0 0
    ShowWindow $OllamaProgress ${SW_HIDE}
    MessageBox MB_ICONEXCLAMATION "This step needs internet for a small, fast download of the latest Ollama service. Connect, then click Next again.$\r$\n$\r$\nOr choose I'll connect later. Haval LocalAI Benchmarking can still be installed; Doctor will finish Ollama when a connection is available."
    Abort
  ${EndIf}

  SendMessage $OllamaStatus ${WM_SETTEXT} 0 "STR:Downloading the latest Ollama service (small and fast)..."
  nsExec::ExecToStack '"$SYSDIR\curl.exe" -L --retry 2 --connect-timeout 15 -o "$PLUGINSDIR\OllamaSetup.exe" https://ollama.com/download/OllamaSetup.exe'
  Pop $0
  Pop $1
  ${If} $0 != 0
    SendMessage $OllamaProgress ${PBM_SETMARQUEE} 0 0
    ShowWindow $OllamaProgress ${SW_HIDE}
    MessageBox MB_ICONEXCLAMATION "Could not download Ollama. Stay connected and try again, or choose I'll connect later and let Doctor finish this after install."
    Abort
  ${EndIf}

  IfFileExists "$PLUGINSDIR\OllamaSetup.exe" +3 0
    MessageBox MB_ICONEXCLAMATION "The Ollama download did not finish. Try again, or continue and let Doctor install it later."
    Abort

  SendMessage $OllamaStatus ${WM_SETTEXT} 0 "STR:Starting the official Ollama setup..."
  ExecWait '"$PLUGINSDIR\OllamaSetup.exe"' $0
  SendMessage $OllamaProgress ${PBM_SETMARQUEE} 0 0
  Call DetectOllama
  ${If} $OllamaFound = 0
    MessageBox MB_OK|MB_ICONINFORMATION "Ollama is not installed yet. Haval LocalAI Benchmarking will still be copied. Open the app and use Doctor when you are online."
  ${EndIf}
FunctionEnd

!define HAVAL_DATA_NAME "Haval LocalAI Bench"
!define HAVAL_REG_KEY "Software\Haval\LocalAIBench"

Function HavalJsonInstallDir
  StrCpy $R9 ""
  IfFileExists "$LOCALAPPDATA\${HAVAL_DATA_NAME}\install.json" 0 json_done
  ClearErrors
  FileOpen $R8 "$LOCALAPPDATA\${HAVAL_DATA_NAME}\install.json" r
  IfErrors json_done
  json_read:
    ClearErrors
    FileRead $R8 $R7
    IfErrors json_close
    ${StrLoc} $R6 $R7 '"install_dir"' ">"
    StrCmp $R6 "" json_read
    ${StrLoc} $R6 $R7 '"' ">"
    ; take text between the last pair of quotes on the line
    StrCpy $R5 $R7 "" -2
    ${StrLoc} $R6 $R7 ': "' ">"
    StrCmp $R6 "" json_read
    IntOp $R6 $R6 + 3
    StrCpy $R7 $R7 "" $R6
    ${StrLoc} $R6 $R7 '"' ">"
    StrCmp $R6 "" json_close
    StrCpy $R9 $R7 $R6
    Goto json_close
  json_close:
    FileClose $R8
  json_done:
FunctionEnd

Function HavalResolveInstallDir
  Call HavalJsonInstallDir
  ${If} $R9 != ""
    StrCpy $INSTDIR $R9
    Return
  ${EndIf}
  ReadRegStr $R9 HKCU "${HAVAL_REG_KEY}" "InstallDir"
  ${If} $R9 != ""
    StrCpy $INSTDIR $R9
  ${EndIf}
FunctionEnd

Function HavalMaybeEnterUpdateMode
  ${If} $UpdateMode = 1
    Return
  ${EndIf}
  IfFileExists "$INSTDIR\${MAINBINARYNAME}.exe" enter_update
  ReadRegStr $R1 HKCU "${HAVAL_REG_KEY}" "InstallDir"
  ${If} $R1 != ""
    IfFileExists "$R1\${MAINBINARYNAME}.exe" 0 check_uninst_loc
    StrCpy $INSTDIR $R1
    Goto enter_update
  ${EndIf}
  check_uninst_loc:
  ReadRegStr $R1 SHCTX "${UNINSTKEY}" "InstallLocation"
  ${If} $R1 != ""
    IfFileExists "$R1\${MAINBINARYNAME}.exe" 0 leave_wizard
    StrCpy $INSTDIR $R1
    Goto enter_update
  ${EndIf}
  leave_wizard:
  Return
  enter_update:
  StrCpy $UpdateMode 1
FunctionEnd

Function HavalWaitForAppExit
  StrCpy $R0 0
  wait_more:
    nsExec::ExecToStack '"$SYSDIR\cmd.exe" /C tasklist /FI "IMAGENAME eq ${MAINBINARYNAME}.exe" /NH | find /I "${MAINBINARYNAME}.exe"'
    Pop $R1
    Pop $R2
    ${If} $R1 != 0
      Return
    ${EndIf}
    IntOp $R0 $R0 + 1
    ${If} $R0 >= 8
      nsExec::ExecToStack '"$SYSDIR\taskkill.exe" /IM "${MAINBINARYNAME}.exe" /F'
      Pop $R1
      Pop $R2
      Return
    ${EndIf}
    Sleep 1000
    Goto wait_more
FunctionEnd

Function HavalStyleUpdateWindow
  System::Call 'user32::SetWindowText(p $HWNDPARENT, t "Updating Haval LocalAI Benchmarking")'
  System::Call 'user32::GetDpiForWindow(p $HWNDPARENT) i .r8'
  IntCmp $8 96 dpi_ok dpi_fix dpi_ok
  dpi_fix:
    StrCpy $8 96
  dpi_ok:
  IntOp $9 560 * $8
  IntOp $9 $9 / 96
  IntOp $R0 300 * $8
  IntOp $R0 $R0 / 96
  System::Call 'user32::GetSystemMetrics(i 0) i .r4'
  System::Call 'user32::GetSystemMetrics(i 1) i .r5'
  IntOp $6 $4 - $9
  IntOp $6 $6 / 2
  IntOp $7 $5 - $R0
  IntOp $7 $7 / 2
  System::Call 'user32::SetWindowPos(p $HWNDPARENT, i 0, i r6, i r7, i r9, i R0, i 0x0040)'

  GetDlgItem $1 $HWNDPARENT 1034
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 1035
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 1036
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 1037
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 1044
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 1256
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 3
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $HWNDPARENT 1
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}

  System::Call '*(i 0, i 0, i 0, i 0) i .r3'
  System::Call 'user32::GetClientRect(p $HWNDPARENT, i r3)'
  System::Call '*$3(i, i, i .r4, i .r5)'
  System::Free $3
  IntOp $6 16 * $8
  IntOp $6 $6 / 96
  IntOp $7 52 * $8
  IntOp $7 $7 / 96
  IntOp $R1 $4 - $6
  IntOp $R1 $R1 - $6
  IntOp $R2 $5 - $6
  IntOp $R2 $R2 - $7
  FindWindow $0 "#32770" "" $HWNDPARENT
  System::Call 'user32::MoveWindow(p r0, i r6, i r6, i R1, i R2, i 1)'
  SetCtlColors $HWNDPARENT 0x1A1A1A 0xF6F1E9
  SetCtlColors $0 0x1A1A1A 0xF6F1E9

  GetDlgItem $1 $0 1016
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}
  GetDlgItem $1 $0 1027
  ${If} $1 != 0
    ShowWindow $1 ${SW_HIDE}
  ${EndIf}

  IntOp $R3 $R1 - $6
  IntOp $R4 44 * $8
  IntOp $R4 $R4 / 96
  GetDlgItem $1 $0 1006
  ${If} $1 != 0
    System::Call 'user32::MoveWindow(p r1, i r6, i r6, i R3, i R4, i 1)'
    SetCtlColors $1 0x1A1A1A 0xF6F1E9
    SendMessage $1 ${WM_SETTEXT} 0 "STR:Updating the current install to ${VERSION}. Reports and settings stay on this PC."
  ${EndIf}

  IntOp $R5 $R4 + $6
  IntOp $R5 $R5 + $6
  IntOp $R6 18 * $8
  IntOp $R6 $R6 / 96
  GetDlgItem $1 $0 1004
  ${If} $1 != 0
    System::Call 'user32::MoveWindow(p r1, i r6, i R5, i R3, i R6, i 1)'
    System::Call 'uxtheme::SetWindowTheme(p r1, w " ", w " ")i .r2'
    SendMessage $1 ${PBM_SETBKCOLOR} 0 0x00E9F1F6
    SendMessage $1 ${PBM_SETBARCOLOR} 0 0x001B4FDB
  ${EndIf}

  GetDlgItem $1 $HWNDPARENT 2
  ${If} $1 != 0
    IntOp $R7 88 * $8
    IntOp $R7 $R7 / 96
    IntOp $R8 28 * $8
    IntOp $R8 $R8 / 96
    IntOp $R9 $4 - $6
    IntOp $R9 $R9 - $R7
    IntOp $R0 $5 - $6
    IntOp $R0 $R0 - $R8
    System::Call 'user32::MoveWindow(p r1, i R9, i R0, i R7, i R8, i 1)'
    ShowWindow $1 ${SW_SHOW}
  ${EndIf}
FunctionEnd

Function HavalWriteInstallJson
  ReadEnvStr $R0 LOCALAPPDATA
  StrCpy $R1 "$R0\${HAVAL_DATA_NAME}"
  CreateDirectory "$R1"
  CreateDirectory "$R1\updates"
  ${GetTime} "" "L" $2 $3 $4 $5 $6 $7 $8
  ; day month year weekday hour min sec
  StrCpy $R2 "$4-$3-$2T$6:$7:$8"
  Push $INSTDIR
  Call HavalFwdSlash
  Pop $R3
  Push $R1
  Call HavalFwdSlash
  Pop $R4
  Push "$INSTDIR\${MAINBINARYNAME}.exe"
  Call HavalFwdSlash
  Pop $R5
  FileOpen $9 "$R1\install.json" w
  FileWrite $9 '{"schema":1,"product":"Haval LocalAI Bench","version":"${VERSION}",'
  FileWrite $9 '"installed_at":"$R2","updated_at":"$R2",'
  FileWrite $9 '"install_dir":"$R3","exe":"$R5",'
  FileWrite $9 '"uninstaller":"$R3/uninstall.exe",'
  FileWrite $9 '"python_dir":"$R3/python","node_dir":"$R3/node",'
  FileWrite $9 '"engine_dir":"$R3","data_dir":"$R4",'
  FileWrite $9 '"reports_dir":"$R4/runs","db":"$R4/runs/run.sqlite"}$\r$\n'
  FileClose $9
  ${If} $UpdateMode = 1
    FileOpen $9 "$R1\just-updated.json" w
    FileWrite $9 '{"version":"${VERSION}"}$\r$\n'
    FileClose $9
  ${EndIf}
  WriteRegStr HKCU "${HAVAL_REG_KEY}" "InstallDir" $INSTDIR
  WriteRegStr HKCU "${HAVAL_REG_KEY}" "DataDir" "$R1"
  WriteRegStr HKCU "${HAVAL_REG_KEY}" "Version" "${VERSION}"
  WriteRegStr HKCU "${HAVAL_REG_KEY}" "DisplayName" "${HAVAL_DATA_NAME}"
  WriteRegStr SHCTX "${UNINSTKEY}" "InstallLocation" $INSTDIR
FunctionEnd

Function HavalFwdSlash
  Exch $0
  Push $1
  Push $2
  Push $3
  StrCpy $1 ""
  StrCpy $2 0
  slash_loop:
    StrCpy $3 $0 1 $2
    StrCmp $3 "" slash_done
    StrCmp $3 "\" 0 slash_keep
    StrCpy $1 "$1/"
    Goto slash_next
    slash_keep:
    StrCpy $1 "$1$3"
    slash_next:
    IntOp $2 $2 + 1
    Goto slash_loop
  slash_done:
  StrCpy $0 $1
  Pop $3
  Pop $2
  Pop $1
  Exch $0
FunctionEnd
