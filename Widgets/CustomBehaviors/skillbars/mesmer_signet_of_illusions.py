from typing import override
from Py4GWCoreLib import Routines
from Py4GWCoreLib.GlobalCache import GLOBAL_CACHE
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skillbars.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.skills.generic.conditional_skill_utility import ConditionalSkillUtility
from Widgets.CustomBehaviors.skills.generic.hero_ai_utility import HeroAiUtility
from Widgets.CustomBehaviors.skills.generic.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.skills.generic.raw_aoe_attack_utility import RawAoeAttackUtility
from Widgets.CustomBehaviors.skills.mesmer.auspicious_incantation_utility import AuspiciousIncantationUtility
from Widgets.CustomBehaviors.skills.mesmer.cry_of_frustration_utility import CryOfFrustrationUtility
from Widgets.CustomBehaviors.skills.mesmer.mistrust_utility import MistrustUtility
from Widgets.CustomBehaviors.skills.mesmer.power_drain_utility import PowerDrainUtility
from Widgets.CustomBehaviors.skills.mesmer.shatter_hex_utility import ShatterHexUtility
from Widgets.CustomBehaviors.skills.monk.heal_party_utility import HealPartyUtility
from Widgets.CustomBehaviors.skills.monk.strength_of_honor_utility import StrengthOfHonorUtility
from Widgets.CustomBehaviors.skills.common.great_dwarf_weapon_utility import GreatDwarfWeaponUtility
from Widgets.CustomBehaviors.skills.necromancer.dark_aura_utility import DarkAuraUtility

class MesmerSignetOfIllusions_UtilitySkillBar(CustomBehaviorBaseUtility):
    def __init__(self):
        super().__init__()

        in_game_build = list(self.skillbar_management.get_in_game_build().values())

        #signet of illusion
        self.signet_of_illusions_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Signet_of_Illusions"), current_build=in_game_build, score_definition=ScoreStaticDefinition(90), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO])

        has_signet_of_illusion_effect = lambda : Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.signet_of_illusions_utility.custom_skill.skill_id)

        self.shatter_hex_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus,
                                                                                   condition=has_signet_of_illusion_effect,
                                                                                   original_skill=ShatterHexUtility(event_bus=self.event_bus,
                                                                                                     current_build=in_game_build,
                                                                                                     score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 81 if enemy_qte >= 2 else 20)))
        self.wandering_eye_utiltiy: CustomSkillUtilityBase = RawAoeAttackUtility(event_bus=self.event_bus, skill=CustomSkill("Wandering_Eye"), current_build=in_game_build)
        self.judges_insight: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=HeroAiUtility(event_bus=self.event_bus, skill=CustomSkill("Judges_Insight"), current_build=in_game_build, score_definition=ScoreStaticDefinition(60)))
        self.strength_of_honor_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=StrengthOfHonorUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(20)))
        self.arcane_conundrum_utility: CustomSkillUtilityBase = RawAoeAttackUtility(event_bus=self.event_bus, skill=CustomSkill("Arcane_Conundrum"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 80 if enemy_qte >= 3 else 52 if enemy_qte <= 2 else 0), mana_required_to_cast=12)
        self.mistrust_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=MistrustUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 70 if enemy_qte >= 3 else 40 if enemy_qte <= 2 else 0), mana_required_to_cast=10))
        self.cry_of_frustration_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=CryOfFrustrationUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(91)))
        self.power_drain_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=PowerDrainUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(92)))
        self.great_dwarf_weapon_utility: CustomSkillUtilityBase = GreatDwarfWeaponUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(30))

        # Must have both
        if any([x for x in in_game_build if x.skill_name == "Chilblains"]):
            self.auspicious_incantation_utility: CustomSkillUtilityBase = ConditionalSkillUtility(
                event_bus=self.event_bus, condition=has_signet_of_illusion_effect,
                original_skill=AuspiciousIncantationUtility(
                    event_bus=self.event_bus, current_build=in_game_build,
                    original_skill_to_cast=RawAoeAttackUtility(
                        event_bus=self.event_bus,
                        skill=CustomSkill("Chilblains"),
                        current_build=in_game_build,
                        score_definition=ScorePerAgentQuantityDefinition(lambda _: 89))))
        else:
            self.auspicious_incantation_utility: CustomSkillUtilityBase = ConditionalSkillUtility(
                event_bus=self.event_bus, condition=has_signet_of_illusion_effect,
                original_skill=AuspiciousIncantationUtility(
                    event_bus=self.event_bus, current_build=in_game_build,
                    original_skill_to_cast=HealPartyUtility(event_bus=self.event_bus, current_build=in_game_build)))
        # has_auspicious_incantation_effect = lambda : Routines.Checks.Effects.HasBuff(GLOBAL_CACHE.Player.GetAgentID(), self.auspicious_incantation_utility.custom_skill.skill_id)
        # self.chiblains_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect,
                                                                                #  original_skill=ConditionalSkillUtility(event_bus=self.event_bus, condition=has_auspicious_incantation_effect,
                                                                                    # original_skill=RawAoeAttackUtility(event_bus=self.event_bus, skill=CustomSkill("Chilblains"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda _: 89))))
        self.dark_aura_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=DarkAuraUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(82)))
        self.mark_of_pain_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect, original_skill=HeroAiUtility(event_bus=self.event_bus, skill=CustomSkill("Mark_of_Pain"), current_build=in_game_build))
        # self.heal_party_utility: CustomSkillUtilityBase = ConditionalSkillUtility(event_bus=self.event_bus, condition=has_signet_of_illusion_effect,
                                                                                #   original_skill=ConditionalSkillUtility(event_bus=self.event_bus, condition=has_auspicious_incantation_effect,
                                                                                                        #   original_skill=))

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return  [
            self.signet_of_illusions_utility,
            self.shatter_hex_utility,
            self.wandering_eye_utiltiy,
            self.strength_of_honor_utility,
            self.arcane_conundrum_utility,
            self.mistrust_utility,
            self.cry_of_frustration_utility,
            self.power_drain_utility,
            self.great_dwarf_weapon_utility,
            self.auspicious_incantation_utility,
            # self.chiblains_utility,
            self.dark_aura_utility,
            self.mark_of_pain_utility,
            self.judges_insight,
            # self.heal_party_utility
        ]
    
    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.signet_of_illusions_utility.custom_skill
        ]