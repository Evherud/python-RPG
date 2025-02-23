import pygame
import random
import math
import gameplay
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

    # Draw mana bar
    mana_ratio = player.mana / player.max_mana
    pygame.draw.rect(window, WHITE, (10, 200, 200, 20), 2)  # Border
    pygame.draw.rect(window, BLUE, (10, 200, 200 * mana_ratio, 20))  # Filled bar


# Game loop
def main():
    player = gameplay.Player()
    level = 1
    base_spawn_rate = 5  # Base number of mobs to spawn
    boss_encounters = 0  # Track the number of boss encounters
    mobs = gameplay.generate_mobs(base_spawn_rate, boss_encounters)
    bullets = []
    potions = []
    projectiles = []  # List to store projectiles
    boss = None
    bosses_unlocked = False
    clock = pygame.time.Clock()
    running = True
    slow_mode = False  # Flag to track slow mode

    # Load the Samurai image
    samurai_face = pygame.image.load('Samurai.webp')
    samurai_face = pygame.transform.scale(samurai_face, (PLAYER_SIZE, PLAYER_SIZE))  # Scale to fit the player

    # Load enemy images
    archer_icon = pygame.image.load('archer.jpg')
    knight_icon = pygame.image.load('knight.webp')
    archer_icon = pygame.transform.scale(archer_icon, (MOB_SIZE, MOB_SIZE))  # Scale to fit the mob
    knight_icon = pygame.transform.scale(knight_icon, (MOB_SIZE, MOB_SIZE))  # Scale to fit the mob

    # Load the background image
    background = pygame.image.load('grass.jpg')
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Scale to fit the window

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    slow_mode = not slow_mode  # Toggle slow mode
                elif event.key == pygame.K_ESCAPE:
                    character_menu(player)  # Open character menu

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

        launching_projectile = False
        if keys[pygame.K_SPACE]:
            new_projectiles = player.launch_projectile()
            if new_projectiles:
                projectiles.extend(new_projectiles)
                launching_projectile = True

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
        player.update(launching_projectile)

        # Move projectiles
        for projectile in projectiles[:]:
            projectile.move()
            if projectile.rect.x > WIDTH or projectile.rect.x < 0 or projectile.rect.y > HEIGHT or projectile.rect.y < 0:
                projectiles.remove(projectile)
            else:
                for mob in mobs[:]:
                    if projectile.rect.colliderect(mob.rect):
                        mob.hp -= projectile.damage
                        projectiles.remove(projectile)
                        if mob.hp <= 0:
                            gameplay.handle_mob_death(mob, player, mobs, potions)
                        break

        # Check for screen transition
        if not boss:  # Only allow transition if no boss is present
            if player.rect.x < 0:
                player.rect.x = WIDTH - PLAYER_SIZE
                level += 1
                mobs = gameplay.generate_mobs(base_spawn_rate, boss_encounters)
                potions.clear()
                if bosses_unlocked and random.random() < 0.2:  # 20% chance to encounter a boss
                    boss_type = random.choice([gameplay.StrengthBoss, gameplay.AgilityBoss, gameplay.IntelligenceBoss, gameplay.VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()  # Clear mobs for boss encounter
            elif player.rect.x > WIDTH - PLAYER_SIZE:
                player.rect.x = 0
                level += 1
                mobs = gameplay.generate_mobs(base_spawn_rate, boss_encounters)
                potions.clear()
                if bosses_unlocked and random.random() < 0.2:
                    boss_type = random.choice([gameplay.StrengthBoss, gameplay.AgilityBoss, gameplay.IntelligenceBoss, gameplay.VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()
            elif player.rect.y < 0:
                player.rect.y = HEIGHT - PLAYER_SIZE
                level += 1
                mobs = gameplay.generate_mobs(base_spawn_rate, boss_encounters)
                potions.clear()
                if bosses_unlocked and random.random() < 0.2:
                    boss_type = random.choice([gameplay.StrengthBoss, gameplay.AgilityBoss, gameplay.IntelligenceBoss, gameplay.VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()
            elif player.rect.y > HEIGHT - PLAYER_SIZE:
                player.rect.y = 0
                level += 1
                mobs = gameplay.generate_mobs(base_spawn_rate, boss_encounters)
                potions.clear()
                if bosses_unlocked and random.random() < 0.2:
                    boss_type = random.choice([gameplay.StrengthBoss, gameplay.AgilityBoss, gameplay.IntelligenceBoss, gameplay.VitalityBoss])
                    boss = boss_type(WIDTH // 2, HEIGHT // 2)
                    mobs.clear()
        else:
            # Restrict player movement within screen boundaries during boss fight
            player.rect.x = max(0, min(player.rect.x, WIDTH - PLAYER_SIZE))
            player.rect.y = max(0, min(player.rect.y, HEIGHT - PLAYER_SIZE))

        # Check if player reaches level 5
        if player.stats['level'] == 5 and not bosses_unlocked:
            bosses_unlocked = True
            display_boss_unlocked_message()

        # Update boss if present
        if boss:
            boss.update(player)
            sword_end_x, sword_end_y = player.sword.get_end_position()
            if boss.rect.clipline(player.rect.centerx, player.rect.centery, sword_end_x, sword_end_y):
                boss.take_damage(0.1 * player.stats['strength']+2)
            if boss.hp <= 0:
                potions.append(gameplay.StatPotion(boss.rect.x, boss.rect.y, boss.stat_name, boss.stat_increase))
                boss = None  # Boss defeated
                boss_encounters += 1  # Increment boss encounters

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
                    gameplay.handle_mob_death(mob, player, mobs, potions)

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
                    gameplay.handle_mob_death(mob, player, mobs, potions)

        # Draw the background image
        window.blit(background, (0, 0))

        # Draw the samurai face on the player's rectangle
        window.blit(samurai_face, player.rect.topleft)

        pygame.draw.line(window, RED, player.rect.center, (int(sword_end_x), int(sword_end_y)), 3)

        for mob in mobs:
            # Draw the appropriate icon on each mob
            if isinstance(mob, gameplay.ShooterMob):
                window.blit(archer_icon, mob.rect.topleft)
            elif isinstance(mob, gameplay.Mob):
                window.blit(knight_icon, mob.rect.topleft)
            else:
                pygame.draw.rect(window, mob.color, mob.rect)

            if isinstance(mob, gameplay.SwordMob):
                sword_x, sword_y = mob.sword.get_position()
                pygame.draw.circle(window, RED, (int(sword_x), int(sword_y)), 5)

        if boss:
            pygame.draw.rect(window, boss.color, boss.rect)
            draw_boss_health_bar(boss)

        for bullet in bullets:
            pygame.draw.rect(window, bullet.color, bullet.rect)
        for potion in potions:
            pygame.draw.rect(window, potion.color, potion.rect)

        for projectile in projectiles:
            projectile.draw(window)

        draw_stats(player)

        pygame.display.flip()

        # Adjust the game speed
        if slow_mode:
            clock.tick(12)  # Slow down the game to 12 FPS
        else:
            clock.tick(60)  # Normal game speed at 60 FPS

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

def draw_boss_health_bar(boss):
    if boss:
        bar_width = 200
        bar_height = 20
        health_ratio = boss.hp / boss.max_hp
        health_bar_width = int(bar_width * health_ratio)
        pygame.draw.rect(window, RED, (WIDTH // 2 - bar_width // 2, 10, bar_width, bar_height))
        pygame.draw.rect(window, GREEN, (WIDTH // 2 - bar_width // 2, 10, health_bar_width, bar_height))

def display_boss_unlocked_message():
    window.fill(BLACK)
    message_text = font.render("Bosses Unlocked!", True, WHITE)
    window.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    pygame.time.delay(2000)  # Pause for 2 seconds

def character_menu(player):
    # Load the Samurai image
    samurai_image = pygame.image.load('Samurai.webp')
    samurai_image = pygame.transform.scale(samurai_image, (300, 500))  # Scale the image as needed

    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_running = False  # Close the menu when 'ESC' is pressed again
                elif event.key == pygame.K_1 and player.stats['stat_points'] > 0:
                    player.distribute_stat_points(strength=1)
                elif event.key == pygame.K_2 and player.stats['stat_points'] > 0:
                    player.distribute_stat_points(agility=1)
                elif event.key == pygame.K_3 and player.stats['stat_points'] > 0:
                    player.distribute_stat_points(intelligence=1)
                elif event.key == pygame.K_4 and player.stats['stat_points'] > 0:
                    player.distribute_stat_points(vitality=1)

        # Fill the window with a semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)  # Set transparency level
        overlay.fill(BLACK)
        window.blit(overlay, (0, 0))

        # Display the Samurai image on the left side
        window.blit(samurai_image, (50, HEIGHT // 2 - samurai_image.get_height() // 2))

        # Display character stats on the right side
        stats_text = font.render(f"Character Stats", True, WHITE)
        window.blit(stats_text, (WIDTH - 250, 50))

        # Display each stat with upgrade option
        y_offset = 100
        for i, (stat, value) in enumerate(player.stats.items()):
            stat_text = font.render(f"{stat.upper()}: {value} [+]", True, WHITE)
            window.blit(stat_text, (WIDTH - 250, y_offset))
            y_offset += 40

        # Display health and mana
        health_text = font.render(f"Health: {player.health}/{player.max_health}", True, WHITE)
        mana_text = font.render(f"Mana: {player.mana}/{player.max_mana}", True, WHITE)
        window.blit(health_text, (WIDTH - 250, y_offset))
        y_offset += 40
        window.blit(mana_text, (WIDTH - 250, y_offset))

        pygame.display.flip()

if __name__ == "__main__":
    main()
