from __future__ import annotations
import platform
from typing import Optional, Any
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from QWeb.internal.config_defaults import CONFIG
from QWeb.internal import browser, user, util

NAMES: list[str] = ["edge", "msedge"]


def open_browser(executable_path: str = "msedgedriver",
                 edge_args: Optional[list[str]] = None,
                 desired_capabilities: Optional[dict[str, Any]] = None,
                 **kwargs: Any) -> WebDriver:
    """Open Edge browser instance and cache the driver.

    Parameters
    ----------
    executable_path : str (Default "msedgedriver")
        path to the executable. If the default is used it assumes the
        executable is in the $PATH.
    port : int (Default 0)
        port you would like the service to run, if left as 0, a free port will
        be found.
    desired_capabilities : dict (Default None)
        Dictionary object with non-browser specific capabilities only, such as
        "proxy" or "loggingPref".
    chrome_args : Optional arguments to modify browser settings
    """
    options = Options()
    options.use_chromium = True  # pylint: disable=no-member

    # Gets rid of Devtools listening .... printing
    # other non-sensical error messages
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # pylint: disable=no-member

    if platform.system().lower() == "windows":
        options.set_capability("platform", "WINDOWS")

    if platform.system().lower() == "linux":
        options.set_capability("platform", "LINUX")

    if platform.system().lower() == "darwin":
        options.set_capability("platform", "MAC")

    # If user wants to re-use existing browser session then
    # he/she has to set variable BROWSER_REUSE_ENABLED to True.
    # If enabled, then web driver connection details are written
    # to an argument file. This file enables re-use of the current
    # chrome session.
    #
    # When variables BROWSER_SESSION_ID and BROWSER_EXECUTOR_URL are
    # set from argument file, then OpenBrowser will use those
    # parameters instead of opening new chrome session.
    # New Remote Web Driver is created in headless mode.
    edge_path = kwargs.get('edge_path', None) or BuiltIn().get_variable_value('${EDGE_PATH}')
    if edge_path:
        options.binary_location = edge_path  # pylint: disable=no-member

    if user.is_root() or user.is_docker():
        options.add_argument("no-sandbox")  # pylint: disable=no-member
    if edge_args:
        if any('--headless' in _.lower() for _ in edge_args):
            CONFIG.set_value('Headless', True)
        for item in edge_args:
            options.add_argument(item.lstrip())  # pylint: disable=no-member
    options.add_argument("start-maximized")  # pylint: disable=no-member
    options.add_argument("--disable-notifications")  # pylint: disable=no-member
    if 'headless' in kwargs:
        CONFIG.set_value('Headless', True)
        options.add_argument("--headless")  # pylint: disable=no-member
    if 'prefs' in kwargs:
        if isinstance(kwargs.get('prefs'), dict):
            prefs = kwargs.get('prefs')
        else:
            prefs = util.prefs_to_dict(str(kwargs.get('prefs')).strip())
        options.add_experimental_option('prefs', prefs)
        logger.warn("prefs: {}".format(prefs))
    driver = Edge(
        BuiltIn().get_variable_value('${EDGEDRIVER_PATH}')  # pylint: disable=unexpected-keyword-arg
        or executable_path,
        options=options,
        capabilities=desired_capabilities)
    browser.cache_browser(driver)
    return driver
