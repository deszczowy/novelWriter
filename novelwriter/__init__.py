"""
novelWriter – Init File
=======================

File History:
Created: 2018-09-22 [0.0.1]  main

This file is a part of novelWriter
Copyright (C) 2018 Veronica Berglyd Olsen and novelWriter contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import getopt
import logging
import sys

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication, QErrorMessage

from novelwriter.config import Config
from novelwriter.error import exceptionHandler
from novelwriter.shared import SharedData

if TYPE_CHECKING:  # pragma: no cover
    from novelwriter.guimain import GuiMain

# Package Meta
# ============

__package__    = "novelwriter"
__copyright__  = "Copyright 2018-2025 Veronica Berglyd Olsen"
__license__    = "GPLv3"
__author__     = "Veronica Berglyd Olsen"
__maintainer__ = "Veronica Berglyd Olsen"
__email__      = "code@vkbo.net"
__version__    = "2.7a2"
__hexversion__ = "0x020700a2"
__date__       = "2025-01-20"
__status__     = "Stable"
__domain__     = "novelwriter.io"

logger = logging.getLogger(__name__)


##
#  Main Program
##

# Globals Singletons
CONFIG = Config()
SHARED = SharedData()

# ANSI Colours
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
WHITE  = "\033[97m"
END    = "\033[0m"

# Log Format Components
TIME = "[{asctime:}]"
FILE = "{filename:>18}"
LINE = "{lineno:<4d}"
LVLP = "{levelname:8}"
LVLC = "{levelname:17}"
TEXT = "{message:}"


def main(sysArgs: list | None = None) -> GuiMain | None:
    """Parse command line, set up logging, and launch main GUI."""
    if sysArgs is None:
        sysArgs = sys.argv[1:]

    # Valid Input Options
    shortOpt = "hv"
    longOpt = [
        "help",
        "version",
        "info",
        "debug",
        "color",
        "style=",
        "config=",
        "data=",
        "meminfo"
    ]

    helpMsg = (
        f"novelWriter {__version__} ({__date__})\n"
        f"{__copyright__}\n"
        "\n"
        "This program is free software: you can redistribute it and/or modify\n"
        "it under the terms of the GNU General Public License as published by\n"
        "the Free Software Foundation, either version 3 of the License, or\n"
        "(at your option) any later version.\n"
        "\n"
        "This program is distributed in the hope that it will be useful,\n"
        "but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
        "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the\n"
        "GNU General Public Licence for more details.\n"
        "\n"
        "You should have received a copy of the GNU General Public License\n"
        "along with this program. If not, see <https://www.gnu.org/licenses/>.\n"
        "\n"
        "Usage:\n"
        " -h, --help     Print this message.\n"
        " -v, --version  Print program version and exit.\n"
        "     --info     Print additional runtime information.\n"
        "     --debug    Print debug output. Includes --info.\n"
        "     --color    Add ANSI colors to log output.\n"
        "     --meminfo  Show memory usage information in the status bar.\n"
        "     --style=   Sets Qt style flag. Defaults to 'Fusion'.\n"
        "     --config=  Alternative config file.\n"
        "     --data=    Alternative user data path.\n"
    )

    # Defaults
    logLevel = logging.WARN
    fmtFlags = 0b00
    confPath = None
    dataPath = None
    qtStyle  = "Fusion"
    cmdOpen  = None

    # Parse Options
    try:
        inOpts, inRemain = getopt.getopt(sysArgs, shortOpt, longOpt)
    except getopt.GetoptError as exc:
        print(helpMsg)
        print(f"ERROR: {str(exc)}")
        sys.exit(2)

    if len(inRemain) > 0:
        cmdOpen = inRemain[0]

    for inOpt, inArg in inOpts:
        if inOpt in ("-h", "--help"):
            print(helpMsg)
            sys.exit(0)
        elif inOpt in ("-v", "--version"):
            print("novelWriter Version %s [%s]" % (__version__, __date__))
            sys.exit(0)
        elif inOpt == "--info":
            logLevel = logging.INFO
        elif inOpt == "--debug":
            CONFIG.isDebug = True
            fmtFlags = fmtFlags | 0b10
            logLevel = logging.DEBUG
        elif inOpt == "--color":
            fmtFlags = fmtFlags | 0b01
        elif inOpt == "--style":
            qtStyle = inArg
        elif inOpt == "--config":
            confPath = inArg
        elif inOpt == "--data":
            dataPath = inArg
        elif inOpt == "--meminfo":
            CONFIG.memInfo = True

    if fmtFlags & 0b01:
        # This will overwrite the default level names, and also ensure that
        # they can be converted back to integer levels
        logging.addLevelName(logging.DEBUG,    f"{BLUE}DEBUG{END}")
        logging.addLevelName(logging.INFO,     f"{GREEN}INFO{END}")
        logging.addLevelName(logging.WARNING,  f"{YELLOW}WARNING{END}")
        logging.addLevelName(logging.ERROR,    f"{RED}ERROR{END}")
        logging.addLevelName(logging.CRITICAL, f"{RED}CRITICAL{END}")

    # Determine Log Format
    if fmtFlags == 0b00:
        logFmt = f"{LVLP}  {TEXT}"
    elif fmtFlags == 0b01:
        logFmt = f"{LVLC}  {TEXT}"
    elif fmtFlags == 0b10:
        logFmt = f"{TIME}  {FILE}:{LINE}  {LVLP}  {TEXT}"
    elif fmtFlags == 0b11:
        logFmt = f"{TIME}  {BLUE}{FILE}{END}:{WHITE}{LINE}{END}  {LVLC}  {TEXT}"

    # Setup Logging
    pkgLogger = logging.getLogger(__package__)
    pkgLogger.setLevel(logLevel)
    if len(pkgLogger.handlers) == 0:
        # Make sure we only create one logger (mostly an issue with tests)
        cHandle = logging.StreamHandler()
        cHandle.setFormatter(logging.Formatter(fmt=logFmt, style="{"))
        pkgLogger.addHandler(cHandle)

    logger.info("Starting novelWriter %s (%s) %s", __version__, __hexversion__, __date__)

    # Check Packages and Versions
    errorData = []
    errorCode = 0
    if sys.hexversion < 0x030a00f0:
        errorData.append(
            "At least Python 3.10 is required, found %s" % CONFIG.verPyString
        )
        errorCode |= 0x04
    if CONFIG.verQtValue < 0x060400:
        errorData.append(
            "At least Qt6 version 6.4 is required, found %s" % CONFIG.verQtString
        )
        errorCode |= 0x08
    if CONFIG.verPyQtValue < 0x060400:
        errorData.append(
            "At least PyQt6 version 6.4 is required, found %s" % CONFIG.verPyQtString
        )
        errorCode |= 0x10

    if errorData:
        errApp = QApplication([])
        errDlg = QErrorMessage()
        errDlg.resize(500, 300)
        errDlg.showMessage((
            "<h3>A critical error was encountered</h3>"
            "<p>novelWriter cannot start due to the following issues:<p>"
            "<p>&nbsp;-&nbsp;%s</p>"
            "<p>Shutting down ...</p>"
        ) % (
            "<br>&nbsp;-&nbsp;".join(errorData)
        ))
        for errLine in errorData:
            logger.critical(errLine)
        errApp.exec()
        sys.exit(errorCode)

    # Finish initialising config
    CONFIG.initConfig(confPath, dataPath)

    if sys.platform == "darwin":
        try:
            from Foundation import NSBundle  # type: ignore
            bundle = NSBundle.mainBundle()
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            info["CFBundleName"] = "novelWriter"
        except Exception:
            pass  # Quietly ignore error
    elif sys.platform == "win32":
        try:
            import ctypes
            appID = f"io.novelwriter.{__version__}"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)  # type: ignore
        except Exception:
            pass  # Quietly ignore error

    # Import GUI (after dependency checks), and launch
    from novelwriter.gui.theme import GuiTheme
    from novelwriter.guimain import GuiMain

    # Create App
    app = _createApp(qtStyle)

    # Connect the exception handler before making the main GUI
    sys.excepthook = exceptionHandler

    # Run Config steps that require the QApplication
    CONFIG.loadConfig()
    CONFIG.initLocalisation(app)
    SHARED.initTheme(GuiTheme())

    # Launch main GUI
    nwGUI = GuiMain()
    nwGUI.postLaunchTasks(cmdOpen)

    sys.exit(app.exec())


def _createApp(style: str) -> QApplication:
    """Create the app. This is done in a function to make it easier to
    block app creation during testing.
    """
    app = QApplication([CONFIG.appName, (f"-style={style}")])
    app.setApplicationName(CONFIG.appName)
    app.setApplicationVersion(__version__)
    app.setOrganizationDomain(__domain__)
    app.setOrganizationName(__domain__)
    app.setDesktopFileName(CONFIG.appName)
    return app
