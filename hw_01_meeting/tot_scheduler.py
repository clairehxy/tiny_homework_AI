"""
思维树(ToT)调度器核心实现
使用束搜索(Beam Search)策略实现会议安排
"""

import heapq
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from models import Meeting, Room, Person, TimeSlot, ScheduledMeeting
from constraints import ConstraintChecker


@dataclass
class Node:
    """思维树节点 - 表示一个部分安排方案"""
    scheduled: List[ScheduledMeeting] = field(default_factory=list)
    remaining: List[Meeting] = field(default_factory=list)
    score: float = 0.0
    depth: int = 0
    
    def __lt__(self, other):
        """用于优先级队列比较"""
        return self.score > other.score  # 分数高的优先
    
    def copy(self) -> 'Node':
        """创建节点的深拷贝"""
        return Node(
            scheduled=self.scheduled.copy(),
            remaining=self.remaining.copy(),
            score=self.score,
            depth=self.depth
        )


class ToTScheduler:
    """
    基于思维树(ToT)的会议调度器
    
    使用束搜索策略，每层保留最优的K个节点
    通过评估函数指导搜索方向，找到近似最优的会议安排方案
    """
    
    def __init__(self, beam_width: int = 3, max_depth: int = 50):
        """
        初始化调度器
        
        Args:
            beam_width: 束宽，每层保留的节点数
            max_depth: 最大搜索深度
        """
        self.beam_width = beam_width
        self.max_depth = max_depth
        self.rooms: Dict[str, Room] = {}
        self.persons: Dict[str, Person] = {}
        self.meetings: List[Meeting] = []
        self.checker = ConstraintChecker()
        
        # 统计信息
        self.stats = {
            'nodes_expanded': 0,
            'max_depth_reached': 0,
            'solution_found': False
        }
    
    def add_room(self, room: Room):
        """添加会议室"""
        self.rooms[room.id] = room
    
    def add_person(self, person: Person):
        """添加人员"""
        self.persons[person.id] = person
    
    def add_meeting(self, meeting: Meeting):
        """添加会议"""
        self.meetings.append(meeting)
    
    def schedule(self) -> Dict:
        """
        执行会议调度
        
        Returns:
            包含安排结果的字典
        """
        if not self.meetings:
            return self._build_result(Node())
        
        # 按优先级排序（高优先级优先）
        sorted_meetings = sorted(
            self.meetings, 
            key=lambda m: (-m.priority, len(m.attendees))
        )
        
        # 初始化根节点
        root = Node(remaining=sorted_meetings)
        
        # 束搜索
        beams = [root]
        best_node = root
        
        for depth in range(min(self.max_depth, len(self.meetings))):
            self.stats['max_depth_reached'] = depth
            
            if not beams:
                break
            
            # 扩展当前层的所有节点
            candidates = []
            for node in beams:
                if not node.remaining:
                    # 所有会议已安排
                    if node.score > best_node.score:
                        best_node = node
                    continue
                
                # 扩展节点
                children = self._expand_node(node)
                candidates.extend(children)
                self.stats['nodes_expanded'] += len(children)
            
            # 选择最优的K个节点作为下一层
            if candidates:
                beams = heapq.nlargest(self.beam_width, candidates)
                # 更新最优解
                for node in beams:
                    if not node.remaining and node.score > best_node.score:
                        best_node = node
            else:
                beams = []
        
        if not best_node.remaining:
            self.stats['solution_found'] = True
        
        return self._build_result(best_node)
    
    def _expand_node(self, node: Node) -> List[Node]:
        """
        扩展节点 - 为下一个会议生成所有可能的安排方案
        
        Args:
            node: 当前节点
            
        Returns:
            子节点列表
        """
        if not node.remaining:
            return []
        
        children = []
        next_meeting = node.remaining[0]
        remaining_meetings = node.remaining[1:]
        
        # 获取所有可能的时间槽
        all_slots = TimeSlot.get_all_slots()
        
        # 如果有偏好时间，优先尝试
        if next_meeting.preferred_slots:
            preferred = [s for s in all_slots if s in next_meeting.preferred_slots]
            other = [s for s in all_slots if s not in next_meeting.preferred_slots]
            all_slots = preferred + other
        
        for slot in all_slots:
            for room in self.rooms.values():
                # 检查约束
                if self.checker.check_all(
                    next_meeting, room, slot, 
                    node.scheduled, self.persons
                ):
                    # 创建新节点
                    child = node.copy()
                    scheduled_meeting = ScheduledMeeting(
                        meeting=next_meeting,
                        room=room,
                        start_slot=slot
                    )
                    child.scheduled.append(scheduled_meeting)
                    child.remaining = remaining_meetings
                    child.depth = node.depth + 1
                    child.score = self._evaluate_node(child)
                    children.append(child)
        
        # 如果没有可行的安排，保留原节点（跳过此会议）
        if not children:
            child = node.copy()
            child.remaining = remaining_meetings
            child.depth = node.depth + 1
            child.score = self._evaluate_node(child)
            children.append(child)
        
        return children
    
    def _evaluate_node(self, node: Node) -> float:
        """
        评估节点得分
        
        评分标准：
        1. 已安排会议的基础分（优先级越高分数越高）
        2. 会议室利用率奖励
        3. 时间连续性奖励（减少碎片化）
        4. 高优先级会议优先安排的奖励
        
        Args:
            node: 待评估的节点
            
        Returns:
            节点得分
        """
        score = 0.0
        
        # 1. 已安排会议的基础分
        for sm in node.scheduled:
            priority_weight = sm.meeting.priority * 10
            score += priority_weight
        
        # 2. 会议室利用率奖励（避免大会议室开小会）
        for sm in node.scheduled:
            utilization = len(sm.meeting.attendees) / sm.room.capacity
            if utilization >= 0.5:
                score += 2  # 利用率合理
            elif utilization < 0.3:
                score -= 1  # 利用率过低
        
        # 3. 时间连续性奖励
        day_groups = {}
        for sm in node.scheduled:
            day = sm.start_slot.day
            if day not in day_groups:
                day_groups[day] = []
            day_groups[day].append(sm.start_slot.hour)
        
        for hours in day_groups.values():
            hours.sort()
            for i in range(1, len(hours)):
                if hours[i] - hours[i-1] == 1:
                    score += 0.5  # 连续会议奖励
        
        # 4. 高优先级会议优先安排的额外奖励
        scheduled_ids = {sm.meeting.id for sm in node.scheduled}
        for meeting in self.meetings:
            if meeting.id in scheduled_ids and meeting.priority >= 4:
                score += 5
        
        return score
    
    def _build_result(self, node: Node) -> Dict:
        """
        构建最终结果
        
        Args:
            node: 最优节点
            
        Returns:
            包含安排结果和统计信息的字典
        """
        scheduled_ids = {sm.meeting.id for sm in node.scheduled}
        unscheduled = [m for m in self.meetings if m.id not in scheduled_ids]
        
        # 计算会议室利用率
        room_usage = {rid: 0 for rid in self.rooms}
        for sm in node.scheduled:
            room_usage[sm.room.id] += sm.meeting.duration
        
        total_slots = len(TimeSlot.get_all_slots())
        avg_utilization = sum(room_usage.values()) / (len(self.rooms) * total_slots) * 100 if self.rooms else 0
        
        return {
            'scheduled': node.scheduled,
            'unscheduled': unscheduled,
            'score': node.score,
            'stats': {
                'total_meetings': len(self.meetings),
                'scheduled_count': len(node.scheduled),
                'unscheduled_count': len(unscheduled),
                'success_rate': len(node.scheduled) / len(self.meetings) * 100 if self.meetings else 0,
                'avg_room_utilization': avg_utilization,
                'nodes_expanded': self.stats['nodes_expanded'],
                'max_depth': self.stats['max_depth_reached'],
                'solution_found': self.stats['solution_found']
            }
        }
