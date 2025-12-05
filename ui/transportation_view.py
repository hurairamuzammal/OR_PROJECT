"""
Transportation Problem View
UI for inputting and solving transportation problems using VAM and MODI
"""

import customtkinter as ctk
import numpy as np
from typing import Optional, List

from ui.components.matrix_input import MatrixInput, VectorInput
from ui.components.result_display import ResultDisplay, AllocationMatrixDisplay
from ui.components.panel_controls import PanelHeader, PanelToggleBar, FullscreenWindow
from algorithms.transportation import TransportationSolver, InitialMethod
from config.settings import PLANTS, DESTINATIONS, DEFAULT_MATRIX_SIZE, COLORS, SPACING, FONTS


class TransportationView(ctk.CTkFrame):
    """
    View for Transportation Problems
    
    Features:
    - Supply/demand input
    - Cost matrix input
    - Multiple solution methods (NW Corner, Least Cost, VAM)
    - MODI optimization
    - Visual allocation display
    - Load sample problem
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.num_sources = DEFAULT_MATRIX_SIZE
        self.num_destinations = DEFAULT_MATRIX_SIZE
        
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
            icon="🚚",
            on_fullscreen=self._fullscreen_inputs,
            on_toggle=lambda: self._toggle_inputs_panel(False),
            fg_color=COLORS["accent"]
        )
        self.left_header.pack(fill="x", padx=0, pady=(0, SPACING["sm"]))
        
        # Left panel (inputs) - scrollable with smooth scrolling
        self.left_panel = ctk.CTkScrollableFrame(
            self.left_container, 
            width=650,
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
            title="Results & Shipping Plan",
            icon="📊",
            on_fullscreen=self._fullscreen_results,
            on_toggle=lambda: self._toggle_results_panel(False)
        )
        self.right_header.pack(fill="x", padx=0, pady=(0, SPACING["sm"]))
        
        # Right panel (results) - scrollable with card styling
        self.right_panel = ctk.CTkScrollableFrame(
            self.right_container, 
            width=580,
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
        self._create_supply_input()
        self._create_cost_matrix_input()
        self._create_demand_input()
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
            fg_color=COLORS["accent"],
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
            text="🚚",
            font=ctk.CTkFont(size=28)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")
        
        ctk.CTkLabel(
            text_frame,
            text="Transportation Problem",
            font=ctk.CTkFont(family=FONTS["family"], size=22, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            text_frame,
            text="VAM + MODI Method Solver",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        # Load sample button
        ctk.CTkButton(
            header_content,
            text="📥 Load TBLP Example",
            command=self._load_sample,
            width=180,
            height=38,
            font=ctk.CTkFont(family=FONTS["family"], size=13, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
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
            text="Sources:",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        self.sources_entry = ctk.CTkEntry(
            size_frame, 
            width=70, 
            justify="center",
            height=32,
            corner_radius=6
        )
        self.sources_entry.insert(0, str(self.num_sources))
        self.sources_entry.pack(side="left", padx=(0, SPACING["lg"]))
        
        ctk.CTkLabel(
            size_frame, 
            text="Destinations:",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["sm"]))
        
        self.dest_entry = ctk.CTkEntry(
            size_frame, 
            width=70, 
            justify="center",
            height=32,
            corner_radius=6
        )
        self.dest_entry.insert(0, str(self.num_destinations))
        self.dest_entry.pack(side="left", padx=(0, SPACING["lg"]))
        
        ctk.CTkButton(
            size_frame,
            text="Resize",
            command=self._resize,
            width=90,
            height=32,
            corner_radius=6,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_light"]
        ).pack(side="left")
        
        # Method selection row
        method_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        method_frame.pack(fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            method_frame, 
            text="Initial Solution:",
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        self.method_var = ctk.StringVar(value="vam")
        
        ctk.CTkRadioButton(
            method_frame,
            text="VAM (Best)",
            variable=self.method_var,
            value="vam",
            font=ctk.CTkFont(family=FONTS["family"], size=12)
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        ctk.CTkRadioButton(
            method_frame,
            text="Least Cost",
            variable=self.method_var,
            value="least_cost",
            font=ctk.CTkFont(family=FONTS["family"], size=12)
        ).pack(side="left", padx=(0, SPACING["md"]))
        
        ctk.CTkRadioButton(
            method_frame,
            text="NW Corner",
            variable=self.method_var,
            value="north_west",
            font=ctk.CTkFont(family=FONTS["family"], size=12)
        ).pack(side="left")
        
        # Optimize toggle row
        optimize_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        optimize_frame.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["sm"], SPACING["card_padding"]))
        
        self.optimize_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            optimize_frame,
            text="Apply MODI Optimization",
            variable=self.optimize_var,
            font=ctk.CTkFont(family=FONTS["family"], size=13)
        ).pack(side="left")
        
        # Balance info
        self.balance_label = ctk.CTkLabel(
            optimize_frame,
            text="",
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            text_color=COLORS["text_muted"]
        )
        self.balance_label.pack(side="right")
    
    def _create_supply_input(self):
        """Create supply input section with card styling"""
        # Supply card
        supply_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        supply_card.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["section_gap"]))
        
        # Card header
        card_header = ctk.CTkFrame(supply_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            card_header,
            text="🏭  Supply at Sources",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            card_header,
            text="Plants",
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(supply_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"]
        )
        
        # Supply input area
        input_frame = ctk.CTkFrame(supply_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["sm"], SPACING["card_padding"]))
        
        self.supply_input = VectorInput(
            input_frame,
            size=self.num_sources,
            labels=PLANTS[:self.num_sources],
            orientation="horizontal",
            default_value="0",
            cell_width=80
        )
        self.supply_input.pack(fill="x")
    
    def _create_cost_matrix_input(self):
        """Create cost matrix input section with card styling"""
        # Cost matrix card
        cost_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        cost_card.pack(fill="both", expand=True, padx=SPACING["sm"], pady=(0, SPACING["section_gap"]))
        
        # Card header
        card_header = ctk.CTkFrame(cost_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            card_header,
            text="💰  Transportation Costs",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            card_header,
            text="Rs. per unit",
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(cost_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"]
        )
        
        # Matrix input area
        matrix_frame = ctk.CTkFrame(cost_card, fg_color="transparent")
        matrix_frame.pack(fill="both", expand=True, padx=SPACING["card_padding"], pady=(SPACING["sm"], SPACING["card_padding"]))
        
        self.cost_matrix = MatrixInput(
            matrix_frame,
            rows=self.num_sources,
            cols=self.num_destinations,
            row_headers=PLANTS[:self.num_sources],
            col_headers=[d[:10] for d in DESTINATIONS[:self.num_destinations]],
            default_value="0",
            cell_width=70
        )
        self.cost_matrix.pack(fill="both", expand=True)
    
    def _create_demand_input(self):
        """Create demand input section with card styling"""
        # Demand card
        demand_card = ctk.CTkFrame(
            self.left_panel,
            fg_color=COLORS["surface"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )
        demand_card.pack(fill="x", padx=SPACING["sm"], pady=(0, SPACING["section_gap"]))
        
        # Card header
        card_header = ctk.CTkFrame(demand_card, fg_color="transparent")
        card_header.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["md"], SPACING["sm"]))
        
        ctk.CTkLabel(
            card_header,
            text="🏗️  Demand at Destinations",
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            card_header,
            text="Construction Sites",
            font=ctk.CTkFont(family=FONTS["family"], size=11),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
        
        # Divider
        ctk.CTkFrame(demand_card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=SPACING["card_padding"], pady=SPACING["sm"]
        )
        
        # Demand input area
        input_frame = ctk.CTkFrame(demand_card, fg_color="transparent")
        input_frame.pack(fill="x", padx=SPACING["card_padding"], pady=(SPACING["sm"], SPACING["card_padding"]))
        
        self.demand_input = VectorInput(
            input_frame,
            size=self.num_destinations,
            labels=[d[:12] for d in DESTINATIONS[:self.num_destinations]],
            orientation="horizontal",
            default_value="0",
            cell_width=80
        )
        self.demand_input.pack(fill="x")
    
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
            text="🔍 Find Optimal Shipment",
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
            text="⚖️ Check Balance",
            command=self._check_balance,
            width=140,
            height=44,
            font=ctk.CTkFont(family=FONTS["family"], size=13),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_light"],
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
            title="Transportation Results"
        )
        self.result_display.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        # Allocation matrix visualization
        self.allocation_display = AllocationMatrixDisplay(
            self.right_panel,
            title="Optimal Shipping Plan"
        )
        self.allocation_display.pack(fill="both", expand=True, padx=SPACING["md"], pady=(SPACING["sm"], SPACING["md"]))
    
    def _load_sample(self):
        """Load sample TBLP transportation problem"""
        # Supply from 10 plants
        supply = np.array([500, 400, 350, 450, 380, 420, 300, 360, 410, 330])
        self.supply_input.set_values(supply)
        
        # Demand at 10 construction sites
        demand = np.array([200, 180, 300, 250, 350, 280, 320, 400, 290, 330])
        self.demand_input.set_values(demand)
        
        # Transportation cost matrix
        cost_matrix = np.array([
            [45, 72, 35, 58, 62, 48, 55, 80, 42, 65],
            [38, 65, 42, 52, 58, 45, 50, 75, 38, 60],
            [55, 48, 58, 42, 45, 52, 48, 62, 55, 45],
            [62, 55, 48, 38, 42, 55, 52, 58, 48, 42],
            [70, 58, 52, 45, 38, 48, 45, 52, 55, 48],
            [58, 52, 55, 48, 45, 35, 42, 48, 52, 55],
            [85, 78, 72, 65, 58, 52, 45, 38, 65, 58],
            [78, 72, 65, 58, 52, 48, 42, 45, 58, 55],
            [72, 68, 62, 55, 48, 52, 48, 42, 52, 48],
            [95, 88, 82, 75, 68, 62, 55, 48, 72, 65]
        ])
        self.cost_matrix.set_matrix(cost_matrix)
        
        self._check_balance()
    
    def _resize(self):
        """Resize the problem dimensions"""
        try:
            new_sources = int(self.sources_entry.get())
            new_dests = int(self.dest_entry.get())
            
            if new_sources < 1 or new_dests < 1:
                return
            
            self.num_sources = new_sources
            self.num_destinations = new_dests
            
            # Resize widgets
            self.supply_input.destroy()
            self.cost_matrix.destroy()
            self.demand_input.destroy()
            
            # Recreate supply input
            supply_parent = self.left_panel.winfo_children()[2]
            self.supply_input = VectorInput(
                supply_parent,
                size=new_sources,
                labels=[PLANTS[i] if i < len(PLANTS) else f"S{i+1}" for i in range(new_sources)],
                orientation="horizontal",
                default_value="0",
                cell_width=80
            )
            self.supply_input.pack(fill="x", padx=10, pady=5)
            
            # Recreate cost matrix
            matrix_parent = self.left_panel.winfo_children()[3]
            self.cost_matrix = MatrixInput(
                matrix_parent,
                rows=new_sources,
                cols=new_dests,
                row_headers=[PLANTS[i] if i < len(PLANTS) else f"S{i+1}" for i in range(new_sources)],
                col_headers=[DESTINATIONS[j][:10] if j < len(DESTINATIONS) else f"D{j+1}" for j in range(new_dests)],
                default_value="0",
                cell_width=70
            )
            self.cost_matrix.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Recreate demand input
            demand_parent = self.left_panel.winfo_children()[4]
            self.demand_input = VectorInput(
                demand_parent,
                size=new_dests,
                labels=[DESTINATIONS[j][:12] if j < len(DESTINATIONS) else f"D{j+1}" for j in range(new_dests)],
                orientation="horizontal",
                default_value="0",
                cell_width=80
            )
            self.demand_input.pack(fill="x", padx=10, pady=5)
            
        except ValueError:
            pass
    
    def _check_balance(self):
        """Check if supply equals demand"""
        supply = self.supply_input.get_values()
        demand = self.demand_input.get_values()
        
        total_supply = np.sum(supply)
        total_demand = np.sum(demand)
        
        if abs(total_supply - total_demand) < 1e-6:
            self.balance_label.configure(
                text=f"✓ Balanced (Supply = Demand = {total_supply:,.0f})",
                text_color="#4CAF50"
            )
        elif total_supply > total_demand:
            diff = total_supply - total_demand
            self.balance_label.configure(
                text=f"⚠ Unbalanced: Excess supply of {diff:,.0f}",
                text_color="#FF9800"
            )
        else:
            diff = total_demand - total_supply
            self.balance_label.configure(
                text=f"⚠ Unbalanced: Excess demand of {diff:,.0f}",
                text_color="#FF9800"
            )
    
    def _solve(self):
        """Solve the transportation problem"""
        try:
            # Get input data
            supply = self.supply_input.get_values()
            demand = self.demand_input.get_values()
            costs = self.cost_matrix.get_matrix()
            
            # Get method
            method_map = {
                'vam': InitialMethod.VOGEL,
                'least_cost': InitialMethod.LEAST_COST,
                'north_west': InitialMethod.NORTH_WEST_CORNER
            }
            method = method_map.get(self.method_var.get(), InitialMethod.VOGEL)
            optimize = self.optimize_var.get()
            
            # Get names
            source_names = [PLANTS[i] if i < len(PLANTS) else f"Source {i+1}" 
                           for i in range(self.num_sources)]
            dest_names = [DESTINATIONS[j] if j < len(DESTINATIONS) else f"Dest {j+1}"
                         for j in range(self.num_destinations)]
            
            # Create and solve
            solver = TransportationSolver(
                supply=supply,
                demand=demand,
                cost_matrix=costs,
                source_names=source_names,
                dest_names=dest_names
            )
            
            result = solver.solve(method=method, optimize=optimize)
            
            # Display results
            result_dict = {
                'success': result.success,
                'message': result.message,
                'total_cost': result.total_cost,
                'routes': result.route_details,
                'is_optimal': result.is_optimal,
                'iterations': result.iterations,
                'initial_method': result.initial_method
            }
            
            # Store for fullscreen display
            self.last_result = result
            self.last_source_names = source_names
            self.last_dest_names = dest_names
            self.last_costs = costs
            
            self.result_display.display_transportation_result(
                result_dict,
                source_names=source_names,
                dest_names=dest_names
            )
            
            # Display allocation matrix
            if result.success:
                self.allocation_display.display_matrix(
                    result.allocation_matrix,
                    cost_matrix=costs,
                    row_names=source_names,
                    col_names=dest_names,
                    highlight_nonzero=True
                )
            
            # Update balance info
            self._check_balance()
            
        except Exception as e:
            self.result_display.set_status(False, f"Error: {str(e)}")
    
    def _clear(self):
        """Clear all inputs and results"""
        self.supply_input.clear()
        self.demand_input.clear()
        self.cost_matrix.clear()
        self.result_display.clear()
        self.allocation_display.clear()
        self.balance_label.configure(text="", text_color="gray")
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
            title="Transportation Data - Fullscreen",
            width=1100,
            height=800
        )
        self.inputs_popup.protocol("WM_DELETE_WINDOW", self._close_inputs_popup)
        
        body = self.inputs_popup.body_frame
        
        ctk.CTkLabel(
            body,
            text="💡 Fullscreen view of transportation data. Edit in main window.",
            font=ctk.CTkFont(family=FONTS["family"], size=12),
            text_color=COLORS["text_secondary"]
        ).pack(pady=SPACING["md"])
        
        # Display data summary
        self._display_data_summary(body)
    
    def _display_data_summary(self, parent):
        """Display transportation data in fullscreen"""
        try:
            supply = self.supply_input.get_values()
            demand = self.demand_input.get_values()
            costs = self.cost_matrix.get_matrix()
            
            # Supply/Demand summary
            summary_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
            summary_card.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
            
            row1 = ctk.CTkFrame(summary_card, fg_color="transparent")
            row1.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
            
            ctk.CTkLabel(
                row1,
                text=f"🏭 Total Supply: {np.sum(supply):,.0f} units",
                font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(side="left", padx=SPACING["lg"])
            
            ctk.CTkLabel(
                row1,
                text=f"🏗️ Total Demand: {np.sum(demand):,.0f} units",
                font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(side="left", padx=SPACING["lg"])
            
            # Cost matrix
            matrix_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
            matrix_card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
            
            ctk.CTkLabel(
                matrix_card,
                text="💰 Transportation Cost Matrix",
                font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
                text_color=COLORS["text_primary"]
            ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
            
            # Grid frame
            grid_frame = ctk.CTkFrame(matrix_card, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
            
            # Header row
            header_row = ctk.CTkFrame(grid_frame, fg_color=COLORS["primary"])
            header_row.pack(fill="x", pady=2)
            
            ctk.CTkLabel(header_row, text="Source / Dest", width=100, text_color="#FFFFFF", 
                        font=ctk.CTkFont(family=FONTS["family"], size=10, weight="bold")).pack(side="left", padx=2)
            for j in range(min(len(demand), 10)):
                dest = DESTINATIONS[j][:8] if j < len(DESTINATIONS) else f"D{j+1}"
                ctk.CTkLabel(header_row, text=dest, width=70, text_color="#FFFFFF",
                            font=ctk.CTkFont(family=FONTS["family"], size=9)).pack(side="left", padx=2)
            
            # Data rows
            for i in range(min(len(costs), 10)):
                row_frame = ctk.CTkFrame(grid_frame, fg_color=COLORS["background"] if i % 2 == 0 else COLORS["surface"])
                row_frame.pack(fill="x", pady=1)
                
                source = PLANTS[i][:10] if i < len(PLANTS) else f"S{i+1}"
                ctk.CTkLabel(row_frame, text=source, width=100,
                            font=ctk.CTkFont(family=FONTS["family"], size=10, weight="bold"),
                            text_color=COLORS["text_primary"]).pack(side="left", padx=2)
                for j in range(min(len(costs[i]), 10)):
                    ctk.CTkLabel(row_frame, text=f"{costs[i][j]:.0f}", width=70,
                                font=ctk.CTkFont(family=FONTS["family"], size=9),
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
            title="Transportation Results - Fullscreen",
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
        """Display transportation results in fullscreen"""
        result = self.last_result
        
        # Summary card
        summary_card = ctk.CTkFrame(parent, fg_color=COLORS["success"], corner_radius=12)
        summary_card.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            summary_card,
            text=f"✓ Total Transportation Cost: Rs. {result.total_cost:,.2f}",
            font=ctk.CTkFont(family=FONTS["family"], size=24, weight="bold"),
            text_color="#FFFFFF"
        ).pack(padx=SPACING["lg"], pady=SPACING["lg"])
        
        # Shipping routes
        routes_card = ctk.CTkFrame(parent, fg_color=COLORS["surface"], corner_radius=10)
        routes_card.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            routes_card,
            text="🚚 Optimal Shipping Routes",
            font=ctk.CTkFont(family=FONTS["family"], size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=SPACING["sm"])
        
        # List routes
        if hasattr(result, 'route_details') and result.route_details:
            for route in result.route_details[:15]:
                item = ctk.CTkFrame(routes_card, fg_color=COLORS["background"], corner_radius=8)
                item.pack(fill="x", padx=SPACING["md"], pady=3)
                
                source_name = route.get('source', 'Source')
                dest_name = route.get('destination', 'Destination')
                qty = route.get('quantity', 0)
                cost = route.get('cost', 0)
                
                ctk.CTkLabel(
                    item,
                    text=f"🏭 {source_name}",
                    font=ctk.CTkFont(family=FONTS["family"], size=12, weight="bold"),
                    text_color=COLORS["text_primary"]
                ).pack(side="left", padx=SPACING["md"], pady=SPACING["sm"])
                
                ctk.CTkLabel(
                    item,
                    text=f"→ 🏗️ {dest_name}",
                    font=ctk.CTkFont(family=FONTS["family"], size=12),
                    text_color=COLORS["secondary"]
                ).pack(side="left", padx=SPACING["sm"])
                
                ctk.CTkLabel(
                    item,
                    text=f"{qty:,.0f} units",
                    font=ctk.CTkFont(family=FONTS["family"], size=11),
                    text_color=COLORS["text_secondary"]
                ).pack(side="right", padx=SPACING["sm"])
                
                ctk.CTkLabel(
                    item,
                    text=f"Rs. {cost:,.0f}",
                    font=ctk.CTkFont(family=FONTS["family"], size=11, weight="bold"),
                    text_color=COLORS["accent"]
                ).pack(side="right", padx=SPACING["md"])
    
    def _close_results_popup(self):
        """Close results fullscreen popup"""
        if self.results_popup:
            self.results_popup.destroy()
            self.results_popup = None

