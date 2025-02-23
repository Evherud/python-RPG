import pygame
import random
import math

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

# Player class
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.base_color = WHITE
        self.color = self.base_color
        self.base_speed = 5
        self.base_health = 100
        self.base_mana = 100
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
        self.health = self.max_health
        self.mana = self.max_mana
        self.sword = PlayerSword(self, 0)  # Initialize the player's sword
        self.invincible_time = 0
        self.damage_time = 0
        self.last_mana_regen_time = pygame.time.get_ticks()  # Timer for mana regeneration

    @property
    def speed(self):
        # Speed increases with agility
        return self.base_speed + self.stats['agility'] * 0.02

    @property
    def max_health(self):
        # Max health increases with vitality
        return self.base_health + self.stats['vitality'] * 10

    @property
    def max_mana(self):
        # Max mana increases with intelligence
        return self.base_mana + self.stats['intelligence'] * 5

    @property
    def mana_regeneration(self):
        # Mana regeneration rate
        return 1 + self.stats['intelligence'] * 0.02

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

    def update(self, launching_projectile=False):
        current_time = pygame.time.get_ticks()
        if current_time - self.damage_time > 300:  # 0.3 seconds to revert color
            self.color = self.base_color

        # Regenerate mana every 0.5 second if not launching projectiles
        if not launching_projectile and current_time - self.last_mana_regen_time > 500:
            self.mana = min(self.max_mana, self.mana + self.mana_regeneration)
            self.last_mana_regen_time = current_time

    def launch_projectile(self):
        if self.mana >= 10:
            self.mana -= 10
            # Get the sword's end position and angle
            sword_end_x, sword_end_y = self.sword.get_end_position()
            sword_angle = self.sword.angle

            # Create a list to store projectiles
            projectiles = []

            # Define offsets for the staggered pattern, rotated by -90 degrees
            offsets = [
                (0, 0),  # Center
                (10, -10),  # Top middle
                (-10, -10),  # Bottom middle
                (20, -20),  # Far top
                (-20, -20)  # Far bottom
            ]

            # Use the sword's original angle for movement
            movement_angle = sword_angle

            # Generate projectiles in a rotated staggered pattern
            for offset_x, offset_y in offsets:
                # Rotate the offset by the sword's angle minus 90 degrees
                rotated_offset_x = offset_x * math.cos(sword_angle - math.pi / 2) - offset_y * math.sin(sword_angle - math.pi / 2)
                rotated_offset_y = offset_x * math.sin(sword_angle - math.pi / 2) + offset_y * math.cos(sword_angle - math.pi / 2)
                projectiles.append(Projectile(sword_end_x + rotated_offset_x, sword_end_y + rotated_offset_y, movement_angle, self.stats['intelligence']))

            return projectiles
        return []

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
        total_points = strength + agility + intelligence + vitality
        if self.stats['stat_points'] >= total_points:
            self.stats['strength'] += strength
            self.stats['agility'] += agility
            self.stats['intelligence'] += intelligence
            self.stats['vitality'] += vitality
            self.stats['stat_points'] -= total_points

            # Increase current health based on vitality investment
            if vitality > 0:
                health_increase = vitality * 10  # Assuming each point in vitality increases max health by 10
                self.health = min(self.max_health, self.health + health_increase)
                print(f"Health increased by {health_increase}! Current health: {self.health}")

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


# Generate mobs for a level
def generate_mobs(base_spawn_rate, boss_encounters):
    # Increase spawn rate based on the number of boss encounters
    spawn_rate = min(base_spawn_rate + boss_encounters * 2, 25)  # Example: 2 extra mobs per boss encounter
    mobs = []
    for _ in range(spawn_rate):
        x = random.randint(0, WIDTH - MOB_SIZE)
        y = random.randint(0, HEIGHT - MOB_SIZE)
        mob_type = random.choice([ShooterMob, SwordMob])
        mobs.append(mob_type(x, y))
    return mobs

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

class Projectile:
    def __init__(self, x, y, angle, intelligence):
        self.rect = pygame.Rect(x, y, BULLET_SIZE, BULLET_SIZE)
        self.color = YELLOW
        self.damage = 10 + intelligence * 0.1
        self.speed = 10
        self.direction = self.calculate_direction(angle)  # Use the original angle for movement

    def calculate_direction(self, angle):
        # Calculate the direction based on the given angle
        return math.cos(angle), math.sin(angle)

    def move(self):
        dx, dy = self.direction
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

