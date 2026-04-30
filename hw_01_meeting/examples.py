"""
示例数据
提供默认的会议室、人员和会议数据用于演示
"""

from models import Room, Person, Meeting, TimeSlot


def get_default_rooms() -> list:
    """获取默认会议室列表"""
    return [
        Room(
            id="R1",
            name="大会议室",
            capacity=50,
            equipment=["projector", "whiteboard", "microphone", "video_conference"]
        ),
        Room(
            id="R2",
            name="中会议室A",
            capacity=20,
            equipment=["projector", "whiteboard"]
        ),
        Room(
            id="R3",
            name="中会议室B",
            capacity=20,
            equipment=["projector", "video_conference"]
        ),
        Room(
            id="R4",
            name="小会议室A",
            capacity=10,
            equipment=["whiteboard"]
        ),
        Room(
            id="R5",
            name="小会议室B",
            capacity=8,
            equipment=["projector"]
        ),
        Room(
            id="R6",
            name="洽谈室",
            capacity=6,
            equipment=["whiteboard"]
        ),
    ]


def get_default_persons() -> list:
    """获取默认人员列表"""
    return [
        Person(id="P1", name="张三", role="manager"),
        Person(id="P2", name="李四", role="engineer"),
        Person(id="P3", name="王五", role="designer"),
        Person(id="P4", name="赵六", role="product_manager"),
        Person(id="P5", name="孙七", role="engineer"),
        Person(id="P6", name="周八", role="tester"),
        Person(id="P7", name="吴九", role="manager"),
        Person(id="P8", name="郑十", role="engineer"),
        Person(id="P9", name="钱十一", role="designer"),
        Person(id="P10", name="陈十二", role="product_manager"),
    ]


def get_default_meetings() -> list:
    """获取默认会议列表"""
    return [
        Meeting(
            id="M1",
            name="全员周会",
            duration=1,
            attendees=["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"],
            required_equipment=["projector"],
            priority=5,
            preferred_slots=[TimeSlot("周一", 9)]
        ),
        Meeting(
            id="M2",
            name="产品评审",
            duration=2,
            attendees=["P1", "P4", "P10", "P3", "P9"],
            required_equipment=["projector", "whiteboard"],
            priority=5,
            preferred_slots=[TimeSlot("周一", 14)]
        ),
        Meeting(
            id="M3",
            name="技术分享",
            duration=1,
            attendees=["P2", "P5", "P8", "P6"],
            required_equipment=["projector"],
            priority=3,
            preferred_slots=[TimeSlot("周二", 10)]
        ),
        Meeting(
            id="M4",
            name="设计评审",
            duration=1,
            attendees=["P3", "P9", "P4", "P1"],
            required_equipment=["whiteboard"],
            priority=4,
            preferred_slots=[TimeSlot("周二", 14)]
        ),
        Meeting(
            id="M5",
            name="1对1面谈",
            duration=1,
            attendees=["P1", "P2"],
            required_equipment=[],
            priority=2,
            preferred_slots=[]
        ),
        Meeting(
            id="M6",
            name="客户演示",
            duration=2,
            attendees=["P1", "P4", "P3", "P7"],
            required_equipment=["projector", "video_conference"],
            priority=5,
            preferred_slots=[TimeSlot("周三", 10)]
        ),
        Meeting(
            id="M7",
            name="测试复盘",
            duration=1,
            attendees=["P6", "P5", "P8", "P4"],
            required_equipment=["whiteboard"],
            priority=3,
            preferred_slots=[TimeSlot("周四", 15)]
        ),
        Meeting(
            id="M8",
            name="架构讨论",
            duration=2,
            attendees=["P2", "P5", "P8", "P7"],
            required_equipment=["whiteboard"],
            priority=4,
            preferred_slots=[TimeSlot("周三", 14)]
        ),
        Meeting(
            id="M9",
            name="需求澄清",
            duration=1,
            attendees=["P4", "P10", "P3", "P2"],
            required_equipment=[],
            priority=3,
            preferred_slots=[]
        ),
        Meeting(
            id="M10",
            name="项目启动会",
            duration=2,
            attendees=["P1", "P7", "P4", "P2", "P3", "P5"],
            required_equipment=["projector", "whiteboard"],
            priority=5,
            preferred_slots=[TimeSlot("周五", 9)]
        ),
    ]
