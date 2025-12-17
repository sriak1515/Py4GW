# python
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, Generator, List, Optional, override

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, AgentArray, Routines
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.enums_src.Model_enums import SPIRIT_BUFF_MAP, SpiritModelID
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.bus.event_type import EventType
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.skills.utility_skill_execution_history import UtilitySkillExecutionHistory
from Widgets.CustomBehaviors.skills.generic.raw_spirit_utility import RawSpiritUtility


spirit_skill_to_model_id: Dict[int, int] = {skill_id: model_id for model_id, skill_id in SPIRIT_BUFF_MAP.items()}


@dataclass
class SpiritSkill:
    name: str
    score: ScoreStaticDefinition
    skill: CustomSkill
    model_id: int

    def __init__(self, name: str, score: ScoreStaticDefinition):
        self.name = name
        self.score = score
        self.skill = CustomSkill(name)
        if self.skill.skill_id not in spirit_skill_to_model_id:
            raise ValueError("Invalid spirit: " + name)
        self.model_id = spirit_skill_to_model_id[self.skill.skill_id]


allowed_spirits: List[SpiritSkill] = [
    SpiritSkill("Shelter", ScoreStaticDefinition(66)),
    SpiritSkill("Union", ScoreStaticDefinition(65)),
    SpiritSkill("Displacement", ScoreStaticDefinition(64)),
    SpiritSkill("Earthbind", ScoreStaticDefinition(60)),
]


class RitualLordUtility(CustomSkillUtilityBase):

    def __init__(
        self,
        event_bus: EventBus,
        current_build: list[CustomSkill],
        sacrifice_life_limit_percent: float = 0.55,
        sacrifice_life_limit_absolute: int = 175,
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO],
    ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=CustomSkill("Ritual_Lord"),
            in_game_build=current_build,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states,
        )

        self.sacrifice_life_limit_percent: float = sacrifice_life_limit_percent
        self.sacrifice_life_limit_absolute: int = sacrifice_life_limit_absolute
        self.ritual_lord_skill = self.custom_skill
        self.is_shelter_covered: bool = False
        skill_ids = [skill.skill_id for skill in current_build]
        self.available_spirits = [spirit for spirit in allowed_spirits if spirit.skill.skill_id in skill_ids]

    def are_common_pre_checks_valid(self, current_state: BehaviorState) -> bool:
        if current_state is BehaviorState.IDLE:
            return False
        if self.allowed_states is not None and current_state not in self.allowed_states:
            return False
        if custom_behavior_helpers.Resources.get_player_absolute_energy() < self.mana_required_to_cast:
            return False
        return True

    def get_spirits_array(self, condition: Optional[Callable[[int], bool]] = None) -> List[int]:
        spirit_array = GLOBAL_CACHE.AgentArray.GetSpiritPetArray()
        spirit_array = AgentArray.Filter.ByDistance(spirit_array, GLOBAL_CACHE.Player.GetXY(), Range.Spellcast.value)
        spirit_array = AgentArray.Filter.ByCondition(
            spirit_array, lambda agent_id: GLOBAL_CACHE.Agent.IsAlive(agent_id)
        )
        spirit_array = AgentArray.Filter.ByCondition(
            spirit_array, lambda agent_id: GLOBAL_CACHE.Agent.IsSpawned(agent_id)
        )
        if condition is not None:
            spirit_array = AgentArray.Filter.ByCondition(spirit_array, condition)
        return spirit_array

    def spirit_exists(self, spirit_skill: SpiritSkill, spirits_array: List[int]) -> bool:
        for spirit_id in spirits_array:
            model_value = GLOBAL_CACHE.Agent.GetPlayerNumber(spirit_id)
            if spirit_skill.model_id == model_value:
                return True
        return False

    def get_spirit_to_cast(self) -> Optional[SpiritSkill]:
        spirits_array = self.get_spirits_array(lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)
        for spirit_skill in self.available_spirits:
            is_spirit_skill_ready = Routines.Checks.Skills.IsSkillIDReady(spirit_skill.skill.skill_id)
            has_energy_for_spirit_skill = custom_behavior_helpers.Resources.has_enough_resources(spirit_skill.skill)

            if not is_spirit_skill_ready or not has_energy_for_spirit_skill:
                continue

            if spirit_skill.name == "Union" and not self.is_shelter_covered:
                return spirit_skill

            if not self.spirit_exists(spirit_skill, spirits_array):
                return spirit_skill

            if (
                spirit_skill.name != "Earthbind"
                and GLOBAL_CACHE.Effects.GetEffectTimeRemaining(
                    GLOBAL_CACHE.Player.GetAgentID(), spirit_skill.skill.skill_id
                )
                < 5 * 1000
            ):
                return spirit_skill

    def is_ritual_lord_ready(self) -> bool:
        is_ritual_lord_ready = Routines.Checks.Skills.IsSkillIDReady(self.ritual_lord_skill.skill_id)
        has_health_for_ritual_lord = custom_behavior_helpers.Resources.player_can_sacrifice_health(
            2, self.sacrifice_life_limit_percent, self.sacrifice_life_limit_absolute
        )
        return is_ritual_lord_ready and has_health_for_ritual_lord

    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:
        if Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.ritual_lord_skill.skill_id):
            return 99

        if self.is_ritual_lord_ready():
            spirit = self.get_spirit_to_cast()
            if spirit is not None:
                return spirit.score.get_score()
        return None

    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        if Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.ritual_lord_skill.skill_id):
            spirit = self.get_spirit_to_cast()
            if spirit is not None:
                result = yield from custom_behavior_helpers.Actions.cast_skill(spirit.skill)
                if result == BehaviorResult.ACTION_PERFORMED:
                    if spirit.name == "Shelter":
                        self.is_shelter_covered = False
                    elif spirit.name == "Union" and Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), CustomSkill("Shelter").skill_id):
                        self.is_shelter_covered = True
                    yield from self.event_bus.publish(EventType.SPIRIT_CREATED, state, data=spirit.model_id)
                return result
        if self.is_ritual_lord_ready():
            result = yield from custom_behavior_helpers.Actions.cast_skill(self.custom_skill)
            return result
        return BehaviorResult.ACTION_SKIPPED

    @override
    def customized_debug_ui(self, current_state: BehaviorState) -> None:
        PyImGui.bullet_text(f"Spirit to cast : {self.get_spirit_to_cast()}")
        PyImGui.bullet_text(f"Union covers shelter: {self.is_shelter_covered}")
