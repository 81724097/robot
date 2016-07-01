
**weixin_rebot** 用Python实现的一个web微信机器人。

## web微信Api
```
1. api: https://login.wx.qq.com/jslogin?appid=wx782c26e4c19acffb&fun=new&lang=zh_CN&_=1467219164569
2. method: post
3. params: appid: //应用ID, 值为wx782c26e4c19acffb,表示"微信网页版"
           fun: new //应用类型, 固定为new
           lang: zh_CN //语言, 表示中文
           _:  //时间戳
4. 返回值: window.QRLogin.code = 200; window.QRLogin.uuid = "xxx"
5. uuid，是生成二维码登陆的必要参数
6. 生成二维码链接: https://login.weixin.qq.com/l/xxxx, xxxx表示uuid
```
## 依赖
```
1. python:
   a. version > 2.6
   b. pip install requests
   c. pip install pyqrcode
   d. pip install pypng
   e. pip install Pillow
   f. pip install pyopenssl ndg-httpsclient pyasn1
```
