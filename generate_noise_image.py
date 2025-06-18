import pygame
import random
import math
import numpy as np
from perlin_noise import PerlinNoise


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

DEATH_BONUS = 50

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

DEFAULT_BLUE_PLAYER = (0, 0, 200)
DEFAULT_RED_ENEMY_LASER = (255, 0, 0)
DEFAULT_GREEN_PLATFORM = (0, 100, 0)
DEFAULT_YELLOW_ROLLING = (255, 255, 0)
DEFAULT_ORANGE_FLYING = (255, 165, 0)
DEFAULT_PURPLE_JUMPING = (128, 0, 128)
DEFAULT_LIGHT_BLUE_SKY = (173, 216, 230)
DEFAULT_DARK_ACCENT = (50, 50, 50)
DEFAULT_MENU_BG = (40, 40, 40)
DEFAULT_MENU_TEXT = (255, 255, 255)
DEFAULT_MENU_BTN_START = (0, 150, 0)
DEFAULT_MENU_BTN_TUTORIAL = (200, 200, 0)
DEFAULT_MENU_BTN_INFO = (100, 0, 100)
DEFAULT_MENU_BTN_QUIT = (150, 0, 0)

COLOR_THEMES = [
    {
        "PLAYER": DEFAULT_BLUE_PLAYER,
        "LASER": DEFAULT_RED_ENEMY_LASER,
        "PLATFORM": DEFAULT_GREEN_PLATFORM,
        "WALL": (80, 80, 80),
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
        "MENU_HOVER_FILL": (80, 80, 80),
        "MENU_CLICK_FLASH": (255, 255, 255),
    },
    {
        "PLAYER": (150, 75, 0), "LASER": (255, 200, 0), "PLATFORM": (210, 180, 140),
        "WALL": (160, 120, 80), "ENEMY_STANDARD": (180, 50, 0), "ENEMY_FLYING": (100, 150, 0),
        "ENEMY_ROLLING": (80, 80, 0), "ENEMY_JUMPING": (100, 50, 0), "SKY": (255, 220, 150),
        "DARK_ACCENT": (100, 70, 40), "MENU_BG": (60, 50, 30), "MENU_TEXT": (255, 255, 200),
        "MENU_START_BTN": (150, 100, 50), "MENU_TUTORIAL_BTN": (200, 150, 50), "MENU_INFO_BTN": (100, 50, 0),
        "MENU_QUIT_BTN": (150, 75, 0), "MENU_HOVER_FILL": (120, 90, 60), "MENU_CLICK_FLASH": (255, 255, 255),
    },
    {
        "PLAYER": (100, 200, 255), "LASER": (0, 255, 255), "PLATFORM": (0, 50, 0),
        "WALL": (30, 30, 60), "ENEMY_STANDARD": (50, 100, 50), "ENEMY_FLYING": (100, 50, 150),
        "ENEMY_ROLLING": (80, 0, 0), "ENEMY_JUMPING": (0, 100, 100), "SKY": (20, 20, 40),
        "DARK_ACCENT": (10, 10, 20), "MENU_BG": (15, 15, 30), "MENU_TEXT": (200, 255, 200),
        "MENU_START_BTN": (0, 100, 0), "MENU_TUTORIAL_BTN": (0, 100, 100), "MENU_INFO_BTN": (50, 0, 50),
        "MENU_QUIT_BTN": (100, 0, 0), "MENU_HOVER_FILL": (40, 40, 80), "MENU_CLICK_FLASH": (255, 255, 255),
    }
]
current_theme_index = 0
COLORS = COLOR_THEMES[current_theme_index]

PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 5
JUMP_STRENGTH = -15
GRAVITY = 0.8
WALL_SLIDE_SPEED = 0.2 * GRAVITY
WALL_JUMP_HORIZONTAL_PUSH = 8
WALL_JUMP_VERTICAL_PUSH = -12
PLAYER_COLOR = None

LASER_WIDTH = 20
LASER_HEIGHT = 5
LASER_SPEED_MAGNITUDE = 15
LASER_COLOR = None
PLAYER_LASER_DAMAGE = 20

ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50
ENEMY_SPEED = 2
ENEMY_HEALTH_DEFAULT = 50
ENEMY_CONTACT_DAMAGE = 10

PLATFORM_HEIGHT = 20
PLATFORM_MIN_WIDTH = 80
PLATFORM_MAX_WIDTH = 200
PLATFORM_MIN_GAP = 80
PLATFORM_MAX_GAP = 200
PLATFORM_MAX_Y_DIFF = 80
PLATFORM_COLOR = None

WALL_WIDTH = 20
WALL_MIN_HEIGHT = 100
WALL_MAX_HEIGHT = 250
WALL_COLOR = None

DIFFICULTY_TIERS = [
    {"score": 0, "enemy_speed_mult": 1.0, "enemy_spawn_chance": 0.2, "platform_gap_mult": 1.0},
    {"score": 200, "enemy_speed_mult": 1.2, "enemy_spawn_chance": 0.25, "platform_gap_mult": 1.1},
    {"score": 500, "enemy_speed_mult": 1.4, "enemy_spawn_chance": 0.3, "platform_gap_mult": 1.2},
    {"score": 1000, "enemy_speed_mult": 1.6, "enemy_spawn_chance": 0.35, "platform_gap_mult": 1.3},
    {"score": 2000, "enemy_speed_mult": 1.8, "enemy_spawn_chance": 0.4, "platform_gap_mult": 1.4},
]

NOISE_SCALE = 100.0
OCTAVES = 6
NOISE_X_OFFSET_BASE = 0
NOISE_Y_OFFSET_BASE = 0

platforms = []
walls = []
enemies = []
lasers = []
player_pos = [SCREEN_WIDTH // 4, 0]
player_vel_y = 0
is_jumping = False
score = 0
health = 100
game_over = False
camera_x_offset = 0
perlin_gen = None
current_map_seed = None

MENU = 0
PLAYING = 1
GAME_OVER_STATE = 2
TUTORIAL = 3
GENERATION_INFO = 4
game_state = MENU

start_button_rect = None
quit_button_rect = None
tutorial_button_rect = None
game_info_button_rect = None
tutorial_back_button_rect = None


def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def check_collision(rect1, rect2):
    return rect1.colliderect(rect2)

def draw_text(surface, text, size, x, y, color=WHITE, anchor='topleft'):
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
    return text_rect

def update_colors_from_theme():
    global COLORS, PLAYER_COLOR, LASER_COLOR, PLATFORM_COLOR, WALL_COLOR
    COLORS = COLOR_THEMES[current_theme_index]
    PLAYER_COLOR = COLORS["PLAYER"]
    LASER_COLOR = COLORS["LASER"]
    PLATFORM_COLOR = COLORS["PLATFORM"]
    WALL_COLOR = COLORS["WALL"]

COLOR_TO_NAME = {
    DEFAULT_BLUE_PLAYER:      "Blue",
    DEFAULT_RED_ENEMY_LASER:  "Red",
    DEFAULT_GREEN_PLATFORM:   "Green",
    DEFAULT_YELLOW_ROLLING:   "Yellow",
    DEFAULT_ORANGE_FLYING:    "Orange",
    DEFAULT_PURPLE_JUMPING:   "Purple",
    (80, 80, 80):             "Dark Grey",
    WHITE:                    "White",
    BLACK:                    "Black",
    DEFAULT_LIGHT_BLUE_SKY:   "Light Blue"
}

_SAMPLE_RATE = 44100

MUSIC_NOTES_FREQ = {
    'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
    'G4': 392.00, 'A4': 440.00, 'B4': 493.88, 'C5': 523.25,
    'E5': 659.25, 'G5': 783.99,
    'REST': 0
}
MUSIC_BEAT_LENGTH = 0.25
music_sequence_freq = []
music_timer = 0
current_music_note_idx = 0
current_sound_obj = None

def generate_random_melody(length_beats=40):
    global music_sequence_freq, current_music_note_idx
    notes_freq_list = list(MUSIC_NOTES_FREQ.values())
    music_sequence_freq = [random.choice(notes_freq_list + [MUSIC_NOTES_FREQ['REST']]*2) for _ in range(length_beats)]
    current_music_note_idx = 0
    print(f"Generated a new melody sequence of {length_beats} notes.")

def play_tone(frequency, duration_ms, volume=0.1):
    if frequency == 0:
        return None

    num_samples = int(duration_ms * _SAMPLE_RATE / 1000)
    arr = np.zeros((num_samples, 2), dtype=np.int16)

    amplitude = 32767 * volume
    for i in range(num_samples):
        sample_val = int(amplitude * math.sin(2 * math.pi * frequency * i / _SAMPLE_RATE))
        arr[i, 0] = sample_val
        arr[i, 1] = sample_val
    
    sound = pygame.sndarray.make_sound(arr)
    sound.play(loops=0)
    return sound

def handle_music_playback(dt):
    global music_timer, current_music_note_idx, current_sound_obj

    if not music_sequence_freq:
        return

    music_timer += dt

    if music_timer >= MUSIC_BEAT_LENGTH * 1000:
        music_timer = 0

        if current_sound_obj:
            current_sound_obj.stop()

        freq = music_sequence_freq[current_music_note_idx]
        current_sound_obj = play_tone(freq, int(MUSIC_BEAT_LENGTH * 1000 * 0.8))

        current_music_note_idx += 1
        if current_music_note_idx >= len(music_sequence_freq):
            current_music_note_idx = 0
            generate_random_melody()


def stop_all_music():
    pygame.mixer.stop()


def generate_platforms_and_walls():
    global platforms, walls, NOISE_X_OFFSET_BASE, NOISE_Y_OFFSET_BASE, perlin_gen, current_map_seed

    platforms = []
    walls = []
    
    if current_map_seed is None:
        current_map_seed = random.randint(0, 1000000)
    
    perlin_gen = PerlinNoise(octaves=OCTAVES, seed=current_map_seed)

    NOISE_X_OFFSET_BASE = random.uniform(0, 1000)
    NOISE_Y_OFFSET_BASE = random.uniform(0, 1000)


    platforms.append(pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH / 2, PLATFORM_HEIGHT))
    
    last_platform_right = platforms[0].right
    last_platform_y = platforms[0].y

    generation_end_x = SCREEN_WIDTH * 5

    while last_platform_right < generation_end_x:
        noise_val_y = perlin_gen([(last_platform_right + NOISE_X_OFFSET_BASE) / (NOISE_SCALE * 2), (NOISE_Y_OFFSET_BASE) / (NOISE_SCALE * 2)])
        
        current_difficulty = get_current_difficulty_tier()
        platform_y_diff_mult = current_difficulty["platform_gap_mult"]

        y_diff = int(noise_val_y * PLATFORM_MAX_Y_DIFF * 2 * platform_y_diff_mult) - PLATFORM_MAX_Y_DIFF

        next_platform_y = last_platform_y + y_diff
        
        min_allowed_y = SCREEN_HEIGHT * 0.4
        max_allowed_y = SCREEN_HEIGHT - PLATFORM_HEIGHT - 50
        next_platform_y = clamp(next_platform_y, min_allowed_y, max_allowed_y)

        gap = random.randint(int(PLATFORM_MIN_GAP * platform_y_diff_mult), int(PLATFORM_MAX_GAP * platform_y_diff_mult))
        platform_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)

        next_platform_x = last_platform_right + gap
        
        new_platform = pygame.Rect(next_platform_x, next_platform_y, platform_width, PLATFORM_HEIGHT)
        platforms.append(new_platform)

        if random.random() < 0.3:
            wall_height = random.randint(WALL_MIN_HEIGHT, WALL_MAX_HEIGHT)
            wall_x = new_platform.left if random.random() < 0.5 else new_platform.right - WALL_WIDTH
            
            wall_y = new_platform.top - wall_height if random.random() < 0.7 else new_platform.top
            
            wall_y = clamp(wall_y, 0, new_platform.top - WALL_WIDTH)
            
            walls.append(pygame.Rect(wall_x, wall_y, WALL_WIDTH, wall_height))


        last_platform_right = new_platform.right
        last_platform_y = new_platform.y
    
    print(f"Generated {len(platforms)} platforms and {len(walls)} walls.")


def spawn_enemies():
    global enemies
    enemies = []

    enemy_types = ['standard', 'flying', 'rolling', 'jumping']

    current_difficulty = get_current_difficulty_tier()
    enemy_speed_mult = current_difficulty["enemy_speed_mult"]
    enemy_spawn_chance = current_difficulty["enemy_spawn_chance"]

    for i in range(1, len(platforms)):
        if random.random() < enemy_spawn_chance:
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
                'vx': ENEMY_SPEED * (1 if random.random() > 0.5 else -1) * enemy_speed_mult,
                'vy': 0,
                'health': ENEMY_HEALTH_DEFAULT,
                'color': RED,
            }

            if enemy_type == 'standard':
                new_enemy['color'] = COLORS["ENEMY_STANDARD"]
                new_enemy['vx'] = 0
            elif enemy_type == 'flying':
                new_enemy['rect'].y = random.randint(SCREEN_HEIGHT // 4, SCREEN_HEIGHT // 2)
                new_enemy['vx'] = ENEMY_SPEED * 1.5 * enemy_speed_mult
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
    for i in range(len(DIFFICULTY_TIERS) - 1, -1, -1):
        if score >= DIFFICULTY_TIERS[i]["score"]:
            return DIFFICULTY_TIERS[i]
    return DIFFICULTY_TIERS[0]

def draw_player(surface, rect, color):
    pygame.draw.rect(surface, color, rect)
    
    head_size = rect.width * 0.8
    head_x = rect.centerx - head_size / 2
    head_y = rect.top - head_size * 0.7
    pygame.draw.ellipse(surface, (color[0]*0.8, color[1]*0.8, color[2]*0.8),
                        (head_x, head_y, head_size, head_size * 0.8))
    
    eye_radius = rect.width * 0.1
    left_eye_center = (int(rect.centerx - rect.width * 0.2), int(rect.top - head_size * 0.4))
    right_eye_center = (int(rect.centerx + rect.width * 0.2), int(rect.top - head_size * 0.4))
    
    pygame.draw.circle(surface, WHITE, left_eye_center, int(eye_radius))
    pygame.draw.circle(surface, BLACK, left_eye_center, int(eye_radius * 0.5))
    pygame.draw.circle(surface, WHITE, right_eye_center, int(eye_radius))
    pygame.draw.circle(surface, BLACK, right_eye_center, int(eye_radius * 0.5))

    arm_width = rect.width * 0.2
    arm_height = rect.height * 0.6
    arm_color = (color[0]*0.9, color[1]*0.9, color[2]*0.9)
    pygame.draw.rect(surface, arm_color, (rect.left - arm_width + 2, rect.top + rect.height * 0.1, arm_width, arm_height))
    pygame.draw.rect(surface, arm_color, (rect.right - 2, rect.top + rect.height * 0.1, arm_width, arm_height))

    leg_width = rect.width * 0.3
    leg_height = rect.height * 0.4
    leg_color = (color[0]*0.7, color[1]*0.7, color[2]*0.7)
    pygame.draw.rect(surface, leg_color, (rect.left + rect.width*0.1, rect.bottom - leg_height, leg_width, leg_height))
    pygame.draw.rect(surface, leg_color, (rect.right - rect.width*0.1 - leg_width, rect.bottom - leg_height, leg_width, leg_height))


def draw_enemy_standard(surface, rect, color):
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, (rect.left + rect.width*0.2, rect.top + rect.height*0.3, rect.width*0.2, rect.height*0.2))
    pygame.draw.rect(surface, BLACK, (rect.right - rect.width*0.4, rect.top + rect.height*0.3, rect.width*0.2, rect.height*0.2))
    pygame.draw.line(surface, BLACK, (rect.left + rect.width*0.2, rect.bottom - rect.height*0.3), (rect.right - rect.width*0.2, rect.bottom - rect.height*0.3), 2)


def draw_enemy_flying(surface, rect, color):
    pygame.draw.ellipse(surface, color, rect)
    wing_color = (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50))
    
    wing_points_left = [
        rect.topleft,
        (rect.left - rect.width * 0.8, rect.centery),
        (rect.left, rect.bottom)
    ]
    pygame.draw.polygon(surface, wing_color, wing_points_left)
    
    wing_points_right = [
        rect.topright,
        (rect.right + rect.width * 0.8, rect.centery),
        (rect.right, rect.bottom)
    ]
    pygame.draw.polygon(surface, wing_color, wing_points_right)

    pygame.draw.circle(surface, BLACK, (rect.centerx - rect.width*0.2, rect.centery - rect.height*0.1), int(rect.width*0.08))
    pygame.draw.circle(surface, BLACK, (rect.centerx + rect.width*0.2, rect.centery - rect.height*0.1), int(rect.width*0.08))

def draw_enemy_rolling(surface, rect, color):
    pygame.draw.circle(surface, color, rect.center, rect.width // 2)
    for i in range(12):
        angle = i * (2 * math.pi / 12)
        x1 = rect.centerx + (rect.width // 2) * math.cos(angle)
        y1 = rect.centery + (rect.width // 2) * math.sin(angle)
        x2 = rect.centerx + (rect.width // 2 + 10) * math.cos(angle)
        y2 = rect.centery + (rect.width // 2 + 10) * math.sin(angle)
        pygame.draw.line(surface, BLACK, (x1,y1), (x2,y2), 2)
    pygame.draw.circle(surface, BLACK, (rect.centerx - int(rect.width*0.15), rect.centery - int(rect.height*0.15)), int(rect.width*0.07))
    pygame.draw.circle(surface, BLACK, (rect.centerx + int(rect.width*0.15), rect.centery - int(rect.height*0.15)), int(rect.width*0.07))


def draw_enemy_jumping(surface, rect, color):
    blob_points = [
        rect.bottomleft,
        rect.bottomright,
        (rect.right, rect.centery + rect.height * 0.2),
        (rect.centerx + rect.width * 0.4, rect.top + rect.height * 0.1),
        (rect.centerx, rect.top - rect.height * 0.1),
        (rect.centerx - rect.width * 0.4, rect.top + rect.height * 0.1),
        (rect.left, rect.centery + rect.height * 0.2)
    ]
    pygame.draw.polygon(surface, color, blob_points)
    
    pygame.draw.circle(surface, BLACK, rect.center, int(rect.width * 0.25))
    pygame.draw.circle(surface, WHITE, (rect.centerx + int(rect.width * 0.08), rect.centery - int(rect.height * 0.08)), int(rect.width * 0.08))


def game_loop():
    global player_pos, player_vel_y, is_jumping, score, health, game_over, camera_x_offset, current_map_seed, lasers, enemies, game_state, clock
    global start_button_rect, quit_button_rect, tutorial_button_rect, game_info_button_rect, tutorial_back_button_rect
    global current_theme_index
    
    dt = clock.get_time()

    on_ground = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop_all_music()
            return False

        if event.type == pygame.KEYDOWN:
            if game_state == PLAYING:
                keys_pressed_current_frame = pygame.key.get_pressed()
                player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

                wall_left_contact = False
                wall_right_contact = False
                all_vertical_surfaces = []
                for p in platforms:
                    adjusted_p_rect = p.move(-camera_x_offset, 0)
                    if adjusted_p_rect.height > PLAYER_HEIGHT:
                        all_vertical_surfaces.append(adjusted_p_rect)
                for w in walls:
                    all_vertical_surfaces.append(w.move(-camera_x_offset, 0))

                for obj_rect in all_vertical_surfaces:
                    player_left_detector = pygame.Rect(player_rect.left - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)
                    player_right_detector = pygame.Rect(player_rect.right - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)

                    if player_left_detector.colliderect(obj_rect):
                        wall_left_contact = True
                    if player_right_detector.colliderect(obj_rect):
                        wall_right_contact = True
                
                if (event.key == pygame.K_SPACE or event.key == pygame.K_UP) and not on_ground:
                    if wall_left_contact and (keys_pressed_current_frame[pygame.K_RIGHT] or keys_pressed_current_frame[pygame.K_d]):
                        player_vel_y = WALL_JUMP_VERTICAL_PUSH
                        player_pos[0] += WALL_JUMP_HORIZONTAL_PUSH
                        is_jumping = True
                        play_tone(MUSIC_NOTES_FREQ['C5'] * 1.5, 70, 0.2)
                    elif wall_right_contact and (keys_pressed_current_frame[pygame.K_LEFT] or keys_pressed_current_frame[pygame.K_a]):
                        player_vel_y = WALL_JUMP_VERTICAL_PUSH
                        player_pos[0] -= WALL_JUMP_HORIZONTAL_PUSH
                        is_jumping = True
                        play_tone(MUSIC_NOTES_FREQ['C5'] * 1.5, 70, 0.2)
                    elif not is_jumping:
                        player_vel_y = JUMP_STRENGTH
                        is_jumping = True
                        play_tone(MUSIC_NOTES_FREQ['C5'] * 2, 70, 0.2)
                
                if event.key == pygame.K_r:
                    if player_pos[1] + PLAYER_HEIGHT < SCREEN_HEIGHT:
                        regenerate_world_in_place()
                
                if event.key == pygame.K_c:
                    current_theme_index = (current_theme_index + 1) % len(COLOR_THEMES)
                    update_colors_from_theme()
                    play_tone(MUSIC_NOTES_FREQ['A4'], 50, 0.1)

            if event.key == pygame.K_ESCAPE:
                if game_state == TUTORIAL or game_state == GENERATION_INFO:
                    game_state = MENU
                else:
                    stop_all_music()
                    return False
            
            if game_state == GAME_OVER_STATE and event.key == pygame.K_r:
                game_state = PLAYING
                reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if game_state == MENU:
                target_rect = None
                if start_button_rect and start_button_rect.collidepoint(mouse_x, mouse_y):
                    target_rect = start_button_rect
                    play_tone(MUSIC_NOTES_FREQ['C5'], 100, 0.2)
                    pygame.time.wait(50)
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
                
                if target_rect:
                    pygame.draw.rect(screen, COLORS["MENU_CLICK_FLASH"], target_rect.inflate(15, 15), 0)
                    pygame.display.flip()
                    pygame.time.wait(50)
            
            elif game_state == PLAYING and event.button == 1:
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


    if game_state == PLAYING:
        handle_music_playback(dt)

        keys = pygame.key.get_pressed()
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if moving_right:
            camera_x_offset += PLAYER_SPEED
        elif moving_left:
            if camera_x_offset > 0:
                camera_x_offset -= PLAYER_SPEED

        player_vel_y += GRAVITY
        player_pos[1] += player_vel_y

        player_pos[1] = clamp(player_pos[1], 0, SCREEN_HEIGHT - PLAYER_HEIGHT)

        player_rect = pygame.Rect(player_pos[0], player_pos[1], PLAYER_WIDTH, PLAYER_HEIGHT)

        on_ground = False

        for p in platforms:
            adjusted_platform_rect = p.move(-camera_x_offset, 0)
            if player_rect.colliderect(adjusted_platform_rect) and player_vel_y >= 0:
                if player_pos[1] + PLAYER_HEIGHT >= adjusted_platform_rect.top and player_pos[1] < adjusted_platform_rect.top + PLATFORM_HEIGHT:
                    player_pos[1] = adjusted_platform_rect.top - PLAYER_HEIGHT
                    player_vel_y = 0
                    is_jumping = False
                    on_ground = True
        if not on_ground and player_vel_y > 0:
            player_left_side_detector = pygame.Rect(player_rect.left - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)
            player_right_side_detector = pygame.Rect(player_rect.right - 2, player_rect.top + 5, 4, PLAYER_HEIGHT - 10)

            for wall_obj in walls + platforms:
                adjusted_wall_obj_rect = wall_obj.move(-camera_x_offset, 0)
                
                if player_left_side_detector.colliderect(adjusted_wall_obj_rect) and (keys[pygame.K_LEFT] or keys[pygame.K_a]):
                    is_jumping = True
                    break
                elif player_right_side_detector.colliderect(adjusted_wall_obj_rect) and (keys[pygame.K_RIGHT] or keys[pygame.K_d]):
                    player_vel_y = WALL_SLIDE_SPEED
                    player_vel_y = WALL_SLIDE_SPEED
                    is_jumping = True
                    break
        if player_pos[1] > SCREEN_HEIGHT:
            score += DEATH_BONUS
            game_state = GAME_OVER_STATE
            stop_all_music()
            play_tone(MUSIC_NOTES_FREQ['C4'] / 2, 200, 0.3)


        enemies_to_remove = []
        for enemy in enemies:
            enemy_rect_adjusted = enemy['rect'].move(-camera_x_offset, 0)

            if enemy['type'] == 'flying':
                enemy['rect'].x += enemy['vx']
                if enemy['rect'].left <= 0 or enemy['rect'].right >= SCREEN_WIDTH * 5:
                    enemy['vx'] *= -1
            
            elif enemy['type'] == 'rolling':
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


            if enemy['id'] not in enemies_to_remove:
                if check_collision(player_rect, enemy_rect_adjusted):
                    health -= ENEMY_CONTACT_DAMAGE / FPS
                    if health <= 0:
                        game_state = GAME_OVER_STATE
                        stop_all_music()
                        play_tone(MUSIC_NOTES_FREQ['C4'], 200, 0.3)
                    player_pos[0] += (15 if player_pos[0] < enemy_rect_adjusted.centerx else -15)
                    play_tone(MUSIC_NOTES_FREQ['F4'] * 0.5, 50, 0.1)

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
                        play_tone(MUSIC_NOTES_FREQ['G4'] / 2, 100, 0.2)
                    else:
                        play_tone(MUSIC_NOTES_FREQ['G4'] * 1.5, 50, 0.15)
                    
                    lasers_to_remove_indices.append(i)
                    score += 10
                    break

        lasers = [laser for i, laser in enumerate(lasers) if i not in lasers_to_remove_indices]
        enemies[:] = [enemy for enemy in enemies if enemy['id'] not in enemies_to_remove]

    screen.fill(COLORS["SKY"])

    if game_state == PLAYING or game_state == GAME_OVER_STATE:
        for p in platforms:
            pygame.draw.rect(screen, COLORS["PLATFORM"], p.move(-camera_x_offset, 0))
            pygame.draw.line(screen, COLORS["DARK_ACCENT"], (p.left - camera_x_offset, p.top), (p.right - camera_x_offset, p.top), 3)

        for w in walls:
            pygame.draw.rect(screen, COLORS["WALL"], w.move(-camera_x_offset, 0))
            pygame.draw.line(screen, COLORS["DARK_ACCENT"], (w.left - camera_x_offset, w.top), (w.left - camera_x_offset, w.bottom), 3)
            pygame.draw.line(screen, COLORS["DARK_ACCENT"], (w.right - camera_x_offset, w.top), (w.right - camera_x_offset, w.bottom), 3)


        draw_player(screen, player_rect, COLORS["PLAYER"])

        for enemy in enemies:
            enemy_rect_draw = enemy['rect'].move(-camera_x_offset, 0)
            if enemy['type'] == 'standard': draw_enemy_standard(screen, enemy_rect_draw, COLORS["ENEMY_STANDARD"])
            elif enemy['type'] == 'flying': draw_enemy_flying(screen, enemy_rect_draw, COLORS["ENEMY_FLYING"])
            elif enemy['type'] == 'rolling': draw_enemy_rolling(screen, enemy_rect_draw, COLORS["ENEMY_ROLLING"])
            elif enemy['type'] == 'jumping': draw_enemy_jumping(screen, enemy_rect_draw, COLORS["ENEMY_JUMPING"])
            
        for laser in lasers:
            pygame.draw.rect(screen, COLORS["LASER"], laser['rect'])

        draw_text(screen, f"Score: {score}", 30, 10, 10, COLORS["MENU_TEXT"])
        draw_text(screen, f"Health: {max(0, int(health))}", 30, 10, 40, COLORS["MENU_TEXT"] if health > 30 else RED)
        draw_text(screen, "Controls: Arrows/WASD, Space/Up to Jump, Click to Shoot, R for New Map, C for Colors", 20, 10, SCREEN_HEIGHT - 30, COLORS["MENU_TEXT"])

    if game_state == GAME_OVER_STATE:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        
        draw_text(screen, "GAME OVER", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, RED, anchor='center')
        draw_text(screen, f"Final Score: {score}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20, COLORS["MENU_TEXT"], anchor='center')
        draw_text(screen, "Press R for New Game or ESC to Quit", 30, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, COLORS["MENU_TEXT"], anchor='center')

    elif game_state == MENU:
        screen.fill(COLORS["MENU_BG"])
        draw_text(screen, "Procedural Jump & Run", 60, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, COLORS["MENU_TEXT"], anchor='center')
        
        mouse_pos = pygame.mouse.get_pos()

        start_button_rect = draw_text(screen, "START GAME", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, COLORS["MENU_START_BTN"], anchor='center')
        if start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], start_button_rect.inflate(10, 10))

        tutorial_button_rect = draw_text(screen, "HOW TO PLAY", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40, COLORS["MENU_TUTORIAL_BTN"], anchor='center')
        if tutorial_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], tutorial_button_rect.inflate(10, 10))

        game_info_button_rect = draw_text(screen, "GAME DETAILS", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120, COLORS["MENU_INFO_BTN"], anchor='center')
        if game_info_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], game_info_button_rect.inflate(10, 10))
        
        quit_button_rect = draw_text(screen, "QUIT", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200, COLORS["MENU_QUIT_BTN"], anchor='center')
        if quit_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, COLORS["MENU_HOVER_FILL"], quit_button_rect.inflate(10, 10))


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


    pygame.display.flip()

    clock.tick(FPS)

    return True

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
def reset_game():
    global player_pos, player_vel_y, is_jumping, score, health, game_over, camera_x_offset, lasers, enemies, current_map_seed
    
    current_map_seed = random.randint(0, 1000000)
    generate_platforms_and_walls()

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


def regenerate_world_in_place():
    global player_pos, player_vel_y, is_jumping
    global camera_x_offset, current_map_seed, lasers, enemies

    old_world_x = player_pos[0] + camera_x_offset

    current_map_seed = random.randint(0, 1000000)
    generate_platforms_and_walls()
    enemies.clear()
    lasers.clear()
    spawn_enemies()
    generate_random_melody()

    player_vel_y = 0
    is_jumping = False

    target_platform = None
    for p in platforms:
        if p.x <= old_world_x <= p.x + p.width:
            target_platform = p
            break
    if not target_platform and platforms:
        target_platform = min(platforms, key=lambda p: abs((p.x + p.width/2) - old_world_x))

    if target_platform:
        camera_x_offset = max(0, int(target_platform.x - player_pos[0]))

    global current_music_note_idx, music_timer
    current_music_note_idx = 0
    music_timer = 0


if __name__ == "__main__":
    running = True
    
    start_button_rect = pygame.Rect(0,0,0,0)
    quit_button_rect = pygame.Rect(0,0,0,0)
    tutorial_button_rect = pygame.Rect(0,0,0,0)
    game_info_button_rect = pygame.Rect(0,0,0,0)
    tutorial_back_button_rect = pygame.Rect(0,0,0,0)

    COLOR_TO_NAME = {
        DEFAULT_BLUE_PLAYER: "Blue",
        DEFAULT_RED_ENEMY_LASER: "Red",
        DEFAULT_GREEN_PLATFORM: "Green",
        DEFAULT_YELLOW_ROLLING: "Yellow",
        DEFAULT_ORANGE_FLYING: "Orange",
        DEFAULT_PURPLE_JUMPING: "Purple",
        (80, 80, 80): "Dark Grey",
    }
    COLOR_TO_NAME[WHITE] = "White"
    COLOR_TO_NAME[BLACK] = "Black"
    COLOR_TO_NAME[DEFAULT_LIGHT_BLUE_SKY] = "Light Blue"

    generate_random_melody()
    update_colors_from_theme()

    clock = pygame.time.Clock()
    while running:
        running = game_loop()

    stop_all_music()
    pygame.quit()
