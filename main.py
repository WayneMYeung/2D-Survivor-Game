import pygame
import random
from pygame.math import Vector2

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background_image = pygame.image.load('background.png')

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Frame rate
FPS = 144
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("wiz1.png").convert_alpha()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.stand_image = self.image
        self.shoot_image = pygame.image.load('wiz2.png')
        self.shoot_left_image = pygame.image.load('wiz3.png')
        self.move_image = pygame.image.load('wind.png').convert_alpha()
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.atk = 1
        self.xp = 0
        self.required_xp = 10
        # Default direction is up
        self.direction = Vector2(0, -1)
        self.animation_index = 0
        self.facing_left = False
        self.animation_speed = 200  # Time in milliseconds for each frame   
        self.last_update_time = pygame.time.get_ticks()
        self.bullet_size = 50
        self.bullet_number = 1
        self.shoot_delay = 1000
        self.last_shot_time = 0
        self.is_shooting = False
        self.animation_speed = 200
    
    def update(self):
        self.handle_input()
        if self.is_shooting and pygame.time.get_ticks() - self.last_shot_time >= self.animation_speed:
            self.is_shooting = False
            
    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
            self.facing_left = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
            self.facing_left = False
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        # Movement detected
        if dx != 0 or dy != 0:
            self.direction = Vector2(dx, dy).normalize()
            self.rect.x += self.direction.x * self.speed
            self.rect.y += self.direction.y * self.speed
            # Use the moving image when there's movement
            self.image = pygame.transform.flip(self.move_image, self.facing_left, False)
        else:
            # Use the standing image when there's no movement
            self.image = pygame.transform.flip(self.stand_image, self.facing_left, False)

        # If the player is shooting, use the shooting image
        if self.is_shooting:
            self.image = pygame.transform.flip(self.shoot_image, self.facing_left, False)
    
    def upgrade_speed(self):
        self.speed += 1

    def upgrade_health(self):
        self.health += 20
        self.max_health += 20

    def upgrade_atk(self):
        self.atk += 1
            
    def gain_xp(self, amount):
        self.xp += amount
    
    def upgrade_bullet_size(self):
        self.bullet_size += 20  # Increase the bullet size

    def upgrade_attack_speed(self):
        self.shoot_delay = max(100, self.shoot_delay - 50)  # Decrease the delay between shots, but not less than 100 ms
        
    def shoot(self, mouse_pos, all_sprites, bullets):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = current_time
            self.is_shooting = True  # Set is_shooting to True when shooting

            # Decide which shooting image to use based on facing direction
            if self.facing_left:
                self.image = self.shoot_left_image
            else:
                self.image = self.shoot_image

            direction = Vector2(mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery).normalize()
            bullet = Bullet(self.rect.center, direction, self.bullet_size)
            all_sprites.add(bullet)
            bullets.add(bullet)
            for _ in range(self.bullet_number):  # Allows for multiple bullets if upgraded
                bullet = Bullet(self.rect.center, direction, self.bullet_size)
                all_sprites.add(bullet)
                bullets.add(bullet)

            # Reset the image back to standing after a delay
            pygame.time.set_timer(pygame.USEREVENT + 1, self.animation_speed)  # Set a timer for animation speed
        
    def walk_animation(self):
        if self.facing_left:
            self.image = pygame.transform.flip(self.stand_image, True, False)
        else:
            self.image = self.stand_image
        



class Enemy(pygame.sprite.Sprite):
    def __init__(self, player, color):
        super().__init__()
        self.speed = 4
        self.player = player
        self.update_delay = 2  # Number of frames to wait before updating position again
        self.current_delay = self.update_delay

    def update(self):
        self.current_delay -= 1
        if self.current_delay <= 0:
            self.current_delay = self.update_delay
            direction = Vector2(self.player.rect.centerx - self.rect.centerx, self.player.rect.centery - self.rect.centery)
            if direction.length() > 0:
                direction = direction.normalize() * self.speed
            else:
                direction = Vector2(0, 0)

            self.rect.x += direction.x
            self.rect.y += direction.y
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
            
    def hit(self, atk):
        self.hp -= atk
        if self.hp <= 0:
            self.kill()
            
class ShieldEnemy(Enemy):
     def __init__(self, player, color):
        super().__init__(player, color)
        self.image = pygame.image.load("enemy.png").convert_alpha()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.hp = 2

class NormalEnemy(Enemy):
     def __init__(self, player, color):
        super().__init__(player, color)
        self.image = pygame.image.load("enemy1.png").convert_alpha()
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.speed = 8
        self.hp = 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, direction, size):
        super().__init__()
        self.images = [
            pygame.transform.scale(pygame.image.load('bullet1.png').convert_alpha(), (size, size)),
            pygame.transform.scale(pygame.image.load('bullet2.png').convert_alpha(), (size, size)),
            pygame.transform.scale(pygame.image.load('bullet3.png').convert_alpha(), (size, size)),
        ]
        self.current_image = 0  # Index of the current image
        self.image = self.images[self.current_image]  # Start with the first image
        self.rect = self.image.get_rect(center=start_pos)
        self.speed = 10
        self.direction = direction
        self.animation_speed = 100  # Time in milliseconds between frames
        self.last_update_time = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > self.animation_speed:
            self.last_update_time = current_time
            self.current_image = (self.current_image + 1) % len(self.images)
            self.image = self.images[self.current_image]
        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed
        # Remove the bullet if it goes off-screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Game:
    def __init__(self):
        self.spawn_delay = 3000  # Initial delay in milliseconds (3 seconds).
        self.minimum_spawn_delay = 500  # Minimum delay in milliseconds (0.5 seconds).
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_rate_decrease = 50  # Decrease spawn delay by 50 milliseconds
        self.time_to_decrease_spawn_rate = 15000  # Decrease spawn rate every 15 seconds
        self.last_spawn_decrease_time = pygame.time.get_ticks()

    def update_spawn_rate(self):
        current_time = pygame.time.get_ticks()
        # Check if it's time to decrease the spawn rate
        if current_time - self.last_spawn_decrease_time > self.time_to_decrease_spawn_rate:
            self.last_spawn_decrease_time = current_time
            # Decrease spawn delay but not less than the minimum
            self.spawn_delay = max(self.minimum_spawn_delay, self.spawn_delay - self.spawn_rate_decrease)

    def try_to_spawn_enemy(self, player, all_sprites, enemies):
        current_time = pygame.time.get_ticks()
        # Check if enough time has passed since the last spawn
        if current_time - self.last_spawn_time > self.spawn_delay:
            self.last_spawn_time = current_time
            # Spawn enemy
            enemy = spawn_enemy_at_border(player)
            all_sprites.add(enemy)
            enemies.add(enemy)
            
def draw_overlay(screen):
    # Create a semi-transparent surface that covers the entire screen
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(50)  # Adjust transparency: 0 is fully transparent, 255 is opaque
    overlay.fill((0, 0, 0))  # Dark overlay; you can choose a different color
    screen.blit(overlay, (0, 0))

def draw_upgrade_menu(screen, options):
    draw_overlay(screen)
    font = pygame.font.Font(None, 36)  # Adjust the font and size as needed

    # Center the menu on the screen
    menu_width = 400  # Set the width of the menu
    menu_height = len(options) * 50 + 40  # Calculate the height based on the number of options
    menu_x = SCREEN_WIDTH // 2 - menu_width // 2
    menu_y = SCREEN_HEIGHT // 2 - menu_height // 2

    # Draw a background for the upgrade menu
    menu_background = pygame.Surface((menu_width, menu_height))
    menu_background.fill(BLACK)
    menu_background.set_alpha(180)  # Semi-transparent
    screen.blit(menu_background, (menu_x, menu_y))

    for i, option in enumerate(options, start=1):
        text = font.render(f"{i}. {option['name']}", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + i * 50))
        screen.blit(text, text_rect)

    # Instructions at the bottom
    instructions_font = pygame.font.Font(None, 24)
    instructions_text = instructions_font.render("Press the corresponding number to choose an upgrade", True, WHITE)
    instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    screen.blit(instructions_text, instructions_rect)

def spawn_enemy_at_border(player):
    # Define the borders with a margin
    top_border = 0
    bottom_border = SCREEN_HEIGHT
    left_border = 0
    right_border = SCREEN_WIDTH

    # Randomly choose an edge of the screen to spawn an enemy
    edge = random.choice(['top', 'bottom', 'left', 'right'])

    if edge == 'top':
        x = random.randrange(left_border, right_border)
        y = top_border
    elif edge == 'bottom':
        x = random.randrange(left_border, right_border)
        y = bottom_border
    elif edge == 'left':
        x = left_border
        y = random.randrange(top_border, bottom_border)
    elif edge == 'right':
        x = right_border
        y = random.randrange(top_border, bottom_border)

    # Instantiate the enemy and set its initial position
    enemy = random.choice([ShieldEnemy(player, RED), NormalEnemy(player, WHITE)])
    enemy.rect.center = (x, y)
    return enemy

def draw_health_bar(screen, pos, size, border_color, inner_color, health, max_health, heart_icon):
    # Scale the heart icon to fit the height of the health bar if necessary
    heart_icon = pygame.transform.scale(heart_icon, (size[1], size[1]))  # Scale heart to match height of health bar

    # Draw the border of the health bar
    border_rect = pygame.Rect(pos, size)
    pygame.draw.rect(screen, border_color, border_rect, 2)  # 2 is the border thickness

    # Calculate the width of the health inside the bar
    inner_width = int((size[0] - heart_icon.get_width()) * (health / max_health))
    inner_rect = pygame.Rect(pos[0] + heart_icon.get_width(), pos[1], inner_width, size[1])
    
    # Draw the health inside the bar
    pygame.draw.rect(screen, inner_color, inner_rect)
    
    # Blit the heart icon
    screen.blit(heart_icon, (pos[0], pos[1]))

    # Set up font for text
    font = pygame.font.Font(None, 24)
    health_text = font.render(f"{health} / {max_health}", True, WHITE)
    text_pos = (pos[0] + heart_icon.get_width() + 5, pos[1] + size[1] / 2 - health_text.get_height() / 2)
    screen.blit(health_text, text_pos)

def draw_score(screen, score, pos, font_size=36):
    font = pygame.font.Font(None, font_size)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, pos)

def main():
    # Sprite groups
    game = Game()
    score = 0
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    paused_for_upgrade = False
    current_player_choice = None
    upgrade_options = [
    {"name": "Increase Speed", "action": lambda player: player.upgrade_speed()},
    {"name": "Increase Health", "action": lambda player: player.upgrade_health()},
    {"name": "Increase Attack", "action": lambda player: player.upgrade_atk()},
    {"name": "Bigger Bullets", "action": lambda player: player.upgrade_bullet_size()},
    {"name": "Faster Shooting", "action": lambda player: player.upgrade_attack_speed()}
]
    # Create player
    player = Player()
    all_sprites.add(player)
    bullets = pygame.sprite.Group()
    heart_icon = pygame.image.load('heart_icon.png').convert_alpha()
    

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif paused_for_upgrade and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    current_player_choice = 0
                elif event.key == pygame.K_2:
                    current_player_choice = 1
                elif event.key == pygame.K_3:
                    current_player_choice = 2
                elif event.key == pygame.K_4:
                    current_player_choice = 3
                elif event.key == pygame.K_5:
                    current_player_choice = 4
                if current_player_choice is not None:
                    upgrade_options[current_player_choice]["action"](player)
                    player.required_xp += 10
                    player.xp = 0
                    paused_for_upgrade = False  # Resume game
                    current_player_choice = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                player.shoot(mouse_pos, all_sprites, bullets)
            elif event.type == pygame.USEREVENT + 1:
                player.is_shooting = False
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_image, (0, 0))
        draw_health_bar(screen, (50, 10), (500, 50), BLACK, RED, player.health, player.max_health, heart_icon)
        draw_score(screen, score, (1800, 10))
        if not paused_for_upgrade:
            player.shoot(mouse_pos, all_sprites, bullets)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Spawning enemies
            game.try_to_spawn_enemy(player, all_sprites, enemies)
                
            collisions = pygame.sprite.groupcollide(bullets, enemies, True, False)
            for hit in collisions.values():  # collisions.values() are the enemies that got hit
                for enemy in hit:
                    enemy.hit(player.atk)  # Call the hit() method for each enemy that got hitsssss
                    if enemy.hp <= 0:
                        score += 1  # Increment the score for each enemy killed
                    player.gain_xp(1)
                    if player.xp >= player.required_xp:
                        paused_for_upgrade = True
            if pygame.sprite.spritecollide(player, enemies, True):
                player.health -= 10  # The player takes 10 damage;
                if player.health <= 0:
                    # Handle the player's death
                    running = False
                    print("Game Over")  # Placeholder for death handling
                    print("You Got " + str(score) + " Points")
            # Update
            all_sprites.update()

            # Drawing
            all_sprites.draw(screen)
        if paused_for_upgrade:
            draw_upgrade_menu(screen, upgrade_options)
            print(player.xp)
        pygame.display.flip()
        # Cap the frame rate
        clock.tick(144)

    pygame.quit()

if __name__ == "__main__":
    main()