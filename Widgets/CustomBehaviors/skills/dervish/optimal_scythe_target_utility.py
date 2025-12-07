from enum import Enum
from typing import Any, Generator, override

from Py4GW import Console
import PyImGui
from Py4GWCoreLib import AgentArray, Overlay, Routines, Utils
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.bus.event_message import EventMessage
from Widgets.CustomBehaviors.primitives.bus.event_type import EventType
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.scores.comon_score import CommonScore
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.skills.utility_skill_typology import UtilitySkillTypology

class OptimalScytheTargetUtility(CustomSkillUtilityBase):
    def __init__(
            self, 
            event_bus: EventBus,
            current_build: list[CustomSkill], 
        ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("scythe_optimal_target"), 
            in_game_build=current_build, 
            utility_skill_typology=UtilitySkillTypology.COMBAT,
            allowed_states= [BehaviorState.CLOSE_TO_AGGRO, BehaviorState.IN_AGGRO])
        self.target_switch_timer = ThrottledTimer(5000)  # 5 seconds
        self.score_definition: ScoreStaticDefinition = ScoreStaticDefinition(0)
        self.current_optimal = None
        self.event_bus.subscribe(EventType.MAP_CHANGED, self.map_changed, subscriber_name=self.custom_skill.skill_name)

    def map_changed(self, message: EventMessage) -> Generator[Any, Any, Any]:
        """Reset combat timer when map changes"""
        self.target_switch_timer.Reset()
        self.current_optimal = None
        yield

    @override
    def are_common_pre_checks_valid(self, current_state):
        if current_state is BehaviorState.IDLE: return False
        if self.allowed_states is not None and current_state not in self.allowed_states: return False
        return True
    
    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        if self.current_optimal is not None:
            if GLOBAL_CACHE.Agent.IsDead(self.current_optimal.enemy_id):
                self.target_switch_timer.Reset()
                return 95
            enemy_xy = GLOBAL_CACHE.Agent.GetXY(self.current_optimal.enemy_id)
            player_xy = GLOBAL_CACHE.Agent.GetXY(GLOBAL_CACHE.Player.GetAgentID())
            if Utils.Distance(enemy_xy, player_xy) > Range.Earshot.value:
                self.target_switch_timer.Reset()
                return 95
        if not self.target_switch_timer.IsExpired():
            return None
        self.target_switch_timer.Reset()
        return 95


    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        optimal = custom_behavior_helpers.Targets.get_optimal_scythe_move_and_target(Range.Earshot, weight_cleave=10, weight_adjacent= 20)
        if optimal is None:
            return BehaviorResult.ACTION_SKIPPED
        else:
        #     Overlay().BeginDraw()
        #     X, Y, Z = GLOBAL_CACHE.Agent.GetXYZ(optimal.enemy_id)
        #     Overlay().DrawPolyFilled3D(X, Y, Z, Range.Nearby.value, Utils.RGBToColor(255, 0, 0, 128))
        #     # Overlay().DrawText3D(X, Y, Z, optimal.score, Utils.RGBToColor(255, 255, 255, 255))
        #     Overlay().EndDraw()
            if self.current_optimal is not None and self.current_optimal.enemy_id == optimal.enemy_id:
                return BehaviorResult.ACTION_SKIPPED
            self.current_optimal = optimal
            print(f"Switch target to {self.current_optimal.enemy_id} = {self.current_optimal.score}")
            yield from self.event_bus.publish(EventType.MOVE_ATTACK_TARGET, state, optimal, self.custom_skill.skill_name)
            return BehaviorResult.ACTION_PERFORMED

    @override
    def customized_debug_ui(self, current_state: BehaviorState) -> None:
        PyImGui.bullet_text(f"Current optimal : {self.current_optimal.enemy_id}: {self.current_optimal.score}")
