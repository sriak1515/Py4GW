# python
from enum import Enum
from typing import Any, Generator, override

import PyImGui

from Py4GWCoreLib import GLOBAL_CACHE, Routines
from Py4GWCoreLib.enums_src.GameData_enums import Range
from Py4GWCoreLib.enums_src.Model_enums import SpiritModelID
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.bus.event_type import EventType
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.skills.generic.raw_spirit_utility import RawSpiritUtility

class RitualLordState(Enum):
    CAST_RITUAL_LORD = 1
    CAST_SKILL = 2
    IDLE = 3

class RitualLordSpiritUtility(CustomSkillUtilityBase):

    def __init__(self,
        event_bus: EventBus,
        spirit_skill: CustomSkill,
        current_build: list[CustomSkill],
        owned_spirit_model_id: SpiritModelID,
        score_definition: ScoreStaticDefinition = ScoreStaticDefinition(60),
        sacrifice_life_limit_percent: float = 0.55,
        sacrifice_life_limit_absolute: int = 175,
        mana_required_to_cast: int = 0,
        allowed_states: list[BehaviorState] = [BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]
        ) -> None:

        super().__init__(
            event_bus=event_bus,
            skill=spirit_skill,
            in_game_build=current_build,
            score_definition=score_definition,
            mana_required_to_cast=mana_required_to_cast,
            allowed_states=allowed_states
        )

        self.score_definition: ScoreStaticDefinition = score_definition
        self.sacrifice_life_limit_percent: float = sacrifice_life_limit_percent
        self.sacrifice_life_limit_absolute: int = sacrifice_life_limit_absolute
        self.ritual_lord_skill = CustomSkill("Ritual_Lord")
        self.spirit_skill = RawSpiritUtility(event_bus=event_bus, skill=spirit_skill, current_build=current_build, owned_spirit_model_id=owned_spirit_model_id)
        self.owned_spirit_model_id: SpiritModelID = owned_spirit_model_id

    def are_common_pre_checks_valid(self, current_state: BehaviorState) -> bool:
        if current_state is BehaviorState.IDLE:
            return False
        if self.allowed_states is not None and current_state not in self.allowed_states:
            return False
        if custom_behavior_helpers.Resources.get_player_absolute_energy() < self.mana_required_to_cast:
            return False
        return True

    def _get_ritual_lord_state(self, current_state: BehaviorState) -> RitualLordState:

        if Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.ritual_lord_skill.skill_id):
            return RitualLordState.CAST_SKILL

        is_ritual_lord_ready = Routines.Checks.Skills.IsSkillIDReady(self.ritual_lord_skill.skill_id)
        is_spirit_skill_ready = Routines.Checks.Skills.IsSkillIDReady(self.spirit_skill.custom_skill.skill_id)
        has_health_for_ritual_lord = custom_behavior_helpers.Resources.player_can_sacrifice_health(2, self.sacrifice_life_limit_percent, self.sacrifice_life_limit_absolute)
        has_energy_for_spirit_skill = custom_behavior_helpers.Resources.has_enough_resources(self.spirit_skill.custom_skill)
        is_target_prechecks_valid = self.spirit_skill.are_common_pre_checks_valid(current_state)
        has_spirit_enough_health = custom_behavior_helpers.Resources.is_spirit_exist(
                within_range=Range.Spellcast,
                associated_to_skill=self.spirit_skill.custom_skill,
                condition=lambda agent_id: GLOBAL_CACHE.Agent.GetHealth(agent_id) > 0.3)

        if is_ritual_lord_ready and is_spirit_skill_ready and has_health_for_ritual_lord and has_energy_for_spirit_skill and is_target_prechecks_valid and not has_spirit_enough_health:
            return RitualLordState.CAST_RITUAL_LORD

        return RitualLordState.IDLE

    def _evaluate(self, current_state: BehaviorState, previously_attempted_skills: list[CustomSkill]) -> float | None:

        state = self._get_ritual_lord_state(current_state)

        match state:
            case RitualLordState.CAST_RITUAL_LORD:
                return self.score_definition.get_score()
            case RitualLordState.CAST_SKILL:
                return 95  # force immediate cast of the target skill while buff is active
            case RitualLordState.IDLE:
                return None

    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:

        ritual_lord_state = self._get_ritual_lord_state(state)

        match ritual_lord_state:
            case RitualLordState.CAST_RITUAL_LORD:
                result = yield from custom_behavior_helpers.Actions.cast_skill(self.ritual_lord_skill)
                return result
            case RitualLordState.CAST_SKILL:
                result = yield from self.spirit_skill.execute(state)
                return result
            case RitualLordState.IDLE:
                return BehaviorResult.ACTION_SKIPPED

    def customized_debug_ui(self, current_state: BehaviorState) -> None:
        PyImGui.bullet_text(f"internal state : {self._get_ritual_lord_state(current_state)}")
