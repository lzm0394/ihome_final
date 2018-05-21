# _*_ coding:utf-8 _*_
""""
create by lu
"""
import qiniu

from Logic import constants

create_time = '2018/5/8 19:56'

from qiniu import Auth

access_key = "yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW"
secret_key = "bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW"

bucket_name = "ihome"


def upload_image(data):
    q = Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, None, data)
    if ret is not None:
        print constants.QINIU_DOMIN_PREFIX + ret.get("key")
        return ret.get("key")
    else:
        raise Exception("上传图片错误")


if __name__ == '__main__':
    file_name = raw_input("请输入图片地址")
    with open(file_name, "rb") as f:
        upload_image(f.read())
