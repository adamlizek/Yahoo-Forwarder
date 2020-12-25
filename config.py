from enum import Enum
from pathlib import Path
import os
import sys


# ENUMS
class CaptchaType(Enum):
    CAPTCHA_YAHOO = 1


class RunningMode(Enum):
    EXECUTABLE = 1
    NONINTERACTIVE = 2
    INTERACTIVE = 3


# DIRECTORY PATHS
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    RUN_MODE = RunningMode.EXECUTABLE  # From an EXE
else:
    try:
        # app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(__file__)
        RUN_MODE = RunningMode.NONINTERACTIVE  # (e.g. 'python myapp.py')
    except NameError:
        application_path = os.getcwd()
        RUN_MODE = RunningMode.INTERACTIVE  # No Clue

ROOT = str(Path(application_path))

# DEFAULT BOT OPTIONS
DEBUG_LOGS_ACTIVE = False
USE_PROXY = True
USE_HEADLESS = False
USE_USER_AGENT = True
FULL_PAGE_LOAD = True
USE_CATCHALL = False

CATCHALL_DOMAIN = ''
GMAIL_EMAIL = ''
GMAIL_PASSWORD = ''
LINUX_USER = False
DESIRED_INSTANCES = 10
DELAY_BETWEEN_THREAD_SPAWN = 2
DETAILED_OUTPUT = False


# URLS
TWO_CAPTCHA_URL_IN = 'https://2captcha.com/in.php'
TWO_CAPTCHA_URL_OUT = 'https://2captcha.com/res.php'
CAPTCHA_URL_YAHOO = 'https://login.yahoo.com/account/challenge/recaptcha?.src=fpctx&.intl=us&.lang=en-US&authMechanism=primary&display=login'

# KEYS
CAPTCHA_API_KEY = ''
CAPTCHA_YAHOO_DATA_SITE_KEY = '6LdI1RoUAAAAANLaawo9A_xn2t5rzAIQOdiBmEkh'

# DISCORD WEBHOOK
WEBHOOK = ''
