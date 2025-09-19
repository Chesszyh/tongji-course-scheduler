#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
自习室推荐系统配置文件
根据NOTE2要求，取消优先级机制，只支持指定的自习区域
"""

import re

# 允许的自习区域定义
ALLOWED_STUDY_AREAS = {
    "嘉定校区": {
        "安楼": {
            # A1xx-A4xx，xxx为三位数字，第1位在1-4之间
            "pattern": re.compile(r"^A[1-4]\d{2}$"),
            "code": "A",
            "description": "嘉定校区安楼",
        },
        "博楼": {
            "pattern": re.compile(r"^B[1-4]\d{2}$"),  # B1xx-B4xx
            "code": "B",
            "description": "嘉定校区博楼",
        },
        "广楼": {
            "pattern": re.compile(r"^G[1-4]\d{2}$"),  # G1xx-G4xx
            "code": "G",
            "description": "嘉定校区广楼",
        },
        "复楼": {
            "pattern": re.compile(r"^F[1-4]\d{2}$"),  # F1xx-F4xx
            "code": "F",
            "description": "嘉定校区复楼",
        },
    },
    "四平路校区": {
        "南楼": {
            "pattern": re.compile(r"^南[1-4]\d{2}$"),  # 南1xx-南4xx
            "code": "南",
            "description": "四平路校区南楼",
        },
        "北楼": {
            "pattern": re.compile(r"^北[1-4]\d{2}$"),  # 北1xx-北4xx
            "code": "北",
            "description": "四平路校区北楼",
        },
    },
    "沪西校区": {
        "二教": {
            "pattern": re.compile(
                r"^沪西二教\d+[^,，\s]*$"
            ),  # 沪西二教xxx，xxx为数字+描述
            "code": "沪西二教",
            "description": "沪西校区二教",
        }
    },
}

# 校区到数据库字段的映射 (基于数据库中campus字段)
CAMPUS_MAPPING = {"四平路校区": "1", "嘉定校区": "3", "沪西校区": "4"}

# 反向映射：数据库字段到校区名称
CAMPUS_ID_TO_NAME = {v: k for k, v in CAMPUS_MAPPING.items()}

# ============================================================================
# 辅助函数
# ============================================================================


def is_allowed_classroom(classroom_name, campus_id=None):
    """
    检查教室是否属于允许的自习区域

    Args:
        classroom_name (str): 教室名称，如 'A101', '南208'等
        campus_id (str, optional): 校区ID，用于进一步验证

    Returns:
        dict: 包含验证结果的字典，格式如下：
        {
            'is_allowed': bool,           # 是否允许
            'campus': str,                # 校区名称
            'building': str,              # 楼宇名称
            'building_code': str,         # 楼宇代码
            'reason': str                 # 验证结果说明
        }
    """

    if not classroom_name:
        return {
            "is_allowed": False,
            "campus": "",
            "building": "",
            "building_code": "",
            "reason": "教室名称为空",
        }

    classroom_name = classroom_name.strip()

    # 遍历所有允许的自习区域
    for campus_name, buildings in ALLOWED_STUDY_AREAS.items():
        for building_name, building_info in buildings.items():
            if building_info["pattern"].match(classroom_name):
                # 如果提供了campus_id，需要验证是否匹配
                if campus_id and CAMPUS_MAPPING.get(campus_name) != str(campus_id):
                    continue

                return {
                    "is_allowed": True,
                    "campus": campus_name,
                    "building": building_name,
                    "building_code": building_info["code"],
                    "reason": f'符合{building_info["description"]}的格式要求',
                }

    return {
        "is_allowed": False,
        "campus": "",
        "building": "",
        "building_code": "",
        "reason": f"教室 {classroom_name} 不属于允许的自习区域",
    }


def get_building_from_classroom(classroom_name):
    """
    从教室名称中提取楼宇信息

    Args:
        classroom_name (str): 教室名称

    Returns:
        dict: 包含楼宇信息的字典，如果不是允许的自习区域则返回None
    """
    result = is_allowed_classroom(classroom_name)

    if result["is_allowed"]:
        return {
            "campus": result["campus"],
            "building": result["building"],
            "building_code": result["building_code"],
        }

    return None


def filter_study_area_classrooms(classrooms_data):
    """
    过滤出属于允许自习区域的教室

    Args:
        classrooms_data (list): 教室数据列表，每个元素应包含classroom_name字段

    Returns:
        list: 过滤后的教室数据列表
    """
    filtered_classrooms = []

    for classroom_data in classrooms_data:
        if isinstance(classroom_data, dict) and "classroom_name" in classroom_data:
            classroom_name = classroom_data["classroom_name"]
        elif isinstance(classroom_data, str):
            classroom_name = classroom_data
        else:
            continue

        result = is_allowed_classroom(classroom_name)
        if result["is_allowed"]:
            if isinstance(classroom_data, dict):
                # 添加楼宇信息到数据中
                classroom_data.update(
                    {
                        "campus_name": result["campus"],
                        "building_name": result["building"],
                        "building_code": result["building_code"],
                    }
                )
                filtered_classrooms.append(classroom_data)
            else:
                # 如果是字符串，转换为包含楼宇信息的字典
                filtered_classrooms.append(
                    {
                        "classroom_name": classroom_name,
                        "campus_name": result["campus"],
                        "building_name": result["building"],
                        "building_code": result["building_code"],
                    }
                )

    return filtered_classrooms


def get_all_allowed_buildings():
    """
    获取所有允许的自习楼宇列表

    Returns:
        list: 按校区组织的楼宇信息列表
    """
    buildings = []

    for campus_name, campus_buildings in ALLOWED_STUDY_AREAS.items():
        campus_info = {
            "campus": campus_name,
            "campus_id": CAMPUS_MAPPING.get(campus_name, ""),
            "buildings": [],
        }

        for building_name, building_info in campus_buildings.items():
            campus_info["buildings"].append(
                {
                    "building": building_name,
                    "building_code": building_info["code"],
                    "description": building_info["description"],
                    "pattern_description": (
                        f"格式要求: {building_info['code']}[1-4]xx"
                        if building_info["code"] != "沪西二教"
                        else "格式要求: 沪西二教xxx"
                    ),
                }
            )

        buildings.append(campus_info)

    return buildings


def get_campus_buildings(campus_id):
    """
    获取指定校区的允许自习楼宇

    Args:
        campus_id (str): 校区ID

    Returns:
        list: 楼宇信息列表
    """
    campus_name = CAMPUS_ID_TO_NAME.get(str(campus_id))
    if not campus_name or campus_name not in ALLOWED_STUDY_AREAS:
        return []

    buildings = []
    for building_name, building_info in ALLOWED_STUDY_AREAS[campus_name].items():
        buildings.append(
            {
                "building": building_name,
                "building_code": building_info["code"],
                "description": building_info["description"],
                "pattern_description": (
                    f"格式要求: {building_info['code']}[1-4]xx"
                    if building_info["code"] != "沪西二教"
                    else "格式要求: 沪西二教xxx"
                ),
            }
        )

    return buildings


# ============================================================================
# 调试和统计函数
# ============================================================================


def get_config_summary():
    """
    获取配置摘要信息

    Returns:
        dict: 配置摘要
    """
    total_buildings = sum(len(buildings) for buildings in ALLOWED_STUDY_AREAS.values())

    return {
        "total_campuses": len(ALLOWED_STUDY_AREAS),
        "total_buildings": total_buildings,
        "campus_details": {
            campus: len(buildings) for campus, buildings in ALLOWED_STUDY_AREAS.items()
        },
        "note": "NOTE2: 已取消优先级机制，只支持指定的自习区域",
    }


# ============================================================================
# 为了向后兼容，保留一些旧的函数接口（但功能已更新）
# ============================================================================


def is_blacklisted_room(classroom_name):
    """
    向后兼容函数：检查教室是否应该被过滤掉
    现在的逻辑是：不在允许列表中的教室都被视为"黑名单"

    Returns:
        dict: 兼容旧格式的返回值
    """
    result = is_allowed_classroom(classroom_name)

    return {
        "is_blacklisted": not result["is_allowed"],
        "reason": result["reason"] if not result["is_allowed"] else "",
    }


def extract_building_from_classroom(classroom_name):
    """
    向后兼容函数：从教室名称中提取楼宇名称
    """
    result = get_building_from_classroom(classroom_name)
    return result["building"] if result else ""


# 为了向后兼容，保留旧的常量名
# 但实际上现在不再使用优先级机制
BUILDING_PRIORITY = {}  # 空字典，因为不再使用优先级
