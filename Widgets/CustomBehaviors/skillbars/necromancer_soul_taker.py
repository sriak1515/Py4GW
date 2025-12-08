from typing import override

from Widgets.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skillbars.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.skills.assassin.assassins_promise_utility import AssassinsPromiseUtility
from Widgets.CustomBehaviors.skills.common.auto_attack_utility import AutoAttackUtility
from Widgets.CustomBehaviors.skills.common.auto_attack_move_utility import AutoAttackMoveUtility
from Widgets.CustomBehaviors.skills.common.breath_of_the_great_dwarf_utility import BreathOfTheGreatDwarfUtility
from Widgets.CustomBehaviors.skills.common.by_urals_hammer_utility import ByUralsHammerUtility
from Widgets.CustomBehaviors.skills.common.drunken_master_utility import DrunkenMasterUtility
from Widgets.CustomBehaviors.skills.common.ebon_battle_standard_of_wisdom_utility import EbonBattleStandardOfWisdom
from Widgets.CustomBehaviors.skills.common.ebon_vanguard_assassin_support_utility import EbonVanguardAssassinSupportUtility
from Widgets.CustomBehaviors.skills.common.finish_him_utility import FinishHimUtility
from Widgets.CustomBehaviors.skills.common.great_dwarf_weapon_utility import GreatDwarfWeaponUtility
from Widgets.CustomBehaviors.skills.common.i_am_unstoppable_utility import IAmUnstoppableUtility
from Widgets.CustomBehaviors.skills.dervish.enchantment_reaping_skill_utility import EnchantmentReapingSkillUtility
from Widgets.CustomBehaviors.skills.dervish.generic_scythe_skill_utility import GenericScytheSkillUtility
from Widgets.CustomBehaviors.skills.dervish.optimal_scythe_target_utility import OptimalScytheTargetUtility
from Widgets.CustomBehaviors.skills.generic.generic_resurrection_utility import GenericResurrectionUtility
from Widgets.CustomBehaviors.skills.generic.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.skills.monk.strength_of_honor_utility import StrengthOfHonorUtility
from Widgets.CustomBehaviors.skills.necromancer.blood_bond_utility import BloodBondUtility
from Widgets.CustomBehaviors.skills.necromancer.dark_aura_utility import DarkAuraUtility
from Widgets.CustomBehaviors.skills.necromancer.signet_of_lost_souls_utility import SignetOfLostSoulsUtility
from Widgets.CustomBehaviors.skills.paragon.fall_back_utility import FallBackUtility


class NecromancerSoulTakerSupport_UtilitySkillBar(CustomBehaviorBaseUtility):

    def __init__(self):
        super().__init__()

        IS_MANUAL = True
        in_game_build = list(self.skillbar_management.get_in_game_build().values())

        # core skills
        self.soul_taker_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Soul_Taker"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90), renew_before_expiration_in_milliseconds=1100)
        self.masochism_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Masochism"), current_build=in_game_build, score_definition=ScoreStaticDefinition(89), renew_before_expiration_in_milliseconds=1100)

        self.grenths_aura_utility = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Grenths_Aura"), current_build=in_game_build, score_definition=ScoreStaticDefinition(82))

        # combat
        self.twin_moon_sweep_utility: CustomSkillUtilityBase = EnchantmentReapingSkillUtility(
            event_bus=self.event_bus,
            excluded_skills=[self.grenths_aura_utility.custom_skill],
            skill_execution_history=self.skill_execution_history,
            original_skill=GenericScytheSkillUtility(
                event_bus=self.event_bus,
                skill=CustomSkill("Twin_Moon_Sweep"),
                current_build=in_game_build,
                mana_required_to_cast=10,
                is_manual=IS_MANUAL,
                score_definition=ScoreStaticDefinition(87)))

        self.rending_sweep_utility: CustomSkillUtilityBase = EnchantmentReapingSkillUtility(
            event_bus=self.event_bus,
            excluded_skills=[self.grenths_aura_utility.custom_skill],
            skill_execution_history=self.skill_execution_history,
            original_skill=GenericScytheSkillUtility(event_bus=self.event_bus,
                                                  skill=CustomSkill("Eremites_Attack"),
                                                  current_build=in_game_build,
                                                  is_manual=IS_MANUAL,
                                                  mana_required_to_cast=15,
                                                  score_definition=ScoreStaticDefinition(86)))

        self.mystic_sweep_utility = GenericScytheSkillUtility(event_bus=self.event_bus,
                                                  skill=CustomSkill("Mystic_Sweep"),
                                                  current_build=in_game_build,
                                                  is_manual=IS_MANUAL,
                                                  mana_required_to_cast=15,
                                                  score_definition=ScoreStaticDefinition(80))
        

        # self.optimal_scythe_target_utility: CustomSkillUtilityBase = OptimalScytheTargetUtility(event_bus=self.event_bus, current_build=in_game_build)
        self.auto_attack_move_utiltiy = CustomSkillUtilityBase = AutoAttackMoveUtility(self.event_bus, in_game_build)

        # common
        self.drunken_master_utility: CustomSkillUtilityBase = DrunkenMasterUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(91))
        self.ebon_vanguard_assassin_support: CustomSkillUtilityBase = EbonVanguardAssassinSupportUtility(event_bus=self.event_bus, score_definition=ScoreStaticDefinition(71), current_build=in_game_build, mana_required_to_cast=15)
        self.ebon_battle_standard_of_wisdom: CustomSkillUtilityBase = EbonBattleStandardOfWisdom(event_bus=self.event_bus, score_definition= ScorePerAgentQuantityDefinition(lambda agent_qte: 80 if agent_qte >= 3 else 60 if agent_qte <= 2 else 40), current_build=in_game_build, mana_required_to_cast=18)
        self.i_am_unstopabble: CustomSkillUtilityBase = IAmUnstoppableUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(99))
        self.fall_back_utility: CustomSkillUtilityBase = FallBackUtility(event_bus=self.event_bus, current_build=in_game_build)
        self.signet_of_lost_souls_utility: CustomSkillUtilityBase = SignetOfLostSoulsUtility(event_bus=self.event_bus, current_build=in_game_build)
        self.by_urals_hammer_utility: CustomSkillUtilityBase = ByUralsHammerUtility(event_bus=self.event_bus, current_build=in_game_build)
        self.assassins_promise_utility: CustomSkillUtilityBase = AssassinsPromiseUtility(event_bus=self.event_bus, current_build=in_game_build)
        self.strength_of_honor_utility: CustomSkillUtilityBase = StrengthOfHonorUtility(event_bus=self.event_bus, current_build=in_game_build)
        self.finish_him_utility: CustomSkillUtilityBase = FinishHimUtility(event_bus=self.event_bus, current_build=in_game_build)

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return False

    # @property
    # @override
    # def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
    #     skills = super().additional_autonomous_skills
    #     skills = [x for x in skills if not isinstance(x, AutoAttackUtility)]
    #     # skills.append(self.optimal_scythe_target_utility)
    #     skills.append(self.auto_attack_move_utiltiy)
    #     return skills

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.soul_taker_utility,
            self.grenths_aura_utility,
            self.twin_moon_sweep_utility,
            self.rending_sweep_utility,
            self.mystic_sweep_utility,
            self.drunken_master_utility,
            self.ebon_vanguard_assassin_support,
            self.ebon_battle_standard_of_wisdom,
            self.i_am_unstopabble,
            self.fall_back_utility,
            self.signet_of_lost_souls_utility,
            self.by_urals_hammer_utility,
            self.soul_taker_utility,
            self.masochism_utility,
            self.assassins_promise_utility,
            self.strength_of_honor_utility,
            self.finish_him_utility,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.soul_taker_utility.custom_skill,
        ]
