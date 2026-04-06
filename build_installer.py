import os
import subprocess
import shutil
import platform

def create_nsis_script():
    nsis_content = """
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

    InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"

    # rtf or txt file - remember if it is txt, it must be in the DOS text format (\\r\\n)
    # LicenseData "license.rtf"
    # Must be in the installer folder
    Name "${COMPANYNAME} - ${APPNAME}"
    Icon "compiler_icon.ico" ; You can add an icon later
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
        RMDir /r "$INSTDIR\\*.*"

        # Files added here should be removed by the uninstaller (see section "uninstall")
        File /r "dist\\UsirevAI\\*"

        # Uninstaller - See function un.onInit and section "uninstall" for configuration
        writeUninstaller "$INSTDIR\\uninstall.exe"

        # Start Menu
        createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
        createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\UsirevAI.exe" "" "$INSTDIR\\UsirevAI.exe"
        createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"

        # Desktop Shortcut
        createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\UsirevAI.exe" "" "$INSTDIR\\UsirevAI.exe"

        # Registry information for add/remove programs
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${COMPANYNAME} - ${APPNAME} - ${DESCRIPTION}"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\\"$INSTDIR$\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\\"$INSTDIR\\UsirevAI.exe$\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "$\\"${COMPANYNAME}\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "$\\"${HELPURL}\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "$\\"${UPDATEURL}\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "$\\"${ABOUTURL}\\""
        WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "$\\"${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}\\""
        WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
        WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
        # There is no option for modifying or repairing the install
        WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
        WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1

        # Launch the app after installation
        ExecShell "" "$INSTDIR\\UsirevAI.exe"
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
        delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
        delete "$SMPROGRAMS\\${COMPANYNAME}\\Uninstall.lnk"
        # Try to remove the Start Menu folder - this will only happen if it is empty
        rmDir "$SMPROGRAMS\\${COMPANYNAME}"

        # Remove Desktop Shortcut
        delete "$DESKTOP\\${APPNAME}.lnk"

        # Remove files
        RMDir /r "$INSTDIR"

        # Remove uninstaller information from the registry
        DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
    sectionEnd
    """
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_content)

def build():
    print("Building UsirevAI with PyInstaller...")

    # We use --onedir (default) instead of --onefile.
    # PyTorch and transformers are massive, and a single file executable
    # would take a very long time to extract every time the app is launched.

    # PyInstaller requires a semicolon on Windows, colon on Unix for add-data
    add_data_sep = os.pathsep

    command = [
        "pyinstaller",
        "--name", "UsirevAI",
        "--add-data", f"static{add_data_sep}static",
        "--noconfirm", # Overwrite output directory
        "--clean",
        "--windowed", # Don't show the command prompt on launch
        "main.py"
    ]

    try:
        subprocess.run(command, check=True)
        print("PyInstaller build finished.")

        # Now create an NSIS installer
        print("Generating NSIS Installer script...")
        # Create a dummy icon since we specified it in NSIS but don't have one
        if not os.path.exists("compiler_icon.ico"):
            with open("compiler_icon.ico", "wb") as f:
                f.write(b"") # Empty file is fine for makensis if we just need it to compile, though a real ico is better. Wait, makensis might fail on empty icon. Let's remove icon definition from script for now to be safe.

        # Re-read and remove Icon line to avoid compilation errors if no real ico exists
        create_nsis_script()
        with open("installer.nsi", "r", encoding="utf-8") as f:
            script = f.read()
        script = script.replace('Icon "compiler_icon.ico"', '; Icon "compiler_icon.ico"')
        with open("installer.nsi", "w", encoding="utf-8") as f:
            f.write(script)

        print("Compiling NSIS Setup executable...")
        try:
            subprocess.run(["makensis", "installer.nsi"], check=True)
            print("Successfully created UsirevAI_Setup.exe!")
        except FileNotFoundError:
            print("WARNING: 'makensis' not found. NSIS compiler is not installed or not in PATH.")
            print("To build the Windows Setup executable, please install NSIS (https://nsis.sourceforge.io/).")
            print("Falling back to creating a zip archive...")
            dist_dir = os.path.join("dist", "UsirevAI")
            shutil.make_archive("UsirevAI_LocalApp", "zip", dist_dir)
            print("Successfully created UsirevAI_LocalApp.zip")

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
