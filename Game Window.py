import pygame, random, os, sys
pygame.init()

GAME_WIDTH, GAME_HEIGHT = 512, 512
FLOOR_Y = GAME_HEIGHT * 3/4
PLAYER_SIZE = 50
JUMP_V = -11
GRAVITY = 0.6
SPEED = 6
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
game_over = False

def reset():
    global player, obstacles, last_spawn, score, game_over
    player = Player(); obstacles=[]; last_spawn = pygame.time.get_ticks()
    score = 0; game_over = False

while True:
    dt = clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN and game_over and e.key == pygame.K_r:
            reset()

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

        for o in obstacles:
            o.update(SPEED)
            if o.offscreen(): obstacles.remove(o); score += 10
            if player.colliderect(o): game_over = True

        ground_offset = (ground_offset - SPEED) % 40

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

    hud = font.render(f"Score: {score}", True, (0,0,0))
    screen.blit(hud, (10,10))
    if game_over:
        over = font.render("GAME OVER - R to restart", True, (200,20,20))
        screen.blit(over, (60, GAME_HEIGHT//2))
    pygame.display.update()