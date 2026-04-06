
    !define APPNAME "UsirevAI"
    !define COMPANYNAME "UsirevAI"
    !define DESCRIPTION "AI Medical Transcription and Anamnesis Extraction"
    !define VERSIONMAJOR 1
    !define VERSIONMINOR 0
    !define VERSIONBUILD 0
    !define HELPURL "https://github.com/your-repo/usirevai" # Replace with real URL
    !define UPDATEURL "https://github.com/your-repo/usirevai" # Replace with real URL
    !define ABOUTURL "https://github.com/your-repo/usirevai" # Replace with real URL

    RequestExecutionLevel admin ;Require admin rights on NT6+ (When UAC is turned on)

    InstallDir "$PROGRAMFILES\${COMPANYNAME}\${APPNAME}"

    # rtf or txt file - remember if it is txt, it must be in the DOS text format (\r\n)
    # LicenseData "license.rtf"
    # Must be in the installer folder
    Name "${COMPANYNAME} - ${APPNAME}"
    ; Icon "compiler_icon.ico" ; You can add an icon later
    outFile "UsirevAI_Setup.exe"

    !include LogicLib.nsh

    page directory
    page instfiles

    !macro VerifyUserIsAdmin
    UserInfo::GetAccountType
    pop $0
    ${If} $0 != "admin" ;Require admin rights on NT4+
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
        quit
    ${EndIf}
    !macroend

    function .onInit
        setShellVarContext all
        !insertmacro VerifyUserIsAdmin
    functionEnd

    section "install"
        # Files for the install directory - to build the installer, these should be in the same directory as the install script (mac OS X/Linux won't work)
        setOutPath $INSTDIR

        # Remove old files before installing new ones
        RMDir /r "$INSTDIR\*.*"

        # Files added here should be removed by the uninstaller (see section "uninstall")
        File /r "dist\UsirevAI\*"

        # Uninstaller - See function un.onInit and section "uninstall" for configuration
        writeUninstaller "$INSTDIR\uninstall.exe"

        # Start Menu
        createDirectory "$SMPROGRAMS\${COMPANYNAME}"
        createShortCut "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk" "$INSTDIR\UsirevAI.exe" "" "$INSTDIR\UsirevAI.exe"
        createShortCut "$SMPROGRAMS\${COMPANYNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"

        # Desktop Shortcut
        createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\UsirevAI.exe" "" "$INSTDIR\UsirevAI.exe"

        # Registry information for add/remove programs
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayName" "${COMPANYNAME} - ${APPNAME} - ${DESCRIPTION}"
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\"$INSTDIR\UsirevAI.exe$\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "Publisher" "$\"${COMPANYNAME}\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "HelpLink" "$\"${HELPURL}\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "$\"${UPDATEURL}\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "$\"${ABOUTURL}\""
        WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "$\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}\""
        WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
        WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
        # There is no option for modifying or repairing the install
        WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoModify" 1
        WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}" "NoRepair" 1

        # Launch the app after installation
        ExecShell "" "$INSTDIR\UsirevAI.exe"
    sectionEnd

    # Uninstaller
    function un.onInit
        SetShellVarContext all
        # Verify the uninstaller - last chance to back out
        MessageBox MB_OKCANCEL "Permanently remove ${APPNAME}?" IDOK next
            Abort
        next:
        !insertmacro VerifyUserIsAdmin
    functionEnd

    section "uninstall"
        # Remove Start Menu launcher
        delete "$SMPROGRAMS\${COMPANYNAME}\${APPNAME}.lnk"
        delete "$SMPROGRAMS\${COMPANYNAME}\Uninstall.lnk"
        # Try to remove the Start Menu folder - this will only happen if it is empty
        rmDir "$SMPROGRAMS\${COMPANYNAME}"

        # Remove Desktop Shortcut
        delete "$DESKTOP\${APPNAME}.lnk"

        # Remove files
        RMDir /r "$INSTDIR"

        # Remove uninstaller information from the registry
        DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${COMPANYNAME} ${APPNAME}"
    sectionEnd
