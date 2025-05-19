import pygame
import random
import os
import sys

# Inicialização
pygame.init()

# Tela
WIDTH, HEIGHT = 1000, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombies Attack - Coop Mode")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Fonte
font = pygame.font.SysFont("Arial", 40)

# Carregar imagens
def load_img(name, size=None):
    path = os.path.join("assets", name)
    img = pygame.image.load(path)
    return pygame.transform.scale(img, size) if size else img

background = load_img("fundo.png", (WIDTH, HEIGHT))
player_img = load_img("human.png", (50, 50))
zombie_img = load_img("zumbi.png", (50, 50))
boss_img = load_img("zumbi2.png", (80, 80))

# Classes
class Player:
    def __init__(self, x, y, controls):
        self.x = x
        self.y = y
        self.speed = 5
        self.bullets = []
        self.controls = controls
        self.cooldown = 0
        self.lives = 3  # Vidas

    def draw(self):
        win.blit(player_img, (self.x, self.y))
        for b in self.bullets:
            pygame.draw.rect(win, RED, (b[0], b[1], 10, 5))

    def move(self, keys):
        if keys[self.controls["up"]] and self.y > 0:
            self.y -= self.speed
        if keys[self.controls["down"]] and self.y < HEIGHT - 50:
            self.y += self.speed
        if keys[self.controls["left"]] and self.x > 0:
            self.x -= self.speed
        if keys[self.controls["right"]] and self.x < WIDTH - 50:
            self.x += self.speed
        if keys[self.controls["shoot"]] and self.cooldown == 0:
            self.bullets.append([self.x + 45, self.y + 20])
            self.cooldown = 30  # Cooldown de 30 frames

    def update_bullets(self):
        for b in self.bullets:
            b[0] += 10
        self.bullets = [b for b in self.bullets if b[0] < WIDTH]
        if self.cooldown > 0:
            self.cooldown -= 1

class Zombie:
    def __init__(self, x, y, is_boss=False, fase=1):
        self.x = x
        self.y = y
        self.img = boss_img if is_boss else zombie_img
        if is_boss:
            # Vida e velocidade do chefão escaláveis por fase
            self.life = 4 + (fase // 10)
            self.speed = 2 + fase * 0.1 - (fase // 20)
        else:
            self.life = 1
            self.speed = 2
        self.is_boss = is_boss
        self.offset = random.randint(-50, 50)  # Desvio vertical único

    def move(self, players):
        # Alvo mais próximo
        target = min(players, key=lambda p: abs(self.x - p.x) + abs(self.y - p.y))

        # Movimento horizontal
        if self.x > target.x:
            self.x -= self.speed

        # Movimento vertical com offset
        if self.y < target.y + self.offset:
            self.y += self.speed / 2
        elif self.y > target.y + self.offset:
            self.y -= self.speed / 2

    def draw(self):
        win.blit(self.img, (self.x, self.y))

# Tela inicial com botões
def menu_screen():
    while True:
        win.fill(BLACK)
        title = font.render("Zombies Attack - Coop Mode", True, WHITE)
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Botão 1 jogador
        one_player_btn = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)
        pygame.draw.rect(win, WHITE, one_player_btn)
        one_player_txt = font.render("1 Player", True, BLACK)
        win.blit(one_player_txt, (WIDTH // 2 - one_player_txt.get_width() // 2, 260))

        # Botão 2 jogadores
        two_player_btn = pygame.Rect(WIDTH // 2 - 150, 350, 300, 50)
        pygame.draw.rect(win, WHITE, two_player_btn)
        two_player_txt = font.render("2 Players", True, BLACK)
        win.blit(two_player_txt, (WIDTH // 2 - two_player_txt.get_width() // 2, 360))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if one_player_btn.collidepoint(event.pos):
                    return 1
                elif two_player_btn.collidepoint(event.pos):
                    return 2

# Jogo principal
# Jogo principal
def main():
    clock = pygame.time.Clock()
    run = True
    fase = 1
    max_fases = 50
    zombies = []

    num_players = menu_screen()

    p1 = Player(50, 200, {
        "up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d, "shoot": pygame.K_SPACE
    })
    p2 = Player(50, 300, {
        "up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT, "shoot": pygame.K_RETURN
    })
    players = []
    if num_players >= 1:
        players.append(p1)
    if num_players == 2:
        players.append(p2)

    def spawn_zombies(fase):
        base = 8 + fase * 2
        for _ in range(base):
            y = random.randint(0, HEIGHT - 50)
            zombies.append(Zombie(WIDTH + random.randint(0, 500), y, fase=fase))
        if fase % 5 == 0:
            qtd_boss = 3 + ((fase // 5) * 2)
            for _ in range(qtd_boss):
                zombies.append(Zombie(WIDTH + random.randint(0, 300), random.randint(0, HEIGHT - 80), is_boss=True, fase=fase))

    spawn_zombies(fase)

    while run:
        clock.tick(60)
        win.blit(background, (0, 0))

        keys = pygame.key.get_pressed()

        for p in players:
            if p.lives > 0:
                p.move(keys)
                p.update_bullets()
                p.draw()

        for z in zombies[:]:
            z.move(players)
            z.draw()

            # Tiros
            for p in players:
                if p.lives > 0:
                    for b in p.bullets[:]:
                        if z.x < b[0] < z.x + z.img.get_width() and z.y < b[1] < z.y + z.img.get_height():
                            z.life -= 1
                            if z.life <= 0:
                                zombies.remove(z)
                            p.bullets.remove(b)

            # Colisão com jogador
            for p in players:
                if p.lives > 0:
                    if z.x < p.x + 50 and z.x + z.img.get_width() > p.x and z.y < p.y + 50 and z.y + z.img.get_height() > p.y:
                        p.lives -= 1
                        zombies.remove(z)

            # Se passar da tela pela esquerda, some
            if z.x < -z.img.get_width():
                zombies.remove(z)

        # Fase completa
        if not zombies:
            fase += 1
            if fase > max_fases:
                run = False
                continue
            spawn_zombies(fase)

        # HUD de vidas
        for idx, p in enumerate(players):
            lives_text = font.render(f"P{idx+1}: {p.lives} vidas", True, WHITE)
            win.blit(lives_text, (10, 10 + idx * 50))

        # Game Over
        if all(p.lives <= 0 for p in players):
            over_text = font.render("GAME OVER", True, RED)
            win.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 20))
            pygame.display.update()
            pygame.time.delay(3000)
            run = False

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False

    pygame.quit()

if __name__ == "__main__":
    main()
