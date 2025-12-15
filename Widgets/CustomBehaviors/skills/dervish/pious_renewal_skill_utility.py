from collections import deque
from enum import Enum
import time
from typing import Any, Generator, override

from HeroAI.custom_skill import CustomSkillClass
from HeroAI.types import SkillType
from Py4GWCoreLib import Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Py4GWCoreLib.enums_src.GameData_enums import Profession
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.helpers import custom_behavior_helpers
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.primitives.skills.utility_skill_execution_history import UtilitySkillExecutionHistory

class PiousRenewalSkillUtility(CustomSkillUtilityBase):
    def __init__(self, 
                    event_bus: EventBus,
                    original_skill: CustomSkillUtilityBase,
                    skill_execution_history: deque[UtilitySkillExecutionHistory]
            ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=original_skill.custom_skill,
            in_game_build=original_skill.in_game_build,
            allowed_states=original_skill.allowed_states
        )
        self.pious_renewal_custom_skill = CustomSkill("Pious_Renewal")
        self.original_skill: CustomSkillUtilityBase = original_skill
        self.skill_execution_history = skill_execution_history
        self.dervish_enchants_skill_ids = [skill.skill_id for skill in original_skill.in_game_build
                         if GLOBAL_CACHE.Skill.Flags.IsEnchantment(skill.skill_id) and GLOBAL_CACHE.Skill.GetProfession(skill.skill_id)[0] == Profession.Dervish.value]
        self.last_evaluate: float = 0

    def __current_time_in_ms(self) -> float:
        return int(time.time() * 1000)

    def _can_cast(self):
        if not Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.pious_renewal_custom_skill.skill_id):
            return False

        enchants_action_performed_history = [skill_execution
                            for skill_execution in self.skill_execution_history
                            if skill_execution.result == BehaviorResult.ACTION_PERFORMED
                            and skill_execution.skill.custom_skill.skill_id in self.dervish_enchants_skill_ids]
        if len(enchants_action_performed_history) == 0:
            return False
        last_enchant_perfomed_skill_execution = enchants_action_performed_history[-1]
        if last_enchant_perfomed_skill_execution.skill.custom_skill.skill_id == self.pious_renewal_custom_skill.skill_id:
            return True

    @override
    def _evaluate(self, current_state, previously_attempted_skills):
        now = self.__current_time_in_ms()
        self.last_evaluate = now
        if self._can_cast():
            return self.original_skill.evaluate(current_state, previously_attempted_skills)

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        if not self._can_cast():
            return BehaviorResult.ACTION_SKIPPED

        result = yield from self.original_skill.execute(state)
        return result
