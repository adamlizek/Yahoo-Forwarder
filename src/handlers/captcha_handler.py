import requests
import time
import re
import config


def handle_captcha(captcha_type):
    if config.DEBUG_LOGS_ACTIVE:
        print('\nHandling captcha of type ' + str(repr(captcha_type)))

    while True:
        response = send_captcha(captcha_type)

        if 'OK' in str(response):
            if config.DEBUG_LOGS_ACTIVE:
                print("Valid Captcha, sending to 2Captcha for solution.")

            break
        else:
            if config.DEBUG_LOGS_ACTIVE:
                print('Error sending captcha, retrying.')

            time.sleep(1)

    return receive_key(captcha_type, response)


def send_captcha(captcha_type):
    r = None

    if captcha_type == config.CaptchaType.CAPTCHA_YAHOO:
        data_site_key = config.CAPTCHA_YAHOO_DATA_SITE_KEY
        r = requests.get(config.TWO_CAPTCHA_URL_IN + '?key=' +
                         config.CAPTCHA_API_KEY + '&method=userrecaptcha&googlekey=' +
                         data_site_key + '&pageurl=' + config.CAPTCHA_URL_YAHOO)

    # sleep 5 seconds to allow captcha to complete
    time.sleep(5)
    return r.content


def receive_key(captcha_type, response):
    response = str(response)
    response_id = re.sub("[^0-9]", "", response)

    # loops to request solved captcha key from 2Captcha
    while True:
        r = requests.get(config.TWO_CAPTCHA_URL_OUT + '?key=' + config.CAPTCHA_API_KEY + '&action=get&id=' + response_id)

        response = str(r.content)

        if 'ERROR_CAPTCHA_UNSOLVABLE' in response:
            print('Captcha Bricked, Retrying')
            return 'Failed'

        response = response[2:4]
        if response == 'OK':
            if config.DEBUG_LOGS_ACTIVE:
                print('Captcha Solved!\n')

            break
        else:
            if config.DEBUG_LOGS_ACTIVE:
                print('Waiting for solution...')

            time.sleep(5)  # we want to limit requests to every ~5 seconds

    captcha_key = str(r.content)[5:-1]
    return captcha_key
