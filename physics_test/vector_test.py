from physics_test.vec2d import Vec2d
import pygame


if __name__ == '__main__':
    pygame.init()

    size = [800, 800]

    screen_real = pygame.display.set_mode(size)
    screen = pygame.Surface(size)
    c1, c2 = Vec2d(300, 300), Vec2d(300, 300)
    v1, v2 = Vec2d(200, -50), Vec2d(25, -100)

    running = True
    c = None
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if c is not None:
                        c = None
                    else:
                        if (c1 - event.pos).get_length_sqrd() <= (c2 - event.pos).get_length_sqrd():
                            c = [c1, v1]
                        else:
                            c = [c2, v2]
                elif event.button == 5:
                    if c is not None:
                        c[1].rotate(2)
                elif event.button == 4:
                    if c is not None:
                        c[1].rotate(-2)
        ms = pygame.mouse.get_pos()
        if c is not None:
            c[0][0], c[0][1] = ms[0], ms[1]
        to_2 = c2 - c1
        cd = c2
        d = v2.intersection(v1, -to_2)
        print(d)

        screen.fill((255, 255, 255))
        pygame.draw.line(screen, (255, 0, 0), c1, c1 + v1, 2)
        pygame.draw.line(screen, (0, 0, 255), c2, c2 + v2, 2)
        pygame.draw.line(screen, (0, 0, 0), c1, c1 + to_2, 2)
        pygame.draw.line(screen, (0, 255, 0), cd, cd + d, 2)
        screen_real.blit(pygame.transform.flip(screen, False, False), (0, 0))

        pygame.display.flip()

    pygame.quit()
