import traceback
import sys

try:
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Test")
    font = pygame.font.SysFont("arial", 28, bold=True)
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((30, 30, 50))
        label = font.render("Funciona! Cierra esta ventana.", True, (255,255,255))
        screen.blit(label, (20, 130))
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
except Exception as e:
    print("ERROR CAPTURADO:")
    traceback.print_exc()
    input("Presiona Enter para cerrar...")