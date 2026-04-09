import pygame, random, os, sys
pygame.init()
start_time = pygame.time.get_ticks()

GAME_WIDTH, GAME_HEIGHT = 512, 512
FLOOR_Y = GAME_HEIGHT * 3/4
PLAYER_SIZE = 50
JUMP_V = -11
GRAVITY = 0.6
BASE_SPEED = 6
max_speed = 32
game_state = 'menu'
FLYING_START_SCORE = 70
FLYING_SPEED_MULT = 1.7
FLYING_HEIGHT_OPTIONS = [
    FLOOR_Y - 60,
    FLOOR_Y - 70,
    FLOOR_Y - 80,
    FLOOR_Y - 90,
    FLOOR_Y - 100,
    FLOOR_Y - 110,
]

PLAYER_IMAGE = pygame.image.load(os.path.join("images", "playerrightright.png"))
PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_SIZE, PLAYER_SIZE))

DUCK_IMG = pygame.image.load("images/playerrightdown.png")
DUCK_IMG = pygame.transform.scale(DUCK_IMG, (PLAYER_SIZE, PLAYER_SIZE // 2))

PLAYER_IMG = pygame.image.load(os.path.join("images", "playerrightright.png"))
PLAYER_IMG = pygame.transform.scale(PLAYER_IMG, (PLAYER_SIZE, PLAYER_SIZE))

screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

class Player(pygame.Rect):
    def __init__(self):
        super().__init__(50, FLOOR_Y-PLAYER_SIZE, PLAYER_SIZE, PLAYER_SIZE)
        self.vy = 0
        self.jumping = False
        self.dir = "right"
        self.ducking = False
        self.original_height = PLAYER_SIZE
        self.duck_height = PLAYER_SIZE // 2
    def update(self):
        # vertical physics
        self.vy += GRAVITY
        self.y += self.vy

        if self.bottom >= FLOOR_Y:
            self.bottom = FLOOR_Y
            self.vy = 0
            self.jumping = False

        # ducking height only on ground
        if self.ducking and not self.jumping:
            self.height = self.duck_height
            self.bottom = FLOOR_Y
        else:
            self.height = self.original_height
            if self.bottom > FLOOR_Y:
                self.bottom = FLOOR_Y

class Obstacle(pygame.Rect):
    def __init__(self, x, y, w, h, is_flying=False):
        super().__init__(x, y, w, h)
        self.is_flying = is_flying

    def update(self, speed):
        self.x -= speed * (FLYING_SPEED_MULT if self.is_flying else 1)

    def offscreen(self):
        return self.right < 0

player = Player()
obstacles = []
last_spawn = pygame.time.get_ticks()
spawn_delay = 1400
ground_offset = 0
score = 0
high_score = 0
game_over = False

# Load high score from file
def load_high_score():
    global high_score
    try:
        with open("highscore.txt", "r") as f:
            high_score = int(f.read())
    except:
        high_score = 0

# Save high score to file
def save_high_score():
    with open("highscore.txt", "w") as f:
        f.write(str(high_score))

load_high_score()

def reset():
    global player, obstacles, last_spawn, score, game_over, start_time, speed, high_score
    if score > high_score:
        high_score = score
        save_high_score()
    player = Player(); obstacles=[]; last_spawn = pygame.time.get_ticks()
    score = 0; game_over = False
    start_time = pygame.time.get_ticks()
    speed = BASE_SPEED

while True:
    dt = clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if game_state == 'menu':
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    game_state = 'playing'
                    start_time = pygame.time.get_ticks()
                elif e.key == pygame.K_q:
                    pygame.quit(); sys.exit()
        elif game_state == 'playing' or game_state == 'game_over':
            if e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                reset()
                game_state = 'playing'
        if game_state == 'playing' and e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            game_state = 'paused'
        elif game_state == 'paused' and e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            game_state = 'playing'

    if game_state == 'playing':
        keys = pygame.key.get_pressed()
        if not game_over:
            if (keys[pygame.K_UP] or keys[pygame.K_SPACE] or keys[pygame.K_w]) and not player.jumping:
                player.vy = JUMP_V; player.jumping = True
            if keys[pygame.K_LEFT]: player.x = max(player.x-5,0)
            if keys[pygame.K_RIGHT]: player.x = min(player.x+5,GAME_WIDTH-player.width)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                if not player.jumping:
                    player.ducking = True
            else:
                player.ducking = False

            player.update()
            now = pygame.time.get_ticks()
            if now - last_spawn > spawn_delay:
                last_spawn = now
                spawn_delay = random.randint(900, 1600)

                # ground obstacle always
                h = random.randint(30, 60)
                obstacles.append(Obstacle(GAME_WIDTH + 20, FLOOR_Y - h, 30, h, is_flying=False))

                # flying obstacle after score threshold
                if score >= FLYING_START_SCORE and random.random() < 0.75:
                    y = random.choice(FLYING_HEIGHT_OPTIONS)
                    obstacles.append(Obstacle(GAME_WIDTH+20, y, 40, 30, is_flying=True))

            elapsed_seconds = (pygame.time.get_ticks() - start_time) / 1000
            speed = BASE_SPEED + elapsed_seconds * 0.1
            speed = min(speed, max_speed)

            for o in obstacles:
                o.update(speed)
                if o.offscreen(): obstacles.remove(o); score += 10
                if player.colliderect(o): game_over = True; game_state = 'game_over'

            ground_offset = (ground_offset - speed) % 40

    if game_state in ('playing', 'game_over', 'paused'):
        screen.fill("#81C6DE")
        pygame.draw.rect(screen, "#5E9B36", (0, FLOOR_Y, GAME_WIDTH, GAME_HEIGHT-FLOOR_Y))
        for i in range(-1, GAME_WIDTH//40 + 3):
            pygame.draw.rect(screen, "#6BAF3E", (i*40 + ground_offset, FLOOR_Y-8, 30, 8))

        if player.ducking and not player.jumping:
            screen.blit(DUCK_IMG, (player.x, player.y))
        else:
            screen.blit(PLAYER_IMG, (player.x, player.y))
        for o in obstacles:
            color = (200, 20, 20) if o.is_flying else (51, 51, 51)
            pygame.draw.rect(screen, color, o)

        hud = font.render(f"Score: {score} High: {high_score}", True, (0,0,0))
        screen.blit(hud, (10,10))
        if game_over:
            over = font.render("GAME OVER - R to restart", True, (200,20,20))
            screen.blit(over, (60, GAME_HEIGHT//2))
            if score == high_score:
                new_high = font.render("NEW HIGH SCORE!", True, (255,215,0))
                screen.blit(new_high, (GAME_WIDTH//2 - 120, GAME_HEIGHT//2 + 40))
        elif game_state == 'paused':
            pause_text = font.render("PAUSED - Press P to resume", True, (0,0,0))
            screen.blit(pause_text, (GAME_WIDTH//2 - 150, GAME_HEIGHT//2))
    elif game_state == 'menu':
        screen.fill("#81C6DE")
        menu_text = font.render("Press P to Play", True, (0,0,0))
        screen.blit(menu_text, (GAME_WIDTH//2 - 100, GAME_HEIGHT//2 - 50))
        exit_text = font.render("Press Q to Quit", True, (0,0,0))
        screen.blit(exit_text, (GAME_WIDTH//2 - 100, GAME_HEIGHT//2))

    pygame.display.update()