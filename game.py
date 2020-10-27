import pygame, math, sys
import data.engine as e
import data.objects as ob
import random

pygame.init()
WIN_DIM = (800, 600)
g = 2
window = pygame.display.set_mode(WIN_DIM)
display = pygame.Surface(WIN_DIM)

font_1 = e.generate_font('data/fonts/small_font.png', e.font_dat, 5, 8, (185,57,57))
font_2 = e.generate_font('data/fonts/small_font.png', e.font_dat, 5, 8, (51,34,40))

pygame.mouse.set_visible(False)
friction = 0.4
player_vel = 2
max_vel = 5

e.load_animations("data/Graphics/")
e.enable_particles()

delta_player = [0, 0]
player_coord = [0, 0]
left = right = up = down = False
player = e.entity(player_coord[0], player_coord[1], 32, 64, "player", colorkey=e.white)
boom = []

cursor = pygame.image.load("data/Graphics/cursor.png").convert()
cursor.set_colorkey(e.black)

bullets = []
clock = pygame.time.Clock()

while True:
    display.fill(e.light_blue)
    player_coord = player.get_pos()
    pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_d:
                right = True
            if event.key == pygame.K_a:
                left = True
            if event.key == pygame.K_w:
                up = True
            if event.key == pygame.K_s:
                down = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                right = False
            if event.key == pygame.K_a:
                left = False
            if event.key == pygame.K_w:
                up = False
            if event.key == pygame.K_s:
                down = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                rot = -math.degrees(math.atan2(pos[1] - (int(player.get_center()[1])), pos[0] - (int(player.get_center()[0])))) - 90
                a = ob.Bullet([player_coord[0] + player.size_x / 2, player_coord[1] + player.size_y / 2], rot)
                bullets.append(a)
            if event.button == 3:
                for i in range(10):
                    boom.append(e.Particle(pos[0] - 16 / 2, pos[1] - 16 / 2, (10 * random.uniform(-2, 2), 10 * random.uniform(-2, 2)), 16, 16, "boom", enable_physics=True, physics=[g, [pygame.Rect(0, 600, 800, 1)]]))

    if up:
        delta_player[1] += -player_vel
    if down:
        delta_player[1] += player_vel
    if left:
        delta_player[0] += -player_vel
    if right:
        delta_player[0] += player_vel

    if (not up) and (not down):
        if delta_player[1] > 0:
            delta_player[1] -= friction
        elif delta_player[1] < 0:
            delta_player[1] += friction
        if delta_player[1] < friction and delta_player[1] > 0:
            delta_player[1] = 0
    if (not left) and (not right):
        if delta_player[0] > 0:
            delta_player[0] -= friction
        elif delta_player[0] < 0:
            delta_player[0] += friction
        if delta_player[0] < friction and delta_player[0] > 0:
            delta_player[0] = 0

    if delta_player[0] >= max_vel:
        delta_player[0] = max_vel
    if delta_player[1] >= max_vel:
        delta_player[1] = max_vel
    if delta_player[0] <= -max_vel:
        delta_player[0] = -max_vel
    if delta_player[1] <= -max_vel:
        delta_player[1] = -max_vel

    if delta_player[0] != 0 or delta_player[1] != 0:
        player.set_action("running")
    else:
        player.set_action("idle")

    delta_player[1] = g

    collisions = player.move(delta_player, [pygame.Rect(0, 600, 800, 1)])

    e.show_text("SUPER GIOCO FANTASTICO!!!", 0, 0, 185, font_2, display, scaling=5)
    player.display(display)
    player.change_frame(1)
    display.blit(pygame.transform.scale2x(cursor), (pos[0] - cursor.get_width() / 2, pos[1] - cursor.get_height() / 2))
    index = 0
    for bullet in bullets:
        bullet.display(display)
        bullet.move()
        if bullet.destroy(WIN_DIM):
            bullets.pop(index)
        index += 1
    index = 0
    for particle in boom:
        if particle.is_alive():
            particle.play(display)
        else:
            boom.pop(index)
        index += 1

    window.blit(display, (0, 0))
    pygame.display.update()
    clock.tick(60)