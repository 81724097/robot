#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
import time
import json
import random
import urllib2
import logging
import pyqrcode
import webbrowser
import config_parser
import safe_session
from PIL import Image
from StringIO import StringIO

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        )

"""
WeiXinReBot功能类
"""
class WeiXinReBot(object):
    def __init__(self):
        self.config_dict = config_parser.ReadConfig('./conf.dat')
        self.session = safe_session.SafeSession()
        self.session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'})
        self.uuid = self.__init_uuid__()

    def __init_uuid__(self):
        '''
        1. web weixin api
           api: https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage&fun=new&lang=zh_CN&_=1467300063012
        2. return: window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"
        '''
        logging.info("Start init uuid ...")
        get_uuid_url = self.config_dict['login']['get_uuid_url']
        response = self.session.get(get_uuid_url)
        if response is None or response.content == "":
            logging.error("get uuid request return None response")
            return ''
        logging.info("login weixin return content:[%s]" % response.content)
        res = re.search('window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"', response.content)
        if res is not None:
            code = res.group(1)
            uuid = res.group(2)
            logging.info("### weixin uuid:[%s]" % uuid)
            return uuid
        logging.info("Fail init uuid")
        return ''

    def __gen_qr_code__(self):
        '''
        1. web weixin qrcode api: https://login.weixin.qq.com/l/xxx
           xxx -> uuid
        2. method: get
        3. generate QR code
        '''
        logging.info("Start generate QR code ...")
        get_qrcode_url = self.config_dict['login']['get_qrcode_url'] % self.uuid
        response = self.session.get(get_qrcode_url)
        if response is None or response.content == "":
            logging.error("get QR code request return None response")
            return False
        qrcode_image = Image.open(StringIO(response.content))
        qrcode_image.show()
        logging.info("Success generate QR code")
        return True

    def __wait_scan_qrcode__(self):
        '''
        1. 扫描二维码链接
           api: https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s
           uuid: uuid
           tip: 1->未扫描
                  201: wait user confirm to login
                  408: timeout
           _: 时间戳, 10 bit
        2. return text
        '''
        logging.info("Wait use wechat scan QR code...")
        base_qrcode_url = self.config_dict['login']['scan_qrcode_url']
        scan_qrcode_url = base_qrcode_url % ("1", self.uuid, str(int(round(time.time() * 1000))))
        time_count = 0
        while True:
            response = self.session.get(scan_qrcode_url)
            if response is None or response.content == "":
                logging.error("scan qr code request return None response")
                return False
            content = response.content
            res = re.search('window.code=(\d+);', content)
            if res is not None:
                code = res.group(1)
                if code == "201":
                    logging.info("Success scan QR code")
                    return True
            time.sleep(1)
            time_count = time_count + 1
            # timeout 30 seconds
            if time_count == 30:
                break
        logging.error("Timeout scan QR code")
        return False

    def __wait_click_confirm__(self):
        '''
        1. 扫描二维码链接
           api: https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s
           uuid: uuid
           tip: 0->已扫描
                  200: confirmed
           _: 时间戳, 10 bit
        2. return text
        '''
        logging.info("Wait user confirm login ...")
        base_qrcode_url = self.config_dict['login']['scan_qrcode_url']
        scan_qrcode_url = base_qrcode_url % ("0", self.uuid, str(int(round(time.time() * 1000))))
        time_count = 0
        while True:
            response = self.session.get(scan_qrcode_url)
            if response is None or response.content == "":
                logging.error("confirm click login request return None response")
                return False
            content = response.content
            res = re.search('window.code=(\d+);', content)
            if res is not None:
                code = res.group(1)
                if code == "200":
                    param = re.search('window.redirect_uri="(\S+?)";', content)
                    redirect_uri = param.group(1) + '&fun=new'
                    self.redirect_uri = redirect_uri
                    logging.info("login wechat success")
                    return True
            time.sleep(1)
            time_count = time_count + 1
            # timeout 30 seconds
            if time_count == 30:
                break
        logging.error("Timeout wait user confirm login")
        return False

    def __get_init_feature__(self):
        '''
        1. redirect_uri: https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AaJ04ugr4H62BcjrEqfVXeOP@qrticket_0&uuid=wff0X123zQ==&lang=zh_CN&scan=1467425289&fun=new&version=v2
        2. method: get
        3. return xml
        '''
        logging.info("Start to login wechat ...")
        response = self.session.get(self.redirect_uri)
        if response is None or response.content == "":
            logging.error("get wxuin and wesid request return None response")
            return False
        content = response.content
        self.wxuin = content[content.find('wxuin>')+len('wxuin>'):content.find('</wxuin')]
        self.wxsid = content[content.find('wxsid>')+len('wxsid>'):content.find('</wxsid')]
        self.pass_ticket = content[content.find('pass_ticket>')+len('pass_ticket>'):content.find('</pass_ticket')]
        self.skey = content[content.find('skey>')+len('skey>'):content.find('</skey')]
        self.device_id = 'e' + str(random.random())[2:17]
        logging.info("### weixin uin:[%s]" % self.wxuin)
        logging.info("### weixin sid:[%s]" % self.wxsid)
        logging.info("### weixin skey:[%s]" % self.skey)
        logging.info("Success login wechat")
        return True

    def __init_wechat__(self):
        '''
        1. api: https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit?r=%s&lang=zh_CN&pass_ticket=%s
        2. method: post
        3. data = {
              'BaseRequest': self.base_request_dict
           }
           Objecy = {
              'Uin': self.wxuin,
              'Sid': self.wxsid,
              'Skey': self.skey,
              'DeviceID': self.device_id
           }
        4. return json
        '''
        logging.info("Start to init wechat ...")
        init_wechat_url = self.config_dict['login']['init_wechat_url'] % (str(int(time.time())),self.pass_ticket)
        self.base_request_dict = {
            'Uin': self.wxuin,
            'Sid': self.wxsid,
            'Skey': self.skey,
            'DeviceID': self.device_id
        }
        json_data = {
            'BaseRequest': self.base_request_dict
        }
        """
        # def post(self, url, data=None, json=None, **kwargs):
        # Sends a POST request. Returns :class:`Response` object.
          a. url: URL for the new :class:`Request` object.
          b. data: (optional) Dictionary, bytes, or file-like object to send in the body of the :class:`Request`.
          c. json: (optional) json to send in the body of the :class:`Request`.
          d. \*\*kwargs: Optional arguments that ``request`` takes.
        # 如果使用data参数需要把字典序列化为字符串
        # 如果使用json参数直接使用dict即可
        """
        response = self.session.post(init_wechat_url, json=json_data)
        if response is None or response.content == "":
            logging.error("init wechat request return None response")
            return False
        content = response.content
        json_dict = json.loads(content)
        if 'BaseResponse' not in json_dict or 'Ret' not in json_dict['BaseResponse'] or \
            json_dict['BaseResponse']['Ret'] != 0:
            logging.error("init wechat request return non 0 status")
            return False
        if 'SyncKey' not in json_dict and 'User' not in json_dict:
            logging.error("init wechat response not found Synckey and User info")
            return False
        self.sync_key_dict = json_dict['SyncKey']
        self.user_info_dict = json_dict['User']
        self.sync_key = ""
        for keyVal in self.sync_key_dict['List']:
            self.sync_key = self.sync_key + '|' + str(keyVal['Key']) + '_' + str(keyVal['Val'])
        self.sync_key = self.sync_key[1:]
        logging.info("### weixin user uin:[%s]" % self.user_info_dict['Uin'])
        logging.info("### weixin user UserName:[%s]" % self.user_info_dict['UserName'].encode('utf-8'))
        logging.info("### weixin user NickName:[%s]" % self.user_info_dict['NickName'].encode('utf-8'))
        logging.info("Success init wechat")
        return True

    def __status_notify__(self):
        '''
        1. api: https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify?lang=zh_CN&pass_ticket=%s
        2. method: post
        3. data = {
              'BaseRequest': self.base_request_dict
              'ClientMsgId': 1467442584656,
              'Code': 3,
              'FromUserName': '@6d3d989396c0160e7f70b8bce436842f',
              'ToUserName': '@6d3d989396c0160e7f70b8bce436842f'
           }
           Objecy = {
              'Uin': self.wxuin,
              'Sid': self.wxsid,
              'Skey': self.skey,
              'DeviceID': self.device_id
           }
        '''
        logging.info("Start to status notify ...")
        status_notify_url = self.config_dict['login']['status_notify_url']
        json_data = {
            'BaseRequest': self.base_request_dict,
            'ClientMsgId': str(int(round(time.time()*1000))),
            'Code': '3',
            'FromUserName': self.user_info_dict['UserName'],
            'ToUserName': self.user_info_dict['UserName']
        }
        response = self.session.post(status_notify_url, json=json_data)
        if response is None or response.content == "":
            logging.error("status notify request return None response")
            return False
        content = response.content
        json_dict = json.loads(content)
        if 'BaseResponse' not in json_dict or 'Ret' not in json_dict['BaseResponse'] or \
            json_dict['BaseResponse']['Ret'] != 0:
            logging.error("status notify request return non 0 status")
            return False
        logging.info("Success status notify")
        return True

    def __get_all_contact__(self):
        logging.info("Start to get all contact ...")
        get_all_contact_url = self.config_dict['login']['get_all_contact_url']
        get_all_contact_url = get_all_contact_url % (self.pass_ticket, str(int(round(time.time()*1000))), self.skey)
        response = self.session.get(get_all_contact_url)
        if response is None or response.content == "":
            logging.error("get all contact request return None response")
            return False
        json_dict = json.loads(response.content)
        if 'BaseResponse' not in json_dict or 'Ret' not in json_dict['BaseResponse'] or \
            json_dict['BaseResponse']['Ret'] != 0:
            logging.error("get all contact request return non 0 status")
            return False
        if 'MemberList' not in json_dict:
            logging.error("get empty member list")
            return False
        self.__contact_classify__(json_dict['MemberList'])
        logging.info("Success get all contact")
        return True

    def __contact_classify__(self, member_list):
        logging.info("Start to classify contact ...")
        self.contact_account = {}
        # 朋友和群聊
        self.contact_account['normal_account'] = {}
        # 其它,包括公众号
        self.contact_account['public_account'] = {}
        for contact_dict in member_list:
            nick_name = contact_dict['NickName']
            if contact_dict['VerifyFlag'] == 0:
                self.contact_account['normal_account'][nick_name] = contact_dict
            else:
                self.contact_account['public_account'][nick_name] = contact_dict
        logging.info("Success classify contact")

    def __sync_check__(self):
        '''
        1. api: https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck?r=%s&skey=%s&synckey=%s&_=%s
        '''
        sync_check_url = self.config_dict['login']['sync_check_url']
        sync_check_url = sync_check_url % (str(int(round(time.time()*1000))), urllib2.quote(self.skey), \
                self.wxsid, self.wxuin, self.device_id, urllib2.quote(self.sync_key), str(int(round(time.time()*1000))))
        response = self.session.get(sync_check_url)
        if response is None or response.content == "":
            logging.error("sync check request return None response")
            return '',''
        res = re.search('window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', response.content)
        if res is not None:
            return res.group(1), res.group(2)
        return '',''

    def __msg_sync__(self):
        '''
        1. https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync?sid=wDCsuyX6ixU3N0XA&skey=@crypt_b13bcf4_aa0d114617b55682becd6ce87667d0a3&lang=zh_CN&pass_ticket=Skm2wlMgbeHdlMxRyAiHnsdgZnVYdezqAb9p8LQYt2ODwzPZ521ZFhAeUEaDTw7S
        2. post
        3. post data
           {
              'BaseRequest': {
                  'Uin': self.wxuin,
                  'Sid': self.wxsid,
                  'Skey': self.skey,
                  'DeviceID': self.device_id
              },
              'SyncKey': self.sync_key_dict,
              'rr': 时间戳取反
           }
        '''
        msg_sync_url = self.config_dict['login']['msg_sync_url'] % (self.wxsid, self.skey, self.pass_ticket)
        json_data = {
            'BaseRequest': self.base_request_dict,
            'SyncKey': self.sync_key_dict,
            'rr': str(~int(time.time()))
        }
        response = self.session.post(msg_sync_url, json=json_data)
        if response is None or response.content == "":
            logging.error("message sync return None response")
            return None
        content = response.content
        json_dict = json.loads(content)
        if 'BaseResponse' not in json_dict or 'Ret' not in json_dict['BaseResponse'] or \
            json_dict['BaseResponse']['Ret'] != 0:
            logging.error("message sync request return non 0 status")
            return None
        self.sync_key_dict = json_dict['SyncKey']
        self.sync_key = ""
        for keyVal in self.sync_key_dict['List']:
            self.sync_key = self.sync_key + '|' + str(keyVal['Key']) + '_' + str(keyVal['Val'])
        self.sync_key = self.sync_key[1:]
        return json_dict['AddMsgList']

    def process_message(self, msg_list):
        for msg in msg_list:
            if msg['MsgType'] == 51: continue
            print msg
        send_message_url = self.config_dict['login']['send_message_url']
        msg_id = str(int(time.time() * 1000)) + str(random.random())[:5].replace('.', '')
        word = "hello son"
        json_data = {
            'BaseRequest': self.base_request_dict,
            'Msg': {
                "Type": 1,
                "Content": word,
                "FromUserName": self.contact_account['normal_account'][u'陈国林']['UserName'],
                "ToUserName": self.contact_account['normal_account'][u'林周治']['UserName'],
                "LocalID": msg_id,
                "ClientMsgId": msg_id
            }
        }
        headers = {'content-type': 'application/json; charset=UTF-8'}
        self.session.post(send_message_url, json=json_data, headers=headers)

    def instant_message(self):
        logging.info("Start receive and send message ...")
        while True:
            try:
                retcode, selector = self.__sync_check__()
                print retcode, selector
                if retcode == '' or selector == '':
                    logging.error("sync check return empty result, process exit" % str(e))
                    sys.exit(2)
                if retcode == '0':
                    if selector == '2':
                        msg_list = self.__msg_sync__()
                        #self.process_message(msg_list)
                    elif selector == '7':
                        msg_list = self.__msg_sync__()
                        #self.process_message(msg_list)
                    else:
                        pass
                elif retcode == '1100':
                    logging.info("check fail or log out wechat")
                    return
                elif retcode == '1101':
                    logging.info("other device login wechat")
                    return
            except Exception, e:
                logging.error("receive and send message exception:[%s]" % str(e))
                sys.exit(2)
            time.sleep(0.2)

    def run(self):
        logging.info("Start run weixin rebot ...")
        if self.__gen_qr_code__() is False:
            logging.error("Fail to generate QR code")
            sys.exit(2)
        if self.__wait_scan_qrcode__() is False:
            logging.error("Fail to scan QR code")
            sys.exit(2)
        if self.__wait_click_confirm__() is False:
            logging.error("Fail to click confirm button")
            sys.exit(2)
        if self.__get_init_feature__() is False:
            logging.error("Fail to get wxuin and wxsid")
            sys.exit(2)
        if self.__init_wechat__() is False:
            logging.error("Fail to init wechat")
            sys.exit(2)
        if self.__status_notify__() is False:
            logging.error("Fail to status notify")
            sys.exit(2)
        if self.__get_all_contact__() is False:
            logging.error("Fail to get all contact")
            sys.exit(2)
        self.instant_message()
        logging.info("Success run weixin rebot")
