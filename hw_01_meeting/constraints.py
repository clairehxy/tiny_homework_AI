"""
约束条件检查模块
实现会议安排的各种约束验证
"""

from typing import List, Dict, Set
from models import Meeting, Room, Person, TimeSlot, ScheduledMeeting


class ConstraintChecker:
    """约束检查器"""
    
    def __init__(self):
        self.violations: List[str] = []
    
    def check_all(self, meeting: Meeting, room: Room, start_slot: TimeSlot,
                  scheduled: List[ScheduledMeeting], persons: Dict[str, Person]) -> bool:
        """检查所有约束条件"""
        self.violations = []
        
        checks = [
            self._check_room_capacity(meeting, room),
            self._check_room_equipment(meeting, room),
            self._check_room_conflict(meeting, room, start_slot, scheduled),
            self._check_person_conflict(meeting, start_slot, scheduled, persons),
            self._check_person_availability(meeting, start_slot, persons),
            self._check_time_validity(meeting, start_slot),
        ]
        
        return all(checks)
    
    def get_violations(self) -> List[str]:
        """获取违规信息"""
        return self.violations
    
    def _check_room_capacity(self, meeting: Meeting, room: Room) -> bool:
        """检查会议室容量"""
        if len(meeting.attendees) > room.capacity:
            self.violations.append(
                f"会议室'{room.name}'容量不足: 需要{len(meeting.attendees)}人, 只有{room.capacity}人"
            )
            return False
        return True
    
    def _check_room_equipment(self, meeting: Meeting, room: Room) -> bool:
        """检查会议室设备"""
        if not room.has_equipment(meeting.required_equipment):
            missing = [eq for eq in meeting.required_equipment if eq not in room.equipment]
            self.violations.append(f"会议室'{room.name}'缺少设备: {', '.join(missing)}")
            return False
        return True
    
    def _check_room_conflict(self, meeting: Meeting, room: Room, start_slot: TimeSlot,
                             scheduled: List[ScheduledMeeting]) -> bool:
        """检查会议室时间冲突"""
        new_slots = set()
        for i in range(meeting.duration):
            hour = start_slot.hour + i
            if hour > 19:
                continue
            slot = TimeSlot(start_slot.day, hour)
            new_slots.add(slot)
        
        for sm in scheduled:
            if sm.room.id != room.id:
                continue
            existing_slots = set(sm.get_time_slots())
            if new_slots & existing_slots:
                self.violations.append(
                    f"会议室'{room.name}'在{start_slot}时段已被占用"
                )
                return False
        return True
    
    def _check_person_conflict(self, meeting: Meeting, start_slot: TimeSlot,
                               scheduled: List[ScheduledMeeting], 
                               persons: Dict[str, Person]) -> bool:
        """检查人员时间冲突"""
        new_slots = set()
        for i in range(meeting.duration):
            hour = start_slot.hour + i
            if hour > 19:
                continue
            slot = TimeSlot(start_slot.day, hour)
            new_slots.add(slot)
        
        for sm in scheduled:
            existing_slots = set(sm.get_time_slots())
            overlap = new_slots & existing_slots
            if not overlap:
                continue
            
            # 检查是否有共同参会人员
            common_attendees = set(meeting.attendees) & set(sm.meeting.attendees)
            if common_attendees:
                names = [persons[pid].name for pid in common_attendees if pid in persons]
                self.violations.append(
                    f"人员冲突: {', '.join(names)} 在重叠时段已有其他会议"
                )
                return False
        return True
    
    def _check_person_availability(self, meeting: Meeting, start_slot: TimeSlot,
                                   persons: Dict[str, Person]) -> bool:
        """检查人员是否可用"""
        for pid in meeting.attendees:
            if pid not in persons:
                continue
            person = persons[pid]
            for i in range(meeting.duration):
                hour = start_slot.hour + i
                if hour > 19:
                    continue
                slot = TimeSlot(start_slot.day, hour)
                if not person.is_available(slot):
                    self.violations.append(
                        f"{person.name}在{slot}时段不可用"
                    )
                    return False
        return True
    
    def _check_time_validity(self, meeting: Meeting, start_slot: TimeSlot) -> bool:
        """检查时间有效性（不超出工作时段）"""
        for i in range(meeting.duration):
            hour = start_slot.hour + i
            if hour > 19:
                self.violations.append(
                    f"会议时长{meeting.duration}小时超出工作时段"
                )
                return False
        return True
