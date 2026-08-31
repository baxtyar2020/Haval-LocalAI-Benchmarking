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
!define MUI_WELCOMEPAGE_TEXT "This wizard installs Haval LocalAI Benchmarking on this PC.$\r$\n$\r$\nIt copies the app and a bundled Python runtime. Doctor then prepares Windows, Ollama, storage, and acceleration the first time you open the app.$\r$\n$\r$\nClick Next to continue."
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
  DetailPrint "Preparing Haval LocalAI Benchmarking files..."
!macroend

!macro NSIS_HOOK_POSTINSTALL
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
FunctionEnd

Function PageOllama
  ${If} $PassiveMode = 1
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
