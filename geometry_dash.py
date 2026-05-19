import traceback
import sys
import random
import pygame
import os

# Forzar posicion de ventana en el centro
os.environ["SDL_VIDEO_CENTERED"] = "1"
# Forzar driver de video de Windows
os.environ["SDL_VIDEODRIVER"] = "windib"

def main():
    pygame.init()

    WIDTH, HEIGHT = 1000, 560
    GROUND_Y = 460
    FPS = 60
    GRAVITY = 0.85
    JUMP_STRENGTH = -15.5
    PLAYER_SIZE = 38

    BG          = (20,  24,  38)
    BG2         = (42,  48,  74)
    GROUND_COL  = (60,  205, 150)
    GROUND_DARK = (26,  120, 95)
    PLAYER_COL  = (255, 230, 109)
    SPIKE_COL   = (255, 95,  95)
    TEXT_COL    = (240, 244, 255)
    ACCENT      = (130, 190, 255)
    WHITE       = (255, 255, 255)
    DARK        = (12,  15,  28)
    BTN_GOLD    = (255, 200, 60)
    BTN_GOLD_H  = (255, 230, 110)
    BTN_BLUE    = (80,  160, 255)
    BTN_BLUE_H  = (130, 200, 255)
    BTN_GREEN   = (60,  210, 130)
    BTN_GREEN_H = (100, 240, 170)
    BTN_RED     = (220, 70,  70)
    BTN_RED_H   = (255, 110, 110)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Geometry Dash")
    clock  = pygame.time.Clock()

    font_big   = pygame.font.SysFont("arial", 36, bold=True)
    font_title = pygame.font.SysFont("arial", 64, bold=True)
    font_med   = pygame.font.SysFont("arial", 26, bold=True)
    font_small = pygame.font.SysFont("arial", 19)
    font_tiny  = pygame.font.SysFont("arial", 15)

    LEVELS = [
        {"name": "Stereo Madness",  "color": (100, 180, 255), "speed": 6,  "difficulty": "Facil"},
        {"name": "Back On Track",   "color": (120, 220, 140), "speed": 7,  "difficulty": "Facil"},
        {"name": "Polargeist",      "color": (200, 130, 255), "speed": 8,  "difficulty": "Normal"},
        {"name": "Dry Out",         "color": (255, 180, 80),  "speed": 8,  "difficulty": "Normal"},
        {"name": "Base After Base", "color": (255, 120, 120), "speed": 9,  "difficulty": "Normal"},
        {"name": "Can't Let Go",    "color": (80,  210, 220), "speed": 10, "difficulty": "Dificil"},
        {"name": "Jumper",          "color": (255, 200, 60),  "speed": 10, "difficulty": "Dificil"},
        {"name": "Time Machine",    "color": (180, 100, 255), "speed": 11, "difficulty": "Dificil"},
        {"name": "Cycles",          "color": (255, 100, 180), "speed": 12, "difficulty": "Muy Dificil"},
        {"name": "xStep",           "color": (100, 255, 180), "speed": 13, "difficulty": "Muy Dificil"},
    ]

    STATE = "MAIN_MENU"
    current_level_idx = [0]

    def draw_rect_alpha(surf, color, rect, radius=0):
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, color, (0, 0, rect[2], rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))

    def draw_button(surf, rect, color, hover_color, text, font, mouse_pos, radius=12):
        hovered = rect.collidepoint(mouse_pos)
        col = hover_color if hovered else color
        sr = rect.move(3, 4)
        draw_rect_alpha(surf, (0, 0, 0, 80), (sr.x, sr.y, sr.w, sr.h), radius)
        pygame.draw.rect(surf, col, rect, border_radius=radius)
        pygame.draw.rect(surf, (255, 255, 255), rect, width=2, border_radius=radius)
        label = font.render(text, True, DARK)
        surf.blit(label, label.get_rect(center=rect.center))
        return hovered

    def draw_player_icon(surf, cx, cy, size, angle=0):
        base = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(base, PLAYER_COL, (0, 0, size, size), border_radius=6)
        s = size // 5
        pygame.draw.rect(base, (40, 40, 60), (s,   s,   s, s), border_radius=2)
        pygame.draw.rect(base, (40, 40, 60), (3*s, s,   s, s), border_radius=2)
        pygame.draw.rect(base, (40, 40, 60), (s+2, 3*s-2, 3*s-4, s-4), border_radius=2)
        rot = pygame.transform.rotate(base, angle)
        surf.blit(rot, rot.get_rect(center=(cx, cy)))

    def draw_bg(ticks):
        screen.fill(BG)
        for i in range(8):
            x = (i * 160 - (ticks * 2) % 160)
            pygame.draw.rect(screen, BG2, (x, 300, 80, 260), border_radius=8)
            pygame.draw.rect(screen, (30, 35, 56), (x + 22, 240, 36, 320), border_radius=6)
        for x in range(0, WIDTH, 40):
            pygame.draw.line(screen, (25, 29, 46), (x, GROUND_Y), (x + 20, HEIGHT), 2)
        pygame.draw.rect(screen, GROUND_COL,  (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(screen, GROUND_DARK, (0, GROUND_Y, WIDTH, 8))

    def draw_spike(rect):
        pts = [(rect.left, rect.bottom), (rect.centerx, rect.top), (rect.right, rect.bottom)]
        pygame.draw.polygon(screen, SPIKE_COL, pts)
        pygame.draw.polygon(screen, (255, 210, 210), pts, 2)

    # Demo menu
    menu_angle = [0]
    demo_spikes = [pygame.Rect(WIDTH + i * 220, GROUND_Y - 34, 34, 34) for i in range(6)]

    def update_demo():
        for sp in demo_spikes:
            sp.x -= 5
        to_remove = [sp for sp in demo_spikes if sp.right < 0]
        for sp in to_remove:
            demo_spikes.remove(sp)
        while len(demo_spikes) < 6:
            tail = demo_spikes[-1].x if demo_spikes else WIDTH
            demo_spikes.append(pygame.Rect(tail + random.randint(200, 320), GROUND_Y - 34, 34, 34))

    # Juego
    class Player:
        def __init__(self):
            self.rect      = pygame.Rect(140, GROUND_Y - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
            self.vel_y     = 0
            self.on_ground = True
            self.angle     = 0
        def jump(self):
            if self.on_ground:
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
        def update(self):
            self.vel_y += GRAVITY
            self.rect.y += int(self.vel_y)
            if self.rect.bottom >= GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.vel_y = 0
                self.on_ground = True
                self.angle = 0
            else:
                self.angle = (self.angle - 8) % 360

    def make_obstacles():
        x = WIDTH + 250
        obs = []
        patterns = [[0],[0,0],[0,60],[0,0,70],[0],[0,50],[0,0],[0,80],[0,0,0],[0],[0,60],[0,0],[0,90],[0,0,50]]
        for pattern in patterns:
            x += random.randint(140, 240)
            for offset in pattern:
                obs.append(pygame.Rect(x + offset, GROUND_Y - 34, 34, 34))
        return obs

    game = {
        "player": Player(),
        "obstacles": make_obstacles(),
        "score": 0,
        "over": False,
        "speed": 7,
    }

    def reset_game(idx):
        game["player"]    = Player()
        game["obstacles"] = make_obstacles()
        game["score"]     = 0
        game["over"]      = False
        game["speed"]     = LEVELS[idx]["speed"]

    COLS   = 5
    CARD_W, CARD_H = 160, 120
    CARD_GAP = 16
    GRID_X = (WIDTH - (COLS * CARD_W + (COLS - 1) * CARD_GAP)) // 2
    GRID_Y = 130

    running = True
    while running:
        clock.tick(FPS)
        ticks     = pygame.time.get_ticks() / 10
        mouse_pos = pygame.mouse.get_pos()
        click     = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
            if event.type == pygame.KEYDOWN:
                if STATE == "PLAYING":
                    if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                        if game["over"]:
                            reset_game(current_level_idx[0])
                        else:
                            game["player"].jump()
                    if event.key == pygame.K_ESCAPE:
                        STATE = "MAIN_MENU"
                else:
                    if event.key == pygame.K_ESCAPE:
                        STATE = "MAIN_MENU"

        # ── MAIN MENU ────────────────────────────────────────────
        if STATE == "MAIN_MENU":
            menu_angle[0] = (menu_angle[0] - 3) % 360
            update_demo()
            draw_bg(ticks)
            for sp in demo_spikes:
                draw_spike(sp)
            draw_player_icon(screen, 130, GROUND_Y - PLAYER_SIZE // 2, PLAYER_SIZE, menu_angle[0])

            sh = font_title.render("Geometry Dash", True, (0, 0, 0))
            tx = font_title.render("Geometry Dash", True, BTN_GOLD)
            screen.blit(sh, sh.get_rect(center=(WIDTH//2 + 3, 95)))
            screen.blit(tx, tx.get_rect(center=(WIDTH//2, 92)))

            btn_play = pygame.Rect(WIDTH//2 - 200, 210, 180, 70)
            btn_cust = pygame.Rect(WIDTH//2 + 20,  210, 180, 70)
            btn_exit = pygame.Rect(WIDTH - 110, 14, 90, 36)
            draw_button(screen, btn_play, BTN_GREEN, BTN_GREEN_H, "JUGAR",  font_big,   mouse_pos)
            draw_button(screen, btn_cust, BTN_BLUE,  BTN_BLUE_H,  "ICONO",  font_big,   mouse_pos)
            draw_button(screen, btn_exit, BTN_RED,   BTN_RED_H,   "Salir",  font_small, mouse_pos, radius=8)

            hint = font_tiny.render("Geometry Dash en Python  -  v0.1", True, (100, 110, 140))
            screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 18)))

            if click:
                if btn_play.collidepoint(mouse_pos):
                    STATE = "LEVEL_SELECT"
                elif btn_cust.collidepoint(mouse_pos):
                    STATE = "CUSTOMIZE"
                elif btn_exit.collidepoint(mouse_pos):
                    running = False

        # ── CUSTOMIZE ────────────────────────────────────────────
        elif STATE == "CUSTOMIZE":
            draw_bg(ticks)
            draw_rect_alpha(screen, (0, 0, 0, 160), (80, 60, WIDTH - 160, HEIGHT - 120), radius=18)
            t = font_big.render("Personalizar icono", True, BTN_GOLD)
            screen.blit(t, t.get_rect(center=(WIDTH//2, 110)))
            pygame.draw.rect(screen, (40, 45, 70), (WIDTH//2 - 70, 155, 140, 140), border_radius=14)
            pygame.draw.rect(screen, BTN_GOLD, (WIDTH//2 - 70, 155, 140, 140), width=2, border_radius=14)
            draw_player_icon(screen, WIDTH//2, 225, 76)
            i1 = font_med.render("Solo hay un icono disponible por ahora.", True, TEXT_COL)
            i2 = font_small.render("Mas personalizaciones proximamente!", True, (130, 140, 180))
            screen.blit(i1, i1.get_rect(center=(WIDTH//2, 330)))
            screen.blit(i2, i2.get_rect(center=(WIDTH//2, 365)))