import pygame
import random
import sys
import os
import json
import numpy as np

pygame.init()
pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
GOLD = (255, 215, 0)
PURPLE = (147, 112, 219)

# Resolutions list
RESOLUTIONS = [(800, 600), (1024, 768), (1280, 720), (1920, 1080), "FULLSCREEN"]
BLOCK_SIZES = [15, 20, 25, 30, 40]

# Default values
DEFAULT_RES_INDEX = 4 # Fullscreen
DEFAULT_BLOCK_SIZE = 20
DEFAULT_BASE_SPEED = 6.0

# Display init
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
dis = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption('Snake Game Pro')

clock = pygame.time.Clock()

# Fonts
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)
title_font = pygame.font.SysFont("impact", 60)
menu_font = pygame.font.SysFont("bahnschrift", 30)
input_font = pygame.font.SysFont("bahnschrift", 40)
timer_font = pygame.font.SysFont("bahnschrift", 18)

# Files
LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE = "settings.json"

# Themes
THEMES = {
    "Midnight Blue": [(15, 30, 60), (30, 50, 80), (40, 70, 100)],
    "Soft Charcoal": [(30, 30, 30), (50, 50, 50), (70, 70, 70)],
    "Forest Night": [(20, 35, 20), (35, 55, 35), (50, 75, 50)],
    "Warm Dusk": [(35, 28, 18), (55, 45, 30), (75, 65, 50)],
    "Ocean Deep": [(15, 32, 39), (25, 52, 63), (45, 72, 83)]
}
THEME_NAMES = list(THEMES.keys())

settings = {
    "theme": "Midnight Blue",
    "sound_on": True,
    "last_player": ""
}

def load_settings():
    global settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings.update(json.load(f))
        except:
            pass

def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_leaderboard(data):
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f)

def get_top_players(data, n=5):
    return sorted(data.items(), key=lambda x: x[1], reverse=True)[:n]

def make_beep(freq, duration):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    wave = 0.5 * np.sin(freq * 2 * np.pi * t)
    audio = (wave * 127 + 128).astype(np.uint8)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

eat_sound = make_beep(800, 0.1)
die_sound = make_beep(200, 0.3)
powerup_sound = make_beep(1200, 0.15)
tick_sound = make_beep(600, 0.05)
poof_sound = make_beep(400, 0.2)

def play_sound(sound):
    if settings["sound_on"]:
        sound.play()

def get_theme_colors():
    return THEMES[settings["theme"]]

def draw_gradient_background(w, h):
    bg_dark, bg_light, _ = get_theme_colors()
    for y in range(h):
        ratio = y / h
        r = int(bg_dark[0] + (bg_light[0] - bg_dark[0]) * ratio)
        g = int(bg_dark[1] + (bg_light[1] - bg_dark[1]) * ratio)
        b = int(bg_dark[2] + (bg_light[2] - bg_dark[2]) * ratio)
        pygame.draw.line(dis, (r, g, b), (0, y), (w, y))

def draw_grid(w, h, block_size):
    _, _, grid_color = get_theme_colors()
    for x in range(0, w, block_size):
        pygame.draw.line(dis, grid_color, (x, 0), (x, h))
    for y in range(0, h, block_size):
        pygame.draw.line(dis, grid_color, (0, y), (w, y))

def draw_snake(snake_list, direction, block_size):
    for i, segment in enumerate(snake_list):
        if i == len(snake_list) - 1:
            pygame.draw.rect(dis, DARK_GREEN, [segment[0], segment[1], block_size, block_size])
            eye_size = max(2, block_size // 6)
            offset = block_size // 4
            if direction == 'RIGHT':
                pygame.draw.circle(dis, WHITE, (segment[0] + block_size - offset, segment[1] + offset), eye_size)
                pygame.draw.circle(dis, WHITE, (segment[0] + block_size - offset, segment[1] + block_size - offset), eye_size)
            elif direction == 'LEFT':
                pygame.draw.circle(dis, WHITE, (segment[0] + offset, segment[1] + offset), eye_size)
                pygame.draw.circle(dis, WHITE, (segment[0] + offset, segment[1] + block_size - offset), eye_size)
            elif direction == 'UP':
                pygame.draw.circle(dis, WHITE, (segment[0] + offset, segment[1] + offset), eye_size)
                pygame.draw.circle(dis, WHITE, (segment[0] + block_size - offset, segment[1] + offset), eye_size)
            elif direction == 'DOWN':
                pygame.draw.circle(dis, WHITE, (segment[0] + offset, segment[1] + block_size - offset), eye_size)
                pygame.draw.circle(dis, WHITE, (segment[0] + block_size - offset, segment[1] + block_size - offset), eye_size)
        else:
            pygame.draw.rect(dis, GREEN, [segment[0], segment[1], block_size, block_size])
            pygame.draw.rect(dis, DARK_GREEN, [segment[0], segment[1], block_size, block_size], 2)

def draw_food(x, y, food_type, timer, block_size):
    if food_type == 'normal':
        pygame.draw.rect(dis, RED, [x, y, block_size, block_size])
    elif food_type == 'gold':
        pygame.draw.rect(dis, GOLD, [x, y, block_size, block_size])
        inner = block_size // 5
        pygame.draw.rect(dis, YELLOW, [x+inner, y+inner, block_size-2*inner, block_size-2*inner])
    elif food_type == 'poison':
        blink = True
        if timer == 2:
            blink = pygame.time.get_ticks() % 500 < 250
        elif timer == 1:
            blink = pygame.time.get_ticks() % 200 < 100
        if blink:
            pygame.draw.rect(dis, PURPLE, [x, y, block_size, block_size])
            dot = block_size // 3
            pygame.draw.rect(dis, WHITE, [x+dot, y+dot, dot, dot])
        if timer > 0:
            timer_text = timer_font.render(str(timer), True, WHITE)
            text_rect = timer_text.get_rect(center=(x + block_size//2, y - 10))
            pygame.draw.rect(dis, BLACK, text_rect.inflate(6, 2))
            dis.blit(timer_text, text_rect)

def show_notification(text, duration=60):
    return {"text": text, "timer": duration}

def draw_notification(notif):
    if notif and notif["timer"] > 0:
        notif_text = menu_font.render(notif["text"], True, YELLOW)
        text_rect = notif_text.get_rect(center=(WIDTH/2, 100))
        pygame.draw.rect(dis, BLACK, text_rect.inflate(20, 10))
        pygame.draw.rect(dis, YELLOW, text_rect.inflate(20, 10), 2)
        dis.blit(notif_text, text_rect)
        notif["timer"] -= 1

def show_score(score, level, player_name, highscore, purple_dodged, speed, manual_speed, block_size, w, h):
    value = score_font.render(f"Score: {score}", True, YELLOW)
    level_text = font_style.render(f"Level: {level}", True, WHITE)
    player_text = font_style.render(f"Player: {player_name}", True, WHITE)
    high_text = font_style.render(f"High: {highscore}", True, GOLD)
    dodge_text = font_style.render(f"Dodged: {purple_dodged}/3", True, PURPLE)
    speed_text = font_style.render(f"Speed: {speed:.1f} {'[M]' if manual_speed else '[A]'}", True, WHITE)
    size_text = font_style.render(f"Block: {block_size}px | {w}x{h}", True, WHITE)
    dis.blit(value, [10, 10])
    dis.blit(level_text, [10, 50])
    dis.blit(player_text, [10, 90])
    dis.blit(dodge_text, [10, 130])
    dis.blit(speed_text, [10, 170])
    dis.blit(size_text, [10, h - 40])
    dis.blit(high_text, [w - 150, 10])

def particles(x, y, color):
    for _ in range(15):
        px = x + random.randint(-10, 30)
        py = y + random.randint(-10, 30)
        pygame.draw.circle(dis, color, (px, py), random.randint(2, 5))

def message(text, color, y_offset=0, font=menu_font):
    mesg = font.render(text, True, color)
    text_rect = mesg.get_rect(center=(WIDTH/2, HEIGHT/2 + y_offset))
    dis.blit(mesg, text_rect)

def draw_text(text, color, x, y, font=menu_font):
    mesg = font.render(text, True, color)
    dis.blit(mesg, (x, y))

def change_resolution(res_index):
    global WIDTH, HEIGHT, dis
    res = RESOLUTIONS[res_index]
    if res == "FULLSCREEN":
        info = pygame.display.Info()
        WIDTH, HEIGHT = info.current_w, info.current_h
        dis = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        WIDTH, HEIGHT = res
        dis = pygame.display.set_mode((WIDTH, HEIGHT))
    return f"Resolution: {WIDTH}x{HEIGHT}"

def name_input_screen():
    name = settings["last_player"]
    active = True
    while active:
        draw_gradient_background(WIDTH, HEIGHT)
        message("Enter Your Name", GOLD, -100, title_font)
        input_box = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 25, 400, 50)
        pygame.draw.rect(dis, WHITE, input_box, 2)
        txt_surface = input_font.render(name, True, WHITE)
        dis.blit(txt_surface, (input_box.x + 10, input_box.y + 5))
        message("Press ENTER to Confirm | ESC to Exit", WHITE, 80)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    settings["last_player"] = name.strip()
                    save_settings()
                    return name.strip()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 15 and event.unicode.isprintable():
                        name += event.unicode

def help_screen():
    active = True
    while active:
        draw_gradient_background(WIDTH, HEIGHT)
        message("HELP & RULES", GOLD, -280, title_font)
        y = HEIGHT//2 - 200
        draw_text("CONTROLS:", YELLOW, WIDTH//2 - 400, y, font_style)
        draw_text("Arrows - Move | SPACE - Pause | W - Wrap Walls | ESC - Exit", WHITE, WIDTH//2 - 400, y+30)
        draw_text("T - Themes | S - Sound | M - Manual/Auto Speed", WHITE, WIDTH//2 - 400, y+60)
        draw_text("CUSTOMIZE:", YELLOW, WIDTH//2 - 400, y+100, font_style)
        draw_text("+/- - Resolution | ]/[ - Block Size | =/- - Speed", WHITE, WIDTH//2 - 400, y+130)
        draw_text("F1-Chill F2-Normal F3-Insane Presets | Only when Paused", WHITE, WIDTH//2 - 400, y+160)
        draw_text("FOOD:", YELLOW, WIDTH//2 - 400, y+200, font_style)
        draw_text("Red +1 | Gold +5 +speed | Purple: Dodge 3 moves or -2", WHITE, WIDTH//2 - 400, y+230)
        draw_text("Dodge 3 purples = Next food Gold", WHITE, WIDTH//2 - 400, y+260)
        draw_text("LEVELS: Every 5 pts = +1 Level, +0.5 Speed in Auto mode", WHITE, WIDTH//2 - 400, y+290)
        message("Press ESC to Return", WHITE, 320)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                active = False

def theme_select_screen():
    global settings
    selected = THEME_NAMES.index(settings["theme"])
    active = True
    while active:
        draw_gradient_background(WIDTH, HEIGHT)
        message("SELECT THEME", GOLD, -200, title_font)
        for i, theme in enumerate(THEME_NAMES):
            color = YELLOW if i == selected else WHITE
            prefix = "> " if i == selected else " "
            draw_text(f"{prefix}{theme}", color, WIDTH//2 - 150, HEIGHT//2 - 80 + i*40)
        message("Arrows - Select | ENTER - Confirm | ESC - Cancel", WHITE, 200)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(THEME_NAMES)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(THEME_NAMES)
                elif event.key == pygame.K_RETURN:
                    settings["theme"] = THEME_NAMES[selected]
                    save_settings()
                    active = False
                elif event.key == pygame.K_ESCAPE:
                    active = False

def main_menu(player_name):
    leaderboard = load_leaderboard()
    while True:
        draw_gradient_background(WIDTH, HEIGHT)
        title = title_font.render("SNAKE PRO", True, GOLD)
        title_rect = title.get_rect(center=(WIDTH/2, HEIGHT/4))
        dis.blit(title, title_rect)
        draw_text(f"Player: {player_name}", WHITE, WIDTH//2 - 150, HEIGHT//2 - 120, menu_font)
        top = get_top_players(leaderboard, 1)
        if top:
            draw_text(f"High Score: {top[0][0]} - {top[0][1]}", GOLD, WIDTH//2 - 150, HEIGHT//2 - 80)
        message("1 - Single Player | 2 - Multi Player", WHITE, -20)
        message("H - Help | T - Themes | S - Sound: " + ("ON" if settings["sound_on"] else "OFF"), WHITE, 20)
        message("ESC - Exit", WHITE, 60)
        draw_text("TOP 5:", YELLOW, WIDTH//2 - 150, HEIGHT//2 + 120, font_style)
        for i, (name, score) in enumerate(get_top_players(leaderboard, 5)):
            draw_text(f"{i+1}. {name} - {score}", WHITE, WIDTH//2 - 150, HEIGHT//2 + 150 + i*25)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "single"
                elif event.key == pygame.K_2:
                    return "multi"
                elif event.key == pygame.K_h:
                    help_screen()
                elif event.key == pygame.K_t:
                    theme_select_screen()
                elif event.key == pygame.K_s:
                    settings["sound_on"] = not settings["sound_on"]
                    save_settings()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def spawn_food(snake_list, w, h, block_size, force_gold=False):
    while True:
        foodx = round(random.randrange(0, w - block_size) / block_size) * block_size
        foody = round(random.randrange(0, h - block_size) / block_size) * block_size
        if [foodx, foody] not in snake_list:
            break
    if force_gold:
        return foodx, foody, 'gold', 0
    rand = random.random()
    if rand < 0.7:
        return foodx, foody, 'normal', 0
    elif rand < 0.9:
        return foodx, foody, 'gold', 0
    else:
        return foodx, foody, 'poison', 3

def game_loop(player_name):
    # Reset all to defaults on new game
    res_index = DEFAULT_RES_INDEX
    block_size = DEFAULT_BLOCK_SIZE
    base_speed = DEFAULT_BASE_SPEED
    manual_speed = False
    change_resolution(res_index)

    game_over = False
    game_close = False
    paused = False
    wrap_walls = False
    notification = None

    x1 = WIDTH / 2
    y1 = HEIGHT / 2
    x1_change = 0
    y1_change = 0
    direction = 'RIGHT'

    snake_list = []
    length_of_snake = 1

    foodx, foody, food_type, purple_timer = spawn_food([], WIDTH, HEIGHT, block_size)

    score = 0
    level = 1
    snake_speed = base_speed
    leaderboard = load_leaderboard()
    highscore = leaderboard.get(player_name, 0)
    purple_dodged = 0
    guarantee_gold = False

    while not game_over:
        while game_close:
            draw_gradient_background(WIDTH, HEIGHT)
            message(f"Game Over - {player_name}", RED, -60, title_font)
            message(f"Final Score: {score} | Level: {level}", WHITE, -20)
            message("C-Play Again | M-Menu | ESC-Exit", WHITE, 20)
            if score > highscore:
                message("NEW HIGH SCORE!", GOLD, 60)
                leaderboard[player_name] = score
                save_leaderboard(leaderboard)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop(player_name) # Restart with defaults
                    if event.key == pygame.K_m:
                        return

        moved_this_frame = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Movement
                if event.key == pygame.K_LEFT and direction!= 'RIGHT':
                    x1_change = -block_size
                    y1_change = 0
                    direction = 'LEFT'
                    moved_this_frame = True
                elif event.key == pygame.K_RIGHT and direction!= 'LEFT':
                    x1_change = block_size
                    y1_change = 0
                    direction = 'RIGHT'
                    moved_this_frame = True
                elif event.key == pygame.K_UP and direction!= 'DOWN':
                    y1_change = -block_size
                    x1_change = 0
                    direction = 'UP'
                    moved_this_frame = True
                elif event.key == pygame.K_DOWN and direction!= 'UP':
                    y1_change = block_size
                    x1_change = 0
                    direction = 'DOWN'
                    moved_this_frame = True
                # Game controls
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_w:
                    wrap_walls = not wrap_walls
                elif event.key == pygame.K_t:
                    idx = THEME_NAMES.index(settings["theme"])
                    settings["theme"] = THEME_NAMES[(idx + 1) % len(THEME_NAMES)]
                    save_settings()
                    notification = show_notification(f"Theme: {settings['theme']}")
                elif event.key == pygame.K_s:
                    settings["sound_on"] = not settings["sound_on"]
                    save_settings()
                    notification = show_notification(f"Sound: {'ON' if settings['sound_on'] else 'OFF'}")
                elif event.key == pygame.K_m:
                    manual_speed = not manual_speed
                    notification = show_notification(f"Speed Mode: {'MANUAL' if manual_speed else 'AUTO'}")
                # Speed control - anytime
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    base_speed = min(20.0, base_speed + 1.0)
                    notification = show_notification(f"Speed: {base_speed:.1f}")
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    base_speed = max(3.0, base_speed - 1.0)
                    notification = show_notification(f"Speed: {base_speed:.1f}")
                # Presets - only when paused
                elif event.key == pygame.K_F1 and paused:
                    block_size = 30
                    base_speed = 4.0
                    res_index = 2
                    change_resolution(res_index)
                    notification = show_notification("Preset: Chill")
                    foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                elif event.key == pygame.K_F2 and paused:
                    block_size = 20
                    base_speed = 6.0
                    res_index = 4
                    change_resolution(res_index)
                    notification = show_notification("Preset: Normal")
                    foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                elif event.key == pygame.K_F3 and paused:
                    block_size = 15
                    base_speed = 12.0
                    res_index = 4
                    change_resolution(res_index)
                    notification = show_notification("Preset: Insane")
                    foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                # Resolution - only when paused
                elif event.key == pygame.K_PLUS and paused or event.key == pygame.K_KP_PLUS and paused:
                    res_index = min(len(RESOLUTIONS) - 1, res_index + 1)
                    msg = change_resolution(res_index)
                    notification = show_notification(msg)
                    foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                elif event.key == pygame.K_UNDERSCORE and paused:
                    res_index = max(0, res_index - 1)
                    msg = change_resolution(res_index)
                    notification = show_notification(msg)
                    foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                # Block size - only when paused
                elif event.key == pygame.K_RIGHTBRACKET and paused:
                    idx = BLOCK_SIZES.index(block_size)
                    if idx < len(BLOCK_SIZES) - 1:
                        block_size = BLOCK_SIZES[idx + 1]
                        notification = show_notification(f"Block Size: {block_size}px")
                        foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                elif event.key == pygame.K_LEFTBRACKET and paused:
                    idx = BLOCK_SIZES.index(block_size)
                    if idx > 0:
                        block_size = BLOCK_SIZES[idx - 1]
                        notification = show_notification(f"Block Size: {block_size}px")
                        foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size)
                elif event.key == pygame.K_ESCAPE:
                    game_over = True

        if paused:
            message("PAUSED", YELLOW, -40)
            message("+/- Res ]/[ Block =/- Speed F1/F2/F3 Presets", WHITE, 0)
            message("SPACE to Resume", WHITE, 40)
            pygame.display.update()
            clock.tick(5)
            continue

        # Speed calculation
        if manual_speed:
            snake_speed = base_speed
        else:
            snake_speed = base_speed + (level - 1) * 0.5
        # Cap speed based on block size to prevent blur
        max_speed = 600 / block_size
        snake_speed = min(snake_speed, max_speed)

        if wrap_walls:
            if x1 >= WIDTH: x1 = 0
            elif x1 < 0: x1 = WIDTH - block_size
            if y1 >= HEIGHT: y1 = 0
            elif y1 < 0: y1 = HEIGHT - block_size
        else:
            if x1 >= WIDTH or x1 < 0 or y1 >= HEIGHT or y1 < 0:
                play_sound(die_sound)
                game_close = True

        x1 += x1_change
        y1 += y1_change

        # Purple dodge timer
        if food_type == 'poison' and moved_this_frame and purple_timer > 0:
            purple_timer -= 1
            play_sound(tick_sound)
            if purple_timer == 0:
                particles(foodx, foody, PURPLE)
                play_sound(poof_sound)
                purple_dodged += 1
                if purple_dodged >= 3:
                    guarantee_gold = True
                    purple_dodged = 0
                foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size, guarantee_gold)
                guarantee_gold = False

        draw_gradient_background(WIDTH, HEIGHT)
        draw_grid(WIDTH, HEIGHT, block_size)
        draw_food(foodx, foody, food_type, purple_timer, block_size)

        snake_head = [x1, y1]
        snake_list.append(snake_head)
        if len(snake_list) > length_of_snake:
            del snake_list[0]

        if length_of_snake > 1:
            for segment in snake_list[:-1]:
                if segment == snake_head:
                    play_sound(die_sound)
                    game_close = True

        draw_snake(snake_list, direction, block_size)
        show_score(score, level, player_name, highscore, purple_dodged, snake_speed, manual_speed, block_size, WIDTH, HEIGHT)

        wall_text = font_style.render(f"Walls: {'WRAP' if wrap_walls else 'SOLID'}", True, GREEN if wrap_walls else RED)
        dis.blit(wall_text, [WIDTH - 200, 50])
        draw_notification(notification)

        pygame.display.update()

        if x1 == foodx and y1 == foody:
            particles(foodx, foody, YELLOW)
            if food_type == 'gold':
                score += 5
                length_of_snake += 5
                if not manual_speed:
                    base_speed += 0.2
                play_sound(powerup_sound)
                purple_dodged = 0
            elif food_type == 'poison':
                score = max(0, score - 2)
                length_of_snake = max(1, length_of_snake - 2)
                if not manual_speed:
                    base_speed = max(DEFAULT_BASE_SPEED, base_speed - 0.5)
                play_sound(die_sound)
                purple_dodged = 0
            else:
                score += 1
                length_of_snake += 1
                play_sound(eat_sound)

            level = score // 5 + 1
            foodx, foody, food_type, purple_timer = spawn_food(snake_list, WIDTH, HEIGHT, block_size, guarantee_gold)
            guarantee_gold = False

        clock.tick(snake_speed)

def multi_player_select():
    leaderboard = load_leaderboard()
    players = list(leaderboard.keys())
    if not players:
        players = [settings["last_player"]] if settings["last_player"] else ["Player1"]
    selected = 0
    active = True
    while active:
        draw_gradient_background(WIDTH, HEIGHT)
        message("SELECT PLAYER", GOLD, -200, title_font)
        for i, name in enumerate(players + ["+ New Player"]):
            color = YELLOW if i == selected else WHITE
            prefix = "> " if i == selected else " "
            score = leaderboard.get(name, 0) if name in leaderboard else 0
            draw_text(f"{prefix}{name} - Best: {score}", color, WIDTH//2 - 200, HEIGHT//2 - 80 + i*40)
        message("Arrows - Select | ENTER - Confirm | ESC - Back", WHITE, 200)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % (len(players) + 1)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % (len(players) + 1)
                elif event.key == pygame.K_RETURN:
                    if selected == len(players):
                        return name_input_screen()
                    else:
                        return players[selected]
                elif event.key == pygame.K_ESCAPE:
                    return None

if __name__ == "__main__":
    load_settings()
    player_name = name_input_screen()
    while True:
        mode = main_menu(player_name)
        if mode == "single":
            game_loop(player_name)
        elif mode == "multi":
            selected_player = multi_player_select()
            if selected_player:
                game_loop(selected_player)