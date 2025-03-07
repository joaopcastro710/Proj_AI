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
font = pygame.font.SysFont("Courier", 14)

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
print(vertex_positions) #debug

def draw_board(player_turn):
    screen.fill(BG_COLOR)
    for x, y in vertex_positions:
        # Draw triangular grid by connecting each vertex appropriately
        for dx, dy in [(VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)), 
                        (-VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)),
                        (VERTEX_SPACING, 0)]:
            if (x + dx, y + dy) in vertex_positions:
                pygame.draw.line(screen, LINE_COLOR, (x, y), (x + dx, y + dy), 1)
    if player_turn == 1:
        label = font.render("White", 1, (255,255,255))
        screen.blit(label,(int(WIDTH/2-50),int(HEIGHT/15)))
    else:
        label = font.render("Black", 1, (0,0,0))
        screen.blit(label,(int(WIDTH/2-50),int(HEIGHT/15)))
    label = font.render("playing...", 1, (255,255,255))
    screen.blit(label,(int(WIDTH/2),int(HEIGHT/15)))

def draw_pieces():
    # Draw rings
    for x, y, player in rings:
        color = RING_COLOR_P1 if player == 1 else RING_COLOR_P2
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 2, 3)
        
    # Draw markers
    for x, y, player in markers:
        color = MARKER_COLOR_P1 if player == 1 else MARKER_COLOR_P2
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 3)

def player_move(mouse_x, mouse_y, player_turn): #If click is in my own ring, read another click. If click is in possible space, place ring and new marker there.
    #Move must be made in a straight line to a blank space, jumped markers must be flipped. Rules https://www.gipf.com/yinsh/index.html for specifics.
    #When 5 straight markers are the same color they are removed from the board, together with a ring. First to remove 3 rings wins.
    print("player move function start")
    print(rings)
    print(mouse_x, mouse_y, player_turn) # check click coordinates
    occupied_positions = {(piece_x, piece_y) for (piece_x, piece_y, piece_p) in rings+markers}  # precompute occupied positions
    for i, (ring_x, ring_y, ring_p) in enumerate(rings):  # see if there is a ring where I clicked
        print(ring_x, ring_y, ring_p)
        if math.hypot(mouse_x - ring_x, mouse_y - ring_y) < VERTEX_SPACING // 2 and ring_p == player_turn:  # check if itss my ring
            print("my ring")
            markers.append((ring_x, ring_y, player_turn)) #place marker before moving the ring
            draw_board(player_turn)
            draw_pieces()
            pygame.draw.circle(screen, (0, 255, 0), (ring_x, ring_y), VERTEX_SPACING // 2, 3)  # paint selected ring green
            while True:
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        m_x, m_y = pygame.mouse.get_pos()  # get space its moving to
                        for x, y in vertex_positions:  # run through every vertex
                            if (x, y) in occupied_positions:  # doesnt work if vertex is occupied by ring or marker
                                continue

                            if math.hypot(m_x - x, m_y - y) < VERTEX_SPACING // 2:  # if not occupied
                                print("moving from " + str(ring_x) + "," + str(ring_y) + " to "+ str(x) + "," + str(y))
                                # move ring
                                path = get_vertices_in_line((ring_x, ring_y),(x, y))
                                if path==[]:
                                    print("not a valid move")
                                    markers.remove((ring_x, ring_y, player_turn))
                                    return False
                                print(path)
                                rings[i] = (x, y, ring_p)
                                return True  # moved a ring
    return False  # didnt click a ring

def get_vertices_in_line(start, end, margin=2): #returns path between start and end of move
    #margin is maximum number of pixels in the gap between expected (calculated with steps) vertex position and actual vertex position
    start_x, start_y = start
    end_x, end_y = end

    path = [start]

    dx = end_x - start_x
    dy = end_y - start_y

    step_x = 0
    step_y = 0

    #BUG MOVING VERTICALLY OR CLOSE TO A DIAGONAL BUT NOT QUITE RIGHT BECAUSE THIS MATHEMATICAL VERIFICATION FAILS
    if abs(dy) <= margin:  # horizontal movement
        step_x = VERTEX_SPACING
        if dx < 0:
            step_x = - VERTEX_SPACING
    elif abs(dx) - abs(dy) * (2 / math.sqrt(3)) <= margin:  # left diagonal
        step_x = VERTEX_SPACING // 2 * (-1 if dx < 0 else 1)
        step_y = VERTEX_SPACING * math.sqrt(3) / 2 * (-1 if dy < 0 else 1)
    elif abs(dx) <= margin:  # right diagonal
        step_y = VERTEX_SPACING * math.sqrt(3) / 2 * (-1 if dy < 0 else 1)

    else:
        return []  # not valid, not a straight line move

    current_x = start_x + step_x
    current_y = start_y + step_y
    # check all positions along the line
    while (abs(current_x - end_x) > margin or abs(current_y - end_y) > margin):
        # find closest vertex to calculated values with the step, if not inside margin yet
        closest_vertex = None
        closest_distance = max(WIDTH,HEIGHT)+1

        for x, y in vertex_positions:
            distance = math.hypot(x - current_x, y - current_y)
            if distance < closest_distance:
                closest_distance = distance
                closest_vertex = (x, y)

        if closest_vertex and closest_distance <= margin: #if vertex inside margin its the next on the path
            path.append(closest_vertex)

        current_x += step_x
        current_y += step_y
        print(current_x, current_y)

    path.append(end)
    return path


def main():
    clock = pygame.time.Clock()
    running = True
    player_turn = 1
    ring_count = {1: 0, 2: 0}
    
    while running:
        draw_board(player_turn)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for x, y in vertex_positions:
                    if math.hypot(mouse_x - x, mouse_y - y) < VERTEX_SPACING // 2:
                        if ring_count[player_turn] < 5:  # placing starting 10 rings
                            if all(rx != x or ry != y for rx, ry, rp in rings):
                                rings.append((x, y, player_turn))
                                print(rings)
                                ring_count[player_turn] += 1
                                if ring_count[player_turn] == 5:
                                    ring_count[player_turn] += 1
                                    player_turn = 3 - player_turn
                        else: 
                            if player_move(mouse_x, mouse_y, player_turn): # calculate move
                                player_turn = 3 - player_turn  # switch turn
                        break
        
        draw_pieces()
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
