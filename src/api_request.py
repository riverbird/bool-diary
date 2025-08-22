import requests
import json

SHIQU_SERVICE_AUTH_TYPE = 'Bearer'
SHIQU_SERVICE_BASE_URL = 'https://restapi.10qu.com.cn'

class APIRequest(object):

    @staticmethod
    def login_by_password(username, password):
        user_input = {'username': username,
                      'password': password}
        req = requests.post(
            url='https://restapi.10qu.com.cn/username_login/',
            data=user_input
        )
        return req

    @staticmethod
    def send_sms(phone_num):
        user_input = {'mobile': phone_num}
        req = requests.post(
            url='https://restapi.10qu.com.cn/sms_code/',
            data=user_input
        )
        return req

    @staticmethod
    def login_by_code(phone_num, sms_code):
        user_input = {'mobile': phone_num,
                      'sms_code': sms_code}
        req = requests.post(
            url='https://restapi.10qu.com.cn/mobile_login/',
            data=user_input
        )
        json_req = json.loads(req.text)
        return json_req

    @staticmethod
    def logout(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(
            url=f'https://restapi.10qu.com.cn/logout/',
            headers=headers
        )
        json_req = json.loads(req.text)
        return json_req.get('code') == '0'

    @staticmethod
    def registry(username, password):
        user_input = {'custom_username': username,
                      'password': password}
        req = requests.post(
            url='https://restapi.10qu.com.cn/username_register/',
            data=user_input
        )
        json_req = json.loads(req.text)
        return json_req

    @staticmethod
    def query_user_info(token):
        headers = {'Authorization': f'Bearer {token}'}
        req = requests.get(
            url='https://restapi.10qu.com.cn/user_info/',
            headers=headers
        )
        json_req = json.loads(req.text)
        dct_ret = json_req.get('results')
        return dct_ret

