import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 900

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Tank dimensions
TANK_WIDTH, TANK_HEIGHT = 40, 40
BULLET_WIDTH, BULLET_HEIGHT = 10, 10
HEALTH_BAR_WIDTH = 50
HEALTH_BAR_HEIGHT = 5

# Movement speed
TANK_SPEED = 5
BOT_SPEED = 2  # Reduced bot speed
BULLET_SPEED = 10

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Player vs AI Tank Game")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Tank class
class Tank:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.health = 5
        self.bullets = []
        self.direction = "UP"

    def move(self, keys=None, up=None, down=None, left=None, right=None, speed=TANK_SPEED):
        if keys:
            if keys[up] and self.y > 0:
                self.y -= speed
                self.direction = "UP"
            if keys[down] and self.y < SCREEN_HEIGHT - TANK_HEIGHT:
                self.y += speed
                self.direction = "DOWN"
            if keys[left] and self.x > 0:
                self.x -= speed
                self.direction = "LEFT"
            if keys[right] and self.x < SCREEN_WIDTH - TANK_WIDTH:
                self.x += speed
                self.direction = "RIGHT"

    def bot_move(self, target):
        if random.randint(1, 100) < 10:  # Adjust chance to shoot
            self.shoot()

        if abs(self.x - target.x) > abs(self.y - target.y):
            if self.x < target.x:
                self.x += BOT_SPEED
                self.direction = "RIGHT"
            elif self.x > target.x:
                self.x -= BOT_SPEED
                self.direction = "LEFT"
        else:
            if self.y < target.y:
                self.y += BOT_SPEED
                self.direction = "DOWN"
            elif self.y > target.y:
                self.y -= BOT_SPEED
                self.direction = "UP"

    def shoot(self):
        if self.direction == "UP":
            bullet = pygame.Rect(
                self.x + TANK_WIDTH // 2 - BULLET_WIDTH // 2, self.y, BULLET_WIDTH, BULLET_HEIGHT
            )
        elif self.direction == "DOWN":
            bullet = pygame.Rect(
                self.x + TANK_WIDTH // 2 - BULLET_WIDTH // 2, self.y + TANK_HEIGHT, BULLET_WIDTH, BULLET_HEIGHT
            )
        elif self.direction == "LEFT":
            bullet = pygame.Rect(
                self.x, self.y + TANK_HEIGHT // 2 - BULLET_HEIGHT // 2, BULLET_HEIGHT, BULLET_WIDTH
            )
        elif self.direction == "RIGHT":
            bullet = pygame.Rect(
                self.x + TANK_WIDTH, self.y + TANK_HEIGHT // 2 - BULLET_HEIGHT // 2, BULLET_HEIGHT, BULLET_WIDTH
            )
        self.bullets.append((bullet, self.direction))

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, TANK_WIDTH, TANK_HEIGHT))
        for bullet, direction in self.bullets:
            pygame.draw.rect(screen, WHITE, bullet)

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Game loop variables
tank1 = Tank(100, 300, RED)
bot_tank = Tank(600, 300, BLUE)
play_again_button = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50, "PLAY AGAIN", GREEN, BLACK)

running = True
show_game_over = False
winner = None

# Game loop
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not show_game_over:
                tank1.shoot()

        if event.type == pygame.MOUSEBUTTONDOWN and show_game_over:
            if play_again_button.is_clicked(event.pos):
                tank1 = Tank(100, 300, RED)
                bot_tank = Tank(600, 300, BLUE)
                show_game_over = False
                winner = None

    if not show_game_over:
        # Handle keys
        keys = pygame.key.get_pressed()

        # Tank 1 movement (Arrow Keys)
        tank1.move(keys, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)

        # Bot movement and logic
        bot_tank.bot_move(tank1)

        # Move bullets
        for tank in [tank1, bot_tank]:
            for bullet, direction in tank.bullets[:]:
                if direction == "UP":
                    bullet.y -= BULLET_SPEED
                elif direction == "DOWN":
                    bullet.y += BULLET_SPEED
                elif direction == "LEFT":
                    bullet.x -= BULLET_SPEED
                elif direction == "RIGHT":
                    bullet.x += BULLET_SPEED

                # Collision and boundary checks
                if bullet.colliderect(pygame.Rect(bot_tank.x, bot_tank.y, TANK_WIDTH, TANK_HEIGHT)) and tank == tank1:
                    bot_tank.health -= 1
                    tank.bullets.remove((bullet, direction))
                elif bullet.colliderect(pygame.Rect(tank1.x, tank1.y, TANK_WIDTH, TANK_HEIGHT)) and tank == bot_tank:
                    tank1.health -= 1
                    tank.bullets.remove((bullet, direction))
                elif bullet.y < 0 or bullet.y > SCREEN_HEIGHT or bullet.x < 0 or bullet.x > SCREEN_WIDTH:
                    tank.bullets.remove((bullet, direction))

        # Draw tanks and bullets
        tank1.draw()
        bot_tank.draw()

        # Display health
        font = pygame.font.Font(None, 36)
        health_text1 = font.render(f"Player Health: {tank1.health}", True, WHITE)
        health_text2 = font.render(f"Bot Health: {bot_tank.health}", True, WHITE)
        screen.blit(health_text1, (10, 10))
        screen.blit(health_text2, (SCREEN_WIDTH - 200, 10))

        # Check for game over
        if tank1.health <= 0 or bot_tank.health <= 0:
            winner = "Player" if bot_tank.health <= 0 else "Bot"
            show_game_over = True

    else:
        # Show game over screen
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("YOU WON!!" if winner == "Player" else "YOU LOST", True, WHITE)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_text, text_rect)
        play_again_button.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
