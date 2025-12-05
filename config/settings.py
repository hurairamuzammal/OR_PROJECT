"""
Application settings and constants for The Best Laboratory Pakistan OR Solver
Developed by: OptimizeX Group
"""

# Application Info
APP_NAME = "The Best Laboratory Pakistan - OR Problem Solver"
APP_VERSION = "1.0.0"
COMPANY_NAME = "The Best Laboratory Pakistan"
GROUP_NAME = "OptimizeX"

# Window Settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MIN_WIDTH = 1280
MIN_HEIGHT = 720

# Theme Colors (Modern Premium Branding - The Best Laboratory Pakistan)
COLORS = {
    # Primary palette - Deep Professional Blue-Purple
    "primary": "#1E3A5F",          # Deep navy blue
    "primary_light": "#2E5077",    # Lighter navy
    "primary_dark": "#152A45",     # Darker navy
    
    # Secondary palette - Elegant Teal
    "secondary": "#00B4D8",        # Vibrant cyan
    "secondary_light": "#48CAE4",  # Light cyan
    
    # Accent colors - Gold/Amber for premium feel
    "accent": "#F59E0B",           # Golden amber
    "accent_light": "#FBBF24",     # Light gold
    "accent_hover": "#D97706",     # Darker gold for hover
    
    # Status colors
    "success": "#10B981",          # Emerald green
    "success_light": "#34D399",    # Light emerald
    "warning": "#F59E0B",          # Amber warning
    "error": "#EF4444",            # Soft red error
    "error_light": "#F87171",      # Light red
    
    # Neutral colors
    "background": "#F0F4F8",       # Soft gray-blue background
    "background_dark": "#0F172A",  # Dark mode background
    "surface": "#FFFFFF",          # White surface
    "surface_dark": "#1E293B",     # Dark mode surface
    "card": "#FFFFFF",             # Card background
    "card_dark": "#334155",        # Dark mode card
    
    # Text colors
    "text_primary": "#0F172A",     # Deep slate
    "text_secondary": "#475569",   # Slate gray
    "text_muted": "#94A3B8",       # Muted text
    "text_light": "#F8FAFC",       # Light text for dark bg
    
    # Border colors
    "border": "#CBD5E1",           # Soft border
    "border_dark": "#475569",      # Dark mode border
    
    # Sidebar colors - Premium gradient feel
    "sidebar_bg": "#1E3A5F",       # Deep navy sidebar
    "sidebar_hover": "#2E5077",    # Sidebar hover
    "sidebar_active": "#3B6998",   # Sidebar active item
    
    # Gradient colors
    "gradient_start": "#1E3A5F",
    "gradient_end": "#00B4D8"
}

# Font settings
FONTS = {
    "family": "Segoe UI",          # Windows default
    "family_mono": "Consolas",     # Monospace for data
    "size_xs": 10,
    "size_sm": 12,
    "size_md": 14,
    "size_lg": 16,
    "size_xl": 20,
    "size_2xl": 24,
    "size_3xl": 32,
    "size_hero": 42
}

# Spacing constants for consistent UI layout
SPACING = {
    "xs": 5,      # Extra small - minimal gaps
    "sm": 10,     # Small - between related elements
    "md": 15,     # Medium - standard section padding
    "lg": 20,     # Large - between major sections
    "xl": 30,     # Extra large - major content areas
    "2xl": 40,    # 2X large - hero sections
    "card_padding": 20,    # Inside card containers
    "section_gap": 25,     # Between section cards
}

# Default Problem Sizes
DEFAULT_LP_VARIABLES = 10
DEFAULT_LP_CONSTRAINTS = 10
DEFAULT_MATRIX_SIZE = 10

# The Best Laboratory Pakistan Product Names (for demo data)
PRODUCTS = [
    "Bitumen Emulsion",
    "Modified Bitumen",
    "Concrete Plasticizer",
    "Curing Compound",
    "Waterproofing Compound",
    "Road Marking Paint",
    "Anti-Strip Agent",
    "Concrete Hardener",
    "Epoxy Coating",
    "Polymer Modified Bitumen"
]

# Worker Names (for assignment demo)
WORKERS = [
    "Ahmed Khan", "Bilal Hussain", "Chaudhry Tariq", "Danish Ali", "Ejaz Ahmed",
    "Farhan Malik", "Ghulam Abbas", "Hassan Raza", "Imran Shah", "Junaid Iqbal"
]

# Task Names (for assignment demo)
TASKS = [
    "Mixing", "Heating", "Testing", "Packing", "Loading",
    "Quality Control", "Maintenance", "Documentation", "Safety Check", "Dispatch"
]

# Plant Names (for transportation demo)
PLANTS = [
    "Karachi Plant", "Lahore Plant", "Islamabad Plant", "Faisalabad Plant",
    "Rawalpindi Plant", "Multan Plant", "Peshawar Plant", "Quetta Plant",
    "Sialkot Plant", "Gujranwala Plant"
]

# Destination Names (for transportation demo)
DESTINATIONS = [
    "M-2 Motorway Project", "Lahore Metro Station", "Attock Bridge Project",
    "Karachi Flyover", "GT Road Widening", "Lowari Tunnel Project",
    "Islamabad Airport", "Gwadar Port Terminal", "Peshawar Railway", "Multan Stadium"
]

# Currency Settings
CURRENCY = {
    "name": "Pakistani Rupee",
    "symbol": "Rs.",
    "code": "PKR"
}

# Constraint Types
CONSTRAINT_TYPES = ["≤", "≥", "="]

# Resource Names (for LP demo)
RESOURCES = [
    "Raw Material A (kg)",
    "Raw Material B (kg)",
    "Production Line 1 (hrs)",
    "Production Line 2 (hrs)",
    "Storage Capacity (tons)",
    "Labor Hours (man-hrs)",
    "Minimum Production (tons)",
    "Quality Control (tests)",
    "Environmental Limit (units)",
    "Energy Consumption (kWh)"
]
