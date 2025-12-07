from collections import deque
from enum import Enum
import time
from typing import Any, Generator, Optional, Tuple, override

from HeroAI.custom_skill import CustomSkillClass
from HeroAI.types import SkillType
from Py4GWCoreLib import AgentArray, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.GameData_enums import Profession, Range
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.bus.event_message import EventMessage
from Widgets.CustomBehaviors.primitives.bus.event_type import EventType
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.skills.utility_skill_execution_history import UtilitySkillExecutionHistory

class GenericScytheSkillUtility(CustomSkillUtilityBase):
    def __init__(self, 
                    event_bus: EventBus,
            current_build: list[CustomSkill], 
                    skill: CustomSkill,
            mana_required_to_cast: int = 5,
            is_manual: bool = False,
            score_definition: ScoreStaticDefinition = ScoreStaticDefinition(60),
            allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
            ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=skill,
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states
        )
        self.skill = skill
        self.current_optimal: Optional[custom_behavior_helpers.ScytheOptimalAttack] = None
        self.is_manual = is_manual
        self.score_definition: ScoreStaticDefinition = score_definition
        # Subscribe to map change events to reset timer
        if not self.is_manual:
            self.event_bus.subscribe(EventType.MAP_CHANGED, self.map_changed, subscriber_name=self.custom_skill.skill_name)
            self.event_bus.subscribe(EventType.MOVE_ATTACK_TARGET, self.move_attack_target, subscriber_name=self.custom_skill.skill_name)

    def map_changed(self, message: EventMessage) -> Generator[Any, Any, Any]:
        """Reset combat timer when map changes"""
        self.current_optimal = None
        yield
    
    def move_attack_target(self, message: EventMessage) -> Generator[Any, Any, Any]:
        self.current_optimal = message.data
        yield
    
    @override
    def _evaluate(self, current_state, previously_attempted_skills):
        if self.is_manual:
            if GLOBAL_CACHE.Player.GetTargetID() == -1:
                return None
        else:
            result = self.current_optimal
            if result is None: return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        if self.is_manual:
            result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
            return result
        optimal_attack = self.current_optimal
        if optimal_attack is None: return BehaviorResult.ACTION_SKIPPED
        if optimal_attack.distance_from_player > 30:
            yield from Routines.Yield.Movement.FollowPath(
                path_points=[optimal_attack.coordinates], 
                custom_exit_condition=lambda: False,
                tolerance=30,
                log=True, 
                timeout=4000, 
                progress_callback=lambda progress: print(f"GenericScytheSkillUtility: progress: {progress}"))
        result = yield from custom_behavior_helpers.Actions.cast_skill_to_target(self.custom_skill, target_agent_id=optimal_attack.enemy_id)
        return result
