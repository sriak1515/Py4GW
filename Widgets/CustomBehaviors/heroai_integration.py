import PyImGui
from Py4GWCoreLib.py4gwcorelib_src.Timer import ThrottledTimer
from Py4GW_widget_manager import get_widget_handler
from Widgets.CustomBehaviors.gui.current_build import render as current_build_render
from Widgets.CustomBehaviors.primitives.custom_behavior_loader import CustomBehaviorLoader
from Widgets.CustomBehaviors.primitives.skillbars.custom_behavior_base_utility import CustomBehaviorBaseUtility
from Widgets.CustomBehaviors.skills.common.scroll_of_resurrection_utility import ScrollOfResurrectionUtility

def get_custom_additional_skills(instance):
    """Helper function to generate a custom list of autonomous skills for an instance."""
    return [
        ScrollOfResurrectionUtility(current_build=instance.in_game_build),
    ]
@property
def custom_additional_autonomous_skills(self):
    return get_custom_additional_skills(self)

def disableCustomBehaviors():
    widget_handler = get_widget_handler()
    if widget_handler.is_widget_enabled("CustomBehaviors"):
        widget_handler.disable_widget("CustomBehaviors")
    # Disable autonomous skills as they are handled by HeroAI
    CustomBehaviorBaseUtility.additional_autonomous_skills = custom_additional_autonomous_skills


loader_throttler = ThrottledTimer(100)
refresh_throttler = ThrottledTimer(1_000)

def customBehaviorAct() -> bool:
    if loader_throttler.IsExpired(): 
        loader_throttler.Reset()
        loaded = CustomBehaviorLoader().initialize_custom_behavior_candidate()
        # Py4GW.Console.Log(MODULE_NAME, f"Tried to load custom behavior {loaded}", Py4GW.Console.MessageType.Info)
        if loaded: return False

    if refresh_throttler.IsExpired(): 
        refresh_throttler.Reset()
        if CustomBehaviorLoader().custom_combat_behavior is not None:
            if not CustomBehaviorLoader().custom_combat_behavior.is_custom_behavior_match_in_game_build():
                CustomBehaviorLoader().refresh_custom_behavior_candidate()
                return False

    if CustomBehaviorLoader().custom_combat_behavior is not None:
        return CustomBehaviorLoader().custom_combat_behavior.act()
    return False

def drawCustomBehaviorPortableGui():
    # PyImGui.set_next_window_size(260, 650)
    # PyImGui.set_next_window_size(460, 800)

    global party_forced_state_combo, monitor, widget_window_size, widget_window_pos

    window_flags = PyImGui.WindowFlags.AlwaysAutoResize

    if PyImGui.begin("Custom behaviors", window_flags):
        widget_window_size = PyImGui.get_window_size()
        widget_window_pos = PyImGui.get_window_pos()
        
        current_build_render()
    PyImGui.end()
    return