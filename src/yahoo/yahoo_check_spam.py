from src.handlers import captcha_handler, proxy_handler, thread_handler
from src.util import discord_webhook
from selenium.webdriver.common.keys import Keys
import config as CONFIG
import queue
import time
import os
import logging
from selenium.common.exceptions import NoSuchElementException


def init():
    print("Beginning Spam Checking...\n")
    logging.info('Beginning Spam Checking...')

    account_queue = None
    with open(CONFIG.ROOT + '/data/yahoo/yahoo_accounts.txt', 'r') as file:
        accounts = list(file.read().split())
        account_queue = queue.Queue()
        [account_queue.put(a) for a in accounts]

    return {
        'account_queue': account_queue
    }


def run(stop_flag, shared_memory):
    while not stop_flag.is_set() and not shared_memory['account_queue'].empty():
        unparsed_account = shared_memory['account_queue'].get()

        result_from_parsing = [x.strip() for x in unparsed_account.split(':')]
        account = {
            'email': result_from_parsing[0],
            'password': result_from_parsing[1]
        }

        if account_already_entered(account['email']):
            continue

        driver = proxy_handler.get_chromedriver()

        successfully_entered = check_spam(driver, account)

        if successfully_entered:
            write_account_to_file(account)
            print(account['email'] + " has been checked for spam!")
            logging.info(account['email'] + ' has been checked for spam!')

            driver.close()

        else:
            shared_memory['account_queue'].put(account)
            print("Failed to check email. Adding email back to queue.")
            logging.info("Failed to check email. Adding email back to queue.")
            driver.close()


def check_spam(driver, account):
    start_time = time.time()

    driver.get(
        'https://login.yahoo.com/config/login?.src=fpctx&.intl=us&.lang=en-US&.done=https%3A%2F%2Fwww.yahoo.com')

    counter = 0
    while True:
        try:
            driver.find_element_by_id('login-username').send_keys(account['email'])
            time.sleep(1)
            break
        except NoSuchElementException:
            if counter == 5:
                # print("Possible Stall, Refresh")
                counter = 0
                driver.refresh()
            time.sleep(1)
            counter += 1

    time.sleep(1)
    next_ele = driver.find_element_by_css_selector(
        "input[data-ylk='elm:btn;elmt:primary;mKey:primary_login_config-login_primaryBtn']")
    driver.execute_script("arguments[0].click();", next_ele)
    time.sleep(3)
    captcha_catcher = 5
    while True:
        try:
            driver.find_element_by_id('login-passwd').send_keys(account['password'])
            time.sleep(1)
            break
        except NoSuchElementException:
            captcha_catcher = captcha_catcher - 1
            time.sleep(1)

            # this is where we want to handle the captchas
            if captcha_catcher == 0:
                # OLD Solution - restart
                # print("Closing driver due to captcha hit. Restarting...")
                # driver.close()
                # forward_yahoos()

                print("Hit Captcha on yahoo login")

                # HANDLING CAPTCHA ONE
                print("Attempting to handle first captcha...")

                # must enter iframe's one by one to reach element
                # try catch here? for NoSuchElementException?
                try:
                    outerIFrame = driver.find_element_by_id('recaptcha-iframe')
                except NoSuchElementException:
                    time.sleep(2)
                    continue

                driver.switch_to.frame(outerIFrame)

                innerIFrame = driver.find_element_by_xpath("//iframe")
                driver.switch_to.frame(innerIFrame)

                # make token box visible, then submit
                tokenBox = driver.find_element_by_id('recaptcha-token')
                driver.execute_script("arguments[0].type='form';", tokenBox)
                tokenBox.send_keys(Keys.RETURN)

                # now that we are done, we must backtrack back out of the iframes to default view
                driver.switch_to.default_content()

                print("Passed first captcha!\n")

                # HANDLING CAPTCHA TWO
                print("Attempting to handle second captcha...")

                frame = driver.find_element_by_id('recaptcha-iframe')
                driver.switch_to.frame(frame)

                # setting captcha token
                captcha_token = captcha_handler.handle_captcha(CONFIG.CaptchaType.CAPTCHA_YAHOO)
                set_token_script = "document.getElementById('g-recaptcha-response').innerHTML='%s';" % captcha_token
                driver.execute_script(set_token_script)

                submit_token_script = "document.getElementById('recaptchaForm').submit();"
                driver.execute_script(submit_token_script)

                print("Passed second captcha!")

                # now that we are done, we must backtrack back out of the iframes to default view
                driver.switch_to.default_content()

    time.sleep(.5)
    next_ele = driver.find_element_by_id('login-signin')
    driver.execute_script("arguments[0].click();", next_ele)

    time.sleep(1)

    driver.get('https://mail.yahoo.com/d/folders/6')

    time.sleep(.5)
    go_to_next_account = False
    counter = 0
    while True:
        time.sleep(8)
        try:
            # print('Check Emails')
            emails = driver.find_elements_by_xpath("//span[@data-test-id='message-subject']")
            for email in emails:
                print(email.text)
                if 'CONGRATULATIONS' in email.text or 'Winner' in email.text:
                    discord_webhook.yahoo_email_spam(account, winner='True!')
                    print('Winner Found!')
                    logging.info(account['email'] + " - Winner Found!")
                    # send to discord
                else:
                    print('Possible Winner')
                    print(email.text)
                    logging.info(account['email'] + ' has spam. Manually check.')
                    #discord_webhook.yahoo_email_spam(account, winner='Unknown?')

            break
        except NoSuchElementException:
            print('No Emails')
            counter += 1
            if counter == 5:
                go_to_next_account = True
                break

    success = True

    return success


def account_already_entered(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/yahoo/spam_checked.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return account in file.read()


def write_account_to_file(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/yahoo/spam_checked.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(account['email'] + '\n')


def shutdown():
    print("\nThere are no more accounts remaining to enter raffles! Shutting down.")
