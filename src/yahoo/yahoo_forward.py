from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from src.handlers import proxy_handler, captcha_handler, thread_handler
from src.util import discord_webhook
from src.yahoo import get_email
import time
import config as CONFIG
import os
import queue
import random
import logging


def init():
    print('Beginning Email Forwarding...\n')
    logging.info('[Forward] Beginning Email Forwarding...')
    if CONFIG.DETAILED_OUTPUT:
        logging.info('Detailed Logging Enabled.')

    account_queue = None
    with open(CONFIG.ROOT + '/data/yahoo/yahoo_accounts.txt', 'r') as file:
        accounts = list(file.read().split())
        account_queue = queue.Queue()
        [account_queue.put(a) for a in accounts]

    first_names = None
    with open(CONFIG.ROOT + '/data/yahoo/first_names.txt', 'r') as file:
        first_names = list(file.read().split())

    return {
        'first_names': first_names,
        'account_queue': account_queue
    }


def run(stop_flag, shared_memory):
    # This email queue will be shared between all threads, and is a thread safe way
    # for them to grab the current email without grabbing another threads email
    while not stop_flag.is_set() and not shared_memory['account_queue'].empty():

        unparsed_account = shared_memory['account_queue'].get()

        result_from_parsing = [x.strip() for x in unparsed_account.split(':')]
        account = {
            'email': result_from_parsing[0],
            'password': result_from_parsing[1]
        }

        if account_already_forwarded(account['email']):
            continue

        driver = proxy_handler.get_chromedriver()

        # Setting up info
        first_name = random.choice(list(shared_memory['first_names']))

        if CONFIG.USE_CATCHALL:
            forward_email = first_name + str(random.randint(100, 999)) + "@" + CONFIG.CATCHALL_DOMAIN
        else:
            result_from_parsing = [x.strip() for x in CONFIG.GMAIL_EMAIL.split('@')]
            email = result_from_parsing[0]
            forward_email = email + "+" + str(random.randint(0, 99999)) + "@gmail.com"

        account['forward_email'] = forward_email

        successfully_forwarded = forward_yahoo(account, driver)

        if successfully_forwarded:
            print(account['email'] + " has been forwarded successfully!")
            logging.info('[Forward] ' + account['email'] + ' has been forwarded successfully!')

            write_account_to_file(account)
            discord_webhook.yahoo_email_forwarded(account['email'], account['forward_email'])
            driver.quit()

        else:
            shared_memory['account_queue'].put(account)
            print("Failed to forward email. Adding email back to queue.")
            logging.info('[Forward] Failed to forward email. Adding email back to queue.')
            driver.quit()


def forward_yahoo(account, driver):
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
                    counter = 0
                    driver.refresh()
                time.sleep(1)
                counter += 1

        time.sleep(1)
        if CONFIG.DETAILED_OUTPUT:
            logging.info("Logging in")


        while True:
            try:
                next_ele = driver.find_element_by_css_selector("input[id='login-signin']")
                driver.execute_script("arguments[0].click();", next_ele)
                break
            except NoSuchElementException:
                print('Cant Find Login button')
                time.sleep(1)

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

                # this is where we want to handle the Captchas
                if captcha_catcher == 0:

                    print("Hit Captcha on yahoo login")

                    # HANDLING CAPTCHA ONE
                    print("Attempting to handle first captcha...")
                    if CONFIG.DETAILED_OUTPUT:
                        logging.info('Hit Captcha: Solving...')

                    # must enter iframe's one by one to reach element
                    # try catch here? for NoSuchElementException?
                    try:
                        print('1')
                        outerIFrame = driver.find_element_by_id('recaptcha-iframe')
                        print('2')
                    except NoSuchElementException:
                        time.sleep(2)
                        continue

                    driver.switch_to.frame(outerIFrame)
                    print('3')
                    innerIFrame = driver.find_element_by_xpath("//iframe")
                    driver.switch_to.frame(innerIFrame)

                    # make token box visible, then submit

                    try:
                        tokenBox = driver.find_element_by_id('recaptcha-token')
                    except NoSuchElementException:
                        return False

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
                    if CONFIG.DETAILED_OUTPUT:
                        logging.info('Hit Captcha: Captcha Solved!')

                    # now that we are done, we must backtrack back out of the iframes to default view
                    driver.switch_to.default_content()

        time.sleep(.5)
        next_ele = driver.find_element_by_id('login-signin')
        driver.execute_script("arguments[0].click();", next_ele)

        time.sleep(1)

        driver.get('https://mail.yahoo.com/d/settings/1')

        counter = 0
        while True:
            try:
                driver.find_element_by_css_selector("li[data-test-id='accounts-list-item']").click()
                time.sleep(.5)
                break
            except NoSuchElementException:
                if counter == 5:
                    #print("Possible 2nd Stall, Refresh")
                    driver.refresh()
                time.sleep(1)
                counter += 1
            except ElementClickInterceptedException:
                driver.find_element_by_xpath('//*[@id="modal-outer"]/div/div/div[3]/div[5]/button').click()

        time.sleep(.5)
        go_to_next_account = False
        counter = 0
        while True:
            try:
                driver.find_element_by_name('stateForwardEmail').send_keys(Keys.CONTROL + "a");
                driver.find_element_by_name('stateForwardEmail').send_keys(Keys.DELETE);
                driver.find_element_by_name('stateForwardEmail').send_keys(account['forward_email'])
                time.sleep(.5)
                break
            except NoSuchElementException:
                time.sleep(1)
                counter += 1
            except ElementNotInteractableException:
                counter += 1
                if counter == 5:
                    go_to_next_account = True
                    break

        if go_to_next_account:
            print("This account has already been forwarded, move to next account.")
            if CONFIG.DETAILED_OUTPUT:
                logging.info("This account has already been forwarded, move to next account.")
            return True

        time.sleep(.5)
        while True:
            try:
                driver.find_element_by_css_selector("button[data-test-id='accounts-verify-forwarding-btn']").click()
                time.sleep(.5)
                break
            except NoSuchElementException:
                time.sleep(1)

        time.sleep(.5)

        if CONFIG.DETAILED_OUTPUT:
            logging.info('Entered Forwarder, Waiting for Email...')
        url = get_verify_url(account['forward_email'])
        if url == 'ERROR':
            return False


        if CONFIG.DETAILED_OUTPUT:
            logging.info('Email Found!')

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        # print(url)
        driver.get(str(url))

        while True:
            try:
                print('3')
                driver.find_element_by_xpath('//*[@id="Stencil"]/body/div[2]/div[2]/div/form/input[4]').click()
                break
            except NoSuchElementException:
                try:
                    driver.find_element_by_xpath('//*[@id="consent-page"]/div/div/div/div[3]/div/form/button[1]').click()
                except Exception as e:
                    time.sleep(1)
                time.sleep(.1)

        time.sleep(1)
        # print('Email Verified')

        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        while True:
            try:
                next_ele = driver.find_element_by_id('ybarAccountMenu')
                driver.execute_script("arguments[0].click();", next_ele)
                break
            except NoSuchElementException:
                time.sleep(.1)

        time.sleep(.5)
        stuck = 0
        while True:
            try:
                next_ele = driver.find_element_by_css_selector("a[data-ylk='sec:yb_accounts;slk:sign out;itc:0;']")
                driver.execute_script("arguments[0].click();", next_ele)
                #print('Clicked!')
                break
            except NoSuchElementException:
                #print('Stuck')
                stuck += 1
                if stuck == 10:
                    break
                time.sleep(.5)

        time.sleep(.5)
        stuck = 0
        while True:
            try:
                next_ele = driver.find_element_by_xpath('//*[@id="login-body"]/div[2]/div[1]/div[2]/form/input[2]')
                driver.execute_script("arguments[0].click();", next_ele)
                if CONFIG.DETAILED_OUTPUT:
                    logging.info('Signed out!')
                #print('Clicked sign out!')
                break
            except NoSuchElementException:
                if stuck == 10:
                    break
                elif stuck == 5:
                    if CONFIG.DETAILED_OUTPUT:
                        logging.info('Stall on Sign Out')
                stuck += 1
                #print('Stuck on Final')
                time.sleep(.5)

        return True


def account_already_forwarded(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/yahoo/forwarded_yahoo.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'r') as file:
        return account in file.read()


def write_account_to_file(account):
    OUTPUT_FILE_PATH = CONFIG.ROOT + '/output/yahoo/forwarded_yahoo.txt'

    if not os.path.exists(OUTPUT_FILE_PATH):
        file = open(OUTPUT_FILE_PATH, 'w+')
        file.close()

    with open(OUTPUT_FILE_PATH, 'a+') as file:
        file.write(account['email'] + '\n')


def get_verify_url(forwarded_email):
    time.sleep(4)
    count = 0
    while True:
        url = get_email.read_email_from_gmail(forwarded_email)
        if url == 'not_found':
            time.sleep(2)
            count += 1
        else:
            break

        if count > 30:
            return 'ERROR'
    return url


def shutdown():
    print('All Yahoo Emails have been forwarded!\n')
    discord_webhook.yahoo_forward_complete()
    logging.info('[Forward] All Yahoo Emails have been forwarded!')
