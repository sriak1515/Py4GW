from collections import deque
from enum import Enum
import time
from typing import Any, Generator, List, Tuple, override

import PyImGui

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

class ReapingState(Enum):
        CAST_ENCHANTMENT=1
        CAST_ATTACK=2
        IDLE=3

class EnchantmentReapingSkillUtility(CustomSkillUtilityBase):
    def __init__(self, 
                    event_bus: EventBus,
                    original_skill: CustomSkillUtilityBase,
                    skill_execution_history: deque[UtilitySkillExecutionHistory],
                    excluded_skills: List[CustomSkill] = []
            ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=original_skill.custom_skill,
            in_game_build=original_skill.in_game_build,
            allowed_states=original_skill.allowed_states
        )
        self.original_skill: CustomSkillUtilityBase = original_skill
        self.excluded_skills = set([skill.skill_id for skill in excluded_skills])
        self.skill_execution_history = skill_execution_history
        self.dervish_enchants_skills: List[CustomSkill] = [skill for skill in original_skill.in_game_build
                         if GLOBAL_CACHE.Skill.Flags.IsEnchantment(skill.skill_id) and
                            GLOBAL_CACHE.Skill.GetProfession(skill.skill_id)[0] == Profession.Dervish.value]
        self.dervish_enchants_skill_ids = [skill.skill_id for skill in self.dervish_enchants_skills]


    def _has_dervish_buf(self):
        enchants_action_performed_history = [skill_execution
                            for skill_execution in self.skill_execution_history
                            if skill_execution.result == BehaviorResult.ACTION_PERFORMED
                            and skill_execution.skill.custom_skill.skill_id in self.dervish_enchants_skill_ids]
        if len(enchants_action_performed_history) == 0:
            return False
        last_enchant_perfomed_skill_id = enchants_action_performed_history[-1].skill.custom_skill.skill_id
        if last_enchant_perfomed_skill_id in self.excluded_skills:
            return False
        else:
            return True

    def _get_state(self, current_state: BehaviorState) -> Tuple[ReapingState, CustomSkill | None]:
        if self._has_dervish_buf():
            return ReapingState.CAST_ATTACK, None
        
        enchantment = self.get_recharched_dervish_enchantment_skill_slot()
        if enchantment:
            is_enchantment_recharged = Routines.Checks.Skills.IsSkillIDReady(enchantment.skill_id)
            is_skill_to_copy_ready = Routines.Checks.Skills.IsSkillIDReady(self.original_skill.custom_skill.skill_id)
            has_enough_energy_to_cast_enchantment = custom_behavior_helpers.Resources.has_enough_resources(enchantment)
            has_enough_energy_to_cast_attack = custom_behavior_helpers.Resources.has_enough_resources(self.original_skill.custom_skill)
            is_skill_to_copy_pre_checks_valid = self.original_skill.are_common_pre_checks_valid(current_state)
            if is_enchantment_recharged and is_skill_to_copy_ready and has_enough_energy_to_cast_enchantment and has_enough_energy_to_cast_attack and is_skill_to_copy_pre_checks_valid:
                return ReapingState.CAST_ENCHANTMENT, enchantment
        return ReapingState.IDLE, None

    def get_recharched_dervish_enchantment_skill_slot(self) -> CustomSkill | None:
        for skill in self.dervish_enchants_skills:
            if skill.skill_id in self.excluded_skills:
                continue
            if Routines.Checks.Skills.IsSkillSlotReady(skill.skill_slot) and custom_behavior_helpers.Resources.has_enough_resources(skill):
                return skill
        return None

    @override
    def _evaluate(self, current_state, previously_attempted_skills):
        state, _ = self._get_state(current_state)
        match state:
            case ReapingState.CAST_ENCHANTMENT | ReapingState.CAST_ATTACK:
                return self.original_skill.evaluate(current_state, previously_attempted_skills)
            case ReapingState.IDLE:
                return None

    @override
    def _execute(self, state: BehaviorState) -> Generator[Any | None, Any | None, BehaviorResult]:
        ench_state, ench = self._get_state(state)
        match ench_state:
            case ReapingState.CAST_ENCHANTMENT:
                if ench:
                    result = yield from custom_behavior_helpers.Actions.cast_skill(ench)
                    return result
                return BehaviorResult.ACTION_SKIPPED
            case ReapingState.CAST_ATTACK:
                result = yield from self.original_skill.execute(state)
                return result
            case ReapingState.IDLE:
                return BehaviorResult.ACTION_SKIPPED

    @override
    def customized_debug_ui(self, current_state: BehaviorState) -> None:
        state, ench = self._get_state(current_state)
        PyImGui.bullet_text(f"internal state : {state}")
        if ench is not None:
            PyImGui.bullet_text(f"enchantment: {ench.skill_name}")

