from flask import Flask, render_template, request, jsonify
from qzone_get import *
from qzone_tell import *
import re

mode = 'pc'


def get_ip():
    response = requests.get("http://www.net.cn/static/customercare/yourip.asp")
    ip = re.findall(r'<h2>[0-9.]+</h2>', response.text)
    return ip[0].replace('<h2>', '').replace('</h2>', '')


with open('cookie.txt', 'r+') as co:
    mycookie = co.read()

mycookie_dict = cookie_str_to_dict(mycookie)
if mode == 'server':
    ip = f'{get_ip()}:5000'
elif mode == 'pc':
    ip = '127.0.0.1:5000'
app = Flask(__name__)
@app.route('/')
def home():
    return 'Qzone_syncer'


@app.route('/tell', methods=['GET'])
def tell():
    qqid = request.args.get('id')
    my_qzone = Qzone(**cookie_str_to_dict(mycookie))
    latest_tell = my_qzone.emotion_list(uin=qqid, num=1, pos=0)[0]
    latest_tell.load()
    imgs = []
    for u in latest_tell.pictures:
        imgs.append(u.url)
    if request.args.get('method') == 'latest':
        return render_template('default.html', text=latest_tell.content, imgs=imgs)
    elif request.args.get('method') == 'update':
        cont = {
            "text": latest_tell.content,
            "images": imgs
        }
        try:
            send_tell(cont, mycookie)
        except:
            return "Failed"
    return "success"


@app.route('/cst')
def cst():
    return render_template('cst.html', ip=ip)


@app.route('/cookie', methods=['GET'])
def cookie():
    new_cookie = request.args.get('s')
    try:
        with open("cookie.txt", 'w+') as co:
            co.truncate()
            co.write(new_cookie)
    except FileNotFoundError:
        return '没设置cookie文件！'
    return 'cookie更新成功！'


if __name__ == '__main__':
    app.run()
