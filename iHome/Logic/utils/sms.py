# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from Logic.libs.yuntongxun.CCPRestSDK import REST

# 主帐号
accountSid = '8aaf070862fae1b501630b90f74b08bf';

# 主帐号Token
accountToken = '7514a43fddb6495a891749d16db7661e';

# 应用Id
appId = '8aaf070862fae1b501630b90f7a708c5';

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com';

# 请求端口
serverPort = '8883';

# REST版本号
softVersion = '2013-12-26';


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

class CCPR(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCPR, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
            return cls._instance

    def sendTemplateSMS(self, to, datas, temp_id):
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        if result.get("statusCode") == "000000":
            return 1
        else:
            return 0


if __name__ == '__main__':
    cp = CCPR()
    cp.sendTemplateSMS("15010286502", ["5211314", "5"], "1")
