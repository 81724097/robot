#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        )

'''
1. overload requests.Session.request
'''
class SafeSession(requests.Session):
    def request(self, method, url, params=None, data=None, headers=None,
            cookies=None, files=None, auth=None, timeout=None, allow_redirects=True,
            proxies=None, hooks=None, stream=None, verify=None, cert=None, json=None):
        for i in xrange(3):
            try:
                return super(SafeSession, self).request(method, url, params,
                        data, headers, cookies, files, auth, timeout, allow_redirects,
                        proxies, hooks, stream, verify, cert, json)
            except Exception,e:
                logging.error("Session call request exception:[%s]" % str(e))
                continue
        return None
