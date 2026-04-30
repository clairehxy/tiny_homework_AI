"""
主程序入口
演示如何使用ToT调度器安排会议
"""

from tot_scheduler import ToTScheduler
from examples import get_default_rooms, get_default_persons, get_default_meetings


def print_schedule_result(result: dict):
    """打印调度结果"""
    scheduled = result['scheduled']
    unscheduled = result['unscheduled']
    stats = result['stats']
    
    print("=" * 60)
    print("会议安排结果")
    print("=" * 60)
    
    # 已安排的会议
    if scheduled:
        print("\n【已安排会议】\n")
        for i, sm in enumerate(scheduled, 1):
            meeting = sm.meeting
            print(f"{i}. {meeting.name} (优先级: {'★' * meeting.priority})")
            print(f"   时间: {sm}")
            print(f"   参会人员: {', '.join(meeting.attendees)} ({len(meeting.attendees)}人)")
            print(f"   所需设备: {', '.join(meeting.required_equipment) if meeting.required_equipment else '无'}")
            print()
    
    # 未安排的会议
    if unscheduled:
        print("\n【未能安排的会议】\n")
        for i, meeting in enumerate(unscheduled, 1):
            print(f"{i}. {meeting.name} (优先级: {'★' * meeting.priority})")
            print(f"   参会: {len(meeting.attendees)}人, 时长: {meeting.duration}小时")
            print(f"   原因: 无满足所有约束条件的时间/会议室组合")
            print()
    
    # 统计信息
    print("\n【统计信息】\n")
    print(f"总会议数: {stats['total_meetings']}")
    print(f"成功安排: {stats['scheduled_count']} ({stats['success_rate']:.1f}%)")
    print(f"未能安排: {stats['unscheduled_count']}")
    print(f"会议室平均利用率: {stats['avg_room_utilization']:.1f}%")
    print(f"思维树搜索深度: {stats['max_depth']}")
    print(f"扩展节点数: {stats['nodes_expanded']}")
    print(f"是否找到完整解: {'是' if stats['solution_found'] else '否'}")
    print(f"方案得分: {result['score']:.2f}")
    print("=" * 60)


def main():
    """主函数"""
    print("\n智能会议安排系统 - 基于思维树(ToT)方法\n")
    print("正在初始化数据...\n")
    
    # 创建调度器
    scheduler = ToTScheduler(beam_width=3, max_depth=20)
    
    # 添加会议室
    print("加载会议室...")
    for room in get_default_rooms():
        scheduler.add_room(room)
        print(f"  [OK] {room}")
    
    # 添加人员
    print("\n加载人员...")
    for person in get_default_persons():
        scheduler.add_person(person)
        print(f"  [OK] {person}")
    
    # 添加会议
    print("\n加载会议...")
    for meeting in get_default_meetings():
        scheduler.add_meeting(meeting)
        print(f"  [OK] {meeting}")
    
    # 执行调度
    print("\n正在使用思维树(ToT)方法进行调度...")
    print("束宽(Beam Width):", scheduler.beam_width)
    print("最大深度(Max Depth):", scheduler.max_depth)
    print()
    
    result = scheduler.schedule()
    
    # 打印结果
    print_schedule_result(result)
    
    # 输出ToT方法说明
    print("\n【思维树(ToT)方法说明】\n")
    print("1. 节点设计: 每个节点代表一个部分安排方案")
    print("2. 分支生成: 为每个待安排会议生成所有可行的时间/会议室组合")
    print("3. 评估函数: 综合优先级、会议室利用率、时间连续性评分")
    print("4. 束搜索: 每层保留评分最高的3个节点，剪枝低分路径")
    print("5. 回溯机制: 当某路径无法继续时，自动回溯尝试其他分支")
    print()


if __name__ == "__main__":
    main()
