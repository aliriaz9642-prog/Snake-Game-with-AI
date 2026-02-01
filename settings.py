import pygame

# SCREEN SETTINGS
WIDTH = 1000
HEIGHT = 700
CELL_SIZE = 25
FPS = 60

# FONTS
# Using default system fonts but we will render them nicely
FONT_MAIN = "Arial"
FONT_BOLD = "Arial Black"

# COLORS (Futuristic Palette)
BG_COLOR = (10, 15, 25)           # Deep Dark Blue
UI_ACCENT = (0, 255, 242)         # Cyan/Neon
UI_SECONDARY = (255, 0, 150)       # Neon Pink
GRID_COLOR = (20, 30, 50)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (70, 80, 90)

# SNAKE COLORS
PLAYER_COLOR = (0, 255, 127)      # Spring Green
PLAYER_TAIL = (0, 100, 50)
AI_COLOR = (255, 69, 0)           # Orange Red
AI_TAIL = (100, 30, 0)
FOOD_COLOR = (255, 215, 0)        # Gold/Yellow
OBSTACLE_COLOR = (150, 150, 150)  # Silver/Gray

# GAME SETTINGS
INITIAL_SPEED = 10  # Higher = Faster (used for ticks per second)
MAX_SPEED = 40
SPEED_INCREMENT = 0.5
AI_SPEED_MULTIPLIER = 0.8  # AI is 80% as fast as player logic
MAX_OBSTACLES = 8
