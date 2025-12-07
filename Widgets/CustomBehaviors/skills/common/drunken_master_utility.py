from enum import Enum
from typing import Any, Generator, override

from Py4GW import Console
from Py4GWCoreLib import AgentArray, Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.enums_src.Model_enums import ModelID
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.scores.comon_score import CommonScore
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.skills.utility_skill_typology import UtilitySkillTypology

class DrunkenMasterUtility(CustomSkillUtilityBase):
    def __init__(
            self, 
            event_bus: EventBus,
            current_build: list[CustomSkill], 
            mana_required_to_cast: int = 5,
            score_definition: ScoreStaticDefinition = ScoreStaticDefinition(60),
            allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO]
        ):
        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Drunken_Master"), 
            score_definition=score_definition,
            in_game_build=current_build, 
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states)
        self.score_definition: ScoreStaticDefinition = score_definition
        
    @override
    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        has_buff = Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.custom_skill.skill_id)
        if has_buff:
            return
        return self.score_definition.get_score()

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        yield from Routines.Yield.Upkeepers.Upkeep_Alcohol(target_alc_level=1, disable_drunk_effects=True)
        result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
        return result 
