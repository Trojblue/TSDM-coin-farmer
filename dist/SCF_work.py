# -*- coding: utf-8 -*-

"""
TSDM-coin-farmer
适配云函数, 单个文件完成天使动漫多人打工
requests方式
cookies.json的例子见 https://github.com/Trojblue/TSDM-coin-farmer/blob/main/doc/cookies.json.example
"""


import json, random, requests, time
from typing import List

# ======== CONSTANT ========
sign_url = 'https://www.tsdm39.com/plugin.php?id=dsu_paulsign:sign'
work_url = 'https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work'
login_url = 'https://www.tsdm39.com/member.php?mod=logging&action=login'

tsdm_domain = ".tsdm39.com"
s1_domain = "bbs.saraba1st.com"


# ========= COOKIE ========

def get_cookies_all():
    """从文件读取所有cookies
    { username: [cookie_list] }
    """
    try:
        with open('cookies.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data

    except FileNotFoundError:  # 文件不存在
        print("cookies.json不存在")
        return {}


def get_cookies_by_domain(domain: str):
    """从所有cookie里分离出指定域名的cookie
    domain: cookie_list domain, (".tsdm39.com")
    """
    cookies_all = get_cookies_all()  # { username: [cookie_list] }
    domain_cookies = {}

    for username in cookies_all.keys():
        curr_user_cookies = cookies_all[username]
        curr_user_cookies_domained = []

        # 同一个用户名下可能有多个网站的cookie
        for cookie in curr_user_cookies:
            if cookie['domain'] == domain:
                curr_user_cookies_domained.append(cookie)

        if curr_user_cookies_domained != []:
            domain_cookies[username] = curr_user_cookies_domained

    return domain_cookies


# ======= WORK ======

def work_single_post(cookie: List):
    """用post方式为一个账户打工
    cookie_list: List[Dict]
    """
    cookie_serialized = "; ".join([i['name'] + "=" + i['value'] for i in cookie])

    # 必须要这个content-type, 否则没法接收
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'cookie': cookie_serialized,
        'connection': 'Keep-Alive',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://www.tsdm39.com/plugin.php?id=np_cliworkdz:work',
        'content-type': 'application/x-www-form-urlencoded'
    }

    # 打工之前必须访问过一次网页
    requests.get(work_url, headers=headers)

    ad_feedback = requests.post(work_url, data="act=clickad", headers=headers)
    if "必须与上一次间隔" in ad_feedback.text:
        print("该账户已经打工过")
        return

    for i in range(7):  # 总共6次打工, 实际打工8次保险
        ad_feedback = requests.post(work_url, data="act=clickad", headers=headers)

        wait_time = round(random.uniform(0.5, 1), 2)
        print("点击广告: 第%s次, 等待%s秒, 服务器标识:%s" % (i + 2, wait_time, ad_feedback.text), end="\r")
        print("点击广告: 第%s次, 等待%s秒, 服务器标识:%s" % (i + 2, wait_time, ad_feedback.text))
        time.sleep(wait_time)

        if int(ad_feedback.text) > 1629134400:
            print("检测到作弊判定, 请尝试重新运行")
            break
        elif int(ad_feedback.text) >= 6:  # 已点击6次, 停止
            break
        else:
            continue

    getcre_response = requests.post(work_url, data="act=getcre", headers=headers)

    if "您已经成功领取了奖励天使币" in getcre_response.text:
        print("打工成功")
        return True
    elif "作弊" in getcre_response.text:
        print("作弊判定, 打工失败, 重试...")
    elif "请先登录再进行点击任务" in getcre_response.text:
        print("打工失败, cookie失效...")
    elif "服务器负荷较重" in getcre_response.text:
        print("打工失败, TSDM:\"服务器负荷较重，操作超时\"...")
    else:
        print("======未知原因打工失败, 已保存response=======")
        print("打工", getcre_response.text)

    return False


def work_multi_post():
    cookies = get_cookies_by_domain(tsdm_domain)

    for user in cookies.keys():
        print("正在打工: %s" % user)
        try:
            work_single_post(cookies[user])
        except Exception as e:
            print("====post打工出错: %s=====" % e)

    print("POST方式: 全部打工完成")
    return

def main_handler(event, context):
    work_multi_post()