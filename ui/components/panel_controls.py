"""
Panel Control Components
Provides fullscreen, expand, and toggle functionality for UI panels
"""

import customtkinter as ctk
from config.settings import COLORS, FONTS, SPACING


class PanelHeader(ctk.CTkFrame):
    """
    A reusable panel header with title and control buttons.
    Features:
    - Title with optional icon
    - Fullscreen button (opens content in large popup window)
    - Toggle/close button to hide the panel
    """
    
    def __init__(
        self, 
        parent, 
        title: str = "Panel",
        icon: str = "📊",
        on_fullscreen = None,
        on_toggle = None,
        show_fullscreen: bool = True,
        show_toggle: bool = True,
        fg_color = None,
        **kwargs
    ):
        super().__init__(parent, fg_color=fg_color or COLORS["primary"], corner_radius=8, **kwargs)
        
        self.on_fullscreen = on_fullscreen
        self.on_toggle = on_toggle
        
        # Inner container with padding
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Title section
        title_frame = ctk.CTkFrame(inner, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        if icon:
            ctk.CTkLabel(
                title_frame,
                text=icon,
                font=ctk.CTkFont(size=16),
                text_color="#FFFFFF"
            ).pack(side="left", padx=(0, 8))
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        # Buttons container
        btn_container = ctk.CTkFrame(inner, fg_color="transparent")
        btn_container.pack(side="right")
        
        # Fullscreen button
        if show_fullscreen:
            self.fullscreen_btn = ctk.CTkButton(
                btn_container,
                text="⛶",
                width=32,
                height=28,
                font=ctk.CTkFont(size=14),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                corner_radius=6,
                command=self._on_fullscreen_click
            )
            self.fullscreen_btn.pack(side="left", padx=(0, 5))
        
        # Toggle/close button
        if show_toggle:
            self.toggle_btn = ctk.CTkButton(
                btn_container,
                text="✕",
                width=32,
                height=28,
                font=ctk.CTkFont(size=12),
                fg_color=COLORS["text_secondary"],
                hover_color="#475569",
                corner_radius=6,
                command=self._on_toggle_click
            )
            self.toggle_btn.pack(side="left")
    
    def _on_fullscreen_click(self):
        if self.on_fullscreen:
            self.on_fullscreen()
    
    def _on_toggle_click(self):
        if self.on_toggle:
            self.on_toggle()


class FullscreenWindow(ctk.CTkToplevel):
    """
    A fullscreen-like popup window for viewing content in a larger space.
    Can be dragged and resized. Closes and returns content to original panel.
    """
    
    def __init__(self, parent, title: str = "Fullscreen View", width: int = 1000, height: int = 700):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.minsize(600, 400)
        
        # Center on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Stay on top briefly
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        
        # Content frame
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["surface"],
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        self.content_frame.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Header
        self.header = ctk.CTkFrame(self.content_frame, fg_color=COLORS["primary"], corner_radius=8)
        self.header.pack(fill="x", padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["md"]))
        
        header_inner = ctk.CTkFrame(self.header, fg_color="transparent")
        header_inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            header_inner,
            text=f"⛶ {title}",
            font=ctk.CTkFont(family=FONTS["family"], size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        # Dock/close button
        ctk.CTkButton(
            header_inner,
            text="✕ Close",
            width=100,
            height=32,
            font=ctk.CTkFont(family=FONTS["family"], size=12, weight="bold"),
            fg_color=COLORS["error"],
            hover_color=COLORS["error_light"],
            corner_radius=6,
            command=self.destroy
        ).pack(side="right")
        
        # Body frame for content
        self.body_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])


class PanelToggleBar(ctk.CTkFrame):
    """
    A toolbar with toggle buttons to show/hide different panels.
    Used at the top of views to control panel visibility.
    """
    
    def __init__(self, parent, panels: dict = None, **kwargs):
        """
        panels: dict of {panel_name: {"label": str, "icon": str, "visible": bool}}
        """
        super().__init__(parent, fg_color=COLORS["surface"], corner_radius=8, height=40, **kwargs)
        
        self.panels = panels or {}
        self.toggle_buttons = {}
        self.callbacks = {}
        
        # Inner container
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])
        
        # Label
        ctk.CTkLabel(
            inner,
            text="👁️ Panels:",
            font=ctk.CTkFont(family=FONTS["family"], size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(5, 10))
        
        # Create toggle buttons for each panel
        for name, config in self.panels.items():
            self._create_toggle_button(inner, name, config)
    
    def _create_toggle_button(self, parent, name: str, config: dict):
        icon = config.get("icon", "📋")
        label = config.get("label", name)
        visible = config.get("visible", True)
        
        btn = ctk.CTkButton(
            parent,
            text=f"{icon} {label}",
            width=120,
            height=28,
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            fg_color=COLORS["secondary"] if visible else COLORS["border"],
            hover_color=COLORS["secondary_light"],
            corner_radius=6,
            command=lambda n=name: self._toggle_panel(n)
        )
        btn.pack(side="left", padx=3)
        self.toggle_buttons[name] = btn
    
    def _toggle_panel(self, name: str):
        if name in self.panels:
            self.panels[name]["visible"] = not self.panels[name]["visible"]
            visible = self.panels[name]["visible"]
            
            # Update button appearance
            btn = self.toggle_buttons[name]
            btn.configure(
                fg_color=COLORS["secondary"] if visible else COLORS["border"]
            )
            
            # Call registered callback
            if name in self.callbacks:
                self.callbacks[name](visible)
    
    def register_callback(self, panel_name: str, callback):
        """Register a callback for panel visibility changes"""
        self.callbacks[panel_name] = callback
    
    def set_visible(self, panel_name: str, visible: bool):
        """Programmatically set panel visibility"""
        if panel_name in self.panels:
            self.panels[panel_name]["visible"] = visible
            btn = self.toggle_buttons[panel_name]
            btn.configure(
                fg_color=COLORS["secondary"] if visible else COLORS["border"]
            )
    
    def is_visible(self, panel_name: str) -> bool:
        return self.panels.get(panel_name, {}).get("visible", True)


class ExpandablePanel(ctk.CTkFrame):
    """
    A panel wrapper that provides show/hide and fullscreen functionality.
    Wraps any content and adds control buttons.
    """
    
    def __init__(
        self,
        parent,
        title: str = "Panel",
        icon: str = "📊",
        initial_visible: bool = True,
        show_fullscreen: bool = True,
        panel_width: int = 500,
        fg_color = None,
        **kwargs
    ):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.title = title
        self.icon = icon
        self.panel_visible = initial_visible
        self.panel_width = panel_width
        self.fullscreen_window = None
        self.show_btn = None
        self.show_btn_parent = None
        
        # Main container
        self.container = ctk.CTkFrame(
            self,
            fg_color=fg_color or COLORS["surface"],
            corner_radius=12
        )
        if initial_visible:
            self.container.pack(fill="both", expand=True)
        
        # Header
        self.header = PanelHeader(
            self.container,
            title=title,
            icon=icon,
            on_fullscreen=self._open_fullscreen if show_fullscreen else None,
            on_toggle=self._toggle_visibility,
            show_fullscreen=show_fullscreen,
            show_toggle=True
        )
        self.header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))
        
        # Content frame (where child widgets go)
        self.content = ctk.CTkFrame(self.container, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=SPACING["md"], pady=(0, SPACING["md"]))
        
        # Callback for when visibility changes
        self.on_visibility_change = None
    
    def get_content_frame(self):
        """Returns the frame where content should be added"""
        return self.content
    
    def _toggle_visibility(self):
        """Toggle panel visibility"""
        if self.panel_visible:
            self.hide()
        else:
            self.show()
    
    def hide(self):
        """Hide the panel"""
        if self.panel_visible:
            self.container.pack_forget()
            self.panel_visible = False
            
            if self.on_visibility_change:
                self.on_visibility_change(False)
    
    def show(self):
        """Show the panel"""
        if not self.panel_visible:
            self.container.pack(fill="both", expand=True)
            self.panel_visible = True
            
            # Destroy show button if it exists
            if self.show_btn:
                self.show_btn.destroy()
                self.show_btn = None
            
            if self.on_visibility_change:
                self.on_visibility_change(True)
    
    def create_show_button(self, parent):
        """Create a button to show this panel (used when panel is hidden)"""
        self.show_btn_parent = parent
        self.show_btn = ctk.CTkButton(
            parent,
            text=f"{self.icon} Show {self.title}",
            width=180,
            height=36,
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            corner_radius=8,
            command=self.show
        )
        self.show_btn.pack(pady=SPACING["md"])
        return self.show_btn
    
    def _open_fullscreen(self):
        """Open panel content in fullscreen window"""
        if self.fullscreen_window is not None:
            # Bring existing window to focus
            self.fullscreen_window.lift()
            self.fullscreen_window.focus()
            return
        
        self.fullscreen_window = FullscreenWindow(
            self.winfo_toplevel(),
            title=self.title,
            width=1100,
            height=750
        )
        
        # Handle close
        self.fullscreen_window.protocol("WM_DELETE_WINDOW", self._close_fullscreen)
        
        # The body_frame in FullscreenWindow is where cloned content goes
        # We'll emit a callback so the parent can populate it
        if hasattr(self, 'on_fullscreen_open'):
            self.on_fullscreen_open(self.fullscreen_window.body_frame)
    
    def _close_fullscreen(self):
        """Close fullscreen window"""
        if self.fullscreen_window:
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
            
            if hasattr(self, 'on_fullscreen_close'):
                self.on_fullscreen_close()
    
    def is_visible(self) -> bool:
        return self.panel_visible
