import gi
import logging
import threading
import ctypes

try:
    # Workaround for linking order issue
    # RTLD_GLOBAL ensures symbols are available to subsequently loaded libraries
    ctypes.CDLL('libgtk4-layer-shell.so', mode=ctypes.RTLD_GLOBAL)
    
    gi.require_version('Gtk', '4.0')
    gi.require_version('Gtk4LayerShell', '1.0')
    from gi.repository import Gtk, Gdk, GLib, Gtk4LayerShell
    GTK_AVAILABLE = True
except (ValueError, OSError):
    GTK_AVAILABLE = False

class FeedbackUI:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.app = None
        self.window = None
        self.label = None
        self.dots_box = None
        self.dots = []
        self.proc_dots_box = None
        self.proc_dots = []
        self.proc_timer = None
        self.icon = None
        self.box = None
        
        if not GTK_AVAILABLE:
            self.logger.warning("GTK4 or Gtk4LayerShell not available. UI disabled.")
            return

        self.app = Gtk.Application(application_id="com.wisprch.feedback")
        self.app.connect('activate', self._on_activate)

    def _on_activate(self, app):
        self.logger.info("UI: Activating...")
        self.window = Gtk.Window(application=app)
        Gtk4LayerShell.init_for_window(self.window)
        
        # Configure Layer Shell
        Gtk4LayerShell.set_namespace(self.window, "wisprch")
        Gtk4LayerShell.set_layer(self.window, Gtk4LayerShell.Layer.OVERLAY)
        Gtk4LayerShell.set_keyboard_mode(self.window, Gtk4LayerShell.KeyboardMode.NONE)
        
        # Anchor to bottom center
        # Anchor to bottom center
        Gtk4LayerShell.set_anchor(self.window, Gtk4LayerShell.Edge.BOTTOM, True)
        Gtk4LayerShell.set_margin(self.window, Gtk4LayerShell.Edge.BOTTOM, 20) # A bit higher
        
        # UI Content
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.set_margin_top(8)
        self.box.set_margin_bottom(8)
        self.box.set_margin_start(12)
        self.box.set_margin_end(12)
        
        # Use a simpler icon without the "waves"
        # audio-input-microphone-symbolic is very standard
        self.icon = Gtk.Image.new_from_icon_name("audio-input-microphone-symbolic")
        self.icon.set_pixel_size(16)
        
        # Vertical dots meter
        self.dots_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.dots_box.set_valign(Gtk.Align.CENTER)
        
        self.dots = []
        for i in range(3):
            d = Gtk.Box()
            d.add_css_class("dot-indicator")
            d.set_size_request(4, 4) # Base size
            d.set_halign(Gtk.Align.CENTER)
            d.set_valign(Gtk.Align.CENTER)
            self.dots.append(d)
            # Prepend to stack bottom-to-top visually (since box is top-to-bottom)
            self.dots_box.prepend(d)
            
        self.label = Gtk.Label(label="Ready")
        
        # Processing dots (Horizontal)
        self.proc_dots_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        self.proc_dots_box.set_valign(Gtk.Align.END) # Align to bottom/baseline
        self.proc_dots_box.set_margin_bottom(4)
        
        self.proc_dots = []
        for i in range(3):
            d = Gtk.Box()
            d.add_css_class("dot-processing")
            d.set_size_request(3, 3)
            d.set_halign(Gtk.Align.CENTER)
            d.set_valign(Gtk.Align.CENTER)
            self.proc_dots.append(d)
            self.proc_dots_box.append(d)
        
        self.box.append(self.icon)
        self.box.append(self.dots_box)
        self.box.append(self.label)
        self.box.append(self.proc_dots_box)
        self.window.set_child(self.box)
        
        # Styling
        css_provider = Gtk.CssProvider()
        css = b"""
        window {
            background-color: rgba(20, 20, 20, 0.9);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        label {
            font-family: 'Inter', sans-serif;
            font-weight: bold;
            font-size: 13px;
            color: white;
        }
        .dot-indicator {
            background-color: #ff4444;
            border-radius: 50%;
            opacity: 0.2;
            min-width: 4px;
            min-height: 4px;
            transition: all 0.1s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        }
        .dot-active {
            opacity: 1.0;
        }
        .dot-half {
            opacity: 0.5;
        }
        .dot-processing {
            background-color: white;
            border-radius: 50%;
            opacity: 0.2;
            min-width: 3px;
            min-height: 3px;
            transition: opacity 0.2s ease-in-out;
        }
        .dot-proc-active {
            opacity: 1.0;
        }
        """
        css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.window.set_visible(False) # Start hidden
        self.logger.info("UI: Activated and ready")
        
        self.proc_timer = None
        self.proc_step = 0

    def update_state(self, state: str):
        if not self.app or not self.window:
            return

        def _update():
            self.logger.info(f"UI: State -> {state}")
            
            # Stop processing animation if running
            if self.proc_timer:
                GLib.source_remove(self.proc_timer)
                self.proc_timer = None
            
            if state == "IDLE":
                self.window.set_visible(False)
            elif state == "RECORDING":
                self.label.set_text("Listening")
                self.icon.set_from_icon_name("audio-input-microphone-symbolic")
                
                # Show and reset dots
                self.dots_box.set_visible(True)
                for d in self.dots:
                    d.remove_css_class("dot-active")
                    d.remove_css_class("dot-half")
                # Default state: Bottom dot is "half"
                self.dots[0].add_css_class("dot-half")
                
                # Hide processing dots
                self.proc_dots_box.set_visible(False)
                
                self.window.set_visible(True)
                self.window.present()
            elif state == "PROCESSING":
                self.label.set_text("Processing") # Removed "..." from text
                self.icon.set_from_icon_name("system-run-symbolic")
                
                # Hide recording dots
                self.dots_box.set_visible(False)
                
                # Show and animate processing dots
                self.proc_dots_box.set_visible(True)
                self.proc_step = 0
                self._animate_processing()
                self.proc_timer = GLib.timeout_add(300, self._animate_processing)
                
                self.window.set_visible(True)
                self.window.present()
            elif state == "ERROR_API":
                self.label.set_text("No API Key")
                self.icon.set_from_icon_name("dialog-error-symbolic")
                self.dots_box.set_visible(False)
                self.proc_dots_box.set_visible(False)
                self.window.set_visible(True)
                self.window.present()
            elif state == "ERROR_CLIPBOARD":
                self.label.set_text("Clipboard Error")
                self.icon.set_from_icon_name("edit-copy-symbolic") # Or error icon
                self.dots_box.set_visible(False)
                self.proc_dots_box.set_visible(False)
                self.window.set_visible(True)
                self.window.present()
            elif state == "ERROR_PASTE":
                self.label.set_text("Paste Failed")
                self.icon.set_from_icon_name("edit-paste-symbolic")
                self.dots_box.set_visible(False)
                self.proc_dots_box.set_visible(False)
                self.window.set_visible(True)
                self.window.present()
            elif state == "ERROR_NO_AUDIO":
                self.label.set_text("No Audio")
                self.icon.set_from_icon_name("microphone-sensitivity-muted-symbolic")
                self.dots_box.set_visible(False)
                self.proc_dots_box.set_visible(False)
                self.window.set_visible(True)
                self.window.present()
            elif state == "ERROR_TRANSCRIPTION":
                self.label.set_text("Transcription Failed")
                self.icon.set_from_icon_name("network-error-symbolic")
                self.dots_box.set_visible(False)
                self.proc_dots_box.set_visible(False)
                self.window.set_visible(True)
                self.window.present()
            return False

        GLib.idle_add(_update)

    def _animate_processing(self):
        # Cycle: 0 -> 1 -> 2 -> 3 (all off) -> 0...
        # Step 0: * . .
        # Step 1: * * .
        # Step 2: * * *
        # Step 3: . . .
        
        step = self.proc_step % 4
        
        for i, d in enumerate(self.proc_dots):
            if step == 3:
                d.remove_css_class("dot-proc-active")
            elif i <= step:
                d.add_css_class("dot-proc-active")
            else:
                d.remove_css_class("dot-proc-active")
        
        self.proc_step += 1
        return True # Keep running

    def show_warning(self, text: str):
        if not self.app or not self.window:
            return

        def _show():
            self.logger.info(f"UI: Warning -> {text}")
            self.label.set_text(text)
            self.icon.set_from_icon_name("dialog-warning-symbolic")
            
            # Hide dots, show window
            self.dots_box.set_visible(False)
            self.proc_dots_box.set_visible(False)
            self.window.set_visible(True)
            self.window.present()
            return False

        GLib.idle_add(_show)

    def update_amplitude(self, level: float):
        if not self.app or not self.window or not self.window.get_visible():
            return

        def _update():
            # Initialize smoothed level if needed
            if not hasattr(self, "smoothed_level"):
                self.smoothed_level = 0.0
            
            # Smoothing: Fast attack, slow decay
            if level > self.smoothed_level:
                self.smoothed_level = level
            else:
                self.smoothed_level = self.smoothed_level * 0.85 + level * 0.15
            
            val = self.smoothed_level
            
            # Map value to 3 dots
            # Dot 0 (Bottom) always at least half
            # Thresholds (very sensitive)
            
            # Reset classes first
            for d in self.dots:
                d.remove_css_class("dot-active")
                d.remove_css_class("dot-half")
            
            # Dot 0 (Bottom)
            if val > 0.001:
                self.dots[0].add_css_class("dot-active")
            else:
                self.dots[0].add_css_class("dot-half") # Default "half dot"
                
            # Dot 1 (Middle)
            if val > 0.01:
                self.dots[1].add_css_class("dot-active")
            elif val > 0.005:
                self.dots[1].add_css_class("dot-half")
                
            # Dot 2 (Top)
            if val > 0.04:
                self.dots[2].add_css_class("dot-active")
            elif val > 0.02:
                self.dots[2].add_css_class("dot-half")

            return False
            
        GLib.idle_add(_update)

    def run(self):
        if self.app:
            self.app.run(None)
        else:
            threading.Event().wait()

    def quit(self):
        if self.app:
            self.app.quit()
