#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库教室数据分析脚本(调试用)
分析当前数据库中的教室数据结构和分布情况
"""

from utils.bckndSql import bckndSql
import sys
import os
import re
from collections import defaultdict, Counter

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def extract_classroom_from_arrange_text(arrange_text):
    """从arrangeInfoText中提取教室信息"""
    if not arrange_text:
        return []

    classrooms = []
    # 匹配各种教室格式
    patterns = [
        r"([A-Z]\d{3})",  # A101, B203等
        r"(南\d{3})",  # 南101等
        r"(北\d{3})",  # 北101等
        r"(沪西二教\d+[^,，\s]*)",  # 沪西二教131小教室等
        r"([ABGF]\d{3})",  # 专门匹配嘉定校区楼宇
        r"(复\d{3})",  # 复楼
        r"(广\d{3})",  # 广楼
    ]

    for pattern in patterns:
        matches = re.findall(pattern, arrange_text)
        classrooms.extend(matches)

    return list(set(classrooms))  # 去重


def analyze_classroom_distribution():
    """分析教室分布情况"""
    print("=" * 60)
    print("开始分析教室数据结构...")
    print("=" * 60)

    sql_helper = bckndSql()

    # 获取所有teacher记录
    try:
        query = """
        SELECT t.arrangeInfoText, cd.campus, cd.calendarId 
        FROM teacher t 
        JOIN coursedetail cd ON t.teachingClassId = cd.id 
        WHERE t.arrangeInfoText IS NOT NULL 
        AND t.arrangeInfoText != ''
        """

        sql_helper.cursor.execute(query)
        results = sql_helper.cursor.fetchall()
        print(f"总共获取到 {len(results)} 条课程安排记录")

        # 统计数据
        classroom_counter = Counter()
        campus_classroom = defaultdict(set)
        calendar_classroom = defaultdict(set)
        building_classroom = defaultdict(set)

        # 按校区分类的教室模式
        jiading_patterns = {
            "A": re.compile(r"A\d{3}"),  # 安楼
            "B": re.compile(r"B\d{3}"),  # 博楼
            "G": re.compile(r"G\d{3}"),  # 广楼
            "F": re.compile(r"F\d{3}"),  # 复楼
        }

        siping_patterns = {
            "南": re.compile(r"南\d{3}"),  # 南楼
            "北": re.compile(r"北\d{3}"),  # 北楼
        }

        huxi_patterns = {
            "沪西二教": re.compile(r"沪西二教\d+[^,，\s]*"),  # 沪西二教
        }

        pattern_stats = {
            "嘉定校区": {"安楼": 0, "博楼": 0, "广楼": 0, "复楼": 0},
            "四平路校区": {"南楼": 0, "北楼": 0},
            "沪西校区": {"二教": 0},
            "其他": 0,
        }

        for row in results:
            arrange_text, campus, calendar_id = row
            classrooms = extract_classroom_from_arrange_text(arrange_text)

            for classroom in classrooms:
                classroom_counter[classroom] += 1
                campus_classroom[campus].add(classroom)
                calendar_classroom[calendar_id].add(classroom)

                # 按楼宇分类
                building = None
                matched = False

                # 检查嘉定校区模式
                for building_name, pattern in jiading_patterns.items():
                    if pattern.match(classroom):
                        if building_name == "A":
                            pattern_stats["嘉定校区"]["安楼"] += 1
                            building = "安楼"
                        elif building_name == "B":
                            pattern_stats["嘉定校区"]["博楼"] += 1
                            building = "博楼"
                        elif building_name == "G":
                            pattern_stats["嘉定校区"]["广楼"] += 1
                            building = "广楼"
                        elif building_name == "F":
                            pattern_stats["嘉定校区"]["复楼"] += 1
                            building = "复楼"
                        matched = True
                        break

                # 检查四平路校区模式
                if not matched:
                    for building_name, pattern in siping_patterns.items():
                        if pattern.match(classroom):
                            if building_name == "南":
                                pattern_stats["四平路校区"]["南楼"] += 1
                                building = "南楼"
                            elif building_name == "北":
                                pattern_stats["四平路校区"]["北楼"] += 1
                                building = "北楼"
                            matched = True
                            break

                # 检查沪西校区模式
                if not matched:
                    for building_name, pattern in huxi_patterns.items():
                        if pattern.match(classroom):
                            pattern_stats["沪西校区"]["二教"] += 1
                            building = "二教"
                            matched = True
                            break

                if not matched:
                    pattern_stats["其他"] += 1

                if building:
                    building_classroom[building].add(classroom)

        # 输出分析结果
        print("\n" + "=" * 40)
        print("1. 教室总体统计")
        print("=" * 40)
        print(f"发现的不重复教室总数: {len(classroom_counter)}")
        print(f"教室使用总次数: {sum(classroom_counter.values())}")

        print("\n" + "=" * 40)
        print("2. 按校区统计教室")
        print("=" * 40)
        for campus, classrooms in campus_classroom.items():
            print(f"{campus}: {len(classrooms)} 个教室")
            # 显示前10个教室示例
            sample_rooms = sorted(list(classrooms))[:10]
            print(f"  示例: {', '.join(sample_rooms)}")
            if len(classrooms) > 10:
                print(f"  ... 还有 {len(classrooms) - 10} 个教室")

        print("\n" + "=" * 40)
        print("3. 按学期统计教室")
        print("=" * 40)
        for calendar_id, classrooms in calendar_classroom.items():
            print(f"学期 {calendar_id}: {len(classrooms)} 个教室")

        print("\n" + "=" * 40)
        print("4. 指定的自习区域统计（参考study_room_config.py）")
        print("=" * 40)
        for campus, buildings in pattern_stats.items():
            if campus == "其他":
                print(f"{campus}: {buildings} 个不符合要求的教室")
            else:
                print(f"{campus}:")
                for building, count in buildings.items():
                    if count > 0:
                        actual_rooms = len(building_classroom.get(building, set()))
                        print(
                            f"  {building}: {count} 次使用, {actual_rooms} 个不重复教室"
                        )

        print("\n" + "=" * 40)
        print("5. 各楼宇详细教室列表")
        print("=" * 40)
        for building, classrooms in building_classroom.items():
            sorted_rooms = sorted(list(classrooms))
            print(f"\n{building} ({len(sorted_rooms)} 个教室):")
            # 每行显示10个教室
            for i in range(0, len(sorted_rooms), 10):
                batch = sorted_rooms[i : i + 10]
                print(f"  {', '.join(batch)}")

        print("\n" + "=" * 40)
        print("6. 最频繁使用的教室 (TOP 20)")
        print("=" * 40)
        most_common = classroom_counter.most_common(20)
        for classroom, count in most_common:
            print(f"{classroom}: {count} 次")

        print("\n" + "=" * 40)
        print("7. 不符合NOTE2要求的教室示例")
        print("=" * 40)
        other_classrooms = []
        for classroom in classroom_counter.keys():
            matched = False

            # 检查是否符合任何允许的模式
            all_patterns = [
                re.compile(r"A[1-4]\d{2}"),  # 安楼 A1xx-A4xx
                re.compile(r"B[1-4]\d{2}"),  # 博楼 B1xx-B4xx
                re.compile(r"G[1-4]\d{2}"),  # 广楼 G1xx-G4xx
                re.compile(r"F[1-4]\d{2}"),  # 复楼 F1xx-F4xx
                re.compile(r"南[1-4]\d{2}"),  # 南楼 南1xx-南4xx
                re.compile(r"北[1-4]\d{2}"),  # 北楼 北1xx-北4xx
                re.compile(r"沪西二教\d+[^,，\s]*"),  # 沪西二教
            ]

            for pattern in all_patterns:
                if pattern.match(classroom):
                    matched = True
                    break

            if not matched:
                other_classrooms.append((classroom, classroom_counter[classroom]))

        # 按使用频率排序
        other_classrooms.sort(key=lambda x: x[1], reverse=True)

        print(f"不符合要求的教室总数: {len(other_classrooms)}")
        if other_classrooms:
            print("示例 (按使用频率排序):")
            for classroom, count in other_classrooms[:20]:
                print(f"  {classroom}: {count} 次")

            if len(other_classrooms) > 20:
                print(f"  ... 还有 {len(other_classrooms) - 20} 个不符合要求的教室")

        return {
            "total_classrooms": len(classroom_counter),
            "classroom_counter": classroom_counter,
            "campus_classroom": campus_classroom,
            "building_classroom": building_classroom,
            "pattern_stats": pattern_stats,
            "other_classrooms": other_classrooms,
        }

    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback

        traceback.print_exc()
        return None

    finally:
        sql_helper.cursor.close()
        sql_helper.db.close()


if __name__ == "__main__":
    result = analyze_classroom_distribution()
    if result:
        print("\n" + "=" * 60)
        print("分析完成!")
        print("=" * 60)
    else:
        print("分析失败!")
