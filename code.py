import pygame
import sys
import math

# Constants
WIDTH, HEIGHT = 800, 800
BG_COLOR = (100, 100, 100)
LINE_COLOR = (200, 200, 200)
RING_COLOR_P1 = (255, 255, 255)  # Player 1 Rings (White)
RING_COLOR_P2 = (0, 0, 0)        # Player 2 Rings (Black)
MARKER_COLOR_P1 = (255, 255, 255)  # Player 1 Markers (White)
MARKER_COLOR_P2 = (0, 0, 0)        # Player 2 Markers (Black)
TRIANGLE_SIZE = 40
VERTEX_SPACING = 50

# Define board structure based on vertex counts per row
VERTEX_ROWS = [
    4, 7, 8, 9, 10, 9, 10 , 9, 8, 7, 4
]

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("YINSH Game")

def generate_board_positions():
    positions = []
    start_x = WIDTH // 2
    start_y = HEIGHT // 6
    
    y = start_y
    for row, count in enumerate(VERTEX_ROWS):
        x_offset = (max(VERTEX_ROWS) - count) * (VERTEX_SPACING // 2)
        for i in range(count):
            x = start_x - (count - 1) * (VERTEX_SPACING // 2) + i * VERTEX_SPACING
            positions.append((x, y))
        y += int(VERTEX_SPACING * math.sqrt(3) / 2)  # Adjust vertical spacing correctly
    return positions

vertex_positions = generate_board_positions()

def draw_board():
    screen.fill(BG_COLOR)
    for x, y in vertex_positions:
        # Draw triangular grid by connecting each vertex appropriately
        for dx, dy in [(VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)), 
                        (-VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)),
                        (VERTEX_SPACING, 0)]:
            if (x + dx, y + dy) in vertex_positions:
                pygame.draw.line(screen, LINE_COLOR, (x, y), (x + dx, y + dy), 1)

def main():
    clock = pygame.time.Clock()
    running = True
    rings = []
    markers = []
    player_turn = 1
    ring_count = {1: 0, 2: 0}
    
    while running:
        draw_board()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for x, y in vertex_positions:
                    if math.hypot(mouse_x - x, mouse_y - y) < VERTEX_SPACING // 2:
                        if ring_count[player_turn] < 5:  # First phase: placing rings
                            rings.append((x, y, player_turn))
                            ring_count[player_turn] += 1
                        elif ring_count[player_turn] == 5:
                            ring_count[player_turn] += 1
                            player_turn = 3 - player_turn
                        else:
                            markers.append((x, y, player_turn))
                            player_turn = 3 - player_turn  # Toggle turn
                        break
        
        # Draw rings
        for x, y, player in rings:
            color = RING_COLOR_P1 if player == 1 else RING_COLOR_P2
            pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 2, 3)
        
        # Draw markers
        for x, y, player in markers:
            color = MARKER_COLOR_P1 if player == 1 else MARKER_COLOR_P2
            pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 3)
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
