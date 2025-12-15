from typing import override

from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skillbars.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.skills.common.i_am_unstoppable_utility import IAmUnstoppableUtility
from Widgets.CustomBehaviors.skills.dervish.pious_renewal_skill_utility import PiousRenewalSkillUtility
from Widgets.CustomBehaviors.skills.generic.conditional_skill_utility import ConditionalSkillUtility
from Widgets.CustomBehaviors.skills.generic.hero_ai_utility import HeroAiUtility
from Widgets.CustomBehaviors.skills.generic.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.skills.generic.raw_simple_attack_utility import RawSimpleAttackUtility

class DervishPiousRenewal_UtilitySkillBar(CustomBehaviorBaseUtility):
    def __init__(self):
        super().__init__()
        in_game_build = list(self.skillbar_management.get_in_game_build().values())

        self.pious_renewal_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Pious_Renewal"), current_build=in_game_build, score_definition=ScoreStaticDefinition(89), renew_before_expiration_in_milliseconds=6 * 1000, allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.pious_fury_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus, original_skill=KeepSelfEffectUpUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Pious_Fury"),
                current_build=in_game_build,
                score_definition=ScoreStaticDefinition(88),
                allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]),
                skill_execution_history=self.skill_execution_history)
        is_pious_renewal_recharged = lambda : GLOBAL_CACHE.SkillBar.GetSkillData(self.pious_renewal_utility.custom_skill.skill_slot).get_recharge < 1
        self.aura_of_holy_might_kurzick_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=is_pious_renewal_recharged, original_skill=KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Aura_of_Holy_Might_kurzick"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]))
        self.aura_of_holy_might_luxon_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=is_pious_renewal_recharged, original_skill=KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Aura_of_Holy_Might_luxon"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO]))
        # attacks
        self.twin_moon_sweep_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus,
            original_skill=RawSimpleAttackUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Twin_Moon_Sweep"),
                current_build=in_game_build,
                mana_required_to_cast=0,
                score_definition=ScoreStaticDefinition(87)),
            skill_execution_history=self.skill_execution_history)

        self.rending_sweep_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus,
            original_skill=RawSimpleAttackUtility(event_bus=self.event_bus,
                                                  skill=CustomSkill("Rending_Sweep"),
                                                  current_build=in_game_build,
                                                  mana_required_to_cast=0,
                                                  score_definition=ScoreStaticDefinition(86)),
            skill_execution_history=self.skill_execution_history)
        self.pious_assault_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus,
            original_skill=RawSimpleAttackUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Pious_Assault"),
                current_build=in_game_build,
                mana_required_to_cast=5,
                score_definition=ScoreStaticDefinition(85)),
            skill_execution_history=self.skill_execution_history)
        self.wearying_strike_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus,
            original_skill=RawSimpleAttackUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Wearying_Strike"),
                current_build=in_game_build,
                mana_required_to_cast=0,
                score_definition=ScoreStaticDefinition(84)),
            skill_execution_history=self.skill_execution_history)
        self.irresistible_sweep_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus,
            original_skill=RawSimpleAttackUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Irresistible_Sweep"),
                current_build=in_game_build,
                mana_required_to_cast=0,
                score_definition=ScoreStaticDefinition(86)),
            skill_execution_history=self.skill_execution_history)
        self.eremites_attack_utility: CustomSkillUtilityBase = PiousRenewalSkillUtility(
            event_bus=self.event_bus,
            original_skill=RawSimpleAttackUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Eremites_Attack"),
                current_build=in_game_build,
                mana_required_to_cast=0,
                score_definition=ScoreStaticDefinition(86)),
            skill_execution_history=self.skill_execution_history)

        self.reap_impurities_utility: CustomSkillUtilityBase = HeroAiUtility(event_bus=self.event_bus, skill=CustomSkill("Reap_Impurities"), current_build=in_game_build, score_definition=ScoreStaticDefinition(83), mana_required_to_cast=0)
        self.i_am_unstopabble: CustomSkillUtilityBase = IAmUnstoppableUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(99))
        self.masochism: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Masochism"), current_build=in_game_build, score_definition=ScoreStaticDefinition(91), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO])
        self.for_great_justice_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("For_Great_Justice"), current_build=in_game_build, score_definition=ScoreStaticDefinition(92), allowed_states=[BehaviorState.IN_AGGRO])
        self.whirlwind_attack_utility: CustomSkillUtilityBase = RawSimpleAttackUtility(event_bus=self.event_bus, skill=CustomSkill("Whirlwind_Attack"), current_build=in_game_build, mana_required_to_cast=0, score_definition=ScoreStaticDefinition(87))

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return  [
            self.pious_renewal_utility,
            self.pious_fury_utility,
            self.aura_of_holy_might_kurzick_utility,
            self.aura_of_holy_might_luxon_utility,
            self.twin_moon_sweep_utility,
            self.rending_sweep_utility,
            self.pious_assault_utility,
            self.wearying_strike_utility,
            self.irresistible_sweep_utility,
            self.eremites_attack_utility,
            self.reap_impurities_utility,
            self.i_am_unstopabble,
            self.masochism,
            self.for_great_justice_utility,
            self.whirlwind_attack_utility
        ]
    
    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.pious_renewal_utility.custom_skill
        ]