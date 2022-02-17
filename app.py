# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask import request
from backend.login import Login
from flask_cors import CORS
from backend.userinfo import UserInfo
from backend.getusers import getAllUsers
from backend.cookies import Cookie
from backend.devices import Device
from backend.settings import Settings
from backend.database import UserInfoDB
import json
from flask import jsonify
import os
import re
import platform
import sys, os, subprocess, time, signal
from jpype import *


app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")


def userlogin(user):
    username = user['username']
    password = user['password']
    devicename = user['devicename']
    devicetype = user['devicetype']
    imei = user['imei']
    if username == '' or password == '' or devicename == '' or devicetype == '' \
            or imei == '':
        return {
                'code': -1,
                'message': '登录失败,账号信息填写不完整'
        }

    user = {
        'username': username,
        'password': password,
        'devicename': devicename,
        'devicetype': devicetype,
        'imei': imei,
        'qimei': imei
    }
    device = Device.findDeviceByQimei(user['imei'])
    if device is None:
        # print("数据库未找到该在线设备,请将该设备录入数据库!")
        # 临时生成一个设备
        device = Device.getRandomDevice()
        device['devicename'] = user['devicename']
        device['devicetype'] = user['devicetype']
        device['imei'] = user['imei']
        if 'qimei' not in user.keys():
            device['qimei'] = user['imei']
        else:
            device['qimei'] = user['qimei']
    device_id = device['imei'] + '_' + device['qimei']
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_path = cur_dir + '/backend/' + Settings.cookiepath + user['username'] + '/'
    qimei = imei
    device_id = imei + '_' + qimei
    cookies = Cookie().getCookies(cookie_path, device_id)
    if cookies is None or cookies == '':
        login = Login(username, password, devicename, devicetype, imei, imei)
        ret = login.login()
        #print(ret)
        cookie = None
        user = None
        device = None
        if ret and 'cookies' in ret.keys():
            cookie = ret['cookies']
        if ret and 'user' in ret.keys():
            user = ret['user']
        if ret and 'device' in ret.keys():
            device = ret['device']
        if cookie is None or cookie == '':
            ret = {
                    'code': -2,
                    'message': '登录失败，账号信息错误'
            }
            return jsonify(ret)
        else:
            ret = {
                'code': 0,
                'data': {
                    'user': user,
                    'device': device,
                    'cookie': cookie
                }
            }
            return jsonify(ret)
    else:
        ret = {
            'code': 0,
            'data': {
                'user': user,
                'device': device,
                'cookie': cookies
            }
        }
        return jsonify(ret)
    return ret


def parseUserfileContent(content):
    # print(content)
    rows = content.split("\n")
    # print(rows)
    users = []
    for i in range(len(rows)):
        cols = re.split("\----+", rows[i])
        if len(cols) != 5:
            continue
        else:
            user = dict()
            user['username'] = cols[0].strip()
            user['password'] = cols[1].strip()
            user['devicename'] = cols[2].strip()
            user['devicetype'] = cols[3].strip()
            user['imei'] = cols[4].strip()
            #print(user)
            users.append(user)
    return users


@app.route('/api/logins', methods=['POST'])
def logins():
    content = ''
    file_obj = request.files.get('userfile')
    print(file_obj)
    dst = os.path.join(os.path.dirname(__file__), file_obj.name)
    file_obj.save(dst)
    # if windows GBK   linux utf-8 
    sys = platform.system()
    if sys == "Windows":
        print("OS is Windows!!!")
        file_encode = 'GBK'
    elif sys == "Linux":
        print("OS is Linux!!!")
        file_encode = 'utf-8'
    with open(dst, 'r', encoding=file_encode) as file:
        content = file.read()
        #print(content)
        if content:
            users = parseUserfileContent(content)
            #print(users)
            for user in users:
                # 存入数据库
                #print(user)
                user = {
                        'username': user['username'],
                        'password': user['password'],
                        'devicetype': user['devicetype'],
                        'devicename': user['devicename'],
                        'imei': user['imei'],
                        'nickname': '',
                        'status': 0,
                        'ticketmain': 0,
                        'ticketwm': 0,
                        'monthticket': 0
                }
                with UserInfoDB() as db:
                    db.saveUserInfo(user)
    os.remove(dst)
    return content

def run_new_start_script():
    current_path = os.path.dirname(os.path.abspath(__file__))
    start_sript = os.path.abspath(os.path.join(current_path, "startGetHongbao.py"))
    process_gethongbao = subprocess.Popen(['python3', start_sript], shell=False)
    os.environ['PID_GETHONGBAO'] = str(process_gethongbao.pid)
    print(os.environ['PID_GETHONGBAO'])
    return process_gethongbao

def exit_script(pid):
    try:
        os.kill(pid,signal.SIGUSR1)
        os.environ['PID_GETHONGBAO'] = ''
    except Exception as e:
        print(e)
        return False
    return True

@app.route('/api/getHongbaoProcStatus', methods=['POST'])
def getHongbaoProcStatus():
    if 'PID_GETHONGBAO' not in os.environ.keys():
        return {
            'code': 0,
            'message': '已停止抢包'
        }
    pid = os.environ['PID_GETHONGBAO']
    code = -1
    if pid:
        code = 1
    if code == 1:
        ret = {
            'code': code,
            'message': '正在抢包'
        }
    else:
        ret = {
            'code': 0,
            'message': '已停止抢包'
        }
    return jsonify(ret)

@app.route('/api/endGetHongbao', methods=['POST'])
def endGethongbao():
    if 'PID_GETHONGBAO' in os.environ.keys():
        pid = os.environ['PID_GETHONGBAO']
    flag = 0
    if pid:
        pid = int(pid)
        print(pid)
        flag = exit_script(pid)
    code = -1
    if flag:
        code = 0
    if code == 0:
        ret = {
            'code': code,
            'message': '退出抢包进程成功'
        }
    else:
        ret = {
            'code': -1,
            'message': '退出抢包进程失败'
        }
    return jsonify(ret)

@app.route('/api/startGetHongbao', methods=['POST'])
def startGethongbao():
    p = run_new_start_script()
    code = -1
    if p and p.pid:
        code = 0
    if code == 0:
        ret = {
            'code': code,
            'message': '启动抢包进程成功'
        }
    else:
        ret = {
            'code': -1,
            'message': '启动抢包进程失败'
        }
    return jsonify(ret)

@app.route('/api/setParams', methods=['POST'])
def setParams():
    values = request.values
    proxy = values.get('proxy')
    threads = values.get('threads')
    relay = values.get('relay')
    if proxy:
        Settings.proxy_gethongbao = 1
    else:
        Settings.proxy_gethongbao = 0
    if threads:
        Settings.num_threads_gethongbao = int(threads)
    if relay:
        Settings.gethongbao_relay = int(relay) * 1000
    print(values)
    ret = {
        'code': 0,
        'message': '设置成功'
    }
    return jsonify(ret)
    


@app.route('/api/deleteAllUsers', methods=['POST'])
def deleteAllUsers():
    with UserInfoDB() as db:
        code = db.deleteAllUsers()
    if code == 0:
        ret = {
            'code': code,
            'message': '删除成功'
        }
    else:
        ret = {
            'code': -1,
            'message': '删除失败'
        }
    return jsonify(ret)


@app.route('/api/login', methods=['POST'])
def login():
    values = request.values
    user = dict()
    user['username'] = values.get('username')
    user['password'] = values.get('password')
    user['devicename'] = values.get('devicename')
    user['devicetype'] = values.get('devicetype')
    user['imei'] = values.get('imei')
    ret = userlogin(user)
    return ret


@app.route('/api/getuserinfo', methods=['POST'])
def getuserinfo():
    values = request.values
    user = values.get('user')
    device = values.get('device')
    cookie = values.get('cookie')
    user = json.loads(user)
    device = json.loads(device)
    cookie = json.loads(cookie)
    if cookie == '' or cookie is None:
        ret = {
                'code': -3,
                'message': '未登录'
        }
        return jsonify(ret)
    ui = UserInfo(user, device, cookie)
    userinfo = ui.getUserInfo()
    if userinfo == '' or userinfo is None:
        ret = {
                'code': -4,
                'message': '获取用户信息失败'
        }
        return jsonify(ret)
    else:
        ret = {
            'code': 0,
            'data': {
                'userinfo': userinfo
            }
        }
        return jsonify(ret)


@app.route('/api/getusers', methods=['POST'])
def getusers():
    infos = getAllUsers()
    if infos == '' or infos is None:
        ret = {
                'code': -4,
                'message': '获取用户信息失败'
        }
        return jsonify(ret)
    else:
        ret = {
            'code': 0,
            'data': {
                'users': infos
            }
        }
        return jsonify(ret)


@app.route('/api/tx_slide')
def tx_slide():
    from backend.tcaptcha_1.src.database_redis import TcaptchaRedisDB
    db = TcaptchaRedisDB()
    cap = {
        'sig':"",
        'code':""
    }
    try:
        cap = db.pop()
        print(cap)
        #pass
    except Exception as e:
        return json.dumps(cap)
    return json.dumps(cap)

@app.route('/api/tx_slide_push', methods=["POST"])
def tx_slide_push():
    values = request.values
    #req = json.loads(request.get_data())
    #print(req)
    captcha = dict()
    captcha['sig'] = values.get('ticket', None)
    captcha['code'] = values.get('randstr', None)
    if not captcha['sig'] or not captcha['code']:
        return json.dumps({"code": 2, "msg": "空滑块"})
    if str(captcha['code'])[0] != "@":
        return json.dumps({"code": 2, "msg": "无效滑块"})
        
    from backend.tcaptcha_1.src.database_redis import TcaptchaRedisDB
    from backend.tcaptcha_1.src.tcaptcha_class import TcaptchaClass
    captcha_obj = TcaptchaClass(captcha)
    db = TcaptchaRedisDB()
    try:
        db.push(captcha_obj)
        return json.dumps({"code": 0, "msg": "sucess"})
    except Exception as e:
        print(e)
        return json.dumps({"code": 1, "msg": "fail"})

@app.route('/api/tx_slide_save', methods=["GET"])
def tx_slide_save():
    values = request.args
    #req = json.loads(request.get_data())
    #print(req)
    #print(values.get('ticket'))
    captcha = dict()
    captcha['sig'] = values.get('ticket', None)
    captcha['code'] = values.get('randstr', None)
    if not captcha['sig'] or not captcha['code']:
        return json.dumps({"code": 2, "msg": "空滑块"})
    if str(captcha['code'])[0] != "@":
        return json.dumps({"code": 2, "msg": "无效滑块"})
        
    from backend.tcaptcha_1.src.database_redis import TcaptchaRedisDB
    from backend.tcaptcha_1.src.tcaptcha_class import TcaptchaClass
    captcha_obj = TcaptchaClass(captcha)
    #print(captcha)
    db = TcaptchaRedisDB()
    try:
        db.push(captcha_obj)
        return json.dumps({"code": 0, "msg": "sucess"})
    except Exception as e:
        print(e)
        return json.dumps({"code": 1, "msg": "fail"})



@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    # 定时任务 扫描红包广场  从数据库获取用户 - 创建扫描线程
    libpath = os.path.dirname(os.path.abspath(__file__)) + '/backend' + "/libs/"
    jarpath = os.path.join(os.path.abspath('.'), libpath)
    if not isJVMStarted():
        startJVM("/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/server/libjvm.so", "-ea","-Djava.class.path=%s" % (jarpath + 'testDes3Cbc.jar'))
    Settings.JDClass = JClass("QDInfo")
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.run(host='0.0.0.0', port=8081, debug=True)
