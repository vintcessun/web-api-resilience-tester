import asyncio
import httpx
import random
import string
import time
import sys
import os
import re
from fake_useragent import UserAgent


# --- 核心配置 ---
def get_config():
    target = os.environ.get("TARGET_URL")
    referer = os.environ.get("REFERER_URL")

    # 兜底逻辑：如果环境变量不存在，尝试读取 url.txt
    if not target or not referer:
        try:
            if os.path.exists("url.txt"):
                with open("url.txt", "r", encoding="utf-8") as f:
                    content = f.read()
                    t_match = re.search(r'TARGET_URL\s*=\s*["\'](.*?)["\']', content)
                    r_match = re.search(r'REFERER_URL\s*=\s*["\'](.*?)["\']', content)
                    if not target and t_match:
                        target = t_match.group(1)
                    if not referer and r_match:
                        referer = r_match.group(1)
        except Exception:
            pass

    return target, referer


TARGET_URL, REFERER_URL = get_config()
DATA_TYPES = ["QQ", "qt", "微信", "potato"]

# 实例化 UA 生成器
try:
    ua_generator = UserAgent()
except Exception:
    ua_generator = None


def get_random_ip():
    """生成随机国内公网 IP，涵盖电信、联通、移动各主要省市段"""
    blocks = [
        # 电信
        [14, 116, 0, 0, 14, 119, 255, 255],  # 广东/广西
        [42, 120, 0, 0, 42, 123, 255, 255],  # 浙江/江苏
        [58, 208, 0, 0, 58, 215, 255, 255],  # 江苏
        [101, 80, 0, 0, 101, 95, 255, 255],  # 北京/上海
        [113, 64, 0, 0, 113, 127, 255, 255],  # 广东
        [121, 8, 0, 0, 121, 31, 255, 255],  # 上海
        [125, 64, 0, 0, 125, 95, 255, 255],  # 湖南/湖北
        [171, 8, 0, 0, 171, 11, 255, 255],  # 四川
        [182, 128, 0, 0, 182, 151, 255, 255],  # 四川
        [183, 0, 0, 0, 183, 63, 255, 255],  # 广东
        [218, 0, 0, 0, 218, 95, 255, 255],  # 全国通用
        [222, 128, 0, 0, 222, 191, 255, 255],  # 全国多省
        # 联通
        [27, 184, 0, 0, 27, 191, 255, 255],  # 河南/山东
        [42, 80, 0, 0, 42, 83, 255, 255],  # 北京
        [60, 0, 0, 0, 60, 31, 255, 255],  # 华北
        [114, 240, 0, 0, 114, 255, 255, 255],  # 全国
        [123, 112, 0, 0, 123, 127, 255, 255],  # 北京
        [157, 0, 0, 0, 157, 15, 255, 255],  # 华东
        # 移动
        [36, 128, 0, 0, 36, 159, 255, 255],  # 全国
        [111, 0, 0, 0, 111, 63, 255, 255],  # 全国
        [117, 128, 0, 0, 117, 191, 255, 255],  # 全国
        [120, 192, 0, 0, 120, 223, 255, 255],  # 广东/福建
        [183, 128, 0, 0, 183, 191, 255, 255],  # 全国
        # 阿里云/云服务出口 (模拟一些高级用户/代理)
        [47, 92, 0, 0, 47, 119, 255, 255],  # 阿里云国内
        [106, 11, 0, 0, 106, 11, 255, 255],  # 阿里云
    ]
    block = random.choice(blocks)
    return ".".join(str(random.randint(block[i], block[i + 4])) for i in range(4))


def generate_mockery():
    """生成小比例嘲讽/脏话彩蛋"""
    mockery_accounts = [
        "StopScamming",
        "ShameOnYou",
        "GetAJob",
        "ScamHunter",
        "FraudAlert",
        "pianzi-nima",
        "nima-si-le",
        "caonima",
        "qusi-ba",
        "sha-bi-pian-zi",
        "StopPianZi",
        "FuckScammer",
        "ScammerDie",
        "NMSL-PianZi",
    ]
    mockery_passwords = [
        "StopScamming2024",
        "ScamIsBad123",
        "YouAreAFraud",
        "cao-ni-ma-123",
        "si-quan-jia-888",
        "pian-zi-sha-bi",
        "NMSL-888",
        "FuckYouPianZi",
        "scam-alert-!!!",
        "GetARealJobNow",
    ]
    return random.choice(mockery_accounts), random.choice(mockery_passwords)


def generate_account(data_type):
    """根据类型生成高仿真账号"""
    # 5% 的概率生成嘲讽账号
    if random.random() < 0.05:
        acc, _ = generate_mockery()
        return acc

    if data_type in ["QQ", "qt"]:
        # 生成 9-11 位纯数字
        return "".join(random.choices(string.digits, k=random.randint(9, 11)))
    elif data_type == "微信":
        # 生成 6-20 位随机组合（模拟微信号格式：字母开头，含数字、下划线或减号）
        prefix = random.choice(string.ascii_letters)
        body = "".join(
            random.choices(
                string.ascii_letters + string.digits + "_-", k=random.randint(5, 19)
            )
        )
        return prefix + body
    elif data_type == "potato":
        # 生成随机手机号格式（13/15/17/18/19开头）
        prefixes = ["13", "15", "17", "18", "19"]
        return random.choice(prefixes) + "".join(random.choices(string.digits, k=9))
    return "".join(random.choices(string.digits, k=10))


def generate_password():
    """按比例随机生成极高仿真的复杂密码"""
    # 5% 的概率生成嘲讽密码 (需独立概率，有时账号正常密码嘲讽效果更好)
    if random.random() < 0.05:
        _, pw = generate_mockery()
        return pw

    rand = random.random()

    # 1. 常用弱口令 (10%)
    if rand < 0.10:
        return random.choice(
            [
                "123456789",
                "666888",
                "admin123",
                "password",
                "88888888",
                "123456ab",
                "11223344",
                "000000",
            ]
        )

    # 2. 姓名/拼音/英文 + 数字/符号 (25%)
    elif rand < 0.35:
        prefixes = [
            "zhang",
            "li",
            "wang",
            "chen",
            "liu",
            "love",
            "smile",
            "lucky",
            "hello",
            "china",
            "iphone",
            "wechat",
        ]
        if random.random() > 0.5:
            prefixes = [p.capitalize() for p in prefixes]
        suffix = random.choice(
            ["1990", "520", "123", "666", "888", "2024", "1314", "123456", "!@#"]
        )
        return random.choice(prefixes) + suffix

    # 3. 姓名缩写 + 日期 (20%)
    elif rand < 0.55:
        initials = [
            "zw",
            "lh",
            "wf",
            "cy",
            "lj",
            "zs",
            "xm",
            "wy",
            "qj",
            "ht",
            "ly",
            "xx",
            "abc",
            "xyz",
            "test",
            "user",
            "admin",
            "guest",
            "root",
            "sys",
            "data",
            "info",
            "wds",
            "wys",
            "wd",
            "wzxh",
            "wys",
            "wdsj",
            "wds123",
        ]
        year = str(random.randint(1985, 2005))
        md = str(random.randint(1, 12)).zfill(2) + str(random.randint(1, 28)).zfill(2)
        return random.choice(initials) + random.choice([year, md])

    # 4. 手机号/生日 (20%)
    elif rand < 0.75:
        if random.random() > 0.5:
            # 模拟11位手机号
            return "1" + "".join(random.choices(string.digits, k=10))
        else:
            # 模拟19901001格式生日
            year = str(random.randint(1980, 2010))
            month = str(random.randint(1, 12)).zfill(2)
            day = str(random.randint(1, 28)).zfill(2)
            return year + month + day

    # 5. 键盘序列/纯字符 (15%)
    elif rand < 0.90:
        return random.choice(
            [
                "asdfghjkl",
                "qwerty123",
                "zxcvbnm",
                "1q2w3e4r",
                "p0o9i8u7",
                "qwaszx",
                "yuiop789",
            ]
        )

    # 6. 混合复杂模式 (10%) - 提高后台可信度
    else:
        prefix = "".join(random.choices(string.ascii_letters, k=random.randint(2, 4)))
        mid = random.choice(["@", ".", "_", ""])
        num = "".join(random.choices(string.digits, k=random.randint(3, 6)))
        return prefix + mid + num


async def send_poison_request(client, data_type):
    """发送单次投毒请求"""
    account = generate_account(data_type)
    password = generate_password()

    payload = {
        "data[user]": account,
        "data[pass]": password,
        "data[type]": data_type,
    }

    ua = (
        ua_generator.random
        if ua_generator
        else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    headers = {
        "User-Agent": ua,
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": REFERER_URL,
        "X-Forwarded-For": get_random_ip(),
    }

    try:
        # 发送前日志
        print(
            f"[{time.strftime('%H:%M:%S')}] 尝试注入 -> 类型: {data_type:6} | 账号: {account:12}",
            end=" ",
            flush=True,
        )

        response = await client.post(
            TARGET_URL, data=payload, headers=headers, timeout=15.0
        )

        # 显式 print 动作：发送后日志
        status_text = response.text.replace("\n", " ")
        print(f"| 状态: {response.status_code} | 返回: {status_text}")

        # 反查验证逻辑
        try:
            res_json = response.json()
            if res_json.get("code") == 1 and "id" in res_json:
                inj_id = res_json["id"]
                # 构造反查 URL
                base_url = TARGET_URL.split("?")[0]
                query_url = f"{base_url}?act=getstate&id={inj_id}"

                # 等待极短时间确保后台已入库
                await asyncio.sleep(1)

                check_res = await client.get(query_url, headers=headers, timeout=10.0)
                check_json = check_res.json()

                if check_json.get("code") == "1" and "data" in check_json:
                    data = check_json["data"]
                    print(
                        f"    └─ [反查验证] 注入成功! IP: {data.get('ip')} | 账号: {data.get('user')} | 密码: {data.get('pass')}"
                    )
        except Exception:
            pass

        if response.status_code in [502, 504]:
            print(f"[!] 服务器返回 {response.status_code}，可能已过载。")
            return "STOP"

    except httpx.ConnectTimeout:
        print("\n[!] 连接超时。")
        return "STOP"
    except Exception as e:
        print(f"\n[!] 异常: {e}")
        return "ERROR"

    return "SUCCESS"


async def main():
    if not TARGET_URL:
        print("[!] 错误: 未配置 TARGET_URL，请检查环境变量或 url.txt")
        sys.exit(1)

    run_count = random.randint(40, 60)
    print(f"--- 启动投毒任务 | 目标执行次数: {run_count} ---")
    print(f"--- 目标 URL: {TARGET_URL} ---")

    async with httpx.AsyncClient(verify=False, http2=True) as client:
        for i in range(run_count):
            data_type = random.choice(DATA_TYPES)
            result = await send_poison_request(client, data_type)

            if result == "STOP":
                sys.exit(0)

            if i < run_count - 1:
                sleep_time = random.uniform(5, 12)
                await asyncio.sleep(sleep_time)

    print("--- 任务圆满完成 ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] 用户中断")
    except Exception as e:
        print(f"\n[!] 运行时错误: {e}")
