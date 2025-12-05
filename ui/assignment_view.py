"""
Assignment Problem View
UI for inputting and solving assignment problems using Hungarian algorithm
"""

import customtkinter as ctk
import numpy as np
from typing import Optional, List

from ui.components.matrix_input import MatrixInput
from ui.components.result_display import ResultDisplay, AllocationMatrixDisplay
from ui.components.panel_controls import PanelHeader, PanelToggleBar, FullscreenWindow
from algorithms.assignment import AssignmentSolver, create_sample_problem
from config.settings import WORKERS, TASKS, DEFAULT_MATRIX_SIZE, COLORS, SPACING, FONTS


class AssignmentView(ctk.CTkFrame):
    """
    View for Assignment Problems
    
    Features:
    - Cost/efficiency matrix input
    - Maximize/Minimize toggle
    - Custom row/column names
    - Visual assignment display
    - Load sample problem
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.matrix_size = DEFAULT_MATRIX_SIZE
        
        self._create_layout()
        self._create_widgets()
    
    def _create_layout(self):
        """Create the main layout structure with panel controls"""
        # Top toolbar for panel controls
        self.toolbar = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0, height=45)
        self.toolbar.pack(fill="x", padx=0, pady=0)
        self.toolbar.pack_propagate(False)
        
        # Panel toggle bar
        self.panel_toggles = PanelToggleBar(
            self.toolbar,
            panels={
                "inputs": {"label": "Inputs", "icon": "📝", "visible": True},
                "results": {"label": "Results", "icon": "📊", "visible": True}
            }
        )
        self.panel_toggles.pack(side="left", padx=SPACING["md"], pady=SPACING["xs"])
        
        # Register toggle callbacks
        self.panel_toggles.register_callback("inputs", self._toggle_inputs_panel)
        self.panel_toggles.register_callback("results", self._toggle_results_panel)
        
        # Main content container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=SPACING["sm"], pady=SPACING["sm"])
        
        # Track panel states
        self.inputs_panel_visible = True
        self.results_panel_visible = True
        self.inputs_popup = None
        self.results_popup = None
        self.last_result = None
        
        # Left panel container (inputs)
        self.left_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_container.pack(side="left", fill="both", expand=True, padx=(0, SPACING["md"]), pady=0)
        
        # Left panel header with fullscreen button
        self.left_header = PanelHeader(
            self.left_container,
            title="Problem Inputs",
            icon="👥",
            on_fullscreen=self._fullscreen_inputs,
            on_toggle=lambda: self._toggle_inputs_panel(False),
            fg_color=COLORS["secondary"]
        )
        self.left_header.pack(fill="x", padx=0, pady=(0, SPACING["sm"]))
        
        # Left panel (inputs) - scrollable with smooth scrolling
        self.left_panel = ctk.CTkScrollableFrame(
            self.left_container, 
            width=600,
            fg_color=COLORS["surface"],
            corner_radius=12,
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        self.left_panel.pack(fill="both", expand=True, pady=0)
        
        # Right panel container (results)
        self.right_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_container.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Right panel header with fullscreen button
        self.right_header = PanelHeader(
            self.right_container,
            title="Results & Assignment",
            icon="📊",
            on_fullscreen=self._fullscreen_results,
            on_toggle=lambda: self._toggle_results_panel(False)
        )
        self.right_header.pack(fill="x", padx=0, pady=(0, SPACING["sm"]))
        
        # Right panel (results) - scrollable with card styling
        self.right_panel = ctk.CTkScrollableFrame(
            self.right_container, 
            width=620,
            fg_color=COLORS["surface"],
            corner_radius=12,
            scrollbar_button_hover_color=COLORS["secondary"],
            scrollbar_button_color=COLORS["border"]
        )
        self.right_panel.pack(fill="both", expand=True, pady=0)
    
    def _create_widgets(self):
        """Create all UI widgets"""
        self._create_header()
        self._create_settings()
        self._create_matrix_input()
        self._create_action_buttons()
        self._create_results_panel()
        self._setup_smooth_scroll()
    
    def _setup_smooth_scroll(self):
        """Setup smooth scrolling for all scrollable panels"""
        self.scroll_speed = 2
        for panel in [self.left_panel, self.right_panel]:
            self._bind_smooth_scroll(panel)
    
    def _bind_smooth_scroll(self, scrollable_frame):
        """Bind smooth scroll events to a scrollable frame"""
        try:
            canvas = scrollable_frame._parent_canvas
            
            def smooth_scroll(event):
                if event.delta:
                    scroll_amount = -1 * (event.delta // 60) * self.scroll_speed
                else:
                    scroll_amount = -4 if event.num == 4 else 4
                canvas.yview_scroll(scroll_amount, "units")
                return "break"
            
            scrollable_frame.bind("<MouseWheel>", smooth_scroll, add="+")
            scrollable_frame.bind("<Button-4>", smooth_scroll, add="+")
            scrollable_frame.bind("<Button-5>", smooth_scroll, add="+")
            canvas.bind("<MouseWheel>", smooth_scroll, add="+")
            canvas.bind("<Button-4>", smooth_scroll, add="+")
            canvas.bind("<Button-5>", smooth_scroll, add="+")
            
            def bind_children(widget):
                widget.bind("<MouseWheel>", smooth_scroll, add="+")
                widget.bind("<Button-4>", smooth_scroll, add="+")
                widget.bind("<Button-5>", smooth_scroll, add="+")
                for child in widget.winfo_children():
                    bind_children(child)
            bind_children(scrollable_frame)
        except Exception:
            pass
    
    def _create_header(self):
        """Create the header section with modern styling"""
        header_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["secondary"],
            corner_radius=12
        )
        header_frame.pack(fill="x", padx=SPACING["sm"], pady=(SPACING["sm"], SPACING["lg"]))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=SPACING["lg"], pady=SPACING["lg"])
        
        # Icon and title
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="👥",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")
        
        ctk.CTkLabel(
            text_frame,
            text="Assignment Problem",
            font=ctk.CTkFont(family=FONTS["family"], size=22, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_frame,
            text="Hungarian Algorithm Solver",
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
    
    def _create_settings(self):
        """Create settings section with card styling"""
        # Settings card container
        settings_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        settings_card.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["section_gap"]))
        
        # Card header
        card_header = ctk.CTkFrame(settings_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            card_header,
            text="⚙️  Configuration",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Divider
        ctk.CTkFrame(settings_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"]
        )
        
        # Size settings row
        size_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        size_frame.pack(fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            size_frame, 
            text="Matrix Size:",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        self.rows_entry = ctk.CTkEntry(
            size_frame, 
            width=70, 
            justify="center",
            height=32,
            corner_radius=6
        )
        self.rows_entry.insert(0, str(self.matrix_size))
        self.rows_entry.pack(side="left", padx=(0, SPACING["sm"]))
        
        ctk.CTkLabel(
            size_frame, 
            text="×",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold")
        ).pack(side="left", padx=SPACING["sm"])
        
        self.cols_entry = ctk.CTkEntry(
            size_frame, 
            width=70, 
            justify="center",
            height=32,
            corner_radius=6
        )
        self.cols_entry.insert(0, str(self.matrix_size))
        self.cols_entry.pack(side="left", padx=(SPACING["sm"], SPACING["lg"]))
        
        ctk.CTkButton(
            size_frame,
            text="Resize",
            command=self._resize_matrix,
            width=90,
            height=32,
            corner_radius=6,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_light"]
        ).pack(side="left")
        
        # Objective type row
        obj_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        obj_frame.pack(fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            obj_frame, 
            text="Objective:",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        self.objective_var = ctk.StringVar(value="maximize")
        ctk.CTkRadioButton(
            obj_frame,
            text="Maximize Efficiency",
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
        
        # Tip section
        tip_frame = ctk.CTkFrame(settings_card, fg_color=COLORS["background"], corner_radius=8)
        tip_frame.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["sm"], SPACING["card_padding"]))
        
        ctk.CTkLabel(
            tip_frame,
            text="💡 Tip: Enter efficiency scores (higher = better) or costs (lower = better)",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color=COLORS["text_secondary"]
        ).pack(padx=SPACING["md"], pady=SPACING["sm"])
    
    def _create_matrix_input(self):
        """Create the matrix input section with card styling"""
        # Matrix card
        matrix_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        matrix_card.pack(fill="both", expand=True, padx=SPACING["sm"], pady=(0, SPACING["section_gap"]))
        
        # Card header
        card_header = ctk.CTkFrame(matrix_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            card_header,
            text="📊  Cost/Efficiency Matrix",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            card_header,
            text="Workers × Tasks",
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(matrix_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"]
        )
        
        # Matrix input area
        matrix_frame = ctk.CTkFrame(matrix_card, fg_color="transparent")
        matrix_frame.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=(SPACING["sm"], SPACING["card_padding"]))
        
        self.matrix_input = MatrixInput(
            matrix_frame,
            rows=self.matrix_size,
            cols=self.matrix_size,
            row_headers=WORKERS[:self.matrix_size],
            col_headers=TASKS[:self.matrix_size],
            default_value="0",
            cell_width=70,
            editable_headers=True
        )
        self.matrix_input.pack(fill="both", expand=True)
    
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
            text="🔍 Find Optimal Assignment",
            command=self._solve,
            width=200,
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
            text="🎲 Random Data",
            command=self._generate_random,
            width=140,
            height=44,
            font=ctk.CTkFont(family=FONTS["family"], size=13),
            fg_color="#9C27B0",
            hover_color="#7B1FA2",
            corner_radius=8
        ).pack(side="left")
    
    def _create_results_panel(self):
        """Create the results display panel with improved spacing"""
        # Panel header
        header_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        header_frame.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            header_frame,
            text="📊  Results",
            font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        # Result display
        self.result_display = ResultDisplay(
            self.right_panel,
            title="Assignment Results"
        )
        self.result_display.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        # Assignment matrix visualization
        self.allocation_display = AllocationMatrixDisplay(
            self.right_panel,
            title="Optimal Assignment Matrix"
        )
        self.allocation_display.pack(fill="both", expand=True, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]))
    
    def _load_sample(self):
        """Load sample TBLP worker assignment"""
        # Sample efficiency matrix
        efficiency_matrix = np.array([
            [85, 70, 65, 80, 75, 90, 60, 50, 70, 65],
            [75, 85, 70, 65, 80, 75, 70, 60, 65, 70],
            [80, 75, 90, 70, 65, 80, 75, 55, 80, 60],
            [65, 80, 75, 90, 70, 65, 80, 70, 75, 80],
            [70, 65, 80, 75, 90, 70, 65, 75, 60, 85],
            [90, 75, 70, 65, 80, 85, 70, 80, 65, 70],
            [60, 90, 65, 80, 75, 70, 95, 65, 80, 75],
            [55, 65, 80, 70, 85, 75, 70, 90, 70, 80],
            [75, 70, 85, 75, 70, 80, 75, 70, 95, 65],
            [70, 75, 60, 85, 80, 70, 80, 75, 70, 90]
        ])
        
        self.matrix_input.set_matrix(efficiency_matrix)
        self.matrix_input.set_row_headers([
            "Ali Khan", "Bilal Ahmed", "Chaudhry Imran", "Danish Malik",
            "Ejaz Shah", "Farhan Raza", "Ghulam Abbas", "Hassan Javed",
            "Irfan Siddiqui", "Junaid Tariq"
        ])
        self.matrix_input.set_col_headers([
            "Mixing", "Heating", "Testing", "Packing", "Loading",
            "QC", "Maintenance", "Docs", "Safety", "Dispatch"
        ])
        
        self.objective_var.set("maximize")
    
    def _resize_matrix(self):
        """Resize the matrix"""
        try:
            new_rows = int(self.rows_entry.get())
            new_cols = int(self.cols_entry.get())
            
            if new_rows < 1 or new_cols < 1:
                return
            
            self.matrix_size = max(new_rows, new_cols)
            self.matrix_input.resize(new_rows, new_cols)
            
        except ValueError:
            pass
    
    def _generate_random(self):
        """Generate random matrix data"""
        matrix = np.random.randint(10, 100, (self.matrix_size, self.matrix_size))
        self.matrix_input.set_matrix(matrix)
    
    def _solve(self):
        """Solve the assignment problem"""
        try:
            # Get input data
            cost_matrix = self.matrix_input.get_matrix()
            maximize = self.objective_var.get() == "maximize"
            row_names = self.matrix_input.get_row_headers()
            col_names = self.matrix_input.get_col_headers()
            
            # Create and solve
            solver = AssignmentSolver(
                cost_matrix=cost_matrix,
                maximize=maximize,
                row_names=row_names,
                col_names=col_names
            )
            
            result = solver.solve()
            
            # Store for fullscreen display
            self.last_result = result
            self.last_row_names = row_names
            self.last_col_names = col_names
            self.last_cost_matrix = cost_matrix
            
            # Display results
            result_dict = {
                'success': result.success,
                'message': result.message,
                'total_cost': result.total_cost,
                'assignments': result.assignments,
                'individual_costs': result.individual_costs,
                'maximize': maximize
            }
            
            self.result_display.display_assignment_result(
                result_dict,
                row_names=row_names,
                col_names=col_names
            )
            
            # Display assignment matrix
            if result.success:
                self.allocation_display.display_matrix(
                    result.assignment_matrix,
                    cost_matrix=cost_matrix,
                    row_names=row_names,
                    col_names=col_names,
                    highlight_nonzero=True
                )
            
        except Exception as e:
            self.result_display.set_status(False, f"Error: {str(e)}")
    
    def _clear(self):
        """Clear all inputs and results"""
        self.matrix_input.clear()
        self.result_display.clear()
        self.allocation_display.clear()
        self.last_result = None
    
    def _toggle_inputs_panel(self, visible=None):
        """Toggle the visibility of the Inputs panel"""
        if visible is None:
            visible = not self.inputs_panel_visible
        
        if visible:
            if not self.inputs_panel_visible:
                self.left_container.pack(side="left", fill="both", expand=True, padx=(0, SPACING["md"]), pady=0, before=self.right_container)
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
                self.right_container.pack(side="right", fill="both", expand=True, padx=0, pady=0)
                self.results_panel_visible = True
        else:
            if self.results_panel_visible:
                self.right_container.pack_forget()
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
            title="Assignment Matrix - Fullscreen",
            width=1100,
            height=800
        )
        self.inputs_popup.protocol("WM_DELETE_WINDOW", self._close_inputs_popup)
        
        body = self.inputs_popup.body_frame
        
        ctk.CTkLabel(
            body,
            text="💡 Fullscreen view of the assignment matrix. Edit in main window.",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=SPACING["md"])
        
        # Display matrix summary
        self._display_matrix_summary(body)
    
    def _display_matrix_summary(self, parent):
        """Display matrix content in fullscreen"""
        try:
            matrix = self.matrix_input.get_matrix()
            row_headers = self.matrix_input.get_row_headers()
            col_headers = self.matrix_input.get_col_headers()
            
            # Matrix card
            matrix_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
            matrix_card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
            
            ctk.CTkLabel(
                matrix_card,
                text="📊 Cost/Efficiency Matrix",
                font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
            
            # Display matrix as grid
            grid_frame = ctk.CTkFrame(matrix_card, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
            
            # Header row
            header_row = ctk.CTkFrame(grid_frame, fg_color=COLORS["primary"])
            header_row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(header_row, text="Worker / Task", width=120, text_color="#FFFFFF", 
                        font=ctk.CTkFont(family=FONTS["family"], size=11, weight="bold")).pack(side="left", padx=2)
            for j, col in enumerate(col_headers[:10]):
                ctk.CTkLabel(header_row, text=str(col)[:12], width=80, text_color="#FFFFFF",
                            font=ctk.CTkFont(family=FONTS["family"], size=10)).pack(side="left", padx=2)
            
            # Data rows
            for i in range(min(len(matrix), 10)):
                row_frame = ctk.CTkFrame(grid_frame, fg_color=COLORS["background"] if i % 2 == 0 else COLORS["surface"])
                row_frame.pack(fill="x", pady=1)
                
                ctk.CTkLabel(row_frame, text=str(row_headers[i])[:15], width=120,
                            font=ctk.CTkFont(family=FONTS["family"], size=11, weight="bold"),
                            text_color=COLORS["text_primary"]).pack(side="left", padx=2)
                for j in range(min(len(matrix[i]), 10)):
                    ctk.CTkLabel(row_frame, text=f"{matrix[i][j]:.0f}", width=80,
                                font=ctk.CTkFont(family=FONTS["family"], size=10),
                                text_color=COLORS["text_secondary"]).pack(side="left", padx=2)
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
            title="Assignment Results - Fullscreen",
            width=1200,
            height=850
        )
        self.results_popup.protocol("WM_DELETE_WINDOW", self._close_results_popup)
        
        body = self.results_popup.body_frame
        
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
        """Display assignment results in fullscreen"""
        result = self.last_result
        maximize = self.objective_var.get() == "maximize"
        
        # Summary card
        summary_card = ctk.CTkFrame(parent, fg_color=COLORS["success"], corner_radius=12)
        summary_card.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        label = "Total Efficiency" if maximize else "Total Cost"
        ctk.CTkLabel(
            summary_card,
            text=f"✓ Optimal {label}: {result.total_cost:,.2f}",
            font=ctk.CTkFont(family=FONTS["family"], size=24, weight="bold"),
            text_color="#FFFFFF"
        ).pack(padx=SPACING["lg"], pady=SPACING["lg"])
        
        # Assignments card
        assign_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
        assign_card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            assign_card,
            text="👥 Optimal Assignments",
            font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
        
        # List assignments
        for i, (worker, task) in enumerate(result.assignments):
            worker_name = self.last_row_names[worker] if hasattr(self, 'last_row_names') else f"Worker {worker+1}"
            task_name = self.last_col_names[task] if hasattr(self, 'last_col_names') else f"Task {task+1}"
            cost = result.individual_costs[i] if i < len(result.individual_costs) else 0
            
            item = ctk.CTkFrame(assign_card, fg_color=COLORS["background"], corner_radius=8)
            item.pack(fill="x", padx=SPACING["md"], pady=3)
            
            ctk.CTkLabel(
                item,
                text=f"➜ {worker_name}",
                font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(side="left", padx=SPACING["md"], pady=SPACING["sm"])
            
            ctk.CTkLabel(
                item,
                text=f"→ {task_name}",
                font=ctk.CTkFont(family=FONTS["family"], size=13),
                text_color=COLORS["secondary"]
            ).pack(side="left", padx=SPACING["sm"])
            
            ctk.CTkLabel(
                item,
                text=f"({cost:,.0f})",
                font=ctk.CTkFont(family=FONTS["family"], size=12),
                text_color=COLORS["accent"]
            ).pack(side="right", padx=SPACING["md"])
    
    def _close_results_popup(self):
        """Close results fullscreen popup"""
        if self.results_popup:
            self.results_popup.destroy()
            self.results_popup = None

