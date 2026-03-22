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
    """生成随机国内公网 IP"""
    blocks = [
        [14, 116, 0, 0, 14, 116, 255, 255],
        [27, 184, 0, 0, 27, 191, 255, 255],
        [36, 48, 0, 0, 36, 63, 255, 255],
        [42, 120, 0, 0, 42, 121, 255, 255],
        [61, 128, 0, 0, 61, 191, 255, 255],
        [101, 4, 0, 0, 101, 7, 255, 255],
        [111, 0, 0, 0, 111, 63, 255, 255],
        [120, 192, 0, 0, 120, 223, 255, 255],
        [183, 0, 0, 0, 183, 63, 255, 255],
        [218, 0, 0, 0, 218, 95, 255, 255],
    ]
    block = random.choice(blocks)
    return ".".join(str(random.randint(block[i], block[i + 4])) for i in range(4))


def generate_account(data_type):
    """根据类型生成高仿真账号"""
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
    """按比例随机生成高仿真密码"""
    rand = random.random()

    # 1. 常用弱口令 (20%)
    if rand < 0.2:
        return random.choice(
            ["123456789", "666888", "admin123", "password", "88888888", "123456ab"]
        )

    # 2. 姓名拼音组合 (30%)
    elif rand < 0.5:
        names = ["zhangwei", "lihua", "wang", "chen", "yang", "zhao", "zhou"]
        suffix = random.choice(["1990", "520", "123", ".123", "666", "888"])
        return random.choice(names) + suffix

    # 3. 手机号/生日 (30%)
    elif rand < 0.8:
        if random.choice([True, False]):
            # 模拟11位数字
            return "1" + "".join(random.choices(string.digits, k=10))
        else:
            # 模拟20000101格式
            year = str(random.randint(1980, 2010))
            month = str(random.randint(1, 12)).zfill(2)
            day = str(random.randint(1, 28)).zfill(2)
            return year + month + day

    # 4. 键盘序列 (20%)
    else:
        return random.choice(
            ["asdfghjkl", "qwerty123", "zxcvbnm", "1q2w3e4r", "p0o9i8u7"]
        )


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
