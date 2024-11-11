import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 50
MOB_SIZE = 30
BULLET_SIZE = 5
POTION_SIZE = 20
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
AURA_COLOR = (255, 255, 255, 50)  # Semi-transparent white
POTION_COLOR = (0, 255, 255)

# Set up display
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple RPG")

# Font setup
font = pygame.font.SysFont(None, 36)

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.color = WHITE
        self.base_speed = 5
        self.base_health = 100
        self.health = self.base_health
        self.stats = {
            'level': 1,
            'exp': 0,
            'exp_to_next_level': 100,
            'strength': 5,
            'agility': 5,
            'intelligence': 5,
            'vitality': 5,
            'stat_points': 0
        }

    @property
    def speed(self):
        # Speed increases with agility
        return self.base_speed + self.stats['agility'] * 0.2

    @property
    def aura_radius(self):
        # Aura radius scales with strength
        return 50 + self.stats['strength'] * 2

    @property
    def max_health(self):
        # Max health increases with vitality
        return self.base_health + self.stats['vitality'] * 10

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def gain_exp(self, amount):
        # Experience gain increases with intelligence
        exp_gain = amount + self.stats['intelligence'] * 0.1
        self.stats['exp'] += exp_gain
        if self.stats['exp'] >= self.stats['exp_to_next_level']:
            self.stats['level'] += 1
            self.stats['exp'] -= self.stats['exp_to_next_level']
            self.stats['exp_to_next_level'] += 50  # Increase the exp needed for the next level
            self.stats['stat_points'] += 5  # Gain stat points on level up
            print(f"Level up! You are now level {self.stats['level']}. You have {self.stats['stat_points']} stat points to distribute.")

    def distribute_stat_points(self, strength=0, agility=0, intelligence=0, vitality=0):
        if self.stats['stat_points'] >= (strength + agility + intelligence + vitality):
            self.stats['strength'] += strength
            self.stats['agility'] += agility
            self.stats['intelligence'] += intelligence
            self.stats['vitality'] += vitality
            self.stats['stat_points'] -= (strength + agility + intelligence + vitality)
            print(f"Distributed points: STR {strength}, AGI {agility}, INT {intelligence}, VIT {vitality}. Remaining points: {self.stats['stat_points']}")

# Base Mob class
class Mob:
    def __init__(self, x, y, color, hp):
        self.rect = pygame.Rect(x, y, MOB_SIZE, MOB_SIZE)
        self.color = color
        self.hp = hp

    def update(self, player):
        pass

# Shooter Mob class
class ShooterMob(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 3)

    def update(self, player):
        if random.random() < 0.01:  # Random chance to shoot
            return self.shoot(player)
        return None

    def shoot(self, player):
        # Calculate direction towards player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        dx, dy = dx / distance, dy / distance  # Normalize
        return Bullet(self.rect.centerx, self.rect.centery, dx, dy)

# Sword class
class Sword:
    def __init__(self, mob, radius, angle):
        self.mob = mob
        self.radius = radius
        self.angle = angle
        self.speed = 0.05  # Speed of rotation

    def update(self):
        # Update the angle for rotation
        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi

    def get_position(self):
        # Calculate the sword's position based on the angle and radius
        x = self.mob.rect.centerx + self.radius * math.cos(self.angle)
        y = self.mob.rect.centery + self.radius * math.sin(self.angle)
        return x, y

# Sword Mob class
class SwordMob(Mob):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, 5)
        self.swing_radius = 40  # Radius of the sword swing
        self.sword = Sword(self, self.swing_radius, 0)  # Initialize the spinning sword

    def update(self, player):
        # Update the sword's position
        self.sword.update()

        # Check for player collision with the spinning sword
        sword_x, sword_y = self.sword.get_position()
        if player.rect.collidepoint(sword_x, sword_y):
            player.health -= 5  # Damage the player
            print(f"Player hit by spinning sword! Health: {player.health}")

        # Swing sword if player is within range
        if self.rect.colliderect(player.rect.inflate(self.swing_radius * 2, self.swing_radius * 2)):
            if random.random() < 0.05:  # Random chance to swing
                self.swing_sword(player)

    def swing_sword(self, player):
        # Check if player is within swing radius
        distance = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        if distance < self.swing_radius:
            player.health -= 5  # Damage the player
            print(f"Player hit by sword! Health: {player.health}")

# Bullet class
class Bullet:
    def __init__(self, x, y, dx, dy):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        self.color = YELLOW
        self.speed = 7
        self.dx = dx * self.speed
        self.dy = dy * self.speed

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

# Health Potion class
class HealthPotion:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, POTION_SIZE, POTION_SIZE)
        self.color = POTION_COLOR

# Draw stats
def draw_stats(player):
    # Draw level
    level_text = font.render(f"Level: {player.stats['level']}", True, WHITE)
    window.blit(level_text, (10, 10))

    # Draw experience bar
    exp_ratio = player.stats['exp'] / player.stats['exp_to_next_level']
    pygame.draw.rect(window, WHITE, (10, 50, 200, 20), 2)  # Border
    pygame.draw.rect(window, GREEN, (10, 50, 200 * exp_ratio, 20))  # Filled bar

    # Draw experience text
    exp_text = font.render(f"EXP: {player.stats['exp']}/{player.stats['exp_to_next_level']}", True, WHITE)
    window.blit(exp_text, (10, 80))

    # Draw other stats
    stats_text = font.render(f"STR: {player.stats['strength']} AGI: {player.stats['agility']} INT: {player.stats['intelligence']} VIT: {player.stats['vitality']}", True, WHITE)
    window.blit(stats_text, (10, 110))

    # Draw stat points
    stat_points_text = font.render(f"Stat Points: {player.stats['stat_points']}", True, WHITE)
    window.blit(stat_points_text, (10, 140))

    # Draw health bar
    health_ratio = player.health / player.max_health
    pygame.draw.rect(window, WHITE, (10, 170, 200, 20), 2)  # Border
    pygame.draw.rect(window, RED, (10, 170, 200 * health_ratio, 20))  # Filled bar

# Generate mobs for a level
def generate_mobs(num_mobs, player):
    mobs = []
    # Reduce the number of mobs based on player's intelligence
    effective_mobs = max(1, int(num_mobs * (1 - player.stats['intelligence'] * 0.02)))
    for _ in range(effective_mobs):
        if random.choice([True, False]):
            mobs.append(ShooterMob(random.randint(0, WIDTH - MOB_SIZE), random.randint(0, HEIGHT - MOB_SIZE)))
        else:
            mobs.append(SwordMob(random.randint(0, WIDTH - MOB_SIZE), random.randint(0, HEIGHT - MOB_SIZE)))
    return mobs

# Game loop
def main():
    player = Player()
    level = 1
    mobs = generate_mobs(level * 5, player)  # Increase number of mobs with level
    bullets = []  # List to store bullets
    potions = []  # List to store health potions
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1

        # Stop the game when ESC is pressed
        if keys[pygame.K_ESCAPE]:
            running = False

        # Distribute stat points
        if keys[pygame.K_1] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(strength=1)
        if keys[pygame.K_2] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(agility=1)
        if keys[pygame.K_3] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(intelligence=1)
        if keys[pygame.K_4] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(vitality=1)

        player.move(dx, dy)

        # Check for screen transition
        if player.rect.x < 0:
            player.rect.x = WIDTH - PLAYER_SIZE
            level += 1
            mobs = generate_mobs(level * 5, player)
        elif player.rect.x > WIDTH - PLAYER_SIZE:
            player.rect.x = 0
            level += 1
            mobs = generate_mobs(level * 5, player)
        elif player.rect.y < 0:
            player.rect.y = HEIGHT - PLAYER_SIZE
            level += 1
            mobs = generate_mobs(level * 5, player)
        elif player.rect.y > HEIGHT - PLAYER_SIZE:
            player.rect.y = 0
            level += 1
            mobs = generate_mobs(level * 5, player)

        # Update mobs and handle shooting
        for mob in mobs:
            bullet = mob.update(player)
            if bullet:
                bullets.append(bullet)

        # Move bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.colliderect(player.rect):
                player.health -= 10
                print(f"Player hit! Health: {player.health}")
                bullets.remove(bullet)
            elif bullet.rect.x < 0 or bullet.rect.x > WIDTH or bullet.rect.y < 0 or bullet.rect.y > HEIGHT:
                bullets.remove(bullet)

        # Check for player death
        if player.health <= 0:
            print("Player has died. Game Over.")
            running = False
            continue

        # Check for collisions with mobs
        for mob in mobs[:]:
            if player.rect.colliderect(mob.rect):
                mob.hp -= player.stats['strength']  # Damage increases with strength
                if mob.hp <= 0:
                    handle_mob_death(mob, player, mobs, potions)

        # Check for collisions with potions
        for potion in potions[:]:
            if player.rect.colliderect(potion.rect):
                heal_amount = player.max_health * 0.2  # Heal 20% of max health
                player.health = min(player.max_health, player.health + heal_amount)
                print(f"Health potion collected! Health: {player.health}")
                potions.remove(potion)

        # Aura effect
        aura_radius = player.aura_radius
        for mob in mobs[:]:
            distance = math.hypot(player.rect.centerx - mob.rect.centerx, player.rect.centery - mob.rect.centery)
            if distance < aura_radius:
                mob.hp -= 0.1 * player.stats['strength']  # Aura damage scales with strength
                if mob.hp <= 0:
                    handle_mob_death(mob, player, mobs, potions)

        # Draw everything
        window.fill(BLACK)
        pygame.draw.rect(window, player.color, player.rect)
        for mob in mobs:
            pygame.draw.rect(window, mob.color, mob.rect)
            # Draw the spinning sword
            if isinstance(mob, SwordMob):
                sword_x, sword_y = mob.sword.get_position()
                pygame.draw.circle(window, RED, (int(sword_x), int(sword_y)), 5)

        for bullet in bullets:
            pygame.draw.rect(window, bullet.color, bullet.rect)
        for potion in potions:
            pygame.draw.rect(window, potion.color, potion.rect)

        # Draw aura
        pygame.draw.circle(window, AURA_COLOR, player.rect.center, int(aura_radius), 1)

        draw_stats(player)

        pygame.display.flip()
        clock.tick(60)

    # Display game over screen
    game_over_screen()

def game_over_screen():
    window.fill(BLACK)
    game_over_text = font.render("Game Over! Press R to Restart or Q to Quit", True, WHITE)
    window.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()  # Restart the game
                waiting = False
            if keys[pygame.K_q]:
                waiting = False

    pygame.quit()

def handle_mob_death(mob, player, mobs, potions):
    player.gain_exp(20)
    mobs.remove(mob)
    # Drop a health potion with a very low chance
    if random.random() < 0.05:  # 5% chance to drop a potion
        potions.append(HealthPotion(mob.rect.x, mob.rect.y))

if __name__ == "__main__":
    main()
