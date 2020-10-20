import data.engine as e

pygame.init()
WIN_DIM = (800, 600)

window = pygame.display.set_mode(WIN_DIM)
display = pygame.Surface(WIN_DIM)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    window.blit(display, (0, 0))
    pygame.display.update()