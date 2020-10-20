import pygame, math, sys
import data.engine as e
import data.objects as ob

pygame.init()
WIN_DIM = (800, 600)
g = 1.7

window = pygame.display.set_mode(WIN_DIM)
display = pygame.Surface(WIN_DIM)
pygame.mouse.set_visible(False)
start = False
scroll = [0, 0]

e.load_animations("data/Graphics/")

player_coord = [0, 0]
delta_player = [0, 0]
player = e.entity(player_coord[0], player_coord[1], 32, 64, "player")

cursor = pygame.image.load("data/Graphics/cursor.png").convert()
cursor.set_colorkey(e.black)

bullets = []

while True:
    player_coord = player.get_pos()
    pos = pygame.mouse.get_pos()
    display.fill(e.white)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_d:
                delta_player[0] = 10
            if event.key == pygame.K_a:
                delta_player[0] = -10
            if event.key == pygame.K_SPACE and collisions["bottom"]: #      if you press space in the first frame the game will crash
                delta_player[1] = - 20
            if event.key == pygame.K_s:
                start = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d or event.key == pygame.K_a:
                delta_player[0] = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            rot = -math.degrees(math.atan2(pos[1] - (int(player.get_center()[1])), pos[0] - (int(player.get_center()[0])))) - 90
            a = ob.Bullet([player_coord[0] + player.size_x / 2, player_coord[1] + player.size_y / 2], rot)
            bullets.append(a)
    if start:
        delta_player[1] += g
        if delta_player[1] > 9 * g:
            delta_player[1] = 9 * g

    collisions = player.move(delta_player, [pygame.Rect(0, 600, 800, 1)])
    player.display(display, scroll)
    player.change_frame(1)
    display.blit(pygame.transform.scale2x(cursor), (pos[0] - cursor.get_width() / 2, pos[1] - cursor.get_height() / 2))
    index = 0
    for bullet in bullets:
        bullet.display(display)
        bullet.move()
        if bullet.destroy(WIN_DIM):
            bullets.pop(index)
        index += 1
    window.blit(display, (0, 0))
    pygame.display.update()
