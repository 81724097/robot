#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
from requests import Session

class SafeSession(requests.Session):
    def __init__(self):
        pass

    def request(self, method, url, params=None, data=None, headers=None, cookies=None, files=None, auth=None,
                timeout=None, allow_redirects=True, proxies=None, hooks=None, stream=None, verify=None, cert=None,
                json=None):
        for i in range(3):
            try:
                return super(SafeSession, self).request(method, url, params, data, headers, cookies, files, auth, timeout,
                        allow_redirects, proxies, hooks, stream, verify, cert, json)
            except Exception as e:
                print e.message, traceback.format_exc()
                continue
