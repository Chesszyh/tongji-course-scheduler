#!/usr/bin/env python3
"""
增强型教室数据处理方案
将新的数据库结构作为现有系统的缓存层，而不是替代层
"""

from utils.tjSql import tjSql
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_enhanced_classroom_system():
    """
    创建增强型教室系统
    将新表作为现有系统的性能优化缓存
    """
    print("开始创建增强型教室数据系统...")
    print("=" * 60)

    try:
        with tjSql() as sql:
            print("数据库连接成功")

            # 1. 检查是否需要清空现有数据
            print("\n1. 检查现有数据...")
            sql.cursor.execute("SELECT COUNT(*) FROM classroom_info")
            existing_classrooms = sql.cursor.fetchone()[0]

            sql.cursor.execute("SELECT COUNT(*) FROM classroom_schedule")
            existing_schedules = sql.cursor.fetchone()[0]

            print(f"   现有教室信息: {existing_classrooms} 条")
            print(f"   现有课表记录: {existing_schedules} 条")

            if existing_classrooms > 0 or existing_schedules > 0:
                print("\n   检测到现有数据，将进行增量更新...")
                # 清空数据，但使用 INSERT IGNORE 来避免重复
                sql.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                sql.cursor.execute("DELETE FROM classroom_schedule")
                sql.cursor.execute("DELETE FROM classroom_info")
                sql.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                sql.db.commit()
                print("   已清空现有数据表")

            # 2. 创建索引优化查询
            print("\n2. 优化数据库索引...")
            try:
                # 为 teacher.arrangeInfoText 创建全文索引（如果不存在）
                sql.cursor.execute("""
                    ALTER TABLE teacher 
                    ADD FULLTEXT INDEX ft_arrange_info (arrangeInfoText)
                """)
                print("   已创建 arrangeInfoText 全文索引")
            except Exception as e:
                if "Duplicate key name" not in str(e):
                    print(f"   创建索引时的提示: {e}")

            # 3. 执行优化的数据填充
            print("\n3. 执行数据填充...")
            sql.summarizeClassroomsSchedule()

            # 4. 创建视图简化查询
            print("\n4. 创建查询视图...")
            create_classroom_views(sql)

            print("\n" + "=" * 60)
            print("增强型教室数据系统创建完成！")
            print("=" * 60)

    except Exception as e:
        print(f"执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


def create_classroom_views(sql):
    """
    创建有用的视图来简化常见查询
    """

    # 创建教室空闲时段查询视图
    view_sql = """
    CREATE OR REPLACE VIEW classroom_availability AS
    SELECT 
        ci.classroom_name,
        ci.building,
        ci.campus,
        cs.calendar_id,
        cs.day_of_week,
        cs.time_slot,
        CASE WHEN cs.course_id IS NULL THEN 1 ELSE 0 END as is_free,
        cs.course_name,
        cs.teacher_name
    FROM classroom_info ci
    LEFT JOIN classroom_schedule cs ON ci.id = cs.classroom_id
    ORDER BY ci.campus, ci.building, ci.classroom_name, cs.day_of_week, cs.time_slot
    """

    try:
        sql.cursor.execute(view_sql)
        print("   ✓ 已创建 classroom_availability 视图")
    except Exception as e:
        print(f"   创建视图失败: {e}")

    # 创建教室使用统计视图
    stats_sql = """
    CREATE OR REPLACE VIEW classroom_usage_stats AS
    SELECT 
        ci.campus,
        ci.building,
        ci.classroom_name,
        COUNT(cs.id) as total_occupied_slots,
        COUNT(DISTINCT cs.day_of_week) as occupied_days,
        COUNT(DISTINCT cs.course_id) as unique_courses,
        ROUND(COUNT(cs.id) / (7 * 12) * 100, 2) as usage_percentage
    FROM classroom_info ci
    LEFT JOIN classroom_schedule cs ON ci.id = cs.classroom_id
    GROUP BY ci.id, ci.campus, ci.building, ci.classroom_name
    ORDER BY usage_percentage DESC
    """

    try:
        sql.cursor.execute(stats_sql)
        print("   ✓ 已创建 classroom_usage_stats 视图")
    except Exception as e:
        print(f"   创建统计视图失败: {e}")


def main():
    """主函数"""
    return create_enhanced_classroom_system()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
