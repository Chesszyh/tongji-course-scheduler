from utils import loginout
from utils import tjSql
import time
import configparser
from rich import print

CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini", encoding="utf-8")

ONLY_DISPLAY = CONFIG.getboolean("Mode", "only_display", fallback=False)
IS_WAIT = CONFIG.getboolean("Mode", "is_wait", fallback=True)
CALENDAR = CONFIG.get(
    "Settings", "calendar", fallback="120"
)  # 爬取的学期：120有特殊含义吗？
IS_DEBUG = CONFIG.getboolean("Mode", "debug", fallback=False)


def fetchCourseList(session):
    """
    Fetch course list from url, receive the authenticated session as parameter
    """

    # 在这里指定每页的大小
    PAGESIZE = 100

    # prepare payload
    payload = {
        "condition": {
            "trainingLevel": "",
            "campus": "",
            "calendar": CALENDAR,
            "college": "",
            "course": "",
            "ids": [],
            "isChineseTeaching": None,
        },
        "pageNum_": 1,
        "pageSize_": PAGESIZE,
    }

    # Mock a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": "https://1.tongji.edu.cn/taskResultQuery",
    }

    # fetch course list
    response = session.post(
        "https://1.tongji.edu.cn/api/arrangementservice/manualArrange/page?profile",
        headers=headers,
        json=payload,
    )

    # Recursively fetch all courses
    total = response.json()["data"]["total_"]

    for i in range(1, total // PAGESIZE + 1 + 1):  # floor division
        # Prepare payload
        payload["pageNum_"] = i

        # Fetch
        response = session.post(
            "https://1.tongji.edu.cn/api/arrangementservice/manualArrange/page?profile",
            headers=headers,
            json=payload,
        )

        # Display info(Better displaying using rich, only 1 blocks)
        data = response.json()
        print(data["data"]["list"][:1])

        # Insert into database
        if not ONLY_DISPLAY:
            with tjSql.tjSql() as sql:
                sql.insertCourseList(response.json()["data"]["list"])

        print("\n\n\n=====================================")
        print("第", i, "页，共", total // PAGESIZE + 1, "页")
        print("=====================================\n\n\n")

        if IS_WAIT:
            print("Press Enter to continue...")
            input()
        else:
            time.sleep(3)

    print("Course list fetched successfully")

    loginout.logout(session)


if __name__ == "__main__":
    # Login
    session = loginout.login()

    if session is None:
        exit(-1)

    if IS_DEBUG:
        import json

        # 测试环境，记录 cookies
        with open("cookies.json", "w") as f:
            json.dump(session.cookies.get_dict(), f)

        # read cookies
        with open("cookies.json", "r") as f:
            cookies = json.load(f)

        import requests

        session = requests.Session()
        session.cookies.update(cookies)

    # Fetch course list
    fetchCourseList(session)
