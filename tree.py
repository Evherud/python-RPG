import pygame
import random

class TalentNode:
    def __init__(self, stat, boost, rarity='common', position=(0, 0)):
        self.stat = stat
        self.boost = boost
        self.rarity = rarity
        self.learned = False
        self.learnable = False
        self.position = position
        self.description = f"Boosts {self.stat} by {self.boost} points."
        self.children = {'up': None, 'down': None, 'left': None, 'right': None}

    def learn(self, player, occupied_positions):
        if self.learnable and player.talent_points > 0:
            player.stats[self.stat] += self.boost
            player.talent_points -= 1
            self.learned = True
            self.learnable = False
            print(f"Learned {self.stat} node: +{self.boost} {self.stat}")
            for child in self.children.values():
                if child:
                    child.learnable = True  # Make children learnable
                    generate_children(child, occupied_positions)  # Generate new observable nodes around them

    def draw(self, surface, offset, mouse_pos):
        adjusted_position = (self.position[0] + offset[0], self.position[1] + offset[1])
        is_hovered = pygame.Rect(adjusted_position[0] - 20, adjusted_position[1] - 20, 40, 40).collidepoint(mouse_pos)
        
        if self.learned:
            color = (0, 255, 0)  # Green if learned
        elif self.learnable:
            color = (255, 255, 255)  # White if learnable
            if is_hovered:
                color = (255, 255, 0)  # Yellow if hovered
        else:
            color = (100, 100, 100)  # Grey if observable

        pygame.draw.circle(surface, color, adjusted_position, 20)
        font = pygame.font.SysFont(None, 24)
        text = font.render(self.stat[0].upper(), True, (0, 0, 0))
        surface.blit(text, (adjusted_position[0] - 5, adjusted_position[1] - 10))

        # Display description if hovered
        if is_hovered:
            description_font = pygame.font.SysFont(None, 20)
            description_text = description_font.render(self.description, True, (255, 255, 255))
            surface.blit(description_text, (adjusted_position[0] + 25, adjusted_position[1] - 10))

        # Draw children
        for direction, child in self.children.items():
            if child:
                adjusted_end = (child.position[0] + offset[0], child.position[1] + offset[1])
                pygame.draw.line(surface, (255, 255, 255), adjusted_position, adjusted_end)
                child.draw(surface, offset, mouse_pos)

def generate_talent_tree():
    stat = random.choice(['strength', 'agility', 'intelligence', 'vitality'])
    boost = random.randint(1, 5)
    root_node = TalentNode(stat, boost, position=(400, 300))
    root_node.learnable = True  # Root node is learnable initially
    occupied_positions = {(400, 300)}
    generate_children(root_node, occupied_positions)  # Generate initial observable nodes
    return [root_node], occupied_positions

def generate_children(node, occupied_positions):
    directions = {
        'up': (0, -100),
        'down': (0, 100),
        'left': (-100, 0),
        'right': (100, 0)
    }
    
    for direction, (dx, dy) in directions.items():
        new_position = (node.position[0] + dx, node.position[1] + dy)
        if node.children[direction] is None and new_position not in occupied_positions and random.random() < 0.5:
            stat = random.choice(['strength', 'agility', 'intelligence', 'vitality'])
            boost = random.randint(1, 5)
            child_node = TalentNode(stat, boost, position=new_position)
            node.children[direction] = child_node
            occupied_positions.add(new_position)
            child_node.learnable = False  # New nodes are observable

def draw_talent_tree(surface, nodes, offset, mouse_pos):
    for node in nodes:
        node.draw(surface, offset, mouse_pos)

def handle_click(nodes, player, mouse_pos, offset, occupied_positions):
    for node in nodes:
        if node is None:
            continue
        adjusted_position = (node.position[0] + offset[0], node.position[1] + offset[1])
        if node.learnable and pygame.Rect(adjusted_position[0] - 20, adjusted_position[1] - 20, 40, 40).collidepoint(mouse_pos):
            node.learn(player, occupied_positions)
            return
        handle_click([child for child in node.children.values() if child], player, mouse_pos, offset, occupied_positions)

def draw_ui(surface, player, mouse_pos):
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Talent Points: {player.talent_points}", True, (255, 255, 255))
    surface.blit(text, (10, 10))

    # Calculate the position of the '+' button based on the text width
    text_width, _ = font.size(f"Talent Points: {player.talent_points}")
    plus_button = pygame.Rect(20 + text_width, 10, 30, 30)

    # Change color if hovered
    if plus_button.collidepoint(mouse_pos):
        pygame.draw.rect(surface, (255, 255, 0), plus_button)  # Yellow if hovered
    else:
        pygame.draw.rect(surface, (255, 255, 255), plus_button)  # White otherwise

    plus_text = font.render("+", True, (0, 0, 0))
    surface.blit(plus_text, (25 + text_width, 5))
    return plus_button

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Talent Tree")

# Set up clock
clock = pygame.time.Clock()

# Generate the talent tree
talent_tree, occupied_positions = generate_talent_tree()

# Dummy player class with talent points
class Player:
    def __init__(self):
        self.stats = {'strength': 0, 'agility': 0, 'intelligence': 0, 'vitality': 0}
        self.talent_points = 100

player = Player()

# Camera offset
offset = [0, 0]
dragging = False
last_mouse_pos = None

# Main loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                dragging = True
                last_mouse_pos = pygame.mouse.get_pos()
            elif event.button == 3:
                handle_click(talent_tree, player, mouse_pos, offset, occupied_positions)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                # Check if the '+' button was clicked
                plus_button = draw_ui(screen, player, mouse_pos)
                if plus_button.collidepoint(mouse_pos):
                    player.talent_points += 100

    if dragging:
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - last_mouse_pos[0]
        dy = mouse_pos[1] - last_mouse_pos[1]
        offset[0] += dx
        offset[1] += dy
        last_mouse_pos = mouse_pos

    screen.fill((0, 0, 0))
    draw_talent_tree(screen, talent_tree, offset, mouse_pos)
    plus_button = draw_ui(screen, player, mouse_pos)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
