import zipfile
import random
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import config

proxy_file = '/data/proxies/proxies.txt'

with open(config.ROOT + proxy_file, "r") as file:
    random_proxy = random.choice(list((file.read().splitlines())))

proxy_parsed = [x.strip() for x in random_proxy.split(':')]


CURRENT_HOST = proxy_parsed[0]
CURRENT_PORT = proxy_parsed[1]

try:
    CURRENT_USER = proxy_parsed[2]
    CURRENT_PASS = proxy_parsed[3]
except IndexError:
    CURRENT_USER = 'user'
    CURRENT_PASS = 'pass'


# Getting a random proxy for this run of the bot.
def set_random_proxy():
    with open(config.ROOT + proxy_file, "r") as file:
        r_proxy = random.choice(list((file.read().splitlines())))

    p_parsed = [x.strip() for x in r_proxy.split(':')]

    global CURRENT_HOST
    global CURRENT_PORT
    global CURRENT_USER
    global CURRENT_PASS
    global background_js

    CURRENT_HOST = p_parsed[0]
    CURRENT_PORT = p_parsed[1]

    try:
        CURRENT_USER = proxy_parsed[2]
        CURRENT_PASS = proxy_parsed[3]
    except IndexError:
        CURRENT_USER = 'user'
        CURRENT_PASS = 'pass'

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (CURRENT_HOST, CURRENT_PORT, CURRENT_USER, CURRENT_PASS)


# Used to dynamically set the proxy every run
manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
          singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
          },
          bypassList: ["localhost"]
        }
      };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (CURRENT_HOST, CURRENT_PORT, CURRENT_USER, CURRENT_PASS)


def get_proxy():
    return {
        'HOST': CURRENT_HOST,
        'PORT': CURRENT_PORT,
        'USER': CURRENT_USER,
        'PASS': CURRENT_PASS
    }


def get_chromedriver():
    # print("Initializing bot, setting options...")

    if config.LINUX_USER:
        chrome_path = config.ROOT + '/data/driver/chromedriver'
    else:
        chrome_path = config.ROOT + '/data/driver/chromedriver.exe'
        
    chrome_options = webdriver.ChromeOptions()

    if config.USE_HEADLESS:
        chrome_options.headless = True

    if config.USE_PROXY:
        set_random_proxy()
        plugin_file = config.ROOT + '/data/driver/proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        chrome_options.add_extension(plugin_file)

    if config.USE_USER_AGENT:
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        chrome_options.add_argument('--user-agent=%s' % user_agent)

    caps = DesiredCapabilities().CHROME
    chrome_options.add_argument('hidden')

    if config.FULL_PAGE_LOAD == True:
        caps["pageLoadStrategy"] = "normal"  # complete
    else:
        caps["pageLoadStrategy"] = "none"

    driver = webdriver.Chrome(desired_capabilities=caps, executable_path=chrome_path, chrome_options=chrome_options)
    return driver
