"""
数据模型定义
包含会议室、人员、会议等基本数据结构
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from enum import Enum


class TimeSlot:
    """时间槽，表示一天中的一个时间段"""
    
    DAYS = ["周一", "周二", "周三", "周四", "周五"]
    HOURS = list(range(9, 20))  # 9:00 - 19:00
    
    def __init__(self, day: str, hour: int):
        if day not in self.DAYS:
            raise ValueError(f"无效的日期: {day}")
        if hour not in self.HOURS:
            raise ValueError(f"无效的时间: {hour}")
        self.day = day
        self.hour = hour
    
    def __repr__(self):
        return f"{self.day} {self.hour:02d}:00-{self.hour+1:02d}:00"
    
    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return False
        return self.day == other.day and self.hour == other.hour
    
    def __hash__(self):
        return hash((self.day, self.hour))
    
    @classmethod
    def get_all_slots(cls) -> List['TimeSlot']:
        """获取所有可能的时间槽"""
        slots = []
        for day in cls.DAYS:
            for hour in cls.HOURS:
                slots.append(cls(day, hour))
        return slots


@dataclass
class Room:
    """会议室"""
    id: str
    name: str
    capacity: int
    equipment: List[str] = field(default_factory=list)
    
    def has_equipment(self, required: List[str]) -> bool:
        """检查是否具备所需设备"""
        return all(eq in self.equipment for eq in required)
    
    def __repr__(self):
        return f"{self.name}(容量:{self.capacity}, 设备:{','.join(self.equipment)})"


@dataclass
class Person:
    """人员"""
    id: str
    name: str
    role: str = "member"
    unavailable_slots: Set[TimeSlot] = field(default_factory=set)
    
    def is_available(self, slot: TimeSlot) -> bool:
        """检查在指定时间是否可用"""
        return slot not in self.unavailable_slots
    
    def __repr__(self):
        return f"{self.name}({self.role})"


@dataclass
class Meeting:
    """会议"""
    id: str
    name: str
    duration: int  # 持续时间（小时）
    attendees: List[str]  # 参会人员ID列表
    required_equipment: List[str] = field(default_factory=list)
    priority: int = 1  # 优先级 1-5
    preferred_slots: List[TimeSlot] = field(default_factory=list)  # 偏好时间
    
    def __post_init__(self):
        if not 1 <= self.priority <= 5:
            raise ValueError("优先级必须在1-5之间")
    
    def __repr__(self):
        return f"{self.name}(优先级:{self.priority}, 时长:{self.duration}h, 参会:{len(self.attendees)}人)"


@dataclass
class ScheduledMeeting:
    """已安排的会议"""
    meeting: Meeting
    room: Room
    start_slot: TimeSlot
    
    def get_time_slots(self) -> List[TimeSlot]:
        """获取该会议占用的所有时间槽"""
        slots = []
        for i in range(self.meeting.duration):
            hour = self.start_slot.hour + i
            if hour <= 19:
                slot = TimeSlot(self.start_slot.day, hour)
                slots.append(slot)
        return slots
    
    def __repr__(self):
        slots = self.get_time_slots()
        if len(slots) == 1:
            time_str = str(slots[0])
        else:
            time_str = f"{slots[0].day} {slots[0].hour:02d}:00-{slots[-1].hour+1:02d}:00"
        return f"{self.meeting.name} @ {self.room.name} [{time_str}]"
