
from typing import override
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.scores.score_per_health_gravity_definition import ScorePerHealthGravityDefinition
from Widgets.CustomBehaviors.primitives.scores.score_static_definition import ScoreStaticDefinition
from Widgets.CustomBehaviors.primitives.skillbars.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.primitives.skills.custom_skill import CustomSkill
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase
from Widgets.CustomBehaviors.skills.common.auto_attack_utility import AutoAttackUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_block_utility import BrawlingBlockUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_jab_utility import BrawlingJabUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_straight_right_utility import BrawlingStraitRightUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_hook_utility import BrawlingHookUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_uppercut_utility import BrawlingUppercutUtility
from Widgets.CustomBehaviors.skills.kilroy.brawling_headbutt_utility import BrawlingHeadbuttUtility
from Widgets.CustomBehaviors.skills.kilroy.stand_up_utility import StandUpUtility


class Kilroy_UtilitySkillBar(CustomBehaviorBaseUtility):
    def __init__(self):
        super().__init__()
        in_game_build = list(self.skillbar_management.get_in_game_build().values())
        self.auto_attack: CustomSkillUtilityBase = AutoAttackUtility(event_bus=self.event_bus, current_build=in_game_build)

        # core
        self.brawling_block_utility: CustomSkillUtilityBase = BrawlingBlockUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(95))
        self.brawling_jab_utility = BrawlingJabUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(70))
        self.brawling_straight_right_utility = BrawlingStraitRightUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(94))
        self.brawling_hook_utility = BrawlingHookUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(91))
        self.brawling_uppercut_utility = BrawlingUppercutUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(93))
        self.brawling_headbutt_utility = BrawlingHeadbuttUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(92))
        self.stand_up_utility = StandUpUtility(event_bus=self.event_bus, current_build=in_game_build, score_definition=ScoreStaticDefinition(99))

    @property
    @override
    def additional_autonomous_skills(self) -> list[CustomSkillUtilityBase]:
        return [
            self.auto_attack,
        ]

    @property
    @override
    def complete_build_with_generic_skills(self) -> bool:
        return True

    @property
    @override
    def skills_allowed_in_behavior(self) -> list[CustomSkillUtilityBase]:
        return [
            self.brawling_block_utility,
            self.brawling_jab_utility,
            self.brawling_straight_right_utility,
            self.brawling_hook_utility,
            self.brawling_uppercut_utility,
            self.brawling_headbutt_utility,
            self.stand_up_utility
        ]

    @property
    @override
    def skills_required_in_behavior(self) -> list[CustomSkill]:
        return [
            self.brawling_block_utility.custom_skill,
            self.brawling_jab_utility.custom_skill,
            self.brawling_straight_right_utility.custom_skill,
            self.brawling_hook_utility.custom_skill,
            self.brawling_uppercut_utility.custom_skill,
            self.brawling_headbutt_utility.custom_skill,
            self.stand_up_utility.custom_skill
        ]
