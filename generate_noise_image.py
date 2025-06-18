import pygame
import random
import math # Needed for mouse aiming calculations
import numpy as np # Needed for procedural audio generation
from perlin_noise import PerlinNoise # For smooth procedural generation

# --- Game Constants ---wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

DEATH_BONUS = 50  # Points awarded when player dies

# Colors (RGB) - Defined as top-level constants now for use in default args
WHITE = (255, 255, 255)
BLACK = (0, 0, 0) # Used for text accents, enemy eyes etc.
RED = (255, 0, 0) # Standard red color for errors and accents

# Base colors for themes (used to define COLOR_THEMES)
DEFAULT_BLUE_PLAYER = (0, 0, 200)
DEFAULT_RED_ENEMY_LASER = (255, 0, 0)
DEFAULT_GREEN_PLATFORM = (0, 100, 0)
DEFAULT_YELLOW_ROLLING = (255, 255, 0)
DEFAULT_ORANGE_FLYING = (255, 165, 0)
DEFAULT_PURPLE_JUMPING = (128, 0, 128)
DEFAULT_LIGHT_BLUE_SKY = (173, 216, 230)
DEFAULT_DARK_ACCENT = (50, 50, 50)
DEFAULT_MENU_BG = (40, 40, 40)
DEFAULT_MENU_TEXT = (255, 255, 255) # Refers to WHITE now
DEFAULT_MENU_BTN_START = (0, 150, 0)
DEFAULT_MENU_BTN_TUTORIAL = (200, 200, 0)
DEFAULT_MENU_BTN_INFO = (100, 0, 100)
DEFAULT_MENU_BTN_QUIT = (150, 0, 0)

# Color Themes - Define distinct sets of colors
COLOR_THEMES = [
    { # Default Theme
        "PLAYER": DEFAULT_BLUE_PLAYER,
        "LASER": DEFAULT_RED_ENEMY_LASER,
        "PLATFORM": DEFAULT_GREEN_PLATFORM,
        "WALL": (80, 80, 80), # Grey
        "ENEMY_STANDARD": DEFAULT_RED_ENEMY_LASER,
        "ENEMY_FLYING": DEFAULT_ORANGE_FLYING,
        "ENEMY_ROLLING": DEFAULT_YELLOW_ROLLING,
        "ENEMY_JUMPING": DEFAULT_PURPLE_JUMPING,
        "SKY": DEFAULT_LIGHT_BLUE_SKY,
        "DARK_ACCENT": DEFAULT_DARK_ACCENT,
        "MENU_BG": DEFAULT_MENU_BG,
        "MENU_TEXT": DEFAULT_MENU_TEXT,
        "MENU_START_BTN": DEFAULT_MENU_BTN_START,
        "MENU_TUTORIAL_BTN": DEFAULT_MENU_BTN_TUTORIAL,
        "MENU_INFO_BTN": DEFAULT_MENU_BTN_INFO,
        "MENU_QUIT_BTN": DEFAULT_MENU_BTN_QUIT,
        "MENU_HOVER_FILL": (80, 80, 80), # Light grey fill on hover
        "MENU_CLICK_FLASH": (255, 255, 255), # White flash on click
    },
    { # Desert Theme
        "PLAYER": (150, 75, 0), "LASER": (255, 200, 0), "PLATFORM": (210, 180, 140),
        "WALL": (160, 120, 80), "ENEMY_STANDARD": (180, 50, 0), "ENEMY_FLYING": (100, 150, 0),
        "ENEMY_ROLLING": (80, 80, 0), "ENEMY_JUMPING": (100, 50, 0), "SKY": (255, 220, 150),
        "DARK_ACCENT": (100, 70, 40), "MENU_BG": (60, 50, 30), "MENU_TEXT": (255, 255, 200),
        "MENU_START_BTN": (150, 100, 50), "MENU_TUTORIAL_BTN": (200, 150, 50), "MENU_INFO_BTN": (100, 50, 0),
        "MENU_QUIT_BTN": (150, 75, 0), "MENU_HOVER_FILL": (120, 90, 60), "MENU_CLICK_FLASH": (255, 255, 255),
    },
    { # Forest Night Theme
        "PLAYER": (100, 200, 255), "LASER": (0, 255, 255), "PLATFORM": (0, 50, 0),
        "WALL": (30, 30, 60), "ENEMY_STANDARD": (50, 100, 50), "ENEMY_FLYING": (100, 50, 150),
        "ENEMY_ROLLING": (80, 0, 0), "ENEMY_JUMPING": (0, 100, 100), "SKY": (20, 20, 40),
        "DARK_ACCENT": (10, 10, 20), "MENU_BG": (15, 15, 30), "MENU_TEXT": (200, 255, 200),
        "MENU_START_BTN": (0, 100, 0), "MENU_TUTORIAL_BTN": (0, 100, 100), "MENU_INFO_BTN": (50, 0, 50),
        "MENU_QUIT_BTN": (100, 0, 0), "MENU_HOVER_FILL": (40, 40, 80), "MENU_CLICK_FLASH": (255, 255, 255),
    }
]
current_theme_index = 0
COLORS = COLOR_THEMES[current_theme_index] # Initialize with default theme

# Player properties
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_STRENGTH = -15 # Negative for upward movement
GRAVITY = 0.8
WALL_SLIDE_SPEED = 0.2 * GRAVITY # Slower fall when wall sliding
WALL_JUMP_HORIZONTAL_PUSH = 8 # Horizontal push off wall
WALL_JUMP_VERTICAL_PUSH = -12 # Vertical push off wall
PLAYER_COLOR = None # Dynamically set from COLORS

# Laser properties
LASER_WIDTH = 20
LASER_HEIGHT = 5
LASER_SPEED_MAGNITUDE = 15 # Consistent speed for lasers
LASER_COLOR = None # Dynamically set from COLORS
PLAYER_LASER_DAMAGE = 20

# Enemy properties
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_SPEED = 2
ENEMY_HEALTH_DEFAULT = 50
ENEMY_CONTACT_DAMAGE = 10

# Platform properties
PLATFORM_HEIGHT = 20
PLATFORM_MIN_WIDTH = 80
PLATFORM_MAX_WIDTH = 200
PLATFORM_MIN_GAP = 80  # Minimum horizontal gap between platforms
PLATFORM_MAX_GAP = 200 # Maximum horizontal gap for a jumpable distance
PLATFORM_MAX_Y_DIFF = 80 # Maximum vertical difference between platforms
PLATFORM_COLOR = None # Dynamically set from COLORS

# Wall properties (new)
WALL_WIDTH = 20
WALL_MIN_HEIGHT = 100
WALL_MAX_HEIGHT = 250
WALL_COLOR = None # Dynamically set from COLORS

# Difficulty scaling (score thresholds)
DIFFICULTY_TIERS = [
    {"score": 0, "enemy_speed_mult": 1.0, "enemy_spawn_chance": 0.2, "platform_gap_mult": 1.0},
    {"score": 200, "enemy_speed_mult": 1.2, "enemy_spawn_chance": 0.25, "platform_gap_mult": 1.1},
    {"score": 500, "enemy_speed_mult": 1.4, "enemy_spawn_chance": 0.3, "platform_gap_mult": 1.2},
    {"score": 1000, "enemy_speed_mult": 1.6, "enemy_spawn_chance": 0.35, "platform_gap_mult": 1.3},
    {"score": 2000, "enemy_speed_mult": 1.8, "enemy_spawn_chance": 0.4, "platform_gap_mult": 1.4},
]

# Noise properties for procedural generation
NOISE_SCALE = 100.0  # Controls the "zoom" of the terrain features
OCTAVES = 6          # Number of noise layers for detail
NOISE_X_OFFSET_BASE = 0 # Base offset for noise, will be randomized per map
NOISE_Y_OFFSET_BASE = 0

# --- Global Game Variables ---
platforms = []
walls = [] # New list for wall objects
enemies = []
lasers = []
player_pos = [SCREEN_WIDTH // 4, 0] # Player's screen X is now largely fixed
player_vel_y = 0
is_jumping = False
score = 0
health = 100
game_over = False
camera_x_offset = 0 # Camera offset for scrolling the world
perlin_gen = None # Perlin noise generator instance
current_map_seed = None # For reproducible maps

# Game States
MENU = 0
PLAYING = 1
GAME_OVER_STATE = 2
TUTORIAL = 3 
GENERATION_INFO = 4 
game_state = MENU # Initial game state

# Global variables for menu button rects, initialized to None
start_button_rect = None
quit_button_rect = None
tutorial_button_rect = None
game_info_button_rect = None
tutorial_back_button_rect = None


# --- Helper Functions ---

def clamp(value, min_val, max_val):
    """Clamps a value between a minimum and maximum."""
    return max(min_val, min(value, max_val))

def check_collision(rect1, rect2):
    """Checks for AABB collision between two Pygame Rects."""
    return rect1.colliderect(rect2)

def draw_text(surface, text, size, x, y, color=WHITE, anchor='topleft'):
    """Draws text on a surface with optional anchoring."""
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if anchor == 'center':
        text_rect.center = (x, y)
    elif anchor == 'topleft':
        text_rect.topleft = (x, y)
    elif anchor == 'topright':
        text_rect.topright = (x, y)
    surface.blit(text_surface, text_rect)
    return text_rect # Return rect for clickable buttons

def update_colors_from_theme():
    """Updates global color constants based on the current theme index."""
    global COLORS, PLAYER_COLOR, LASER_COLOR, PLATFORM_COLOR, WALL_COLOR
    COLORS = COLOR_THEMES[current_theme_index]
    PLAYER_COLOR = COLORS["PLAYER"]
    LASER_COLOR = COLORS["LASER"]
    PLATFORM_COLOR = COLORS["PLATFORM"]
    WALL_COLOR = COLORS["WALL"]

# Map raw color tuples to human‐readable names for tutorial/info screens
COLOR_TO_NAME = {
    DEFAULT_BLUE_PLAYER:      "Blue",
    DEFAULT_RED_ENEMY_LASER:  "Red",
    DEFAULT_GREEN_PLATFORM:   "Green",
    DEFAULT_YELLOW_ROLLING:   "Yellow",
    DEFAULT_ORANGE_FLYING:    "Orange",
    DEFAULT_PURPLE_JUMPING:   "Purple",
    (80, 80, 80):             "Dark Grey",  # walls
    WHITE:                    "White",
    BLACK:                    "Black",
    DEFAULT_LIGHT_BLUE_SKY:   "Light Blue"
}

# --- Music Functions (Simple Procedural Melody) ---
# _BUFFER_SIZE = 1024 # Number of samples in buffer (removed as unused)
# _BUFFER_SIZE removed as unused

# Define the sample rate for audio generation
_SAMPLE_RATE = 44100  # Standard CD-quality sample rate

MUSIC_NOTES_FREQ = { # Frequencies for a simple C Major scale (approximate)
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
    'E5': 659.25, 'G5': 783.99,
    'REST': 0 # For silence
}
MUSIC_BEAT_LENGTH = 0.25 # Seconds per note (faster tempo)
music_sequence_freq = []
music_timer = 0
current_music_note_idx = 0
current_sound_obj = None

def generate_random_melody(length_beats=40): # Longer melody
    """Generates a sequence of random frequencies (notes) for the melody."""
    global music_sequence_freq, current_music_note_idx
    notes_freq_list = list(MUSIC_NOTES_FREQ.values())
    # Add rests to make it a bit more musical
    music_sequence_freq = [random.choice(notes_freq_list + [MUSIC_NOTES_FREQ['REST']]*2) for _ in range(length_beats)]
    current_music_note_idx = 0
    print(f"Generated a new melody sequence of {length_beats} notes.")

def play_tone(frequency, duration_ms, volume=0.1):
    """Generates and plays a sine wave tone using Pygame sndarray."""
    if frequency == 0: # Represent silence
        return None # Return None for no sound object

    num_samples = int(duration_ms * _SAMPLE_RATE / 1000)
    # FIX: Create a 2D array with 2 channels for stereo, and fill both with the same mono data.
    # This robustly handles Pygame's sndarray.make_sound expecting a 2D array, even if the mixer
    # was configured for mono, due to underlying SDL behavior.
    arr = np.zeros((num_samples, 2), dtype=np.int16) # Corrected shape to (num_samples, 2) for stereo

    # Generate sine wave and fill both channels
    amplitude = 32767 * volume # Max amplitude for int16, scaled by volume
    for i in range(num_samples):
        sample_val = int(amplitude * math.sin(2 * math.pi * frequency * i / _SAMPLE_RATE))
        arr[i, 0] = sample_val # Left channel
        arr[i, 1] = sample_val # Right channel (duplicate for stereo effect from mono source)
    
    # Create Pygame sound object from numpy array (now 2D with 2 channels)
    sound = pygame.sndarray.make_sound(arr)
    sound.play(loops=0) # Play once
    return sound

def handle_music_playback(dt):
    """Manages the playing of the random melody over time."""
    global music_timer, current_music_note_idx, current_sound_obj

    if not music_sequence_freq:
        return

    music_timer += dt # Add delta time since last frame (in ms)

    if music_timer >= MUSIC_BEAT_LENGTH * 1000: # If enough time for a note (in ms)
        music_timer = 0 # Reset timer

        if current_sound_obj: # Stop previous note if it's still playing (unlikely with short notes)
            current_sound_obj.stop()

        # Play current note
        freq = music_sequence_freq[current_music_note_idx]
        current_sound_obj = play_tone(freq, int(MUSIC_BEAT_LENGTH * 1000 * 0.8)) # Play for 80% of beat length

        current_music_note_idx += 1
        if current_music_note_idx >= len(music_sequence_freq):
            current_music_note_idx = 0 # Loop the melody
            generate_random_melody() # Generate a new melody after current one finishes


def stop_all_music():
    """Stops any currently playing music."""
    # This will stop all sounds, including any active notes
    pygame.mixer.stop() 


# --- Procedural Generation Functions ---

def generate_platforms_and_walls(): # Renamed to include walls
    """
    Generates playable platforms and walls using Perlin noise for vertical variation.
    The goal is to ensure platforms are jumpable and walls usable.
    """
    global platforms, walls, NOISE_X_OFFSET_BASE, NOISE_Y_OFFSET_BASE, perlin_gen, current_map_seed

    platforms = []
    walls = [] # Clear walls for new generation
    
    # Ensure a random seed is used for Perlin noise every time generate_platforms is called
    if current_map_seed is None: 
        current_map_seed = random.randint(0, 1000000)
    
    # Initialize Perlin noise generator with the current_map_seed
    perlin_gen = PerlinNoise(octaves=OCTAVES, seed=current_map_seed)

    # Use unique offsets for each map based on its seed, for visual variety
    NOISE_X_OFFSET_BASE = random.uniform(0, 1000)
    NOISE_Y_OFFSET_BASE = random.uniform(0, 1000)


    # Start with a base platform at the beginning, ensuring player can land on it
    platforms.append(pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH / 2, PLATFORM_HEIGHT))
    
    # Track the last platform's right edge for generating the next one
    last_platform_right = platforms[0].right
    last_platform_y = platforms[0].y

    # Generate platforms across a wider range than the screen to allow for scrolling
    generation_end_x = SCREEN_WIDTH * 5 # Generate platforms for 5 screens worth

    while last_platform_right < generation_end_x:
        # Calculate next platform's Y based on noise for smooth terrain
        noise_val_y = perlin_gen([(last_platform_right + NOISE_X_OFFSET_BASE) / (NOISE_SCALE * 2), (NOISE_Y_OFFSET_BASE) / (NOISE_SCALE * 2)])
        
        # Map noise value to a vertical difference, scaled by difficulty
        current_difficulty = get_current_difficulty_tier()
        platform_y_diff_mult = current_difficulty["platform_gap_mult"]

        y_diff = int(noise_val_y * PLATFORM_MAX_Y_DIFF * 2 * platform_y_diff_mult) - PLATFORM_MAX_Y_DIFF # Maps noise to -MAX to +MAX

        next_platform_y = last_platform_y + y_diff
        
        # Clamp Y position to keep platforms within a reasonable height range
        min_allowed_y = SCREEN_HEIGHT * 0.4 # Platforms can go a bit higher now
        max_allowed_y = SCREEN_HEIGHT - PLATFORM_HEIGHT - 50 
        next_platform_y = clamp(next_platform_y, min_allowed_y, max_allowed_y)

        # Calculate gap and width
        gap = random.randint(int(PLATFORM_MIN_GAP * platform_y_diff_mult), int(PLATFORM_MAX_GAP * platform_y_diff_mult))
        platform_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)

        next_platform_x = last_platform_right + gap
        
        # Create the new platform
        new_platform = pygame.Rect(next_platform_x, next_platform_y, platform_width, PLATFORM_HEIGHT)
        platforms.append(new_platform)

        # Randomly generate a wall attached to this platform
        if random.random() < 0.3: # 30% chance for a wall
            wall_height = random.randint(WALL_MIN_HEIGHT, WALL_MAX_HEIGHT)
            wall_x = new_platform.left if random.random() < 0.5 else new_platform.right - WALL_WIDTH # Left or right side
            
            # Wall extends upwards from platform or downwards to ground if needed
            wall_y = new_platform.top - wall_height if random.random() < 0.7 else new_platform.top # Mostly upwards
            
            # Clamp wall Y to stay on screen
            wall_y = clamp(wall_y, 0, new_platform.top - WALL_WIDTH) # Max Y is top of platform minus wall width (small buffer)
            
            walls.append(pygame.Rect(wall_x, wall_y, WALL_WIDTH, wall_height))


        last_platform_right = new_platform.right
        last_platform_y = new_platform.y
    
    print(f"Generated {len(platforms)} platforms and {len(walls)} walls.")


def spawn_enemies():
    """Spawns enemies on platforms or in the air, with difficulty scaling."""
    global enemies
    enemies = []

    enemy_types = ['standard', 'flying', 'rolling', 'jumping'] 

    current_difficulty = get_current_difficulty_tier()
    enemy_speed_mult = current_difficulty["enemy_speed_mult"]
    enemy_spawn_chance = current_difficulty["enemy_spawn_chance"]

    # Spread enemies across the generated platforms
    for i in range(1, len(platforms)): 
        if random.random() < enemy_spawn_chance: # Spawn chance from difficulty
            platform = platforms[i]
            if platform.width < ENEMY_WIDTH:
                continue 

            enemy_type = random.choice(enemy_types)
            enemy_x = platform.x + random.randint(0, platform.width - ENEMY_WIDTH)
            enemy_y = platform.y - ENEMY_HEIGHT
            
            new_enemy = {
                'id': f"e_{i}_{random.randint(0,999)}", 
                'type': enemy_type,
                'rect': pygame.Rect(enemy_x, enemy_y, ENEMY_WIDTH, ENEMY_HEIGHT),
                'vx': ENEMY_SPEED * (1 if random.random() > 0.5 else -1) * enemy_speed_mult, # Speed scaled
                'vy': 0,
                'health': ENEMY_HEALTH_DEFAULT,
                'color': RED, 
            }

            if enemy_type == 'standard': 
                new_enemy['color'] = COLORS["ENEMY_STANDARD"]
                new_enemy['vx'] = 0 
            elif enemy_type == 'flying':
                new_enemy['rect'].y = random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT // 2) 
                new_enemy['vx'] = ENEMY_SPEED * 1.5 * enemy_speed_mult # Faster flying, scaled
                new_enemy['color'] = COLORS["ENEMY_FLYING"]
            elif enemy_type == 'rolling':
                new_enemy['color'] = COLORS["ENEMY_ROLLING"]
                new_enemy['walk_start_x'] = platform.x 
                new_enemy['walk_end_x'] = platform.x + platform.width - ENEMY_WIDTH
            elif enemy_type == 'jumping':
                new_enemy['color'] = COLORS["ENEMY_JUMPING"]
                new_enemy['jump_cooldown'] = random.randint(90, 180) 
                new_enemy['current_jump_cooldown'] = new_enemy['jump_cooldown']
                new_enemy['is_jumping'] = False

            enemies.append(new_enemy)
    print(f"Spawned {len(enemies)} enemies.")

def get_current_difficulty_tier():
    """Determines the current difficulty tier based on the score."""
    for i in range(len(DIFFICULTY_TIERS) - 1, -1, -1): # Iterate backwards
        if score >= DIFFICULTY_TIERS[i]["score"]:
            return DIFFICULTY_TIERS[i]
    return DIFFICULTY_TIERS[0] # Fallback to easiest

# --- Drawing Functions for Characters ---
def draw_player(surface, rect, color):
    # Body (main rectangle)
    pygame.draw.rect(surface, color, rect)
    
    # Head (ellipse)
    head_size = rect.width * 0.8
    head_x = rect.centerx - head_size / 2
    head_y = rect.top - head_size * 0.7
    pygame.draw.ellipse(surface, (color[0]*0.8, color[1]*0.8, color[2]*0.8), 
                        (head_x, head_y, head_size, head_size * 0.8))
    
    # Eyes (small white circles with black pupils)
    eye_radius = rect.width * 0.1
    left_eye_center = (int(rect.centerx - rect.width * 0.2), int(rect.top - head_size * 0.4))
    right_eye_center = (int(rect.centerx + rect.width * 0.2), int(rect.top - head_size * 0.4))
    
    pygame.draw.circle(surface, WHITE, left_eye_center, int(eye_radius))
    pygame.draw.circle(surface, BLACK, left_eye_center, int(eye_radius * 0.5)) # Pupil
    pygame.draw.circle(surface, WHITE, right_eye_center, int(eye_radius))
    pygame.draw.circle(surface, BLACK, right_eye_center, int(eye_radius * 0.5)) # Pupil

    # Arms (simple rectangles, slightly offset from body)
    arm_width = rect.width * 0.2
    arm_height = rect.height * 0.6
    arm_color = (color[0]*0.9, color[1]*0.9, color[2]*0.9)
    pygame.draw.rect(surface, arm_color, (rect.left - arm_width + 2, rect.top + rect.height * 0.1, arm_width, arm_height))
    pygame.draw.rect(surface, arm_color, (rect.right - 2, rect.top + rect.height * 0.1, arm_width, arm_height))

    # Legs (simple rectangles)
    leg_width = rect.width * 0.3
    leg_height = rect.height * 0.4
    leg_color = (color[0]*0.7, color[1]*0.7, color[2]*0.7)
    pygame.draw.rect(surface, leg_color, (rect.left + rect.width*0.1, rect.bottom - leg_height, leg_width, leg_height))
    pygame.draw.rect(surface, leg_color, (rect.right - rect.width*0.1 - leg_width, rect.bottom - leg_height, leg_width, leg_height))


def draw_enemy_standard(surface, rect, color):
    # Base block
    pygame.draw.rect(surface, color, rect)
    # Simple "angry" eyes
    pygame.draw.rect(surface, BLACK, (rect.left + rect.width*0.2, rect.top + rect.height*0.3, rect.width*0.2, rect.height*0.2))
    pygame.draw.rect(surface, BLACK, (rect.right - rect.width*0.4, rect.top + rect.height*0.3, rect.width*0.2, rect.height*0.2))
    # Mouth
    pygame.draw.line(surface, BLACK, (rect.left + rect.width*0.2, rect.bottom - rect.height*0.3), (rect.right - rect.width*0.2, rect.bottom - rect.height*0.3), 2)


def draw_enemy_flying(surface, rect, color):
    # Body (ellipse)
    pygame.draw.ellipse(surface, color, rect)
    # Wings (simple triangles slightly translucent)
    wing_color = (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)) # No alpha for direct drawing
    
    # Create surfaces for translucent wings if desired (more complex)
    # For simplicity with direct drawing, just use the calculated color.
    
    # Left wing
    wing_points_left = [
        rect.topleft, 
        (rect.left - rect.width * 0.8, rect.centery), 
        (rect.left, rect.bottom)
    ]
    pygame.draw.polygon(surface, wing_color, wing_points_left)
    
    # Right wing
    wing_points_right = [
        rect.topright, 
        (rect.right + rect.width * 0.8, rect.centery), 
        (rect.right, rect.bottom)
    ]
    pygame.draw.polygon(surface, wing_color, wing_points_right)

    # Small eyes
    pygame.draw.circle(surface, BLACK, (rect.centerx - rect.width*0.2, rect.centery - rect.height*0.1), int(rect.width*0.08))
    pygame.draw.circle(surface, BLACK, (rect.centerx + rect.width*0.2, rect.centery - rect.height*0.1), int(rect.width*0.08))

def draw_enemy_rolling(surface, rect, color):
    # Circle body
    pygame.draw.circle(surface, color, rect.center, rect.width // 2)
    # Spikes (simple lines radiating from center)
    for i in range(12): # More spikes
        angle = i * (2 * math.pi / 12) # Divide full circle by 12
        x1 = rect.centerx + (rect.width // 2) * math.cos(angle)
        y1 = rect.centery + (rect.width // 2) * math.sin(angle)
        x2 = rect.centerx + (rect.width // 2 + 10) * math.cos(angle)
        y2 = rect.centery + (rect.width // 2 + 10) * math.sin(angle)
        pygame.draw.line(surface, BLACK, (x1,y1), (x2,y2), 2)
    # Small eyes
    pygame.draw.circle(surface, BLACK, (rect.centerx - int(rect.width*0.15), rect.centery - int(rect.height*0.15)), int(rect.width*0.07))
    pygame.draw.circle(surface, BLACK, (rect.centerx + int(rect.width*0.15), rect.centery - int(rect.height*0.15)), int(rect.width*0.07))


def draw_enemy_jumping(surface, rect, color):
    # Slime-like blob body (more pronounced top)
    blob_points = [
        rect.bottomleft,
        rect.bottomright,
        (rect.right, rect.centery + rect.height * 0.2),
        (rect.centerx + rect.width * 0.4, rect.top + rect.height * 0.1),
        (rect.centerx, rect.top - rect.height * 0.1), # Higher peak
        (rect.centerx - rect.width * 0.4, rect.top + rect.height * 0.1),
        (rect.left, rect.centery + rect.height * 0.2)
    ]
    pygame.draw.polygon(surface, color, blob_points)
    
    # Big eye
    pygame.draw.circle(surface, BLACK, rect.center, int(rect.width * 0.25))
    pygame.draw.circle(surface, WHITE, (rect.centerx + int(rect.width * 0.08), rect.centery - int(rect.height * 0.08)), int(rect.width * 0.08)) # Highlight


# --- Game Loop ---
def game_loop():
    # Declare global variables that will be modified in this function
    global player_pos, player_vel_y, is_jumping, score, health, game_over, camera_x_offset, current_map_seed, lasers, enemies, game_state, clock
    global start_button_rect, quit_button_rect, tutorial_button_rect, game_info_button_rect, tutorial_back_button_rect # Declare global for menu button rects
    global current_theme_index # For color cycling
    
    dt = clock.get_time() # Time since last frame in milliseconds

    # Ensure on_ground is always defined before use
    on_ground = False

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop_all_music() # Stop music before quitting
            return False # Exit game loop

        if event.type == pygame.KEYDOWN:
            if game_state == PLAYING:
                # Wall Jump Logic: Check before standard jump
                # Player must be pressing against a wall AND in the air (not on ground)
                # and trying to jump.
                keys_pressed_current_frame = pygame.key.get_pressed() # Get current frame's key state
                player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

                # Check player's sides against ALL walls and platforms (as potential vertical surfaces)
                wall_left_contact = False
                wall_right_contact = False
                # Combine platforms and walls for wall detection
                all_vertical_surfaces = []
                for p in platforms:
                    adjusted_p_rect = p.move(-camera_x_offset, 0)
                    # Exclude the top surface of platforms from being considered "walls"
                    # Only consider sides of platforms that are taller than the player as walls
                    if adjusted_p_rect.height > PLAYER_HEIGHT: # Or check if player is NOT above it
                        all_vertical_surfaces.append(adjusted_p_rect)
                for w in walls:
                    all_vertical_surfaces.append(w.move(-camera_x_offset, 0))

                for obj_rect in all_vertical_surfaces:
                    # Create thin collision rects for player sides
                    player_left_detector = pygame.Rect(player_rect.left - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)
                    player_right_detector = pygame.Rect(player_rect.right - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)

                    if player_left_detector.colliderect(obj_rect):
                        wall_left_contact = True
                    if player_right_detector.colliderect(obj_rect):
                        wall_right_contact = True
                
                # If attempting to jump while contacting a wall and not on ground
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not on_ground:
                    if wall_left_contact and (keys_pressed_current_frame[pygame.K_RIGHT] or keys_pressed_current_frame[pygame.K_d]):
                        player_vel_y = WALL_JUMP_VERTICAL_PUSH
                        player_pos[0] += WALL_JUMP_HORIZONTAL_PUSH # Push away from left wall
                        is_jumping = True
                        play_tone(MUSIC_NOTES_FREQ['C5'] * 1.5, 70, 0.2) # Wall jump sound
                    elif wall_right_contact and (keys_pressed_current_frame[pygame.K_LEFT] or keys_pressed_current_frame[pygame.K_a]):
                        player_vel_y = WALL_JUMP_VERTICAL_PUSH
                        player_pos[0] -= WALL_JUMP_HORIZONTAL_PUSH # Push away from right wall
                        is_jumping = True
                        play_tone(MUSIC_NOTES_FREQ['C5'] * 1.5, 70, 0.2) # Wall jump sound
                    elif not is_jumping: # Standard jump if not wall jumping
                        player_vel_y = JUMP_STRENGTH
                        is_jumping = True
                        play_tone(MUSIC_NOTES_FREQ['C5'] * 2, 70, 0.2) # Standard jump sound
                
                if event.key == pygame.K_r: # 'R' to regenerate map
                    # Only allow regenerate if player is still above the bottom (not fallen off)
                    if player_pos[1] + PLAYER_HEIGHT < SCREEN_HEIGHT:
                        regenerate_world_in_place()
                
                if event.key == pygame.K_c: # 'C' to cycle colors
                    current_theme_index = (current_theme_index + 1) % len(COLOR_THEMES)
                    update_colors_from_theme() # Update global COLORS
                    play_tone(MUSIC_NOTES_FREQ['A4'], 50, 0.1) # Color cycle sound

            # Escape key to quit from any state, or go back from tutorial/game info
            if event.key == pygame.K_ESCAPE: 
                if game_state == TUTORIAL or game_state == GENERATION_INFO:
                    game_state = MENU 
                else:
                    stop_all_music() 
                    return False 
            
            # Handle R key for new game from GAME_OVER state
            if game_state == GAME_OVER_STATE and event.key == pygame.K_r:
                game_state = PLAYING 
                reset_game() 

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            # Menu button clicks
            if game_state == MENU:
                # Add click visual flash
                target_rect = None
                if start_button_rect and start_button_rect.collidepoint(mouse_x, mouse_y):
                    target_rect = start_button_rect
                    play_tone(MUSIC_NOTES_FREQ['C5'], 100, 0.2) 
                    pygame.time.wait(50) # Small delay for visual/audio feedback
                    game_state = PLAYING
                    reset_game() 
                elif tutorial_button_rect and tutorial_button_rect.collidepoint(mouse_x, mouse_y):
                    target_rect = tutorial_button_rect
                    play_tone(MUSIC_NOTES_FREQ['E5'], 100, 0.2)
                    pygame.time.wait(50)
                    game_state = TUTORIAL 
                elif game_info_button_rect and game_info_button_rect.collidepoint(mouse_x, mouse_y):
                    target_rect = game_info_button_rect
                    play_tone(MUSIC_NOTES_FREQ['G5'], 100, 0.2)
                    pygame.time.wait(50)
                    game_state = GENERATION_INFO
                elif quit_button_rect and quit_button_rect.collidepoint(mouse_x, mouse_y):
                    target_rect = quit_button_rect
                    play_tone(MUSIC_NOTES_FREQ['C4'], 150, 0.2)
                    pygame.time.wait(50)
                    stop_all_music() 
                    return False 
                
                if target_rect: # Draw flash if a button was clicked
                    pygame.draw.rect(screen, COLORS["MENU_CLICK_FLASH"], target_rect.inflate(15, 15), 0) # Fill the flash
                    pygame.display.flip() # Update screen to show flash
                    pygame.time.wait(50) # Small delay to see flash
            
            # Shooting in Play state
            elif game_state == PLAYING and event.button == 1: # Left mouse click to shoot
                if not game_over: 
                    player_center_x = player_pos[0] + PLAYER_WIDTH // 2
                    player_center_y = player_pos[1] + PLAYER_HEIGHT // 2
                    
                    target_x = mouse_x
                    target_y = mouse_y
                    
                    dx = target_x - player_center_x
                    dy = target_y - player_center_y
                    
                    magnitude = math.sqrt(dx**2 + dy**2)
                    if magnitude > 0:
                        norm_dx = dx / magnitude
                        norm_dy = dy / magnitude
                    else: 
                        norm_dx = 1
                        norm_dy = 0
                        
                    lasers.append({
                        'rect': pygame.Rect(player_center_x, player_center_y, LASER_WIDTH, LASER_HEIGHT),
                        'vx': norm_dx * LASER_SPEED_MAGNITUDE,
                        'vy': norm_dy * LASER_SPEED_MAGNITUDE
                    })
                    play_tone(MUSIC_NOTES_FREQ['C4'] * 2, 80, 0.15) 
            # Back buttons in tutorial/info
            elif game_state == TUTORIAL:
                if tutorial_back_button_rect and tutorial_back_button_rect.collidepoint(mouse_x, mouse_y):
                    play_tone(MUSIC_NOTES_FREQ['G4'], 100, 0.2)
                    pygame.time.wait(50)
                    game_state = MENU
            elif game_state == GENERATION_INFO:
                if tutorial_back_button_rect and tutorial_back_button_rect.collidepoint(mouse_x, mouse_y): 
                    play_tone(MUSIC_NOTES_FREQ['G4'], 100, 0.2)
                    pygame.time.wait(50)
                    game_state = MENU


    # --- Game Logic ---
    if game_state == PLAYING:
        handle_music_playback(dt) # Handle music updates

        # Player movement (held keys)
        keys = pygame.key.get_pressed()
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        # Player horizontal movement and camera scrolling
        if moving_right:
            camera_x_offset += PLAYER_SPEED
        elif moving_left:
            if camera_x_offset > 0: # Don't scroll beyond the start of the world
                camera_x_offset -= PLAYER_SPEED

        # Apply gravity to player
        player_vel_y += GRAVITY
        player_pos[1] += player_vel_y

        # Player cannot go outside vertical screen bounds if not scrolling
        player_pos[1] = clamp(player_pos[1], 0, SCREEN_HEIGHT - PLAYER_HEIGHT)

        # Define player_rect for collision checks
        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

        # on_wall_slide = False  # Removed as unused
        # on_wall_slide removed as unused
        on_ground = False

        # Check for contact with ground platforms
        for p in platforms:
            adjusted_platform_rect = p.move(-camera_x_offset, 0)
            if player_rect.colliderect(adjusted_platform_rect) and player_vel_y >= 0:
                if player_pos[1] + PLAYER_HEIGHT >= adjusted_platform_rect.top and player_pos[1] < adjusted_platform_rect.top + PLATFORM_HEIGHT:
                    player_pos[1] = adjusted_platform_rect.top - PLAYER_HEIGHT
                    player_vel_y = 0
                    is_jumping = False
                    on_ground = True
        # If not on ground, check for wall slide
        if not on_ground and player_vel_y > 0: # Only slide if falling
            # Create thin collision rects for player sides
            player_left_side_detector = pygame.Rect(player_rect.left - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)
            player_right_side_detector = pygame.Rect(player_rect.right - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)

            for wall_obj in walls + platforms: # Check all potential vertical surfaces
                adjusted_wall_obj_rect = wall_obj.move(-camera_x_offset, 0)
                
                if player_left_side_detector.colliderect(adjusted_wall_obj_rect) and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                    # on_wall_slide removed as unused
                    is_jumping = True # Still considered 'jumping' for animation/state
                    break # Only one wall at a time
                elif player_right_side_detector.colliderect(adjusted_wall_obj_rect) and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                    player_vel_y = WALL_SLIDE_SPEED # Slow vertical fall
                    # on_wall_slide removed as unused
                    player_vel_y = WALL_SLIDE_SPEED # Slow vertical fall
                    # on_wall_slide removed as unused
                    is_jumping = True # Still considered 'jumping' for animation/state
                    break # Only one wall at a time
        if player_pos[1] > SCREEN_HEIGHT:  # die immediately when falling off screen
            score += DEATH_BONUS  # award bonus points on death
            game_state = GAME_OVER_STATE
            stop_all_music()
            play_tone(MUSIC_NOTES_FREQ['C4'] / 2, 200, 0.3)  # Lower death sound


        # --- Enemy Updates ---
        enemies_to_remove = []
        for enemy in enemies:
            # Adjust enemy position for camera scrolling
            enemy_rect_adjusted = enemy['rect'].move(-camera_x_offset, 0)

            # Enemy type specific movement
            if enemy['type'] == 'flying':
                enemy['rect'].x += enemy['vx']
                if enemy['rect'].left <= 0 or enemy['rect'].right >= SCREEN_WIDTH * 5: 
                    enemy['vx'] *= -1
            
            elif enemy['type'] == 'rolling':
                enemy['vy'] += GRAVITY # Apply gravity to rolling
                enemy['rect'].y += enemy['vy']

                on_platform = False
                for p in platforms:
                    adjusted_p_rect = p.move(-camera_x_offset, 0)
                    if enemy['rect'].colliderect(adjusted_p_rect) and enemy['vy'] >= 0:
                        if enemy['rect'].y + ENEMY_HEIGHT >= adjusted_p_rect.top and enemy['rect'].y < adjusted_p_rect.top + PLATFORM_HEIGHT:
                            enemy['rect'].y = adjusted_p_rect.top - ENEMY_HEIGHT
                            enemy['vy'] = 0
                            on_platform = True
                            break 

                if on_platform:
                    enemy['rect'].x += enemy['vx']
                    if enemy['rect'].x < enemy['walk_start_x'] or \
                       enemy['rect'].x + enemy['rect'].width > enemy['walk_end_x']:
                        enemy['vx'] *= -1 
                else: 
                    if enemy['rect'].y > SCREEN_HEIGHT + 50: 
                        enemies_to_remove.append(enemy['id'])


            elif enemy['type'] == 'jumping':
                enemy['vy'] += GRAVITY
                enemy['rect'].y += enemy['vy']

                on_platform = False
                for p in platforms:
                    adjusted_p_rect = p.move(-camera_x_offset, 0)
                    if enemy['rect'].colliderect(adjusted_p_rect) and enemy['vy'] >= 0:
                        if enemy['rect'].y + ENEMY_HEIGHT >= adjusted_p_rect.top and enemy['rect'].y < adjusted_p_rect.top + PLATFORM_HEIGHT:
                            enemy['rect'].y = adjusted_p_rect.top - ENEMY_HEIGHT
                            enemy['vy'] = 0
                            enemy['is_jumping'] = False
                            on_platform = True
                            break
                
                if on_platform:
                    enemy['current_jump_cooldown'] -= 1
                    if enemy['current_jump_cooldown'] <= 0:
                        enemy['vy'] = JUMP_STRENGTH * 0.8 
                        enemy['is_jumping'] = True
                        enemy['current_jump_cooldown'] = enemy['jump_cooldown'] 
                else: 
                    if enemy['rect'].y > SCREEN_HEIGHT + 50:
                        enemies_to_remove.append(enemy['id'])

            # Standard enemy (Red block) - no special movement, just exists and takes damage
            elif enemy['type'] == 'standard':
                enemy['vy'] += GRAVITY 
                enemy['rect'].y += enemy['vy']
                on_platform = False
                for p in platforms:
                    adjusted_p_rect = p.move(-camera_x_offset, 0)
                    if enemy['rect'].colliderect(adjusted_p_rect) and enemy['vy'] >= 0:
                        if enemy['rect'].y + ENEMY_HEIGHT >= adjusted_p_rect.top and enemy['rect'].y < adjusted_p_rect.top + PLATFORM_HEIGHT:
                            enemy['rect'].y = adjusted_p_rect.top - ENEMY_HEIGHT
                            enemy['vy'] = 0
                            on_platform = True
                            break
                if not on_platform and enemy['rect'].y > SCREEN_HEIGHT + 50: 
                    enemies_to_remove.append(enemy['id'])


            # Player-Enemy contact damage (only if not already removed)
            if enemy['id'] not in enemies_to_remove:
                if check_collision(player_rect, enemy_rect_adjusted):
                    health -= ENEMY_CONTACT_DAMAGE / FPS 
                    if health <= 0:
                        game_state = GAME_OVER_STATE 
                        stop_all_music() # Stop music on death
                        play_tone(MUSIC_NOTES_FREQ['C4'], 200, 0.3) 
                    # Simple knockback
                    player_pos[0] += (15 if player_pos[0] < enemy_rect_adjusted.centerx else -15)
                    play_tone(MUSIC_NOTES_FREQ['F4'] * 0.5, 50, 0.1) # Player hurt sound

        # --- Laser Updates ---
        lasers_to_remove_indices = [] 
        for i, laser in enumerate(lasers):
            laser['rect'].x += laser['vx']
            laser['rect'].y += laser['vy']

            if laser['rect'].x > SCREEN_WIDTH or laser['rect'].x < 0 or \
               laser['rect'].y > SCREEN_HEIGHT or laser['rect'].y < 0:
                lasers_to_remove_indices.append(i)
                continue

            for enemy in enemies: 
                if enemy['id'] in enemies_to_remove: 
                    continue

                enemy_rect_adjusted = enemy['rect'].move(-camera_x_offset, 0)
                if check_collision(laser['rect'], enemy_rect_adjusted):
                    enemy['health'] -= PLAYER_LASER_DAMAGE
                    if enemy['health'] <= 0:
                        enemies_to_remove.append(enemy['id']) 
                        play_tone(MUSIC_NOTES_FREQ['G4'] / 2, 100, 0.2) # Enemy death sound
                    else: # Enemy hit, but not dead
                        play_tone(MUSIC_NOTES_FREQ['G4'] * 1.5, 50, 0.15) # Enemy hit sound
                    
                    lasers_to_remove_indices.append(i)
                    score += 10
                    break 

        lasers = [laser for i, laser in enumerate(lasers) if i not in lasers_to_remove_indices]
        enemies[:] = [enemy for enemy in enemies if enemy['id'] not in enemies_to_remove] 

    # --- Drawing ---
    screen.fill(COLORS["SKY"]) 

    if game_state == PLAYING or game_state == GAME_OVER_STATE:
        # Draw platforms
        for p in platforms:
            pygame.draw.rect(screen, COLORS["PLATFORM"], p.move(-camera_x_offset, 0))
            pygame.draw.line(screen, COLORS["DARK_ACCENT"], (p.left - camera_x_offset, p.top), (p.right - camera_x_offset, p.top), 3)

        # Draw walls
        for w in walls:
            pygame.draw.rect(screen, COLORS["WALL"], w.move(-camera_x_offset, 0))
            pygame.draw.line(screen, COLORS["DARK_ACCENT"], (w.left - camera_x_offset, w.top), (w.left - camera_x_offset, w.bottom), 3)
            pygame.draw.line(screen, COLORS["DARK_ACCENT"], (w.right - camera_x_offset, w.top), (w.right - camera_x_offset, w.bottom), 3)


        # Draw player (using new drawing function)
        draw_player(screen, player_rect, COLORS["PLAYER"])

        # Draw enemies (using new drawing functions)
        for enemy in enemies:
            enemy_rect_draw = enemy['rect'].move(-camera_x_offset, 0)
            if enemy['type'] == 'standard': draw_enemy_standard(screen, enemy_rect_draw, COLORS["ENEMY_STANDARD"])
            elif enemy['type'] == 'flying': draw_enemy_flying(screen, enemy_rect_draw, COLORS["ENEMY_FLYING"])
            elif enemy['type'] == 'rolling': draw_enemy_rolling(screen, enemy_rect_draw, COLORS["ENEMY_ROLLING"])
            elif enemy['type'] == 'jumping': draw_enemy_jumping(screen, enemy_rect_draw, COLORS["ENEMY_JUMPING"])
            
        # Draw lasers
        for laser in lasers:
            pygame.draw.rect(screen, COLORS["LASER"], laser['rect']) 

        # Draw HUD
        draw_text(screen, f"Score: {score}", 30, 10, 10, COLORS["MENU_TEXT"])
        draw_text(screen, f"Health: {max(0, int(health))}", 30, 10, 40, COLORS["MENU_TEXT"] if health > 30 else RED)
        draw_text(screen, "Controls: Arrows/WASD, Space/Up to Jump, Click to Shoot, R for New Map, C for Colors", 20, 10, SCREEN_HEIGHT - 30, COLORS["MENU_TEXT"])

    # Game Over screen
    if game_state == GAME_OVER_STATE:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        screen.blit(overlay, (0,0))
        
        draw_text(screen, "GAME OVER", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, RED, anchor='center')
        draw_text(screen, f"Final Score: {score}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, COLORS["MENU_TEXT"], anchor='center')
        draw_text(screen, "Press R for New Game or ESC to Quit", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, COLORS["MENU_TEXT"], anchor='center')

    # Menu Screen
    elif game_state == MENU:
        screen.fill(COLORS["MENU_BG"]) 
        draw_text(screen, "Procedural Jump & Run", 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, COLORS["MENU_TEXT"], anchor='center')
        
        # Get mouse position for hover effect
        mouse_pos = pygame.mouse.get_pos()

        # Start Button
        start_button_rect = draw_text(screen, "START GAME", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, COLORS["MENU_START_BTN"], anchor='center')
        if start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], start_button_rect.inflate(10, 10))

        # Tutorial Button
        tutorial_button_rect = draw_text(screen, "HOW TO PLAY", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, COLORS["MENU_TUTORIAL_BTN"], anchor='center')
        if tutorial_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], tutorial_button_rect.inflate(10, 10))

        # Game Info Button
        game_info_button_rect = draw_text(screen, "GAME DETAILS", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, COLORS["MENU_INFO_BTN"], anchor='center')
        if game_info_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], game_info_button_rect.inflate(10, 10))
        
        # Quit Button
        quit_button_rect = draw_text(screen, "QUIT", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, COLORS["MENU_QUIT_BTN"], anchor='center')
        if quit_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], quit_button_rect.inflate(10, 10))


    # Tutorial Screen
    elif game_state == TUTORIAL:
        screen.fill(BLACK) 
        draw_text(screen, "--- HOW TO PLAY ---", 60, SCREEN_WIDTH // 2, 50, COLORS["MENU_TEXT"], anchor='center')
        
        tutorial_text = [
            "Your goal is to survive as long as possible and get a high score!",
            "",
            "CONTROLS:",
            f"- Move Left:  <-- Arrow Key or 'A'",
            f"- Move Right: --> Arrow Key or 'D'",
            f"- Jump:       ^ Arrow Key or 'W' or SPACEBAR",
            f"- Shoot Laser: LEFT MOUSE CLICK (aim with mouse cursor)",
            f"- New Map:    Press 'R' (regenerate world around you, score persists!)",
            f"- Change Colors: Press 'C' (cycle through visual themes)",
            f"- Back/Quit:  Press 'ESC' (from any menu/info screen)",
            "",
            "ABILITIES:",
            f"- Wall Run: While jumping, move against a {COLOR_TO_NAME[COLORS['WALL']]} wall to slide slowly.",
            f"- Wall Jump: While wall running, press Jump again to leap off the wall!",
            "",
            "ENEMIES:",
            f"- Player (You): A {COLOR_TO_NAME[COLORS['PLAYER']]} figure.",
            f"- Standard Enemies: {COLOR_TO_NAME[COLORS['ENEMY_STANDARD']]} simple blocks (stationary, but fall with gravity).",
            f"- Rolling Enemies:  {COLOR_TO_NAME[COLORS['ENEMY_ROLLING']]} spiky circles (patrol platforms).",
            f"- Jumping Enemies:  {COLOR_TO_NAME[COLORS['ENEMY_JUMPING']]} bouncy blobs (periodically leap).",
            f"- Flying Enemies:   {COLOR_TO_NAME[COLORS['ENEMY_FLYING']]} ellipses with wings (move horizontally in air).",
            "  Beware! Contact with enemies damages your health!",
            "",
            "GAME FLOW:",
            "Each map is randomly generated using advanced noise algorithms. ",
            "Platforms, walls, and enemy placements are unique every time you press 'R'.",
            "Your score and health persist when you regenerate the world in place!",
            "",
            "The 'art' of this game comes from the procedurally generated shapes and colors!",
        ]
        
        text_y = 120
        for line in tutorial_text:
            draw_text(screen, line, 25, SCREEN_WIDTH // 2, text_y, COLORS["MENU_TEXT"], anchor='center')
            text_y += 30 

        tutorial_back_button_rect = draw_text(screen, "BACK TO MENU", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60, COLORS["MENU_START_BTN"], anchor='center')

    # Generation Info Screen
    elif game_state == GENERATION_INFO:
        screen.fill(BLACK) 
        draw_text(screen, "--- GAME GENERATION DETAILS ---", 60, SCREEN_WIDTH // 2, 50, COLORS["MENU_TEXT"], anchor='center')

        info_text = [
            f"Current Map Seed: {current_map_seed}",
            f"Noise Scale (Roughness): {NOISE_SCALE}",
            f"Noise Octaves (Detail): {OCTAVES}",
            "",
            "Procedural Art (Colors & Shapes - Cycle with 'C'):",
            f"- Player Color: {COLOR_TO_NAME[COLORS['PLAYER']]}",
            f"- Platform Color: {COLOR_TO_NAME[COLORS['PLATFORM']]}",
            f"- Wall Color: {COLOR_TO_NAME[COLORS['WALL']]}",
            f"- Laser Color: {COLOR_TO_NAME[COLORS['LASER']]}",
            "",
            "Enemy Types (Colors & Behavior):",
            f"- Standard Enemy: {COLOR_TO_NAME[COLORS['ENEMY_STANDARD']]}",
            f"- Flying Enemy:   {COLOR_TO_NAME[COLORS['ENEMY_FLYING']]}",
            f"- Rolling Enemy:  {COLOR_TO_NAME[COLORS['ENEMY_ROLLING']]}",
            f"- Jumping Enemy:  {COLOR_TO_NAME[COLORS['ENEMY_JUMPING']]}",
            "",
            "Procedural Music:",
            "  A simple, randomized chiptune-like melody plays during the game.",
            "  Each new map (generated with 'R') will generate a unique sequence of notes!",
            "",
            "NOTE ON CUSTOMIZATION (Image/Music):",
            "This game is designed to run purely locally on your computer with Pygame.",
            "It does NOT use external AI services for image or complex music generation",
            "to ensure it remains completely free and does NOT require internet access or",
            "API keys, preventing any potential costs for you."
        ]

        text_y = 120
        for line in info_text:
            draw_text(screen, line, 25, SCREEN_WIDTH // 2, text_y, COLORS["MENU_TEXT"], anchor='center')
            text_y += 30

        tutorial_back_button_rect = draw_text(screen, "BACK TO MENU", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60, COLORS["MENU_START_BTN"], anchor='center')


    # Update the display
    pygame.display.flip()

    # Cap frame rate
    clock.tick(FPS)

    return True 
# --- Game Reset Function ---
# Initialize the Pygame display surface (screen) at the top-level so it's available globally
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
def reset_game():
    """Resets game state for a new game."""
    global player_pos, player_vel_y, is_jumping, score, health, game_over, camera_x_offset, lasers, enemies, current_map_seed
    """Resets game state for a new game."""
    global player_pos, player_vel_y, is_jumping, score, health, game_over, camera_x_offset, lasers, enemies, current_map_seed
    
    current_map_seed = random.randint(0, 1000000) 
    generate_platforms_and_walls() # This populates the 'platforms' and 'walls' list first

    # Set player position on the first platform
    if platforms:
        player_pos[0] = SCREEN_WIDTH // 4 
        player_pos[1] = platforms[0].y - PLAYER_HEIGHT 
    else:
        player_pos = [SCREEN_WIDTH // 4, SCREEN_HEIGHT - PLAYER_HEIGHT - 50]

    player_vel_y = 0
    is_jumping = False
    score = 0
    health = 100
    game_over = False 
    camera_x_offset = 0
    lasers.clear() 
    enemies.clear() 
    spawn_enemies() 
    generate_random_melody() 
    
    global current_music_note_idx, music_timer
    current_music_note_idx = 0
    music_timer = 0


# --- Regenerate World in Place Function ---
def regenerate_world_in_place():
    """
    Generates a new set of platforms and enemies without resetting score/health.
    Keeps player X, Y, and the platform under them fixed; regenerates everything else.
    """
    global player_pos, player_vel_y, is_jumping
    global camera_x_offset, current_map_seed, lasers, enemies

    # Save world X coordinate of player
    old_world_x = player_pos[0] + camera_x_offset

    # Regenerate terrain and music without moving player
    current_map_seed = random.randint(0, 1000000)
    generate_platforms_and_walls()
    enemies.clear()
    lasers.clear()
    spawn_enemies()
    generate_random_melody()

    # Reset vertical velocity and jump flag
    player_vel_y = 0
    is_jumping = False

    # Find platform under old_world_x, or closest if none
    target_platform = None
    for p in platforms:
        if p.x <= old_world_x <= p.x + p.width:
            target_platform = p
            break
    if not target_platform and platforms:
        target_platform = min(platforms, key=lambda p: abs((p.x + p.width/2) - old_world_x))

    # Compute camera offset so that platform remains under player
    if target_platform:
        camera_x_offset = max(0, int(target_platform.x - player_pos[0]))

    # Reset procedural music timing
    global current_music_note_idx, music_timer
    current_music_note_idx = 0
    music_timer = 0


# --- Main Game Execution ---
if __name__ == "__main__":
    running = True
    
    # Initialize placeholder rects, which will be updated by draw_text in game_loop
    start_button_rect = pygame.Rect(0,0,0,0)
    quit_button_rect = pygame.Rect(0,0,0,0)
    tutorial_button_rect = pygame.Rect(0,0,0,0)
    game_info_button_rect = pygame.Rect(0,0,0,0)
    tutorial_back_button_rect = pygame.Rect(0,0,0,0)

    # Dictionary to map color tuples to names for display in info/tutorial
    # This dictionary needs to be dynamically updated when theme changes
    # So, we map base colors defined at the top to their names, and look up
    # the active COLORS dictionary at runtime for display.
    COLOR_TO_NAME = {
        DEFAULT_BLUE_PLAYER: "Blue",
        DEFAULT_RED_ENEMY_LASER: "Red",
        DEFAULT_GREEN_PLATFORM: "Green",
        DEFAULT_YELLOW_ROLLING: "Yellow",
        DEFAULT_ORANGE_FLYING: "Orange",
        DEFAULT_PURPLE_JUMPING: "Purple",
        (80, 80, 80): "Dark Grey", # WALL color
    }
    # Add other common colors directly
    COLOR_TO_NAME[WHITE] = "White"
    COLOR_TO_NAME[BLACK] = "Black"
    COLOR_TO_NAME[DEFAULT_LIGHT_BLUE_SKY] = "Light Blue" # Default Sky

    # Initial music generation (even if not played immediately, sequence is ready)
    generate_random_melody()
    update_colors_from_theme() # Set initial theme colors

    clock = pygame.time.Clock()
    while running:
        running = game_loop() 

    stop_all_music() # Ensure music is stopped when the game loop ends
    pygame.quit()
