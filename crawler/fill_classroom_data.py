#!/usr/bin/env python3
"""
填充教室课表数据的脚本
执行 summarizeClassroomsSchedule 函数，将 teacher.arrangeInfoText 中的数据解析并填充到新的教室数据库表中
"""

from utils.tjSql import tjSql
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """
    主函数，执行教室数据填充
    """
    print("开始执行教室数据填充...")
    print("=" * 60)

    try:
        # 使用with语句确保数据库连接正确关闭
        with tjSql() as sql:
            print("数据库连接成功")

            # 执行教室课表数据汇总
            sql.summarizeClassroomsSchedule()

            print("=" * 60)
            print("教室数据填充完成！")

    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
