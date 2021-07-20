import logging
import time

from requests import post, get
from scrapy_app.settings import CAPTCHA_API_KEY, RECAPTCHA_SITE_KEY


class CaptchaUpload:
    def __init__(self, site_key=RECAPTCHA_SITE_KEY, wait_time=2):
        self.settings = {
            "site_key": site_key,
            "wait_time": wait_time
        }

    def solve(self, page_url='', solved_list=[]):
        payload = {
            'key': CAPTCHA_API_KEY,
            'googlekey': self.settings['site_key'],
            'f': 'userrecaptcha',
            'pageurl': page_url
        }
        logging.info('Start solving captcha')
        request = post('http://2captcha.com/in.php', data=payload)
        logging.info(payload)
        if request.ok and request.text.split('|')[0] == "OK":
            solution_id = request.text.split('|')[1]
            full_url = 'http://2captcha.com/res.php?key={}&action=get&id={}'.format(CAPTCHA_API_KEY, solution_id)
            logging.info('2captcha solution url: {}'.format(full_url))
            time.sleep(10)
            return self.getresult(full_url, solved_list)
        else:
            raise ValueError(request.text)

    def getresult(self, full_url, solved_list=[]):
        time.sleep(self.settings['wait_time'])
        request = get(full_url)
        if request.text.split('|')[0] == "OK":
            logging.info('2captcha response: {}...'.format(request.text[:90]))
            result = request.text.split('|')[1]
            solved_list.append(result)
            return result

        elif request.text == "CAPCHA_NOT_READY":
            logging.debug('Captcha not ready')
            return self.getresult(full_url, solved_list)

        else:
            logging.info(request.text)
            raise ValueError(request.text)
