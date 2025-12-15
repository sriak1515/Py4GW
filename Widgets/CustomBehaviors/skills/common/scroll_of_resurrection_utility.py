from enum import Enum
from typing import Any, Generator, override

from Py4GW import Console
from Py4GWCoreLib import AgentArray, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.scores.comon_score import CommonScore
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.skills.utility_skill_typology import UtilitySkillTypology

class ScrollOfResurrectionUtility(CustomSkillUtilityBase):
    def __init__(
            self, 
            event_bus: EventBus,
            current_build: list[CustomSkill], 
        ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("scroll_of_resurrection"), 
            in_game_build=current_build, 
            utility_skill_typology=UtilitySkillTypology.SCROLL_OF_RESURRECTION,
            allowed_states= [BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO, BehaviorState.IN_AGGRO])
        
        self.scroll_of_resurrection_item_id = ModelID.Scroll_Of_Resurrection
        self.score_definition: ScoreStaticDefinition = ScoreStaticDefinition(CommonScore.REZ.value)

    @override
    def are_common_pre_checks_valid(self, current_state):
        if current_state is BehaviorState.IDLE: return False
        if self.allowed_states is not None and current_state not in self.allowed_states: return False
        return True
    
    def _get_scroll_item_id(self):
        return GLOBAL_CACHE.Inventory.GetFirstModelID(self.scroll_of_resurrection_item_id)

    @staticmethod
    def _get_targets() -> list[int]:
        player_pos: tuple[float, float] = GLOBAL_CACHE.Player.GetXY()
        agent_ids: list[int] = GLOBAL_CACHE.AgentArray.GetAllyArray()
        agent_ids = AgentArray.Filter.ByCondition(agent_ids, lambda agent_id: GLOBAL_CACHE.Agent.IsDead(agent_id))
        agent_ids = AgentArray.Filter.ByDistance(agent_ids, player_pos, Range.Earshot.value)
        return agent_ids

    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        item_id = self._get_scroll_item_id()
        if item_id == 0:
            return None
        targets = self._get_targets()
        if len(targets) == 0:
            return None
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        """Execute resurrection on the target dead ally"""
        item_id = self._get_scroll_item_id()
        if item_id == 0:
            return BehaviorResult.ACTION_SKIPPED
        targets = self._get_targets()
        if len(targets) == 0:
            return BehaviorResult.ACTION_SKIPPED
        GLOBAL_CACHE.Inventory.UseItem(item_id)
        yield from Routines.Yield.wait(500)
        return BehaviorResult.ACTION_PERFORMED
