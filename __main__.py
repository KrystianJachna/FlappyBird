import pygame
import  sys
import random
from pathlib import Path

project_dir = Path(__file__).parent
pygame.mixer.init()
pygame.init()
pygame.display.set_caption("FlappyBird")

E = 7
WHITE = (255, 255, 255)
WIDTH, HEIGHT = 576, 1024
BASE_HEIGHT = 150
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60
BIRD_WIDTH = 70
BIRD_HEIGHT = 50
BACKGROUND = pygame.transform.scale(
    pygame.image.load(
         (str(project_dir)) +"/sprites/background-day.png"),
    (WIDTH, HEIGHT)
)

BIRD_IMG0 = pygame.image.load(
        (str(project_dir)) + "/sprites/yellowbird-downflap.png")
BIRD_IMG1 = pygame.image.load(
       (str(project_dir)) +  "/sprites/yellowbird-midflap.png")
BIRD_IMG2 = pygame.image.load(
       (str(project_dir)) + "/sprites/yellowbird-upflap.png")
BIRD_IMAGES = [BIRD_IMG0, BIRD_IMG1, BIRD_IMG2]
BIRD = pygame.transform.scale(BIRD_IMG1, (BIRD_WIDTH, BIRD_HEIGHT))
GROUND = pygame.transform.scale(
    pygame.image.load(
       (str(project_dir)) + "/sprites/base.png"),
    (WIDTH, BASE_HEIGHT)
)
HIT_GROUND = pygame.USEREVENT + 1
GAMEOVER = pygame.transform.scale(
    pygame.image.load(
       (str(project_dir)) + "/sprites/gameover.png"),
    (WIDTH//2 + 100, BASE_HEIGHT)
)
GAMESTART = pygame.transform.scale(
    pygame.image.load(
       (str(project_dir)) + "/sprites/message.png"),
    (WIDTH//2, BASE_HEIGHT * 3)
)
POINTS_FONT = pygame.font.SysFont('Montserrat', 100)
BASE_WIDTH = GROUND.get_width()

PIPE_WIDTH = 110


PIPE_IMG = pygame.image.load(
    (str(project_dir)) + "/sprites/pipe-green.png")
PIPE_DOWN = pygame.transform.rotate(
    pygame.transform.scale(PIPE_IMG, (PIPE_WIDTH + E, 874)), 0)
PIPE_UP = pygame.transform.rotate(
    pygame.transform.scale(PIPE_IMG, (PIPE_WIDTH + E, 874)), 180)


start_sound = pygame.mixer.Sound((str(project_dir)) + "/music/swoosh.wav")
wing_sound = pygame.mixer.Sound((str(project_dir)) + "/music/wing.wav")
point_sound = pygame.mixer.Sound((str(project_dir)) + "/music/point.wav")
hit_sound = pygame.mixer.Sound((str(project_dir)) + "/music/hit.wav")



def draw_window(bird_body, start, end, points, base_x_pos, pipes, bird_velocity, bird_state):
    WIN.blit(BACKGROUND, (0, 0))

    if bird_velocity < 10:
        bird_angle = bird_velocity * 2
    else:
        bird_angle = bird_velocity * 1*2

    if bird_angle < -90:
        bird_angle = 90
    elif bird_angle > 30:
        bird_angle = 30


    bird = pygame.transform.scale(BIRD_IMAGES[bird_state], (BIRD_WIDTH, BIRD_HEIGHT))
    bird_rotated = pygame.transform.rotate(bird, bird_angle)
    WIN.blit(bird_rotated, (bird_body.x, bird_body.y))

    for pipe in pipes:
        WIN.blit(PIPE_UP, (pipe[0].x - E, pipe[0].y + E))
        WIN.blit(PIPE_DOWN, (pipe[1].x - E, pipe[1].y + E))
    WIN.blit(GROUND, (base_x_pos, 874))
    WIN.blit(GROUND, (base_x_pos + BASE_WIDTH, 874))



    points_text = POINTS_FONT.render(str(points), True, WHITE)
    if not start and not end:
        WIN.blit(points_text, (WIDTH // 2 - points_text.get_width() // 2, 200))
    elif start:
        WIN.blit(GAMESTART, (WIDTH // 2 - GAMESTART.get_width() // 2, 200))
    pygame.display.update()


def handle_colision(bird, ground):
    if bird.colliderect(ground):
        pygame.event.post(pygame.event.Event(HIT_GROUND))


def game_over(points):

    WIN.blit(GAMEOVER, (WIDTH // 2 - GAMEOVER.get_width() // 2, 200))
    font = pygame.font.SysFont('Montserrat', 120)
    points_text = font.render("score: " + str(points), True, WHITE)
    best = 0
    with open(project_dir / 'best.txt', 'r', encoding='utf-8') as f:
        best = int(f.read().strip())
        f.close()

    newRec = False
    if points > best:
        best = points
        points_text = font.render("score: " + str(points), True, WHITE)
        newRec = True
        with open(project_dir / 'best.txt', 'w', encoding='utf-8') as f:
            f.write(str(points))
            f.close()
    font = pygame.font.SysFont('Montserrat', 120)
    if newRec:
        newB = font.render("NEW BEST!", True, (255,215,5))
        WIN.blit(newB, (WIDTH // 2 - newB.get_width() // 2, 390))

    WIN.blit(points_text, (WIDTH // 2 - points_text.get_width() // 2, 500)) 
    if not newRec:
        points_text = font.render("BEST: " + str(best), True, 	(255,215,0))
        WIN.blit(points_text, (WIDTH // 2 - points_text.get_width() // 2, 380))

    pygame.display.update()


def handle_pipes(pipes, base_move_speed, bird):
    for pipe in pipes:
        pipe[0].x -= base_move_speed
        pipe[1].x -= base_move_speed
        if bird.colliderect(pipe[1]) or bird.colliderect(pipe[0]) or (bird.y < 0 and  pipe[0].x<bird.x and bird.x<  pipe[0].x+ pipe[0].width):
            pygame.event.post(pygame.event.Event(HIT_GROUND))
        elif pipe[0].x + pipe[0].width < -100:
            pipes.remove(pipe)
        elif not pipe[2] and pipe[0].x + pipe[0].width < bird.x:
            pipe[2] = True
            return 1
    return 0

def main(space_between_pies):
    distance_between_pipes = 500
    clock = pygame.time.Clock()
    run = True
    bird_body = pygame.Rect(100, 500, BIRD_WIDTH, BIRD_HEIGHT)
    ground_body = pygame.Rect(0, 874, WIDTH, BASE_HEIGHT)
    gravity = 6                                   
    jump_speed = 20             
    jump_acceleration = 0.9     
    start = True
    points = 0

    bird_start_move_direct = 1
    i = 0

    j = 0
    bird_state = 0
    base_x_pos = 0
    base_move_speed = 1
    pipes = []
    road = distance_between_pipes



    while run:
        clock.tick(FPS)
        j += 1
        if j % 3 == 0:
            bird_state = (bird_state + 1) % 3

        if j == 1000:
            j = 0

        base_x_pos -= base_move_speed
        if base_x_pos < -BASE_WIDTH:
            base_x_pos = 0

        if start:
            bird_body.y += 1 * bird_start_move_direct
            if i == 20:                         # falowanie ptaka
                bird_start_move_direct *= -1
                i = 0
            i += 1
            draw_window(bird_body, start, False, points, base_x_pos, pipes, 0, 1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE :
                        start = False
                        base_move_speed = 5
                        start_sound.play()
                    if event.key == pygame.K_ESCAPE:
                        run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        start = False
                        base_move_speed = 3
                        start_sound.play()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    jump_speed = 20
                    wing_sound.play()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    jump_speed = 20
                    wing_sound.play()

            if event.type == HIT_GROUND:
                hit_sound.play()
                gravity = 0
                tmp = jump_speed
                jump_speed = 0
                jump_acceleration = 0
                draw_window(bird_body, start, True, points, base_x_pos, pipes, tmp, bird_state)
                game_over(points)
                pygame.time.delay(3000)
                main(space_between_pies)

        road += base_move_speed

        if road > distance_between_pipes:
            
            random_pipeUP = random.randint(-PIPE_UP.get_height() + BASE_HEIGHT- 100, -space_between_pies - 120)
            pipeUP = pygame.Rect(
                WIDTH, random_pipeUP, PIPE_WIDTH - E - 10, 874
            )
            pipeDOWN = pygame.Rect(
                WIDTH, random_pipeUP + space_between_pies + pipeUP.height, PIPE_WIDTH - E - 10, 874
            )
            pipes.append([pipeUP, pipeDOWN, False])
            road = 0

        bird_body.y -= jump_speed  
        jump_speed -= jump_acceleration  
        bird_body.y += gravity

        if handle_pipes(pipes, base_move_speed, bird_body) == 1:
            points += 1

            base_move_speed += 0.1
            point_sound.play()


        draw_window(bird_body, start, False, points, base_x_pos, pipes, jump_speed, bird_state)
        handle_colision(bird_body, ground_body)
    pygame.quit()
    exit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        main(int(sys.argv[1]))
    else:
        main(220)