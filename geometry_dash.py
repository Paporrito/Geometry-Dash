import math
import random
import sys
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 560
GROUND_Y = 460
FPS = 60
SCROLL_SPEED = 7
GRAVITY = 0.85
JUMP_STRENGTH = -15.5
PLAYER_SIZE = 38

BG = (20, 24, 38)
BG2 = (42, 48, 74)
GROUND = (60, 205, 150)
GROUND_DARK = (26, 120, 95)
PLAYER = (255, 230, 109)
SPIKE = (255, 95, 95)
TEXT = (240, 244, 255)
ACCENT = (130, 190, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Sencillo")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 28, bold=True)
small_font = pygame.font.SysFont("arial", 20)


def make_level():
    x = WIDTH + 250
    level = []
    patterns = [
        [0], [0, 0], [0, 60], [0, 0, 70], [0], [0, 50], [0, 0],
        [0, 80], [0, 0, 0], [0], [0, 60], [0, 0], [0, 90], [0, 0, 50]
    ]
    for pattern in patterns:
        gap = random.randint(150, 250)
        x += gap
        for offset in pattern:
            level.append(pygame.Rect(x + offset, GROUND_Y - 34, 34, 34))
    return level


class Player:
    def __init__(self):
        self.rect = pygame.Rect(140, GROUND_Y - PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
        self.vel_y = 0
        self.on_ground = True
        self.angle = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
            self.angle = 0
        else:
            self.angle = (self.angle - 8) % 360

    def draw(self, surface):
        base = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(base, PLAYER, (0, 0, PLAYER_SIZE, PLAYER_SIZE), border_radius=6)
        pygame.draw.rect(base, (40, 40, 60), (8, 9, 7, 7), border_radius=2)
        pygame.draw.rect(base, (40, 40, 60), (23, 9, 7, 7), border_radius=2)
        pygame.draw.rect(base, (40, 40, 60), (10, 23, 18, 5), border_radius=2)
        rotated = pygame.transform.rotate(base, self.angle)
        rotated_rect = rotated.get_rect(center=self.rect.center)
        surface.blit(rotated, rotated_rect)


def draw_background(ticks):
    screen.fill(BG)
    for i in range(7):
        x = (i * 180 - (ticks * 2) % 180)
        pygame.draw.rect(screen, BG2, (x, 310, 90, 150), border_radius=10)
        pygame.draw.rect(screen, (30, 35, 56), (x + 25, 250, 40, 210), border_radius=8)

    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, (25, 29, 46), (x, GROUND_Y), (x + 20, HEIGHT), 2)

    pygame.draw.rect(screen, GROUND, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    pygame.draw.rect(screen, GROUND_DARK, (0, GROUND_Y, WIDTH, 8))


def draw_spike(surface, rect):
    points = [
        (rect.left, rect.bottom),
        (rect.centerx, rect.top),
        (rect.right, rect.bottom),
    ]
    pygame.draw.polygon(surface, SPIKE, points)
    pygame.draw.polygon(surface, (255, 210, 210), points, 3)


def reset_game():
    return Player(), make_level(), 0, False


player, obstacles, score, game_over = reset_game()

while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if game_over:
                    player, obstacles, score, game_over = reset_game()
                else:
                    player.jump()
            if event.key == pygame.K_r:
                player, obstacles, score, game_over = reset_game()

    if not game_over:
        player.update()

        for spike in obstacles:
            spike.x -= SCROLL_SPEED

        if obstacles and obstacles[0].right < 0:
            passed = [o for o in obstacles if o.right < 0]
            if passed:
                score += len(passed)
            obstacles = [o for o in obstacles if o.right >= 0]

        if len(obstacles) < 7:
            tail = obstacles[-1].x if obstacles else WIDTH
            extra = random.choice([[0], [0, 50], [0, 0], [0, 70], [0, 0, 55]])
            start = tail + random.randint(180, 270)
            for offset in extra:
                obstacles.append(pygame.Rect(start + offset, GROUND_Y - 34, 34, 34))

        for spike in obstacles:
            if player.rect.colliderect(spike.inflate(-10, -6)):
                game_over = True
                break

    draw_background(pygame.time.get_ticks() / 10)

    for spike in obstacles:
        draw_spike(screen, spike)

    player.draw(screen)

    title = font.render(f"Puntos: {score}", True, TEXT)
    screen.blit(title, (24, 20))

    info = small_font.render("ESPACIO / ARRIBA para saltar   |   R para reiniciar", True, ACCENT)
    screen.blit(info, (24, 54))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        msg = font.render("Has perdido", True, TEXT)
        msg2 = small_font.render("Pulsa ESPACIO o R para volver a empezar", True, TEXT)
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 18)))
        screen.blit(msg2, msg2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 18)))

    pygame.display.flip()