# -*- coding: utf-8 -*-
# author: flower
# modified by shigure

import json
from base64 import b64encode

import requests


def get_g_tk(skey):
    key_hash = 5381
    for i in range(0, len(skey)):
        key_hash += (key_hash << 5) + ord(skey[i])
    return key_hash & 2147483647


def checkip(qzonetoken, g_tk, home_page):
    check_url = f'https://h5.qzone.qq.com/pc/api/checkip?qzonetoken={qzonetoken}&g_tk={g_tk}'
    data = {
        'format': 'fs',
        'qzreferrer': home_page
    }
    ret = requests.post(check_url, data)


def upload_img(qzonetoken, g_tk, p_skey, img, self_id, skey, headers):
    up_url = f'https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image?g_tk={g_tk}&qzonetoken={qzonetoken}&g_tk={g_tk}'
    data = {
        "filename": "filename",
        "uin": str(self_id),
        "skey": skey,
        "zzpaneluin": str(self_id),
        "zzpanelkey": "",
        "p_uin": str(self_id),
        "p_skey": p_skey,
        "qzonetoken": qzonetoken,
        "uploadtype": "1",
        "albumtype": "7",
        "exttype": "0",
        "refer": "shuoshuo",
        "output_type": "jsonhtml",
        "charset": "utf-8",
        "output_charset": "utf-8",
        "upload_hd": "1",
        "hd_width": "2048",
        "hd_height": "10000",
        "hd_quality": "96",
        "backUrls": "http://upbak.photo.qzone.qq.com/cgi-bin/upload/cgi_upload_image,http://119.147.64.75/cgi-bin/upload/cgi_upload_image",
        "url": "https://up.qzone.qq.com/cgi-bin/upload/cgi_upload_image?g_tk=" + str(g_tk),
        "base64": "1",
        "jsonhtml_callback": "callback",
        "picfile": img,
    }
    checkip(qzonetoken, g_tk, headers['Referer'])
    img_heders = headers.copy()
    img_heders['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
    img_heders['Sec-Fetch-Mode'] = 'cors'
    img_heders['Origin'] = 'https://user.qzone.qq.com'
    img_result = requests.post(up_url, data=data, headers=headers)
    img_result = img_result.text
    json_str = img_result.split(
        'frameElement.callback(')[-1].split(');</sc')[0]
    img_data = json.loads(json_str)
    if not img_data['data'].get('url', None):
        print(img)
    pic_bo = img_data['data']['url'].split('&bo=')[-1]
    albumid = img_data['data']['albumid']
    lloc = img_data['data']['lloc']
    sloc = img_data['data']['sloc']
    img_type = img_data['data']['type']
    width = img_data['data']['width']
    height = img_data['data']['height']
    richval = ',%s,%s,%s,%s,%s,%s,,%s,%s' % (
        albumid, lloc, sloc, img_type,  img_data['data']['height'], img_data['data']['width'], img_data['data']['height'], img_data['data']['width'])
    return richval, pic_bo

default_content = {
    "text": "内容",
    "images": [
        'http://666',
        'http://777'
    ]}


def send_tell(content: dict, cookie_ret: str):
    # 空间主页连接
    self_id = 632076240
    home_page = 'https://user.qzone.qq.com/' + str(self_id)
    headers = {}
    headers['cookie'] = cookie_ret
    headers['user-agent'] ='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.87 Safari/537.36'
    headers['Referer'] = home_page
    # 读取参数
    skey = cookie_ret.split("; skey=")[-1].split(';')[0]
    p_skey = cookie_ret.split("; p_skey=")[-1].split(';')[0]
    g_tk = get_g_tk(skey)

    # 建立请求头

    # 获取token
    a = requests.get(home_page, headers=headers)
    a = a.text
    qzone_toekn = a.split(
        'window.g_qzonetoken = (function(){ try{return "')[-1].split('";}')[0]

    # 提取图片连接
    urls_list = content['images']
    img_richval = ''
    img_pic_bo = ''
    if urls_list:
        # 上传图片
        for img_index, img_url in enumerate(urls_list):
            # 读取图片转换base64
            img_ret = requests.get(img_url)
            img_base64 = b64encode(img_ret.content).decode()
            if not img_base64:
                print(f'第{img_index+1}张图片上传失败换一张吧')
                return
            richval, pic_bo = upload_img(qzone_toekn, g_tk, p_skey, img_base64, self_id, skey, headers)
            img_richval += richval + '	'

            img_pic_bo += pic_bo + ','
            print('----', img_pic_bo)

    # 提取文字信息
    raw_content = content['text']

    # 发送说说（判断是否纯文字or带图）
    send_api = 'https://user.qzone.qq.com/proxy/domain/taotao.qzone.qq.com/cgi-bin/emotion_cgi_publish_v6?qzonetoken=%s&g_tk=%s' % (
        qzone_toekn, g_tk)
    total_data = {
        "syn_tweet_verson": "1",
        "paramstr": "1",
        "pic_template": "",
        "richtype": "",
        "richval": "",
        "special_url": "",
        "subrichtype": "",
        "con": "",
        "feedversion": "1",
        "ver": "1",
        "ugc_right": "1",
        "to_sign": "0",
        "hostuin": str(self_id),
        "code_version": "1",
        "format": "fs",
        "qzreferrer": home_page
    }
    if img_pic_bo:  # 带图
        if len(urls_list) != 1:
            total_data['pic_template'] = f'tpl-{len(urls_list)}-1'
        img_pic_bo = img_pic_bo[:-1] + '    ' + img_pic_bo[:-1]
        img_richval = img_richval.strip()
        total_data = total_data.copy()
        total_data['richtype'] = '1'
        total_data['richval'] = img_richval
        total_data['pic_bo'] = img_pic_bo
        total_data['who'] = '1'
        total_data["subrichtype"] = '1'
        total_data['con'] = raw_content.strip()

    else:  # 不带图
        total_data['con'] = raw_content.strip()
    checkip(qzone_toekn, g_tk, headers['Referer'])

    retry = 0
    while retry < 4:
        result = requests.post(send_api, data=total_data, headers=headers)
        if result.text and '不是有效链接' not in result.text:
            print('发送完毕！')
            return
        retry += 1
    print('发送失败！')
    return
