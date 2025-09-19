# -*- coding: utf-8 -*-
"""
自习室推荐系统配置文件
包含楼宇优先级、教室黑名单等配置
"""

# 楼宇优先级配置（数字越小优先级越高）
BUILDING_PRIORITY = {
    # 因为在选择楼宇之前已经对校区进行了分类，所以两校区楼宇优先级可以顺延
    # 只定义了四平/嘉定的优先级，其他校区不清楚
    '安楼': 1,      # 设备最新，开放到0:30，最适合自习
    '博楼': 2,      # 开放到21:40，时间短但条件也不错
    '广楼': 3,      # 设备有换新，现在电源多了不少
    '诚楼': 4,      # 同样是开放时间短
    '复楼': 5,      # 大阶梯教室多，电源少，开放到22:00左右？
    '南楼': 10,      # 设备新，电源多
    '北楼': 11,      # 北楼也可以，但我很久没去过了
    'A楼': 1,       # 别名映射
    'B楼': 2,
    'G楼': 3
}

# HACK 教室白名单机制？避免以后每次上游系统更新都要调整新的黑名单

# 教室黑名单配置（不适合自习的教室，或者接口有错的特判）
ROOM_BLACKLIST = {
    # 按关键词过滤
    'keywords': [
        # '机房',   # 济事楼机房，其实也不是不行
        '实验室',  
        '实验',
        '机械',    
        '化学',    
        '物理',    
        '生物',    
        '材料',    
        '电气',    
        '自动化',  
        '工程',    
        '制图',    
        '学院安排',
        '不排教室'
    ],

    # 按具体教室名称过滤
    'specific_rooms': [
        # 可以添加具体的教室名称
        # 例如：'A101机房', 'B203实验室'
    ],
}

# 楼宇名称标准化映射
BUILDING_NAME_MAPPING = {
    'A': '安楼',
    'B': '博楼',
    'C': 'C楼',
    'D': 'D楼',
    'E': 'E楼',
    'F': 'F楼',
    'G': 'G楼',
    'H': 'H楼',
    'J': 'J楼',
    'K': 'K楼',
    'L': 'L楼',
    'M': 'M楼',
    'N': '南楼',
    'S': '南楼',
    'Bei': '北楼',
    'Nan': '南楼',
    '北': '北楼',
    '南': '南楼',
    '安': '安楼',
    '博': '博楼',
    '综合': '综合楼',
    '图书': '图书馆',
    '实验': '实验楼',
    '教学': '教学楼'
}

# 推荐算法权重配置
RECOMMENDATION_WEIGHTS = {
    'priority_weight': 0.4,        # 楼宇优先级权重
    'availability_weight': 0.5,    # 可用时长权重
    'distance_weight': 0.1         # 距离权重（暂未实现）
}


def is_room_blacklisted(room_name):
    """
    检查教室是否在黑名单中

    Args:
        room_name (str): 教室名称

    Returns:
        bool: True if blacklisted, False otherwise
    """
    room_name_lower = room_name.lower()

    # 检查关键词 - 具体教室名称
    for keyword in ROOM_BLACKLIST['keywords']:
        if keyword in room_name or keyword.lower() in room_name_lower:
            return True

    # 检查黑名单
    if room_name in ROOM_BLACKLIST['specific_rooms']:
        return True

    return False

def is_room_whitelisted(room_name)

def get_building_priority(building_name):
    """
    获取楼宇优先级

    Args:
        building_name (str): 楼宇名称

    Returns:
        int: 优先级数字（越小优先级越高）
    """
    return BUILDING_PRIORITY.get(building_name, 99)  # 未知楼宇优先级最低


def normalize_building_name(raw_building):
    """
    标准化楼宇名称

    Args:
        raw_building (str): 原始楼宇名称

    Returns:
        str: 标准化后的楼宇名称
    """
    import re

    raw_building = raw_building.strip()

    # 首先尝试完整匹配
    for key, value in BUILDING_NAME_MAPPING.items():
        if key in raw_building:
            return value

    # 如果是单字母+数字的格式（如A101），提取字母部分
    match = re.match(r'^([A-Za-z]+)', raw_building)
    if match:
        letter = match.group(1).upper()
        if letter in BUILDING_NAME_MAPPING:
            return BUILDING_NAME_MAPPING[letter]
        return f"{letter}"

    # 提取中文楼宇名称
    chinese_match = re.search(r'([\u4e00-\u9fff]+楼?)', raw_building)
    if chinese_match:
        return chinese_match.group(1)

    # 如果都匹配不到，返回清理后的原始名称
    clean_name = re.sub(r'[^A-Za-z\u4e00-\u9fff]', '', raw_building)
    return clean_name if clean_name else raw_building
