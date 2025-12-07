from typing import Any, Generator, Optional, override

from Py4GWCoreLib import GLOBAL_CACHE, Routines, Range
from Py4GWCoreLib.Py4GWcorelib import ThrottledTimer
from Widgets.CustomBehaviors.primitives.bus.event_message import EventMessage
from Widgets.CustomBehaviors.primitives.bus.event_type import EventType
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.scores.comon_score import CommonScore
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.helpers.targeting_order import TargetingOrder
import time
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus

class AutoAttackMoveUtility(CustomSkillUtilityBase):
    def __init__(
            self,
            event_bus: EventBus,
            current_build: list[CustomSkill],
            allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("auto_attack"),
            in_game_build=current_build,
            score_definition=ScoreStaticDefinition(CommonScore.AUTO_ATTACK.value),
            allowed_states=allowed_states)

        self.score_definition: ScoreStaticDefinition = ScoreStaticDefinition(CommonScore.AUTO_ATTACK.value)
        self.current_optimal: Optional[custom_behavior_helpers.ScytheOptimalAttack] = None
        self.throttle_timer = ThrottledTimer(1000)
        # Subscribe to map change events to reset timer
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
    def are_common_pre_checks_valid(self, current_state: BehaviorState) -> bool:
        if current_state is BehaviorState.IDLE: return False
        if self.allowed_states is not None and current_state not in self.allowed_states: return False
        return True

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        if self.allowed_states is not None and current_state not in self.allowed_states:
            return None

        if not self.throttle_timer.IsExpired():
            return None

        if custom_behavior_helpers.Resources.is_player_holding_an_item():
            return None

        result = self.current_optimal
        if result is None: return None

        if GLOBAL_CACHE.Agent.IsAttacking(GLOBAL_CACHE.Player.GetAgentID()):
            self.throttle_timer.Reset()
            return None

        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
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

        result = yield from custom_behavior_helpers.Actions.auto_attack(target_id=optimal_attack.enemy_id)
        self.throttle_timer.Reset()
        return result
