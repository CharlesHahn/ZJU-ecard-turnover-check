# author : charlie
# a lot of headers have not been dealt well, but have no impact about running

import requests 
from bs4 import BeautifulSoup as bs
import json
import time
from prettytable import PrettyTable


def get_login_page():
    root_url = "https://zjuam.zju.edu.cn/cas/login"
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'http://ecardhall.zju.edu.cn:808/',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    session = requests.Session()
    response = session.get(root_url, headers = headers)
    
    # get the hidden arguments: execution and _eventId
    # this two arguments will be post while loginzju
    soup = bs(response.text, 'lxml')
    inputs = [inp for inp in soup.find_all('input', type='hidden') if 'name' in inp.attrs]
    for inp in inputs:
        if inp['name'] == 'execution':
            execution = inp['value']
        elif inp['name'] == '_eventId':
            eventid = inp['value']

    print("\r:::> get login page -> ", response.status_code)
    return session, execution, eventid
    

def getpubkey(session):
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://zjuam.zju.edu.cn/cas/login?service=http^%^3A^%^2F^%^2Fecardsso.zju.edu.cn^%^2Fias^%^2Fprelogin^%^3Fsysid^%^3DFWDT',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    response = session.get('https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=headers)
    print("\r:::> getpubkey -> ", response.status_code)

    # get RSA pubkey for password encryption
    pubkey = json.loads(response.text)
    modulus = pubkey['modulus']
    exponent = pubkey['exponent']
    
    return session, modulus, exponent


def rsa_encrypt(password_str, e_str, M_str):
    # password encryption
    # rsa_encrypt function is copied from https://github.com/zjuchenyuan/zjuauthme, thanks
    password_bytes = bytes(password_str, 'ascii') # I guess no other characters in password
    password_int = int.from_bytes(password_bytes,'big') # big endian bytes->int
    e_int = int(e_str, 16) # equal to 0x10001
    M_int = int(M_str, 16) # Modulus number
    result_int = pow(password_int, e_int, M_int) # pow is a built-in function in python
    return hex(result_int)[2:].rjust(128, '0') # int->hex str, thanks to @96486d9b


def loginzju(session, execution, eventid, userid, password_encrypted):
    params = {
        "username":userid,
        "password":password_encrypted,
        "authcode":'',
        "execution":execution,
        "_eventId":eventid
        }
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'https://zjuam.zju.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://zjuam.zju.edu.cn/cas/login?service=http^%^3A^%^2F^%^2Fecardsso.zju.edu.cn^%^2Fias^%^2Fprelogin^%^3Fsysid^%^3DFWDT',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    post_url = "https://zjuam.zju.edu.cn/cas/login"
    # allow redirection to set cookies
    resp = session.post(post_url, headers = headers, data = params)
    print("\r:::> login zjuauthme -> ", resp.status_code)
    #for c in session.cookies:
        #print(c)
    #print(resp.text)
    return session


def login_test(session):
    # this if for loginzju test
    headers = {
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/css,*/*;q=0.1',
        'Referer': 'http://my.zju.edu.cn/_web/fusionportal/things.jsp?_p=YXM9MSZwPTEmbT1OJg',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    response = session.get('http://my.zju.edu.cn/_web/fusionportal/_libs/bootstrap/css/bootstrap.min.css', headers=headers)
    print(response.text[:100])


def login_ecardhall(session):
    # to login ecardhall need a lot of allow_redirects, and post hidden arguments
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
        'Host':'ecardhall.zju.edu.cn:808',
    }
    # this session.get is to set cookies for ecardhall.zju.edu.cn
    response = session.get('http://ecardhall.zju.edu.cn:808', headers = headers)
    #print('ecard first -> ', response.status_code)
    #for c in session.cookies:
        #print(c)
        #print()
    #print(response.text)

    # first index
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://ecardhall.zju.edu.cn:808/',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    # allow_redirects to set cookies
    response = session.get('http://ecardhall.zju.edu.cn:808/cassyno/index', headers=headers)
    #print("first index page -> ", response.status_code)
    #print(response.text)

    # find out hidden arguments for post in index page
    soup = bs(response.text, 'lxml')
    inputs = [inp for inp in soup.find_all('input', type='hidden') if 'name' in inp.attrs]
    for inp in inputs:
        if inp['name'] == 'errorcode':
            errorcode = inp['value']
        elif inp['name'] == 'continueurl':
            continueurl = inp['value']
        elif inp['name'] == 'ssoticketid':
            ssoticketid = inp['value']
    #print(errorcode, continueurl, ssoticketid)
    
    # second index
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Origin': 'http://ecardsso.zju.edu.cn',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://ecardsso.zju.edu.cn/ias/prelogin?sysid=FWDT^&continueurl=http^%^3a^%^2f^%^2fecardhall.zju.edu.cn^%^3a808^%^2fcassyno^%^2findex',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    data = {
      'errorcode': errorcode,
      'continueurl': continueurl, 
      'ssoticketid': ssoticketid
    }
    # post data and set one cookies
    response = session.post('http://ecardhall.zju.edu.cn:808/cassyno/index', headers=headers, data=data)
    #print('second index -> ', response.status_code)
    #print(response.text)

    # into user
    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Referer': 'http://ecardsso.zju.edu.cn/ias/prelogin?sysid=FWDT^&continueurl=http^%^3a^%^2f^%^2fecardhall.zju.edu.cn^%^3a808^%^2fcassyno^%^2findex',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    # need to get user page which set cookies again, the login_ecardhall is done
    response = session.get('http://ecardhall.zju.edu.cn:808/user/user', headers=headers)
    print("\r:::> login ecardhall -> ", response.status_code)


def get_tjin(session, account, sdate, edate):
    headers = {
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://ecardhall.zju.edu.cn:808',
        'Referer': 'http://ecardhall.zju.edu.cn:808/Page/Page',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7',
    }
    data = {
      #'sdate': time.strftime("%Y-%m-%d", time.localtime()),
      #'edate': time.strftime("%Y-%m-%d", time.localtime()),
      'sdate': sdate,
      'edate': edate,
      'account': account,
      'page': '1',
      'rows': '15'
    }
    
    # get tjin data
    response = session.post('http://ecardhall.zju.edu.cn:808/Report/GetPersonTrjn', headers=headers, data=data)
    print("\r:::> get tjin -> ", response.status_code)
    print()
    tjin_data = json.loads(response.text)
    counts = tjin_data['total']
    rows = tjin_data['rows']
    consume = 0
    #print('ro', 'occtime', 'mercname', 'tranname', 'tranamt', 'cardbal')
    table2pring = PrettyTable(['ro', 'occtime', 'mercname', 'tranname', 'tranamt', 'cardbal'])
    table2pring.padding_width = 1
    for row in rows:
        #print(row)
        ro = str(row['RO']).strip()
        occtime = str(row['OCCTIME']).strip().split()[-1]
        mercname = str(row['MERCNAME']).strip()
        tranamt = str(row['TRANAMT']).strip()
        tranname = str(row['TRANNAME']).strip()
        cardbal = str(row['CARDBAL']).strip()
        #print(ro, occtime, mercname, tranname, tranamt, cardbal)
        table2pring.add_row([ro, occtime, mercname, tranname, tranamt, cardbal])
        if float(tranamt) < 0:
            consume += float(tranamt)
    print('\r{} 消费次数：{}, 总消费金额：{}'.format(time.strftime("%Y-%m-%d", time.localtime()), counts, consume))
    print(table2pring)


def main():
    # default : quiry turnover of today
    sdate = time.strftime("%Y-%m-%d", time.localtime())
    edate = time.strftime("%Y-%m-%d", time.localtime())

    password = '密码写这里'      # like 'zju123456'
    userid = '学号写这里'        # like '3150101111'
    account = '校园卡卡号写这里' # like '121212'
    # if you wanna define the start date and end date
    # sdate = '' # like '2020-09-10'
    # edate = '' # like '2020-09-10'
    
    session, execution, eventid = get_login_page()
    session, modulus, exponent = getpubkey(session)
    password_encrypted = rsa_encrypt(password, exponent, modulus)
    #print(password_encrypted)
    session = loginzju(session, execution, eventid, userid, password_encrypted)
    #login_test(session)
    login_ecardhall(session)
    get_tjin(session, account, sdate, edate)

    print(">>>>>>>>>> Deposit and Future <<<<<<<<<<")
    # type enter to close windows
    input("type <Enter> to close...")


main()
