"""
Simplex (Linear Programming) View
UI for inputting and solving LP problems with sensitivity analysis
"""

import customtkinter as ctk
import numpy as np
from tkinter import messagebox
from typing import Optional, List

from ui.components.matrix_input import MatrixInput, VectorInput
from ui.components.result_display import ResultDisplay
from ui.components.sensitivity_table import SensitivityTable
from ui.components.what_if_panel import WhatIfPanel
from ui.components.panel_controls import PanelHeader, PanelToggleBar, FullscreenWindow
from algorithms.simplex import SimplexSolver, create_sample_problem
from config.settings import PRODUCTS, RESOURCES, DEFAULT_LP_VARIABLES, DEFAULT_LP_CONSTRAINTS, COLORS, SPACING, FONTS


class SimplexView(ctk.CTkFrame):
    """
    View for Linear Programming (Simplex) problems
    
    Features:
    - Objective function input
    - Constraint matrix input
    - Maximize/Minimize toggle
    - Solve with sensitivity analysis
    - Load sample problem
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.num_variables = DEFAULT_LP_VARIABLES
        self.num_constraints = DEFAULT_LP_CONSTRAINTS
        
        self._create_layout()
        self._create_widgets()
        self._setup_smooth_scroll()
    
    def _create_layout(self):
        """Create the main layout structure with expandable panels and toggle controls"""
        # Top toolbar for panel controls
        self.toolbar = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=45)
        self.toolbar.pack(fill="x", padx=0, pady=0)
        self.toolbar.pack_propagate(False)
        
        # Panel toggle bar
        self.panel_toggles = PanelToggleBar(
            self.toolbar,
            panels={
                "inputs": {"label": "Inputs", "icon": "📝", "visible": True},
                "results": {"label": "Results", "icon": "📊", "visible": True},
                "whatif": {"label": "What-If", "icon": "🔮", "visible": True}
            }
        )
        self.panel_toggles.pack(side="left", padx=SPACING["md"], pady=SPACING["xs"])
        
        # Register toggle callbacks (will be set after panels are created)
        self.panel_toggles.register_callback("inputs", self._toggle_inputs_panel)
        self.panel_toggles.register_callback("results", self._toggle_results_panel)
        self.panel_toggles.register_callback("whatif", self._toggle_whatif_panel)
        
        # Container for all panels with padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Track panel states
        self.inputs_panel_visible = True
        self.results_panel_visible = True
        self.right_panel_visible = True
        self.right_panel_expanded = False
        self.right_panel_popped = False
        self.right_panel_width = 350  # Default width
        self.right_panel_min_width = 350
        self.right_panel_max_width = 800
        
        # Left panel container (inputs)
        self.left_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_container.pack(side="left", fill="both", expand=True, padx=(0, SPACING["md"]), pady=0)
        
        # Left panel header with fullscreen button
        self.left_header = PanelHeader(
            self.left_container,
            title="Problem Inputs",
            icon="📝",
            on_fullscreen=self._fullscreen_inputs,
            on_toggle=lambda: self._toggle_inputs_panel(False)
        )
        self.left_header.pack(fill="x", padx=0, pady=(0, SPACING["sm"]))
        
        # Left panel (inputs) - scrollable with smooth scrolling
        self.left_panel = ctk.CTkScrollableFrame(
            self.left_container, 
            width=550,
            fg_color=COLORS["surface"],
            corner_radius=12,
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        self.left_panel.pack(fill="both", expand=True, pady=0)
        
        # Middle panel container (results)
        self.middle_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.middle_container.pack(side="left", fill="both", expand=True, padx=SPACING["sm"], pady=0)
        
        # Middle panel header with fullscreen button
        self.middle_header = PanelHeader(
            self.middle_container,
            title="Results & Analysis",
            icon="📊",
            on_fullscreen=self._fullscreen_results,
            on_toggle=lambda: self._toggle_results_panel(False)
        )
        self.middle_header.pack(fill="x", padx=0, pady=(0, SPACING["sm"]))
        
        # Middle panel (results) - scrollable
        self.middle_panel = ctk.CTkScrollableFrame(
            self.middle_container, 
            width=480,
            fg_color=COLORS["surface"],
            corner_radius=12,
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        self.middle_panel.pack(fill="both", expand=True, pady=0)
        
        # Right panel container - for resize handle
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_container.pack(side="right", fill="both", expand=False, padx=(SPACING["sm"], 0), pady=0)
        
        # Right panel (What-If Analysis) - resizable
        self.right_panel = ctk.CTkScrollableFrame(
            self.right_container, 
            width=self.right_panel_width,
            fg_color=COLORS["surface"],
            corner_radius=12,
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        self.right_panel.pack(side="right", fill="both", expand=True)
        
        # Store last solution for what-if analysis
        self.last_result = None
        self.last_solver = None
        
        # Popup window references
        self.popup_window = None
        self.inputs_popup = None
        self.results_popup = None
    
    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_header()
        self._create_problem_settings()
        self._create_objective_input()
        self._create_constraints_input()
        self._create_action_buttons()
        self._create_results_panel()
        self._create_whatif_panel()
    
    def _setup_smooth_scroll(self):
        """Setup smooth scrolling for all scrollable panels"""
        # Scroll speed multiplier (higher = faster, lower = smoother)
        self.scroll_speed = 2
        
        # Bind mousewheel to all scrollable frames
        for panel in [self.left_panel, self.middle_panel, self.right_panel]:
            self._bind_smooth_scroll(panel)
    
    def _bind_smooth_scroll(self, scrollable_frame):
        """Bind smooth scroll events to a scrollable frame"""
        # Get the internal canvas of CTkScrollableFrame
        try:
            canvas = scrollable_frame._parent_canvas
            
            def smooth_scroll(event):
                # Windows uses event.delta, Linux/Mac uses event.num
                if event.delta:
                    # Windows - delta is typically 120 per notch
                    scroll_amount = -1 * (event.delta // 60) * self.scroll_speed
                else:
                    # Linux - button 4 is scroll up, button 5 is scroll down
                    scroll_amount = -4 if event.num == 4 else 4
                
                canvas.yview_scroll(scroll_amount, "units")
                return "break"
            
            # Bind to the scrollable frame and all its children
            scrollable_frame.bind("<MouseWheel>", smooth_scroll, add="+")
            scrollable_frame.bind("<Button-4>", smooth_scroll, add="+")
            scrollable_frame.bind("<Button-5>", smooth_scroll, add="+")
            
            # Also bind to canvas
            canvas.bind("<MouseWheel>", smooth_scroll, add="+")
            canvas.bind("<Button-4>", smooth_scroll, add="+")
            canvas.bind("<Button-5>", smooth_scroll, add="+")
            
            # Bind to all children recursively
            def bind_children(widget):
                widget.bind("<MouseWheel>", smooth_scroll, add="+")
                widget.bind("<Button-4>", smooth_scroll, add="+")
                widget.bind("<Button-5>", smooth_scroll, add="+")
                for child in widget.winfo_children():
                    bind_children(child)
            
            bind_children(scrollable_frame)
            
        except Exception:
            pass  # Silently fail if canvas not accessible
    
    def _create_header(self):
        """Create the header section with modern styling"""
        header_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["primary"],
            corner_radius=10
        )
        header_frame.pack(fill="x", padx=SPACING["xs"], pady=(SPACING["xs"], SPACING["sm"]))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Icon and title
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="📊",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")
        
        ctk.CTkLabel(
            text_frame,
            text="Linear Programming",
            font=ctk.CTkFont(family=FONTS["family"], size=22, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_frame,
            text="Simplex Method Solver",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        
        # Load sample button
        ctk.CTkButton(
            header_content,
            text="📥 Load TBLP Example",
            command=self._load_sample,
            width=180,
            height=38,
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=8
        ).pack(side="right")
    
    def _create_problem_settings(self):
        """Create problem settings section with card styling"""
        # Settings card container - compact
        settings_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        settings_card.pack(fill="x", padx=SPACING["xs"], pady=(0, SPACING["sm"]))
        
        # Card header - compact
        card_header = ctk.CTkFrame(settings_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))
        
        ctk.CTkLabel(
            card_header,
            text="⚙️  Problem Configuration",
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Divider
        ctk.CTkFrame(settings_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["md"], pady=SPACING["xs"]
        )
        
        # Size settings row - compact
        size_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        size_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])
        
        ctk.CTkLabel(
            size_frame, 
            text="Variables:",
            font=ctk.CTkFont(family=FONTS["family"], size=12)
        ).pack(side="left", padx=(0, SPACING["xs"]))
        
        self.var_spinbox = ctk.CTkEntry(
            size_frame, 
            width=60, 
            justify="center",
            height=28,
            corner_radius=4
        )
        self.var_spinbox.insert(0, str(self.num_variables))
        self.var_spinbox.pack(side="left", padx=(0, SPACING["md"]))
        
        ctk.CTkLabel(
            size_frame, 
            text="Constraints:",
            font=ctk.CTkFont(family=FONTS["family"], size=12)
        ).pack(side="left", padx=(0, SPACING["xs"]))
        
        self.const_spinbox = ctk.CTkEntry(
            size_frame, 
            width=60, 
            justify="center",
            height=28,
            corner_radius=4
        )
        self.const_spinbox.insert(0, str(self.num_constraints))
        self.const_spinbox.pack(side="left", padx=(0, SPACING["md"]))
        
        ctk.CTkButton(
            size_frame,
            text="Resize",
            command=self._resize_problem,
            width=70,
            height=28,
            corner_radius=4,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_light"]
        ).pack(side="left")
        
        # Objective type row - compact
        obj_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        obj_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["sm"]))
        
        ctk.CTkLabel(
            obj_frame, 
            text="Objective:",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        self.objective_var = ctk.StringVar(value="maximize")
        ctk.CTkRadioButton(
            obj_frame,
            text="Maximize Profit",
            variable=self.objective_var,
            value="maximize",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["lg"]))
        
        ctk.CTkRadioButton(
            obj_frame,
            text="Minimize Cost",
            variable=self.objective_var,
            value="minimize",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left")
    
    def _create_objective_input(self):
        """Create objective function input section with card styling"""
        # Objective card - compact
        obj_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        obj_card.pack(fill="x", padx=SPACING["xs"], pady=(0, SPACING["sm"]))
        
        # Card header - compact
        card_header = ctk.CTkFrame(obj_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))
        
        ctk.CTkLabel(
            card_header,
            text="💰  Objective Function",
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            card_header,
            text="Profit/Cost per unit",
            font=ctk.CTkFont(family=FONTS["family"], size=10),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(obj_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["md"], pady=SPACING["xs"]
        )
        
        # Input area - compact
        input_frame = ctk.CTkFrame(obj_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["sm"]))
        
        self.objective_input = VectorInput(
            input_frame,
            size=self.num_variables,
            labels=PRODUCTS[:self.num_variables],
            orientation="horizontal",
            default_value="0",
            cell_width=90
        )
        self.objective_input.pack(fill="x")
    
    def _create_constraints_input(self):
        """Create constraints matrix input section with card styling"""
        # Constraints card - compact
        const_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        const_card.pack(fill="x", padx=SPACING["xs"], pady=(0, SPACING["sm"]))
        
        # Card header - compact
        card_header = ctk.CTkFrame(const_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))
        
        ctk.CTkLabel(
            card_header,
            text="📝  Constraint Coefficients",
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            card_header,
            text="Resources per unit",
            font=ctk.CTkFont(family=FONTS["family"], size=10),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(const_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["md"], pady=SPACING["xs"]
        )
        
        # Matrix input area - compact
        matrix_frame = ctk.CTkFrame(const_card, fg_color="transparent")
        matrix_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["xs"])
        
        self.constraint_matrix = MatrixInput(
            matrix_frame,
            rows=self.num_constraints,
            cols=self.num_variables,
            row_headers=RESOURCES[:self.num_constraints],
            col_headers=[p[:12] for p in PRODUCTS[:self.num_variables]],
            default_value="0",
            cell_width=70
        )
        self.constraint_matrix.pack(fill="x")
        
        # RHS Section - compact
        rhs_header = ctk.CTkFrame(const_card, fg_color="transparent")
        rhs_header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["xs"], SPACING["xs"]))
        
        ctk.CTkLabel(
            rhs_header,
            text="📋  Right-Hand Side (RHS)",
            font=ctk.CTkFont(family=FONTS["family"], size=12, weight="bold"),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        # RHS input area - compact
        rhs_input_frame = ctk.CTkFrame(const_card, fg_color="transparent")
        rhs_input_frame.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))
        
        self.rhs_input = VectorInput(
            rhs_input_frame,
            size=self.num_constraints,
            labels=RESOURCES[:self.num_constraints],
            orientation="vertical",
            default_value="0",
            cell_width=100
        )
        self.rhs_input.pack(fill="x")
    
    def _create_action_buttons(self):
        """Create action buttons with modern styling"""
        # Action buttons card
        btn_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        btn_card.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["lg"]))
        
        btn_frame = ctk.CTkFrame(btn_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=SPACING["card_padding"], pady=SPACING["card_padding"])
        
        ctk.CTkButton(
            btn_frame,
            text="🔍 Solve Problem",
            command=self._solve,
            width=160,
            height=44,
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            corner_radius=8
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Clear All",
            command=self._clear,
            width=130,
            height=44,
            font=ctk.CTkFont(family=FONTS["family"], size=13),
            fg_color=COLORS["error"],
            hover_color=COLORS["error_light"],
            corner_radius=8
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        ctk.CTkButton(
            btn_frame,
            text="📋 Export Results",
            command=self._export,
            width=140,
            height=44,
            font=ctk.CTkFont(family=FONTS["family"], size=13),
            fg_color=COLORS["success"],
            hover_color=COLORS["success_light"],
            corner_radius=8
        ).pack(side="left")
    
    def _create_results_panel(self):
        """Create the results display panel with improved spacing"""
        # Panel header
        header_frame = ctk.CTkFrame(self.middle_panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            header_frame,
            text="📊  Results",
            font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Result display
        self.result_display = ResultDisplay(
            self.middle_panel,
            title="Solution Results"
        )
        self.result_display.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        # Sensitivity analysis table
        self.sensitivity_table = SensitivityTable(
            self.middle_panel,
            title="Sensitivity Analysis"
        )
        self.sensitivity_table.pack(fill="both", expand=True, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]))
    
    def _create_whatif_panel(self):
        """Create the What-If analysis panel with expand/pop-out controls"""
        # Control bar at top
        control_frame = ctk.CTkFrame(self.right_panel, fg_color=COLORS["primary"], corner_radius=8)
        control_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))
        
        control_inner = ctk.CTkFrame(control_frame, fg_color="transparent")
        control_inner.pack(fill="x", padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Panel title
        ctk.CTkLabel(
            control_inner,
            text="📊 What-If Analysis",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        # Button container on right
        btn_container = ctk.CTkFrame(control_inner, fg_color="transparent")
        btn_container.pack(side="right")
        
        # Expand button (makes panel wider)
        self.expand_btn = ctk.CTkButton(
            btn_container,
            text="⇔",
            width=32,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_light"],
            corner_radius=6,
            command=self._toggle_expand_panel
        )
        self.expand_btn.pack(side="left", padx=(0, 5))
        
        # Pop-out button (opens in separate window)
        self.popout_btn = ctk.CTkButton(
            btn_container,
            text="⧉",
            width=32,
            height=28,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=6,
            command=self._popout_panel
        )
        self.popout_btn.pack(side="left", padx=(0, 5))
        
        # Hide button
        self.toggle_btn = ctk.CTkButton(
            btn_container,
            text="✕",
            width=32,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS["text_secondary"],
            hover_color="#475569",
            corner_radius=6,
            command=self._toggle_whatif_panel
        )
        self.toggle_btn.pack(side="left")
        
        # What-If Panel content
        self.whatif_panel = WhatIfPanel(
            self.right_panel,
            on_resolve=self._resolve_whatif,
            on_variable_change=self._on_variable_change,
            on_constraint_change=self._on_constraint_change
        )
        self.whatif_panel.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
    
    def _toggle_expand_panel(self):
        """Toggle panel between compact and expanded width"""
        if self.right_panel_expanded:
            # Shrink back to default
            self.right_panel_width = self.right_panel_min_width
            self.right_panel.configure(width=self.right_panel_width)
            self.expand_btn.configure(text="⇔")
            self.right_panel_expanded = False
        else:
            # Expand to max width
            self.right_panel_width = self.right_panel_max_width
            self.right_panel.configure(width=self.right_panel_width)
            self.expand_btn.configure(text="⇐")
            self.right_panel_expanded = True
    
    def _popout_panel(self):
        """Pop out the What-If panel into a separate draggable window"""
        if self.right_panel_popped and self.popup_window:
            # Bring existing window to front
            self.popup_window.lift()
            self.popup_window.focus()
            return
        
        # Hide the embedded panel
        self.right_container.pack_forget()
        self.right_panel_visible = False
        
        # Create popup window
        self.popup_window = ctk.CTkToplevel(self)
        self.popup_window.title("What-If Analysis - Linear Programming")
        self.popup_window.geometry("600x700")
        self.popup_window.minsize(400, 500)
        
        # Make it stay on top initially
        self.popup_window.attributes('-topmost', True)
        self.popup_window.after(100, lambda: self.popup_window.attributes('-topmost', False))
        
        # Handle close
        self.popup_window.protocol("WM_DELETE_WINDOW", self._close_popup)
        
        # Create content in popup
        popup_frame = ctk.CTkScrollableFrame(
            self.popup_window,
            fg_color=COLORS["surface"],
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        popup_frame.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Header in popup
        header = ctk.CTkFrame(popup_frame, fg_color=COLORS["primary"], corner_radius=8)
        header.pack(fill="x", padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["md"]))
        
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            header_inner,
            text="📊 What-If Analysis",
            font=ctk.CTkFont(family=FONTS["family"], size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        # Dock button to put it back
        ctk.CTkButton(
            header_inner,
            text="📌 Dock Panel",
            width=120,
            height=32,
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            corner_radius=6,
            command=self._close_popup
        ).pack(side="right")
        
        # Move whatif_panel to popup
        self.whatif_panel.pack_forget()
        self.whatif_panel = WhatIfPanel(
            popup_frame,
            on_resolve=self._resolve_whatif,
            on_variable_change=self._on_variable_change,
            on_constraint_change=self._on_constraint_change
        )
        self.whatif_panel.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Reload current problem data if available
        if self.last_result and self.last_solver:
            self._reload_whatif_data()
        
        self.right_panel_popped = True
        
        # Add show button to results panel
        self.show_panel_btn = ctk.CTkButton(
            self.middle_panel,
            text="📊 Open What-If Panel",
            width=180,
            height=36,
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            corner_radius=8,
            command=self._focus_popup
        )
        self.show_panel_btn.pack(pady=SPACING["md"])
    
    def _focus_popup(self):
        """Bring popup window to focus"""
        if self.popup_window:
            self.popup_window.lift()
            self.popup_window.focus()
    
    def _close_popup(self):
        """Close popup and restore embedded panel"""
        if self.popup_window:
            self.popup_window.destroy()
            self.popup_window = None
        
        self.right_panel_popped = False
        
        # Remove show button
        if hasattr(self, 'show_panel_btn'):
            self.show_panel_btn.destroy()
        
        # Restore embedded panel
        self.right_container.pack(side="right", fill="both", expand=False, padx=(SPACING["sm"], 0), pady=0)
        self.right_panel_visible = True
        
        # Recreate whatif panel in embedded location
        self.whatif_panel = WhatIfPanel(
            self.right_panel,
            on_resolve=self._resolve_whatif,
            on_variable_change=self._on_variable_change,
            on_constraint_change=self._on_constraint_change
        )
        self.whatif_panel.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        # Reload data
        if self.last_result and self.last_solver:
            self._reload_whatif_data()
    
    def _reload_whatif_data(self):
        """Reload problem data into What-If panel"""
        try:
            if hasattr(self, 'last_solver') and self.last_solver:
                var_names = [PRODUCTS[i] if i < len(PRODUCTS) else f"x{i+1}" 
                            for i in range(self.num_variables)]
                const_names = [RESOURCES[i] if i < len(RESOURCES) else f"Constraint {i+1}"
                              for i in range(self.num_constraints)]
                
                c = self.objective_input.get_values()
                A_ub = self.constraint_matrix.get_matrix()
                b_ub = self.rhs_input.get_values()
                
                result_dict = {
                    'success': self.last_result.success,
                    'optimal_value': self.last_result.optimal_value,
                    'solution': self.last_result.solution,
                }
                
                self.whatif_panel.load_problem(
                    num_variables=self.num_variables,
                    num_constraints=self.num_constraints,
                    variable_names=var_names,
                    constraint_names=const_names,
                    objective_coeffs=c,
                    constraint_matrix=A_ub,
                    rhs_values=b_ub,
                    solution=result_dict
                )
        except Exception:
            pass
    
    def _toggle_inputs_panel(self, visible=None):
        """Toggle the visibility of the Inputs panel"""
        if visible is None:
            visible = not self.inputs_panel_visible
        
        if visible:
            if not self.inputs_panel_visible:
                self.left_container.pack(side="left", fill="both", expand=True, padx=(0, SPACING["md"]), pady=0, before=self.middle_container)
                self.inputs_panel_visible = True
        else:
            if self.inputs_panel_visible:
                self.left_container.pack_forget()
                self.inputs_panel_visible = False
        
        self.panel_toggles.set_visible("inputs", visible)
    
    def _toggle_results_panel(self, visible=None):
        """Toggle the visibility of the Results panel"""
        if visible is None:
            visible = not self.results_panel_visible
        
        if visible:
            if not self.results_panel_visible:
                self.middle_container.pack(side="left", fill="both", expand=True, padx=SPACING["sm"], pady=0, before=self.right_container)
                self.results_panel_visible = True
        else:
            if self.results_panel_visible:
                self.middle_container.pack_forget()
                self.results_panel_visible = False
        
        self.panel_toggles.set_visible("results", visible)
    
    def _fullscreen_inputs(self):
        """Open inputs panel in fullscreen window"""
        if self.inputs_popup:
            self.inputs_popup.lift()
            self.inputs_popup.focus()
            return
        
        self.inputs_popup = FullscreenWindow(
            self.winfo_toplevel(),
            title="Problem Inputs - Fullscreen",
            width=1100,
            height=800
        )
        self.inputs_popup.protocol("WM_DELETE_WINDOW", self._close_inputs_popup)
        
        # Create cloned input content in popup
        body = self.inputs_popup.body_frame
        
        # Info label
        ctk.CTkLabel(
            body,
            text="💡 This is a read-only fullscreen view. Edit inputs in the main window.",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=SPACING["md"])
        
        # Display current values
        self._display_inputs_summary(body)
    
    def _display_inputs_summary(self, parent):
        """Display a summary of current input values"""
        # Objective function card
        obj_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
        obj_card.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            obj_card,
            text="💰 Objective Function Coefficients",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
        
        try:
            obj_values = self.objective_input.get_values()
            obj_text = ", ".join([f"{PRODUCTS[i] if i < len(PRODUCTS) else f'x{i+1}'}: {v:,.2f}" 
                                  for i, v in enumerate(obj_values)])
            ctk.CTkLabel(
                obj_card,
                text=obj_text,
                font=ctk.CTkFont(family=FONTS["family"], size=12),
                text_color=COLORS["text_secondary"],
                wraplength=1000
            ).pack(anchor="w", padx=SPACING["md"], pady=(0, SPACING["md"]))
        except:
            pass
        
        # Constraints summary
        const_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
        const_card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            const_card,
            text="📝 Constraint Matrix Summary",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
        
        try:
            matrix = self.constraint_matrix.get_matrix()
            rhs = self.rhs_input.get_values()
            
            for i in range(min(len(matrix), 10)):
                row_name = RESOURCES[i] if i < len(RESOURCES) else f"Constraint {i+1}"
                constraint_text = f"{row_name}: "
                terms = []
                for j in range(len(matrix[i])):
                    if matrix[i][j] != 0:
                        var_name = PRODUCTS[j] if j < len(PRODUCTS) else f"x{j+1}"
                        terms.append(f"{matrix[i][j]:.1f}·{var_name[:10]}")
                constraint_text += " + ".join(terms[:5]) + f" ≤ {rhs[i]:,.0f}"
                
                ctk.CTkLabel(
                    const_card,
                    text=constraint_text,
                    font=ctk.CTkFont(family=FONTS["family"], size=11),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="w", padx=SPACING["lg"], pady=2)
        except:
            pass
    
    def _close_inputs_popup(self):
        """Close inputs fullscreen popup"""
        if self.inputs_popup:
            self.inputs_popup.destroy()
            self.inputs_popup = None
    
    def _fullscreen_results(self):
        """Open results panel in fullscreen window"""
        if self.results_popup:
            self.results_popup.lift()
            self.results_popup.focus()
            return
        
        self.results_popup = FullscreenWindow(
            self.winfo_toplevel(),
            title="Results & Analysis - Fullscreen",
            width=1200,
            height=850
        )
        self.results_popup.protocol("WM_DELETE_WINDOW", self._close_results_popup)
        
        # Create cloned results content
        body = self.results_popup.body_frame
        
        # Display current results in larger format
        if self.last_result and self.last_result.success:
            self._display_results_fullscreen(body)
        else:
            ctk.CTkLabel(
                body,
                text="⚠️ No solution available. Solve a problem first.",
                font=ctk.CTkFont(family=FONTS["family"], size=16),
                text_color=COLORS["warning"]
            ).pack(pady=SPACING["xl"])
    
    def _display_results_fullscreen(self, parent):
        """Display results in fullscreen format"""
        result = self.last_result
        
        # Optimal value card
        value_card = ctk.CTkFrame(parent, fg_color=COLORS["success"], corner_radius=12)
        value_card.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            value_card,
            text=f"✓ Optimal Value: Rs. {result.optimal_value:,.2f}",
            font=ctk.CTkFont(family=FONTS["family"], size=24, weight="bold"),
            text_color="#FFFFFF"
        ).pack(padx=SPACING["lg"], pady=SPACING["lg"])
        
        # Solution details
        sol_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
        sol_card.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            sol_card,
            text="📊 Optimal Production Plan",
            font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Grid for solution values
        grid_frame = ctk.CTkFrame(sol_card, fg_color="transparent")
        grid_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        for i, val in enumerate(result.solution[:10]):
            if val > 0.001:
                var_name = PRODUCTS[i] if i < len(PRODUCTS) else f"Variable {i+1}"
                item = ctk.CTkFrame(grid_frame, fg_color=COLORS["background"], corner_radius=8)
                item.pack(fill="x", pady=3)
                
                ctk.CTkLabel(
                    item,
                    text=f"{var_name}:",
                    font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(side="left", padx=SPACING["md"], pady=SPACING["sm"])
                
                ctk.CTkLabel(
                    item,
                    text=f"{val:,.2f} units",
                    font=ctk.CTkFont(family=FONTS["family"], size=13),
                    text_color=COLORS["accent"]
                ).pack(side="right", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Sensitivity info if available
        if result.sensitivity:
            sens_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
            sens_card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
            
            ctk.CTkLabel(
                sens_card,
                text="📈 Sensitivity Analysis Summary",
                font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
            
            # Shadow prices
            ctk.CTkLabel(
                sens_card,
                text="Shadow Prices (marginal value of each constraint):",
                font=ctk.CTkFont(family=FONTS["family"], size=12),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["sm"], 0))
            
            for i, sp in enumerate(result.sensitivity.shadow_prices[:5]):
                res_name = RESOURCES[i] if i < len(RESOURCES) else f"Constraint {i+1}"
                ctk.CTkLabel(
                    sens_card,
                    text=f"  • {res_name}: Rs. {sp:,.2f}",
                    font=ctk.CTkFont(family=FONTS["family"], size=11),
                    text_color=COLORS["text_secondary"]
                ).pack(anchor="w", padx=SPACING["lg"])
    
    def _close_results_popup(self):
        """Close results fullscreen popup"""
        if self.results_popup:
            self.results_popup.destroy()
            self.results_popup = None
    
    def _toggle_whatif_panel(self, visible=None):
        """Toggle the visibility of the What-If panel"""
        if self.right_panel_popped:
            self._close_popup()
            return
        
        if visible is None:
            visible = not self.right_panel_visible
        
        if visible:
            if not self.right_panel_visible:
                if hasattr(self, 'show_panel_btn') and self.show_panel_btn:
                    self.show_panel_btn.destroy()
                self.right_container.pack(side="right", fill="both", expand=False, padx=(SPACING["sm"], 0), pady=0)
                self.right_panel_visible = True
        else:
            if self.right_panel_visible:
                self.right_container.pack_forget()
                self.right_panel_visible = False
                # Add a button to show the panel again
                self.show_panel_btn = ctk.CTkButton(
                    self.middle_panel,
                    text="📊 Show What-If Panel",
                    width=180,
                    height=36,
                    font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
                    fg_color=COLORS["primary"],
                    hover_color=COLORS["primary_dark"],
                    corner_radius=8,
                    command=lambda: self._toggle_whatif_panel(True)
                )
                self.show_panel_btn.pack(pady=SPACING["md"])
        
        self.panel_toggles.set_visible("whatif", visible)

    
    def _on_variable_change(self, action: str, index: int, name: str):
        """Handle variable addition/removal from What-If panel"""
        if action == 'add':
            # Update the main input fields to reflect the change
            messagebox.showinfo(
                "Variable Added", 
                f"Variable added. Click 'Re-Solve' in the What-If panel to update results."
            )
        elif action == 'remove':
            messagebox.showinfo(
                "Variable Removed", 
                f"Variable removed. Click 'Re-Solve' in the What-If panel to update results."
            )
    
    def _on_constraint_change(self, action: str, index: int, name: str):
        """Handle constraint addition/removal from What-If panel"""
        if action == 'add':
            messagebox.showinfo(
                "Constraint Added", 
                f"Constraint added. Click 'Re-Solve' in the What-If panel to update results."
            )
        elif action == 'remove':
            messagebox.showinfo(
                "Constraint Removed", 
                f"Constraint removed. Click 'Re-Solve' in the What-If panel to update results."
            )
    
    def _resolve_whatif(self):
        """Re-solve with modified parameters from What-If panel"""
        try:
            # Get modified problem data
            problem = self.whatif_panel.get_modified_problem()
            
            c = np.array(problem['objective_coeffs'])
            A_ub = problem['constraint_matrix']
            b_ub = np.array(problem['rhs_values'])
            var_names = problem['variable_names']
            const_names = problem['constraint_names']
            maximize = self.objective_var.get() == "maximize"
            
            # Create and solve
            solver = SimplexSolver(
                c=c,
                A_ub=A_ub,
                b_ub=b_ub,
                maximize=maximize,
                variable_names=var_names,
                constraint_names=const_names
            )
            
            result = solver.solve()
            
            # Build result dictionary
            result_dict = {
                'success': result.success,
                'message': result.message,
                'optimal_value': result.optimal_value,
                'solution': result.solution,
                'iterations': result.iterations
            }
            
            if result.sensitivity:
                result_dict['shadow_prices'] = result.sensitivity.shadow_prices
                result_dict['slack_values'] = result.sensitivity.slack_values
            
            # Get sensitivity report with ranges
            if result.success and result.sensitivity:
                sens_report = solver.get_sensitivity_report()
                result_dict['objective_ranges'] = sens_report.get('objective_ranges', [])
                result_dict['rhs_ranges'] = sens_report.get('rhs_ranges', [])
            
            # Update What-If panel with new solution
            self.whatif_panel.update_solution(result_dict)
            
            # Update main displays
            self.result_display.display_lp_result(result_dict, var_names)
            
            if result.success and result.sensitivity:
                sens_report = solver.get_sensitivity_report()
                self.sensitivity_table.display_full_analysis(sens_report)
            
            messagebox.showinfo("Re-Solved", "Problem re-solved with modified parameters!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to re-solve: {str(e)}")
    
    def _load_sample(self):
        """Load sample TBLP (The Best Laboratory Pakistan) problem"""
        # Sample objective coefficients (profit per ton)
        objectives = np.array([5000, 7500, 4000, 3500, 6000, 4500, 8000, 3000, 9000, 8500])
        self.objective_input.set_values(objectives)
        
        # Sample constraint matrix
        constraints = np.array([
            [2, 3, 1, 2, 1, 2, 3, 1, 2, 3],    # Raw Material A
            [1, 2, 3, 1, 2, 1, 2, 3, 1, 2],    # Raw Material B
            [3, 2, 4, 1, 2, 3, 1, 2, 4, 2],    # Production Line 1
            [1, 2, 1, 3, 4, 2, 1, 2, 1, 3],    # Production Line 2
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],    # Storage
            [4, 5, 3, 4, 5, 3, 4, 5, 3, 4],    # Labor
            [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],  # QC
            [0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1, 0.2, 0.15, 0.1],  # Environmental
            [10, 15, 8, 12, 10, 8, 15, 10, 12, 14],  # Energy
            [1, 2, 1, 1, 2, 1, 2, 1, 1, 2]     # Packaging
        ])
        self.constraint_matrix.set_matrix(constraints)
        
        # Sample RHS values
        rhs = np.array([5000, 4000, 480, 400, 1000, 2000, 300, 100, 10000, 2500])
        self.rhs_input.set_values(rhs)
        
        # Set to maximize
        self.objective_var.set("maximize")
    
    def _resize_problem(self):
        """Resize the problem dimensions"""
        try:
            new_vars = int(self.var_spinbox.get())
            new_const = int(self.const_spinbox.get())
            
            if new_vars < 1 or new_const < 1:
                return
            
            self.num_variables = new_vars
            self.num_constraints = new_const
            
            # Recreate input widgets
            self.objective_input.destroy()
            self.constraint_matrix.destroy()
            self.rhs_input.destroy()
            
            # Update headers
            var_labels = [PRODUCTS[i] if i < len(PRODUCTS) else f"x{i+1}" for i in range(new_vars)]
            const_labels = [RESOURCES[i] if i < len(RESOURCES) else f"C{i+1}" for i in range(new_const)]
            
            # Recreate objective input
            obj_parent = self.left_panel.winfo_children()[2]  # Objective frame
            self.objective_input = VectorInput(
                obj_parent,
                size=new_vars,
                labels=var_labels,
                orientation="horizontal",
                default_value="0",
                cell_width=90
            )
            self.objective_input.pack(fill="x", padx=10, pady=5)
            
            # Recreate constraint matrix
            const_parent = self.left_panel.winfo_children()[3]  # Constraint frame
            self.constraint_matrix = MatrixInput(
                const_parent,
                rows=new_const,
                cols=new_vars,
                row_headers=const_labels,
                col_headers=[v[:12] for v in var_labels],
                default_value="0",
                cell_width=70
            )
            self.constraint_matrix.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Recreate RHS input
            rhs_parent = const_parent.winfo_children()[-1]  # RHS frame
            self.rhs_input = VectorInput(
                rhs_parent,
                size=new_const,
                labels=const_labels,
                orientation="vertical",
                default_value="0",
                cell_width=100
            )
            self.rhs_input.pack(fill="x", padx=10, pady=5)
            
        except ValueError:
            pass
    
    def _solve(self):
        """Solve the LP problem"""
        try:
            # Get input data
            c = self.objective_input.get_values()
            A_ub = self.constraint_matrix.get_matrix()
            b_ub = self.rhs_input.get_values()
            maximize = self.objective_var.get() == "maximize"
            
            # Get variable names
            var_names = [PRODUCTS[i] if i < len(PRODUCTS) else f"x{i+1}" 
                        for i in range(self.num_variables)]
            const_names = [RESOURCES[i] if i < len(RESOURCES) else f"Constraint {i+1}"
                          for i in range(self.num_constraints)]
            
            # Create and solve
            solver = SimplexSolver(
                c=c,
                A_ub=A_ub,
                b_ub=b_ub,
                maximize=maximize,
                variable_names=var_names,
                constraint_names=const_names
            )
            
            result = solver.solve()
            
            # Display results
            result_dict = {
                'success': result.success,
                'message': result.message,
                'optimal_value': result.optimal_value,
                'solution': result.solution,
                'iterations': result.iterations
            }
            
            if result.sensitivity:
                result_dict['shadow_prices'] = result.sensitivity.shadow_prices
                result_dict['slack_values'] = result.sensitivity.slack_values
            
            self.result_display.display_lp_result(result_dict, var_names)
            
            # Display sensitivity analysis
            if result.success and result.sensitivity:
                sens_report = solver.get_sensitivity_report()
                self.sensitivity_table.display_full_analysis(sens_report)
                
                # Add ranges to result dict for What-If panel
                result_dict['objective_ranges'] = sens_report.get('objective_ranges', [])
                result_dict['rhs_ranges'] = sens_report.get('rhs_ranges', [])
            
            # Store for What-If analysis
            self.last_result = result
            self.last_solver = solver
            
            # Load problem into What-If panel
            self.whatif_panel.load_problem(
                num_variables=self.num_variables,
                num_constraints=self.num_constraints,
                variable_names=var_names,
                constraint_names=const_names,
                objective_coeffs=c,
                constraint_matrix=A_ub,
                rhs_values=b_ub,
                solution=result_dict
            )
            
        except Exception as e:
            self.result_display.set_status(False, f"Error: {str(e)}")
    
    def _clear(self):
        """Clear all inputs and results"""
        self.objective_input.clear()
        self.constraint_matrix.clear()
        self.rhs_input.clear()
        self.result_display.clear()
        self.sensitivity_table.clear()
        # Reset What-If panel
        self.whatif_panel.load_problem(
            num_variables=0,
            num_constraints=0,
            variable_names=[],
            constraint_names=[],
            objective_coeffs=[],
            constraint_matrix=None,
            rhs_values=[],
            solution={}
        )
        self.last_result = None
        self.last_solver = None
    
    def _export(self):
        """Export results to file"""
        # TODO: Implement export functionality
        pass
