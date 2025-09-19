#!/usr/bin/env python3
"""
测试新的自习室推荐功能
验证NOTE1和NOTE2的实现效果
"""

import json
from utils.bckndSql import bckndSql
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_get_all_buildings():
    """测试获取楼宇信息"""
    print("=" * 60)
    print("测试 getAllBuildings 方法")
    print("=" * 60)

    campuses = ["四平路校区", "嘉定校区", "沪西校区"]
    calendar_id = 120  # 使用response.json中的学期ID

    with bckndSql() as sql:
        for campus in campuses:
            print(f"\n{campus}:")
            try:
                buildings = sql.getAllBuildings(campus, calendar_id)
                print(f"  总楼宇数: {len(buildings)}")
                for building in buildings:
                    print(
                        f"  {building['building']}: {building['roomCount']} 间教室")
                    if building['roomCount'] <= 5:  # 显示少量教室的具体名称
                        print(f"    教室: {', '.join(building['rooms'][:5])}")
            except Exception as e:
                print(f"  错误: {e}")


def test_study_room_suggestions():
    """测试自习室推荐功能"""
    print("\n" + "=" * 60)
    print("测试 getStudyRoomSuggestions 方法")
    print("=" * 60)

    # 测试用例
    test_cases = [
        {
            "name": "嘉定校区博楼周一下午",
            "campus": "嘉定校区",
            "building": "博楼",
            "dayOfWeek": 1,  # 周一
            "startTime": 6,   # 第6节
            "endTime": 8,     # 第8节
            "calendarId": 120
        },
        {
            "name": "四平路校区南楼周三上午",
            "campus": "四平路校区",
            "building": "南楼",
            "dayOfWeek": 3,  # 周三
            "startTime": 1,   # 第1节
            "endTime": 4,     # 第4节
            "calendarId": 120
        },
        {
            "name": "沪西校区二教周五晚上",
            "campus": "沪西校区",
            "building": "二教",
            "dayOfWeek": 5,  # 周五
            "startTime": 9,   # 第9节
            "endTime": 11,    # 第11节
            "calendarId": 120
        }
    ]

    with bckndSql() as sql:
        for case in test_cases:
            print(f"\n测试用例: {case['name']}")
            print(
                f"参数: {case['campus']} {case['building']} 星期{case['dayOfWeek']} 第{case['startTime']}-{case['endTime']}节")

            try:
                suggestions = sql.getStudyRoomSuggestions(
                    case["campus"],
                    case["building"],
                    case["dayOfWeek"],
                    case["startTime"],
                    case["endTime"],
                    case["calendarId"]
                )

                total_rooms = len(suggestions)
                fully_free_rooms = len(
                    [s for s in suggestions if s["isFullyFree"]])
                available_rooms = len(
                    [s for s in suggestions if s["freePeriods"]])

                print(f"  总教室数: {total_rooms}")
                print(f"  完全空闲: {fully_free_rooms}")
                print(f"  部分可用: {available_rooms}")

                # 显示前5个推荐结果
                for i, suggestion in enumerate(suggestions[:5]):
                    status = "✅完全空闲" if suggestion["isFullyFree"] else "⚠️部分空闲"
                    print(f"  {i+1}. {suggestion['room']} - {status}")
                    for period in suggestion["freePeriods"]:
                        print(
                            f"     可用时段: 第{period['start']}-{period['end']}节 ({period['duration']}节)")

            except Exception as e:
                print(f"  错误: {e}")
                import traceback
                traceback.print_exc()


def test_study_area_filtering():
    """测试自习区域过滤功能"""
    print("\n" + "=" * 60)
    print("测试自习区域过滤功能 (NOTE2验证)")
    print("=" * 60)

    from study_room_config import is_valid_study_area, get_allowed_study_areas_info

    # 测试有效的自习区域
    valid_areas = [
        ("嘉定校区", "安楼", "A101"),
        ("嘉定校区", "博楼", "B202"),
        ("嘉定校区", "广楼", "G301"),
        ("嘉定校区", "复楼", "F401"),
        ("四平路校区", "南楼", "南205"),
        ("四平路校区", "北楼", "北108"),
        ("沪西校区", "二教", "沪西二教131小教室")
    ]

    # 测试无效的自习区域
    invalid_areas = [
        ("嘉定校区", "实验楼", "E101"),  # 不在允许列表中
        ("四平路校区", "西楼", "西201"),  # 不在允许列表中
        ("沪西校区", "一教", "一教101"),  # 不在允许列表中
    ]

    print("有效自习区域测试:")
    for campus, building, room in valid_areas:
        result = is_valid_study_area(campus, building, room)
        print(f"  {campus} {building} {room}: {'✅有效' if result else '❌无效'}")

    print("\n无效自习区域测试:")
    for campus, building, room in invalid_areas:
        result = is_valid_study_area(campus, building, room)
        print(f"  {campus} {building} {room}: {'✅有效' if result else '❌无效'}")

    print("\n允许的自习区域配置:")
    info = get_allowed_study_areas_info()
    print(json.dumps(info, ensure_ascii=False, indent=2))


def main():
    """主测试函数"""
    print("开始测试新的自习室推荐功能...")
    print("验证NOTE1(数据库优化)和NOTE2(区域限制)的实现")

    try:
        # 测试楼宇信息获取
        test_get_all_buildings()

        # 测试自习室推荐
        test_study_room_suggestions()

        # 测试区域过滤
        test_study_area_filtering()

        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)

    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
