import argparse
import time, sys, schedule

from v1_selenium import *
from v2_request import *
def heartbeat():
    print("heartbeat: ", datetime.now())


def do_parse():
    """
    命令行读取参数
    """
    parser = argparse.ArgumentParser()
    action_group = parser.add_mutually_exclusive_group()

    action_group.add_argument("-s", "--selenium", help="运行: 使用selenium模式(不填默认用post模式)", action="store_true")
    action_group.add_argument("-r", "--reset", help="刷新cookie", action="store_true")

    parser.add_argument("-n", "--now", help="立刻运行打工和签到", action="store_true")

    args = parser.parse_args()

    sign_hour = random.randint(10, 20)
    sign_minute = random.randint(11, 55)
    sign_time = str(sign_hour)+':'+str(sign_minute)

    if args.reset:

        print("刷新cookie")
        refresh_cookies_tsdm()
        # todo: 包含s1
        print("所有cookie刷新完毕")

        sys.exit()

    elif args.selenium:

        print("使用selenium模式运行, 签到时间: ", sign_time)
        schedule.every(362).minutes.do(work_multi_selenium)
        schedule.every().day.at(sign_time).do(sign_multi_selenium)  # 每天 10:30 签到

    else:

        print("默认: 使用post模式运行, 签到时间: ", sign_time)
        schedule.every(362).minutes.do(work_multi_post)
        schedule.every().day.at(sign_time).do(sign_multi_post)

    if args.now:
        print("[-n] 立即进行:")
        if args.reset:
            print("刷新cookie时-n选项无效")
            pass
        elif args.selenium:
            work_multi_selenium()
            sign_multi_selenium()
        else:
            work_multi_post()
            sign_multi_post()

    try:
        # 万一有人没改settings.py, 也不会闪退
        from settings import enable_s1_read
        if enable_s1_read:
            from dlc_stage1st import do_read_s1_all
            schedule.every(20).minutes.do(do_read_s1_all)
    except Exception:
        print("====未发现settings.py, 使用默认设置运行===")
        pass

def do_schedule():
    print("正在运行计划任务, 每6小时签到一次")

    while True:
        print("距离下一次任务的时间: {:.1f}分钟".format(schedule.idle_seconds()/60), end='\r')
        schedule.run_pending()  # 运行所有可以运行的任务
        time.sleep(10)


if __name__ == '__main__':
    do_parse()
    do_schedule()
