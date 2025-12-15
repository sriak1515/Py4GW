from typing import Any, Callable, Generator, override
from Widgets.CustomBehaviors.primitives.behavior_state import BehaviorState
from Widgets.CustomBehaviors.primitives.bus.event_bus import EventBus
from Widgets.CustomBehaviors.primitives.helpers.behavior_result import BehaviorResult
from Widgets.CustomBehaviors.primitives.skills.custom_skill_utility_base import CustomSkillUtilityBase


class ConditionalSkillUtility(CustomSkillUtilityBase):

    def __init__(self, 
                    condition: Callable[[], bool], 
                    original_skill: CustomSkillUtilityBase,
                    event_bus: EventBus
            ) -> None:
        super().__init__(
            event_bus=event_bus,
            skill=original_skill.custom_skill,
            in_game_build=original_skill.in_game_build,
            mana_required_to_cast=original_skill.mana_required_to_cast,
            allowed_states=original_skill.allowed_states
        )
        self.condition = condition
        self.original_skill = original_skill

    @override
    def _evaluate(self, current_state, previously_attempted_skills):
        if not self.condition(): return None
        return self.original_skill._evaluate(current_state, previously_attempted_skills)
    
    @override
    def _execute(self, state: BehaviorState) -> Generator[Any, None, BehaviorResult]:
        if not self.condition(): return BehaviorResult.ACTION_SKIPPED
        result = yield from self.original_skill._execute(state)
        return result
