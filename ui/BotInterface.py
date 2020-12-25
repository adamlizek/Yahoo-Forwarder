import sys
import os
from PyQt5.QtWidgets import *
from ui.Logger import Logger
from src.multithreading.thread_manager import ThreadManager
import config
import json
from enum import Enum
import threading

from src.yahoo import yahoo_forward, yahoo_check_spam


class Mode(Enum):
    FORWARD_YAHOO = 1
    CHECK_SPAM = 2
    GENERATE_OUTLOOKS = 3


class BotInterface:
    def __init__(self):
        self.app = QApplication([])
        self.init_ui_components()
        sys.exit(self.app.exec_())

    def init_ui_components(self):
        self.window = QWidget()
        form = QFormLayout()

        user_json = config.ROOT + '/data/driver/USER_INFO.json'

        if not os.path.exists(user_json):
            user_info = {
                "CAPTCHA_API_KEY": "",
                "CATCHALL": "",
                "GMAIL": "",
                "PASSWORD": "",
                "WEBHOOK": ""
            }
            with open(user_json, 'w') as f:
                json.dump(user_info, f, indent=2)

        with open(user_json) as f:
            user_info = json.load(f)
        # 
        # KEYS
        #
        form.addRow(QLabel('<b>Keys:</b>'))
        
        self.captcha_api_key = QLineEdit(user_info["CAPTCHA_API_KEY"])
        form.addRow(QLabel('Captcha API Key: '), self.captcha_api_key)

        form.addRow(QLabel(''))

        # 
        # EMAIL CONFIG
        #
        form.addRow(QLabel('<b>Email Config:</b>'))

        self.catchall = QLineEdit(user_info["CATCHALL"])
        form.addRow(QLabel('Catchall Domain: '), self.catchall)

        self.gmail_email = QLineEdit(user_info["GMAIL"])
        form.addRow(QLabel('Gmail Email: '), self.gmail_email)

        self.gmail_password = QLineEdit(user_info["PASSWORD"])
        form.addRow(QLabel('Gmail Password: '), self.gmail_password)

        form.addRow(QLabel(''))


        # 
        # BOT CONFIG
        #
        form.addRow(QLabel('<b>Bot Config:</b>'))
        
        self.bot_mode = QComboBox()
        self.bot_mode.addItem('Forward Yahoos')
        self.bot_mode.addItem('Check Spam')
        form.addRow(QLabel('Bot Mode: '), self.bot_mode)

        self.forward_mode = QComboBox()
        self.forward_mode.addItem('Plus Trick')
        self.forward_mode.addItem('Forward to Catchall')
        form.addRow(QLabel('Forward Mode: '), self.forward_mode)

        self.desired_instances = QSpinBox()
        self.desired_instances.setMinimum(1)
        self.desired_instances.setMaximum(100)
        form.addRow(QLabel('Desired Instances of Bot: '), self.desired_instances)

        self.detailed_output_option = QCheckBox()
        form.addRow(QLabel('Detailed Output: '), self.detailed_output_option)

        form.addRow(QLabel(''))


        # 
        # EXTRAS
        #
        form.addRow(QLabel('<b>Extras:</b>'))

        self.discord_webhook = QLineEdit(user_info["WEBHOOK"])
        form.addRow(QLabel('Discord Webhook: '), self.discord_webhook)

        form.addRow(QLabel(''))

        # 
        # SUBMIT
        #
        self.start_bot_btn = QPushButton('START BOT')
        self.start_bot_btn.clicked.connect(self.start_btn_action)
        form.addRow(self.start_bot_btn)

        logger = Logger()
        logger.raise_()
        form.addRow(logger)

        # apply form to window and display
        self.window.setLayout(form)
        self.window.setWindowTitle("Bot Config")
        self.window.resize(600, 700)
        self.window.show()

    def start_btn_action(self):
        self.update_config()
        user_info = {
            "CAPTCHA_API_KEY": config.CAPTCHA_API_KEY,
            "CATCHALL": config.CATCHALL_DOMAIN,
            "GMAIL": config.GMAIL_EMAIL,
            "PASSWORD": config.GMAIL_PASSWORD,
            "WEBHOOK": config.WEBHOOK
        }
        with open(config.ROOT + '/data/driver/USER_INFO.json', 'w') as f:
            json.dump(user_info, f, indent=2)

        ui_thread = threading.Thread(target=self.run_bot)
        ui_thread.start()
    
    def update_config(self):
        config.CAPTCHA_API_KEY = self.captcha_api_key.text()
        config.CATCHALL_DOMAIN = self.catchall.text()
        config.DESIRED_INSTANCES = self.desired_instances.value()
        config.WEBHOOK = self.discord_webhook.text()
        config.GMAIL_EMAIL = self.gmail_email.text()
        config.GMAIL_PASSWORD = self.gmail_password.text()
        config.DETAILED_OUTPUT = self.detailed_output_option.isChecked()

        bot_mode_index = self.bot_mode.currentIndex()
        if bot_mode_index == 0:
            self.selected_action = Mode.FORWARD_YAHOO
        elif bot_mode_index == 1:
            self.selected_action = Mode.CHECK_SPAM
        else:
            self.selected_action = Mode.GENERATE_OUTLOOKS

        forward_mode_index = self.forward_mode.currentIndex()
        if forward_mode_index == 0:
            config.USE_CATCHALL = False
        else:
            config.USE_CATCHALL = True

    def display_error(self, text):
        error_box = QMessageBox()
        error_box.setText(text)
        error_box.setWindowTitle("Error!")
        error_box.exec_()

    def run_bot(self):
        thread_manager = ThreadManager()

        if self.selected_action == Mode.FORWARD_YAHOO:
            thread_manager.start_threads(yahoo_forward.run, yahoo_forward.init, config.DESIRED_INSTANCES)
        elif self.selected_action == Mode.CHECK_SPAM:
            thread_manager.start_threads(yahoo_check_spam.run, yahoo_check_spam.init, config.DESIRED_INSTANCES)
