
from typing import override
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.scores.score_per_agent_quantity_definition import ScorePerAgentQuantityDefinition
from Widgets.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skillbars.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.skills.common.auto_attack_utility import AutoAttackUtility
from Widgets.CustomBehaviors.skills.generic.keep_self_effect_up_utility import KeepSelfEffectUpUtility
from Widgets.CustomBehaviors.skills.generic.raw_aoe_attack_utility import RawAoeAttackUtility
from Widgets.CustomBehaviors.skills.generic.raw_simple_attack_utility import RawSimpleAttackUtility
from Widgets.CustomBehaviors.skills.halloween.sugar_shock_utility import SugarShockUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_block_utility import BrawlingBlockUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_jab_utility import BrawlingJabUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_straight_right_utility import BrawlingStraitRightUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_hook_utility import BrawlingHookUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_uppercut_utility import BrawlingUppercutUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_headbutt_utility import BrawlingHeadbuttUtility
from Widgets.CustomBehaviors.skills.kilroy.stand_up_utility import StandUpUtility


class Halloween_UtilitySkillBar(CustomBehaviorBaseUtility):
    def __init__(self):
        super().__init__()
        in_game_build = list(self.skillbar_management.get_in_game_build().values())
        self.auto_attack: CustomSkillUtilityBase = AutoAttackUtility(event_bus=self.event_bus, current_build=in_game_build)

        # core
        self.sugar_rush_utility: CustomSkillUtilityBase = KeepSelfEffectUpUtility(event_bus=self.event_bus, skill=CustomSkill("Sugar_Rush_Agent_of_the_Mad_King"), current_build=in_game_build, score_definition=ScoreStaticDefinition(80), allowed_states=[BehaviorState.IN_AGGRO, BehaviorState.CLOSE_TO_AGGRO, BehaviorState.FAR_FROM_AGGRO])
        self.sticky_ground_utility = RawAoeAttackUtility(event_bus=self.event_bus, skill=CustomSkill("Sticky_Ground"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 70 if enemy_qte >= 3 else 0 if enemy_qte <= 2 else 0), mana_required_to_cast=30)
        self.sugar_shock_utility = SugarShockUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(79), mana_required_to_cast=20)
        self.the_mad_kings_influence_utility = RawAoeAttackUtility(event_bus=self.event_bus, skill=CustomSkill("The_Mad_Kings_Influence"), current_build=in_game_build, score_definition=ScorePerAgentQuantityDefinition(lambda enemy_qte: 80 if enemy_qte >= 3 else 60 if enemy_qte <= 2 else 0))

    @property
    @override
    def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
        return []

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return True

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.sugar_rush_utility,
            self.sticky_ground_utility,
            self.sugar_shock_utility,
            self.the_mad_kings_influence_utility,
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.sugar_rush_utility.custom_skill,
            self.sticky_ground_utility.custom_skill,
            self.sugar_shock_utility.custom_skill,
            self.the_mad_kings_influence_utility.custom_skill
        ]
