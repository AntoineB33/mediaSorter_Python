from controllers import TaskController
from models import Settings

def test_toggle_sound():
    controller = TaskController(None)
    settings = controller.settings
    
    initial_state = settings.sound_enabled
    assert initial_state
    controller.toggle_sound()
    assert settings.sound_enabled != initial_state  # Should toggle

