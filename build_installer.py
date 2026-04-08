import os
import subprocess
import shutil
import platform
import urllib.request
import zipfile
import io

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

        # Determine makensis command
        makensis_cmd = "makensis"

        # Try to find makensis in PATH first
        if shutil.which(makensis_cmd) is None:
            print("makensis not found in PATH. Downloading portable NSIS compiler...")
            # Download NSIS portable zip
            # Using SourceForge download link for NSIS 3.10
            nsis_url = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.10/nsis-3.10.zip/download"
            nsis_dir = "nsis_temp"
            try:
                with urllib.request.urlopen(nsis_url) as response:
                    with zipfile.ZipFile(io.BytesIO(response.read())) as z:
                        z.extractall(nsis_dir)

                # The zip extracts into a folder called 'nsis-3.10'
                if platform.system() == "Windows":
                    makensis_cmd = os.path.join(nsis_dir, "nsis-3.10", "makensis.exe")
                else:
                    # On Linux/macOS, we can't just run the Windows makensis.exe directly.
                    # We would need Wine, or a native build of makensis.
                    # If they are on Linux and didn't apt-get install nsis, fallback to zip.
                    print("NSIS download successful, but you are not on Windows.")
                    print("To compile the Windows Setup on Linux/macOS, please install native 'makensis' (e.g. sudo apt install nsis).")
                    makensis_cmd = None

            except Exception as e:
                print(f"Failed to download NSIS: {e}")
                makensis_cmd = None

        if makensis_cmd is not None:
            try:
                subprocess.run([makensis_cmd, "installer.nsi"], check=True)
                print("Successfully created UsirevAI_Setup.exe!")
            except subprocess.CalledProcessError as e:
                print(f"NSIS compilation failed: {e}")
                makensis_cmd = None # Fallback to zip
            except FileNotFoundError:
                print(f"Could not execute {makensis_cmd}")
                makensis_cmd = None

        if makensis_cmd is None:
            print("Falling back to creating a zip archive...")
            dist_dir = os.path.join("dist", "UsirevAI")
            shutil.make_archive("UsirevAI_LocalApp", "zip", dist_dir)
            print("Successfully created UsirevAI_LocalApp.zip")

        # Cleanup temp NSIS dir if it was created
        if os.path.exists("nsis_temp"):
            print("Cleaning up temporary NSIS files...")
            shutil.rmtree("nsis_temp", ignore_errors=True)

    except subprocess.CalledProcessError as e:
        print(f"Error during build process: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    build()
