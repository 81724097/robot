
**weixin_rebot** 用Python实现的一个web微信机器人。

## 依赖
```
1. linux: 
   1). ubuntu 12.04
   2). sudo apt-get install imagemagick
2 python:
   1). version > 2.6
   2). pip install requests
   3). pip install pypng
   4). pip install Pillow
   5). pip install pyopenssl ndg-httpsclient pyasn1
```

## web微信Api
```
1. 获取uuid
   1). 说明: 微信Web版本不使用用户名和密码登录，而是采用二维码登录，所以服务器需要首先分配一个唯一的会话ID，用来标识当前的一次登录
   2). api: https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&redirect_uri=https%3A%2F%2Fwx.qq.com%2Fcgi-bin%2Fmmwebwx-bin%2Fwebwxnewloginpage&fun=new&lang=zh_CN&_=1467390116155
   3). get 请求
   3). 参数说明:
        a. appid 固定值wx782c26e4c19acffb表示微信网页版
        b. redirect_uri 固定值
        c. fun 固定值 new
        d. lang 固定值 表示中文
        e. _ 表示13位时间戳
2. 获取登录二维码
   1). 说明: get请求拿到数据，再保存为图片并展示
   2). api: https://login.weixin.qq.com/qrcode/xxxx
   3). get 请求
   4). 参数说明:
       a. xxxx表示uuid
3. 扫描二维码等待用户确认
   1). 说明: 当用户拿到二维码数据之后，用户需要扫描二维码并点击确认登录
   2). api: https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?uuid=454d958c7f6243&tip=1&_=1388975883859
   3). get 请求
   4). 参数说明
       a. uuid 表示当前uuid
       b. tip
          1->表示的是未扫描，等待用户扫描。返回window.code=201表示扫描成功，返回window.code=408表示扫描超时
          0->表示等待用户确认登录。返回window.code=200;window.redirect_uri="https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage?ticket=AWskQEu2O8VUs7Wf2TVOH8UW@qrticket_0&uuid=IZu2xb_hIQ==&lang=zh_CN&scan=1467393709"; 表示登录成功
       c. _表示当前时间戳，13位
```

## 参考
```
1. https://github.com/xiangzhai/qwx/blob/master/doc/protocol.md
2. https://github.com/Urinx/WeixinBot
3. https://github.com/liuwons/wxBot
```
