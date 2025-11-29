# Wisprch

![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/platform-Arch%20Linux-1793d1.svg?logo=archlinux&logoColor=white)


**Wisprch** is a minimal, speech-to-text utility for Arch Linux.

**Philosophy:** Press key → Speak → Release key → Text pasted.

## Installation

### AUR

```bash
# Coming soon
```

### Manual (Arch Linux)

Since `python-sounddevice` is not in the official Arch repositories, you must install it manually (via pip or AUR) before or after installing the package.

1.  **Install Runtime Dependency:**
    ```bash
    # Recommended: Use an AUR helper (handles system python automatically)
    yay -S python-sounddevice

    # Alternative: Manual pip install (must target system python)
    # sudo /usr/bin/python -m pip install sounddevice --break-system-packages
    ```

2.  **Install Wisprch:**
    ```bash
    git clone https://github.com/eloi-abran/wisprch.git
    cd wisprch
    makepkg -si
    ```
   *This will install all necessary dependencies (python, wl-clipboard, wtype) and the systemd service.*

## Getting Started

### 1. Start the Daemon

Wisprch requires a background service to handle audio recording and transcription.

**Recommended: Use systemd (Auto-start)**
```bash
systemctl --user enable --now wisprch
```
*This ensures Wisprch runs in the background and starts automatically on reboot.*

**Alternative: Run manually**
```bash
wisprch-server
```

### 2. Configuration

The configuration file is **automatically created** at `~/.config/wisprch/wisprch.conf` the first time you run the client or server.

Edit it to set your OpenAI API key:

```ini
[openai]
api_key = your-openai-api-key-here
```

### 3. Bind Keys (Hyperland Example)

Add these bindings to your `hyprland.conf` to control Wisprch:

**Option A: Hold-to-Talk**
   ```ini
   bind = SUPER, Z, exec, wisprch start
   bindr = SUPER, Z, exec, wisprch stop
   ```

**Option B: Toggle-to-Talk**
   ```ini
   bind = SUPER, Z, exec, wisprch toggle
   ```

## Roadmap

- [ ] **Wider Support**: Integration with Anthropic, Google, and others.
- [ ] **Local Models**: Support for running local models.
- [ ] **IDE Integration**: Context-aware so you can reference files in your directory.
- [ ] **Context Awareness**: Integration with other applications to better understand user context.
- [ ] **Custom Vocabulary**: Ability to create a custom dictionary for your own use.
- [ ] **AUR Package**: Publish to the Arch User Repository for easier installation.

## CLI Reference

You can control the Wisprch daemon using the following commands:

- `wisprch start`   - Start recording audio immediately.
- `wisprch stop`    - Stop recording and begin transcription/pasting.
- `wisprch toggle`  - Toggle recording state useful for hands-free operation.
- `wisprch cancel`  - Cancel the current recording without transcribing.
- `wisprch status`  - Check if the daemon is running and healthy.
- `wisprch version` - Display the installed version.
- `wisprch help`    - Show help message.