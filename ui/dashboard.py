"""
Main Dashboard View
Home screen with company branding and quick navigation
"""

import customtkinter as ctk
from config.settings import APP_NAME, COMPANY_NAME, COLORS, FONTS


class DashboardView(ctk.CTkFrame):
    """
    Dashboard/Home view with company branding and quick access to problem types
    """
    
    def __init__(self, parent, on_navigate=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_navigate = on_navigate
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dashboard widgets"""
        # Main scrollable container
        main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_scroll.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Hero Header Section
        hero_frame = ctk.CTkFrame(
            main_scroll, 
            fg_color=COLORS["primary"],
            corner_radius=0
        )
        hero_frame.pack(fill="x", padx=0, pady=0)
        
        hero_content = ctk.CTkFrame(hero_frame, fg_color="transparent")
        hero_content.pack(fill="x", padx=50, pady=40)
        
        # Welcome text
        ctk.CTkLabel(
            hero_content,
            text="Welcome to",
            font=ctk.CTkFont(family=FONTS["family"], size=16),
            text_color=COLORS["text_muted"]
        ).pack(anchor="w")
        
        # Company name with gradient effect simulation
        title_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
        title_frame.pack(anchor="w", pady=(5, 0))
        
        ctk.CTkLabel(
            title_frame,
            text="PP CHEMICALS",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_hero"], weight="bold"),
            text_color="#FFFFFF"
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text="  ®",
            font=ctk.CTkFont(family=FONTS["family"], size=16),
            text_color=COLORS["accent"]
        ).pack(side="left", anchor="n", pady=(5, 0))
        
        ctk.CTkLabel(
            hero_content,
            text="Operations Research Decision Support System",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_lg"]),
            text_color=COLORS["secondary_light"]
        ).pack(anchor="w", pady=(10, 0))
        
        # Accent bar
        accent_bar = ctk.CTkFrame(
            hero_content,
            height=4,
            width=100,
            fg_color=COLORS["accent"],
            corner_radius=2
        )
        accent_bar.pack(anchor="w", pady=(20, 0))
        
        # Stats row
        stats_frame = ctk.CTkFrame(hero_content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(25, 0))
        
        stats = [
            ("3", "Solver Types"),
            ("10+", "Variables"),
            ("10×10+", "Matrix Size"),
            ("Rs.", "PKR Currency")
        ]
        
        for value, label in stats:
            stat_item = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_item.pack(side="left", padx=(0, 50))
            
            ctk.CTkLabel(
                stat_item,
                text=value,
                font=ctk.CTkFont(family=FONTS["family"], size=28, weight="bold"),
                text_color=COLORS["accent"]
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                stat_item,
                text=label,
                font=ctk.CTkFont(family=FONTS["family"], size=12),
                text_color=COLORS["text_muted"]
            ).pack(anchor="w")
        
        # Content section
        content_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=50, pady=30)
        
        # Section title
        section_header = ctk.CTkFrame(content_frame, fg_color="transparent")
        section_header.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_header,
            text="Choose a Problem Type",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xl"], weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            section_header,
            text="Select an optimization method to get started",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_secondary"]
        ).pack(side="right", pady=(8, 0))
        
        # Problem type cards
        cards_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True)
        
        # Configure grid for 3 columns
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="card")
        cards_frame.rowconfigure(0, weight=1)
        
        # Simplex card
        self._create_card(
            cards_frame,
            title="Linear Programming",
            subtitle="Simplex Method",
            description="Optimize production planning with multiple products and "
                       "resource constraints. Maximize profit or minimize costs "
                       "with full sensitivity analysis.",
            icon="📊",
            features=[
                ("10+ decision variables", COLORS["success"]),
                ("10+ constraints supported", COLORS["success"]),
                ("Shadow prices analysis", COLORS["secondary"]),
                ("Reduced costs report", COLORS["secondary"])
            ],
            color=COLORS["primary"],
            gradient_color=COLORS["primary_light"],
            command=lambda: self._navigate("simplex"),
            row=0, col=0
        )
        
        # Assignment card
        self._create_card(
            cards_frame,
            title="Assignment Problem",
            subtitle="Hungarian Algorithm",
            description="Optimally assign workers to tasks based on skills, "
                       "efficiency ratings, or costs. Find the perfect one-to-one "
                       "matching for maximum productivity.",
            icon="👥",
            features=[
                ("10×10+ assignment matrix", COLORS["success"]),
                ("Maximize or minimize", COLORS["success"]),
                ("Visual assignment grid", COLORS["secondary"]),
                ("Detailed cost breakdown", COLORS["secondary"])
            ],
            color=COLORS["secondary"],
            gradient_color=COLORS["secondary_light"],
            command=lambda: self._navigate("assignment"),
            row=0, col=1
        )
        
        # Transportation card
        self._create_card(
            cards_frame,
            title="Transportation",
            subtitle="VAM + MODI Method",
            description="Plan cost-effective distribution from plants to "
                       "construction sites. Minimize shipping costs while "
                       "meeting supply and demand requirements.",
            icon="🚚",
            features=[
                ("10+ sources/destinations", COLORS["success"]),
                ("VAM initial solution", COLORS["success"]),
                ("MODI optimization", COLORS["secondary"]),
                ("Route cost details", COLORS["secondary"])
            ],
            color=COLORS["accent"],
            gradient_color=COLORS["accent_light"],
            command=lambda: self._navigate("transportation"),
            row=0, col=2
        )
        
        # Footer
        footer_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        footer_frame.pack(fill="x", padx=50, pady=(10, 30))
        
        # Divider
        ctk.CTkFrame(
            footer_frame,
            height=1,
            fg_color=COLORS["border"]
        ).pack(fill="x", pady=(0, 15))
        
        footer_content = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_content.pack(fill="x")
        
        ctk.CTkLabel(
            footer_content,
            text="🏭 PP Chemicals - Manufacturing Excellence for Roads & Buildings",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_secondary"]
        ).pack(side="left")
        
        ctk.CTkLabel(
            footer_content,
            text="Made in Pakistan 🇵🇰",
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_muted"]
        ).pack(side="right")
    
    def _create_card(
        self,
        parent,
        title: str,
        subtitle: str,
        description: str,
        icon: str,
        features: list,
        color: str,
        gradient_color: str,
        command,
        row: int,
        col: int
    ):
        """Create a modern problem type card"""
        # Card container with shadow effect
        card = ctk.CTkFrame(
            parent, 
            corner_radius=16,
            fg_color=COLORS["surface"],
            border_width=1,
            border_color=COLORS["border"]
        )
        card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
        
        # Top accent gradient bar
        accent = ctk.CTkFrame(
            card, 
            height=6, 
            fg_color=color, 
            corner_radius=3
        )
        accent.pack(fill="x", padx=20, pady=(20, 0))
        
        # Icon with background
        icon_container = ctk.CTkFrame(card, fg_color="transparent")
        icon_container.pack(pady=(20, 15))
        
        icon_bg = ctk.CTkFrame(
            icon_container,
            width=70,
            height=70,
            corner_radius=20,
            fg_color=color
        )
        icon_bg.pack()
        icon_bg.pack_propagate(False)
        
        ctk.CTkLabel(
            icon_bg,
            text=icon,
            font=ctk.CTkFont(size=32),
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_xl"], weight="bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=(5, 0))
        
        # Subtitle badge
        subtitle_frame = ctk.CTkFrame(
            card,
            fg_color=gradient_color,
            corner_radius=12
        )
        subtitle_frame.pack(pady=(8, 15))
        
        ctk.CTkLabel(
            subtitle_frame,
            text=f"  {subtitle}  ",
            font=ctk.CTkFont(family=FONTS["family"], size=11, weight="bold"),
            text_color="#FFFFFF"
        ).pack(padx=12, pady=4)
        
        # Description
        ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(family=FONTS["family"], size=FONTS["size_sm"]),
            text_color=COLORS["text_secondary"],
            wraplength=260,
            justify="center"
        ).pack(padx=20, pady=(0, 15))
        
        # Features list with colored checkmarks
        features_frame = ctk.CTkFrame(card, fg_color=COLORS["background"])
        features_frame.pack(fill="x", padx=15, pady=10)
        
        for feature_text, feature_color in features:
            feature_row = ctk.CTkFrame(features_frame, fg_color="transparent")
            feature_row.pack(fill="x", padx=15, pady=4)
            
            ctk.CTkLabel(
                feature_row,
                text="✓",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=feature_color,
                width=20
            ).pack(side="left")
            
            ctk.CTkLabel(
                feature_row,
                text=feature_text,
                font=ctk.CTkFont(family=FONTS["family"], size=12),
                text_color=COLORS["text_primary"],
                anchor="w"
            ).pack(side="left", padx=(5, 0))
        
        # Action button
        btn = ctk.CTkButton(
            card,
            text="Open Solver  →",
            command=command,
            font=ctk.CTkFont(family=FONTS["family"], size=14, weight="bold"),
            fg_color=color,
            hover_color=self._darken_color(color),
            height=45,
            corner_radius=10
        )
        btn.pack(fill="x", padx=20, pady=(15, 25))
    
    def _navigate(self, view_name: str):
        """Navigate to a view"""
        if self.on_navigate:
            self.on_navigate(view_name)
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color by 15%"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darker = tuple(max(0, int(c * 0.85)) for c in rgb)
        return f"#{darker[0]:02x}{darker[1]:02x}{darker[2]:02x}"
