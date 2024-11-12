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
        self.base_color = WHITE
        self.color = self.base_color
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
            'vitality': 500,
            'stat_points': 0
        }
        self.sword = PlayerSword(self, 0)  # Initialize the player's sword
        self.invincible_time = 0
        self.damage_time = 0

    @property
    def speed(self):
        # Speed increases with agility
        return self.base_speed + self.stats['agility'] * 0.02

    @property
    def max_health(self):
        # Max health increases with vitality
        return self.base_health + self.stats['vitality'] * 10

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.invincible_time > 300:  # 0.3 seconds of invincibility
            self.health -= amount
            self.color = RED
            self.damage_time = current_time
            self.invincible_time = current_time
            print(f"Player hit! Health: {self.health}")

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.damage_time > 300:  # 0.3 seconds to revert color
            self.color = self.base_color

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

    def update_sword(self):
        self.sword.update()

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
        self.speed = 2  # Speed of the SwordMob

    def update(self, player):
        # Move towards the player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:  # Avoid division by zero
            dx, dy = dx / distance, dy / distance  # Normalize
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed

        # Update the sword's position
        self.sword.update()

        # Check for player collision with the spinning sword
        sword_x, sword_y = self.sword.get_position()
        if player.rect.collidepoint(sword_x, sword_y):
            player.take_damage(5)  # Damage the player
            print(f"Player hit by spinning sword! Health: {player.health}")

        # Swing sword if player is within range
        if self.rect.colliderect(player.rect.inflate(self.swing_radius * 2, self.swing_radius * 2)):
            if random.random() < 0.05:  # Random chance to swing
                self.swing_sword(player)

    def swing_sword(self, player):
        # Check if player is within swing radius
        distance = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        if distance < self.swing_radius:
            player.take_damage(5)  # Damage the player
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

    def apply(self, player):
        # Increase the player's health by the heal amount, up to the max health
        new_health = min(player.max_health, player.health + 10 + player.stats['vitality'] * 0.5 )
        heal_amount = new_health - player.health
        player.health = new_health
        print(f"Health increased by {heal_amount}! Current health: {player.health}")

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
    mobs = generate_mobs(level * 5, player)
    bullets = []
    potions = []
    boss = None
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

        if keys[pygame.K_ESCAPE]:
            running = False

        if keys[pygame.K_1] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(strength=1)
        if keys[pygame.K_2] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(agility=1)
        if keys[pygame.K_3] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(intelligence=1)
        if keys[pygame.K_4] and player.stats['stat_points'] > 0:
            player.distribute_stat_points(vitality=1)

        player.move(dx, dy)
        player.update_sword()
        player.update()

        # Check for screen transition
        if not boss:  # Only allow transition if no boss is present
            if player.rect.x < 0:
                player.rect.x = WIDTH - PLAYER_SIZE
                level += 1
                mobs = generate_mobs(level * 5, player)
                potions.clear()
                # Random chance to encounter a boss
                if random.random() < 0.2:  # 20% chance to encounter a boss
                    boss_type = random.choice([StrengthBoss, AgilityBoss, IntelligenceBoss, VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()  # Clear mobs for boss encounter
            elif player.rect.x > WIDTH - PLAYER_SIZE:
                player.rect.x = 0
                level += 1
                mobs = generate_mobs(level * 5, player)
                potions.clear()
                if random.random() < 0.2:
                    boss_type = random.choice([StrengthBoss, AgilityBoss, IntelligenceBoss, VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()
            elif player.rect.y < 0:
                player.rect.y = HEIGHT - PLAYER_SIZE
                level += 1
                mobs = generate_mobs(level * 5, player)
                potions.clear()
                if random.random() < 0.2:
                    boss_type = random.choice([StrengthBoss, AgilityBoss, IntelligenceBoss, VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()
            elif player.rect.y > HEIGHT - PLAYER_SIZE:
                player.rect.y = 0
                level += 1
                mobs = generate_mobs(level * 5, player)
                potions.clear()
                if random.random() < 0.2:
                    boss_type = random.choice([StrengthBoss, AgilityBoss, IntelligenceBoss, VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()
        else:
            # Restrict player movement within screen boundaries during boss fight
            player.rect.x = max(0, min(player.rect.x, WIDTH - PLAYER_SIZE))
            player.rect.y = max(0, min(player.rect.y, HEIGHT - PLAYER_SIZE))

        # Update boss if present
        if boss:
            boss.update(player)
            sword_end_x, sword_end_y = player.sword.get_end_position()
            if boss.rect.clipline(player.rect.centerx, player.rect.centery, sword_end_x, sword_end_y):
                boss.take_damage(0.1 * player.stats['strength'])
            if boss.hp <= 0:
                potions.append(StatPotion(boss.rect.x, boss.rect.y, boss.stat_name, boss.stat_increase))
                boss = None  # Boss defeated

        # Update mobs and handle shooting
        for mob in mobs:
            bullet = mob.update(player)
            if bullet:
                bullets.append(bullet)

        # Move bullets
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.colliderect(player.rect):
                player.take_damage(10)
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
                mob.hp -= player.stats['strength']
                if mob.hp <= 0:
                    handle_mob_death(mob, player, mobs, potions)

        # Check for collisions with potions
        for potion in potions[:]:
            if player.rect.colliderect(potion.rect):
                potion.apply(player)
                potions.remove(potion)

        sword_end_x, sword_end_y = player.sword.get_end_position()
        for mob in mobs[:]:
            if mob.rect.clipline(player.rect.centerx, player.rect.centery, sword_end_x, sword_end_y):
                mob.hp -= 0.1 * player.stats['strength']
                if mob.hp <= 0:
                    handle_mob_death(mob, player, mobs, potions)

        window.fill(BLACK)
        pygame.draw.rect(window, player.color, player.rect)
        pygame.draw.line(window, RED, player.rect.center, (int(sword_end_x), int(sword_end_y)), 3)

        for mob in mobs:
            pygame.draw.rect(window, mob.color, mob.rect)
            if isinstance(mob, SwordMob):
                sword_x, sword_y = mob.sword.get_position()
                pygame.draw.circle(window, RED, (int(sword_x), int(sword_y)), 5)

        if boss:
            pygame.draw.rect(window, boss.color, boss.rect)
            draw_boss_health_bar(boss)

        for bullet in bullets:
            pygame.draw.rect(window, bullet.color, bullet.rect)
        for potion in potions:
            pygame.draw.rect(window, potion.color, potion.rect)

        draw_stats(player)

        pygame.display.flip()
        clock.tick(60)

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

class PlayerSword:
    def __init__(self, player, angle):
        self.player = player
        self.angle = angle

    @property
    def speed(self):
        # Base speed plus a small increment based on agility
        return max(0.05 + self.player.stats['agility'] * 0.0002, 0.2)

    @property
    def length(self):
        # Sword length scales with the square root of strength, rounded up
        return 50 + math.ceil(math.sqrt(self.player.stats['strength'] * 2500))*0.13

    def update(self):
        # Update the angle for rotation using the calculated speed
        self.angle += self.speed
        if self.angle >= 2 * math.pi:
            self.angle -= 2 * math.pi

    def get_end_position(self):
        # Calculate the sword's end position based on the angle and length
        x = self.player.rect.centerx + self.length * math.cos(self.angle)
        y = self.player.rect.centery + self.length * math.sin(self.angle)
        return x, y

class Boss(Mob):
    def __init__(self, x, y, color, hp, stat_increase, stat_name):
        super().__init__(x, y, color, hp)
        self.max_hp = hp
        self.stat_increase = stat_increase
        self.stat_name = stat_name
        self.base_color = color
        self.invincible_time = 0
        self.damage_time = 0

    def update(self, player):
        # Boss logic to move towards the player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.rect.x += dx * 1  # Boss speed
            self.rect.y += dy * 1

        # Handle blinking effect
        current_time = pygame.time.get_ticks()
        if current_time - self.damage_time > 200:  # 0.2 seconds to revert color
            self.color = self.base_color

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if current_time - self.invincible_time > 500:  # 0.5 seconds of invincibility
            self.hp -= amount
            self.color = WHITE  # Change color to indicate damage
            self.damage_time = current_time
            self.invincible_time = current_time
            if self.hp <= 0:
                self.hp = 0

class StrengthBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW, 50, 10, 'strength')

class AgilityBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN, 50, 10, 'agility')

class IntelligenceBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, 50, 10, 'intelligence')

class VitalityBoss(Boss):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 50, 10, 'vitality')

class StatPotion:
    def __init__(self, x, y, stat_name, increase_amount):
        self.rect = pygame.Rect(x, y, POTION_SIZE, POTION_SIZE)
        self.color = POTION_COLOR
        self.stat_name = stat_name
        self.increase_amount = increase_amount

    def apply(self, player):
        player.stats[self.stat_name] += self.increase_amount
        print(f"{self.stat_name.capitalize()} increased by {self.increase_amount}!")

def draw_boss_health_bar(boss):
    if boss:
        bar_width = 200
        bar_height = 20
        health_ratio = boss.hp / boss.max_hp
        health_bar_width = int(bar_width * health_ratio)
        pygame.draw.rect(window, RED, (WIDTH // 2 - bar_width // 2, 10, bar_width, bar_height))
        pygame.draw.rect(window, GREEN, (WIDTH // 2 - bar_width // 2, 10, health_bar_width, bar_height))

if __name__ == "__main__":
    main()
