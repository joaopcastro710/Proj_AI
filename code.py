import pygame
import sys
import math

# Constants
WIDTH, HEIGHT = 800, 800
BG_COLOR = (96, 96, 96)
LINE_COLOR = (192, 192, 192)
RING_COLOR_P1 = (255, 255, 255)  # Player 1 Rings (White)
RING_COLOR_P2 = (0, 0, 0)        # Player 2 Rings (Black)
MARKER_COLOR_P1 = (255, 255, 255)  # Player 1 Markers (White)
MARKER_COLOR_P2 = (0, 0, 0)        # Player 2 Markers (Black)
VERTEX_SPACING = 50

# Define board structure based on vertex counts per row
VERTEX_ROWS = [
    4, 7, 8, 9, 10, 9, 10 , 9, 8, 7, 4
]

rings = []
markers = []

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yinsh!")

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
print(vertex_positions) #Change coordinates to board coordinates instead of pixel values to facilitate computation

def draw_board():
    screen.fill(BG_COLOR)
    for x, y in vertex_positions:
        # Draw triangular grid by connecting each vertex appropriately
        for dx, dy in [(VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)), 
                        (-VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)),
                        (VERTEX_SPACING, 0)]:
            if (x + dx, y + dy) in vertex_positions:
                pygame.draw.line(screen, LINE_COLOR, (x, y), (x + dx, y + dy), 1)

def draw_pieces():
    # Draw rings
    for x, y, player in rings:
        color = RING_COLOR_P1 if player == 1 else RING_COLOR_P2
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 2, 3)
        
    # Draw markers
    for x, y, player in markers:
        color = MARKER_COLOR_P1 if player == 1 else MARKER_COLOR_P2
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 3)

def move(mouse_x, mouse_y, player_turn): #If click is in my own ring, read another click. If click is in possible space, place ring and new marker there.
    #Move must be made in a straight line to a blank space, jumped markers must be flipped. Rules https://www.gipf.com/yinsh/index.html for specifics.
    #When 5 straight markers are the same color they are removed from the board, together with a ring. First to remove 3 rings wins.
    print("move function start")
    print(rings)
    print(mouse_x, mouse_y, player_turn) # check click coordinates
    occupied_positions = {(piece_x, piece_y) for (piece_x, piece_y, piece_p) in rings+markers}  # precompute occupied positions
    for i, (ring_x, ring_y, ring_p) in enumerate(rings):  # see if there is a ring where I clicked
        print(ring_x, ring_y, ring_p)
        if math.hypot(mouse_x - ring_x, mouse_y - ring_y) < VERTEX_SPACING // 2 and ring_p == player_turn:  # check if itss my ring
            print("my ring")
            draw_board()
            draw_pieces()
            pygame.draw.circle(screen, (0, 255, 0), (ring_x, ring_y), VERTEX_SPACING // 2, 3)  # paint it green
            while True:
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        m_x, m_y = pygame.mouse.get_pos()  # check space its moving to
                        for x, y in vertex_positions:  # run through every vertex
                            if (x, y) in occupied_positions:  #advance if space occupied by ring or marker
                                continue

                            if math.hypot(m_x - x, m_y - y) < VERTEX_SPACING // 2:  # if not occupied and within range
                                print("moving")
                                # move ring and place marker
                                rings[i] = (x, y, ring_p)
                                markers.append((x, y, player_turn))
                                return True  # moved a ring
    return False  # didnt click a ring


def main():
    clock = pygame.time.Clock()
    running = True
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
                        if ring_count[player_turn] < 5:  # placing starting 10 rings
                            valid = True
                            for (rx,ry,rp) in rings:
                                if rx==x and ry==y:
                                    valid = False
                            if (valid):
                                rings.append((x, y, player_turn))
                                print(rings)
                                ring_count[player_turn] += 1
                                if ring_count[player_turn] == 5:
                                    ring_count[player_turn] += 1
                                    player_turn = 3 - player_turn
                        else: 
                            if move(mouse_x, mouse_y, player_turn): # calculate move
                                player_turn = 3 - player_turn  # switch turn
                        break
        
        draw_pieces()
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
