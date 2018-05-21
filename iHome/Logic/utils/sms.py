# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from Logic.libs.yuntongxun.CCPRestSDK import REST

# ���ʺ�
accountSid = '8aaf070862fae1b501630b90f74b08bf';

# ���ʺ�Token
accountToken = '7514a43fddb6495a891749d16db7661e';

# Ӧ��Id
appId = '8aaf070862fae1b501630b90f7a708c5';

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com';

# ����˿�
serverPort = '8883';

# REST�汾��
softVersion = '2013-12-26';


# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id

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
