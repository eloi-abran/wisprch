import configparser
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_PATHS = [
    Path.home() / ".config/wisprch/wisprch.conf",
    Path("/etc/wisprch/wisprch.conf"),
]

class Config:
    def __init__(self, config_path: str | Path | None = None):
        self.config = configparser.ConfigParser()
        self._load_defaults()
        
        user_config_path = Path.home() / ".config/wisprch/wisprch.conf"
        
        if config_path:
            self.config.read(config_path)
        else:
            # Check if user config exists
            if user_config_path.exists():
                self.config.read(user_config_path)
            elif Path("/etc/wisprch/wisprch.conf").exists():
                self.config.read("/etc/wisprch/wisprch.conf")
            else:
                # No config found, create default user config
                self._create_default_config(user_config_path)
                # Read it back if it was created
                if user_config_path.exists():
                    self.config.read(user_config_path)
        if not self.config.has_option("openai", "refinement_model"):
            self.config.set("openai", "refinement_model", "gpt-4o-mini")

    def _create_default_config(self, path: str):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write("""[openai]
# Your OpenAI API Key (sk-...)
api_key = {api_key}

# Model for audio trancription
model = gpt-4o-transcribe

# Smart refinement: Use llm to remvoe fillers and fix formatting
smart_formatting = true

# model for refinemet
refinement_model = gpt-4o-mini

[audio]
# optional: Save recordings to ~/.local/share/wisprch/recordings
# save_recordings = true

[output]
# auto, hyprland, wtype, xdotool, or custom
paste_method = auto
# Delay before pasting (in ms)
paste_delay_ms = 50

[feedback]
# Play sounds for start/stop
sounds = true
# Show UI overlay
ui = true
""".format(api_key=os.environ.get("OPENAI_API_KEY", "")))
            print(f"Created default config at {path}")
        except Exception as e:
            print(f"Error creating default config at {path}: {e}")
            # If we can't write (e.g. permission error), just ignore it and use defaults in memory
            pass

    def _load_defaults(self):
        self.config.read_dict({
            "service": {
                "log_level": "info",
            },
            "audio": {
                "input_device": "default",
                "output_device": "default",
                "trailing_record_ms": "300",
                "max_duration_sec": "600",
                "save_recordings": "true",
                "save_dir": str(Path.home() / ".local/share/wisprch/recordings"),
            },
            "openai": {
                "api_key": "", # Allow setting api_key directly in config for ease of use
                "api_key_env": "OPENAI_API_KEY",
                "model": "whisper-1",
                "prompt_context": "Coding, Technical, Arch Linux",
                "language": "auto",
            },
            "formatting": {
                "mode": "smart",
            },
            "output": {
                "paste_method": "auto",
                "clipboard_method": "auto",
                "paste_delay_ms": "50",
                "clipboard_action": "always",
            },
            "ui": {
                "type": "overlay",
                "position": "bottom_center",
                "show_on_idle": "false",
                "error_display_ms": "3000",
            },
            "feedback": {
                "sounds": "true",
                "ui": "true",
                "sound_start": str(Path(__file__).parent / "sounds" / "toggle.wav"),
                "sound_stop": str(Path(__file__).parent / "sounds" / "toggle.wav"),
            }
        })

    def get(self, section: str, key: str, fallback: Any = None) -> str:
        return self.config.get(section, key, fallback=fallback)

    def getint(self, section: str, key: str, fallback: Any = None) -> int:
        return self.config.getint(section, key, fallback=fallback)

    def getboolean(self, section: str, key: str, fallback: Any = None) -> bool:
        return self.config.getboolean(section, key, fallback=fallback)

    @property
    def socket_path(self) -> str:
        # Default to XDG_RUNTIME_DIR or /run/user/$UID
        runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
        if not runtime_dir:
            uid = os.getuid()
            runtime_dir = f"/run/user/{uid}"
        
        return self.config.get("service", "socket_path", fallback=f"{runtime_dir}/wisprch.sock")
