import pygame
import sys
import math
import random

# Options
RANDOM_BOT = True
BOT_COLOR = 1

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
screen = pygame.display.set_mode((WIDTH, HEIGHT-200))
pygame.display.set_caption("Yinsh!")
font = pygame.font.SysFont("Courier", 14)
font2 = pygame.font.SysFont("Courier", 20)


####################################################################  ---UTILS
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
        screen.blit(label,(int(WIDTH/2-60),int(HEIGHT/15)))
    else:
        label = font.render("Black", 1, (0,0,0))
        screen.blit(label,(int(WIDTH/2-60),int(HEIGHT/15)))
    label = font.render("playing...", 1, (255,255,255))
    screen.blit(label,(int(WIDTH/2-10),int(HEIGHT/15)))

    scorewhite = scoreblack = 5
    for (ring_x, ring_y, player_ring) in rings:
        if player_ring==1:
            scorewhite-=1
        else:
            scoreblack-=1

    label = font2.render(f"White {scorewhite} ", 1, (255,255,255))
    screen.blit(label,(int(WIDTH/2-90),int(HEIGHT/10)))
    label = font2.render(f"{scoreblack} Black", 1, (0,0,0))
    screen.blit(label,(int(WIDTH/2),int(HEIGHT/10)))

def draw_message(message, color):
    label = font2.render(message, 1, color)
    screen.blit(label,(int(WIDTH/2-6*len(message)),5))
    pygame.display.update()

def draw_pieces():
    # Draw rings
    for x, y, player in rings:
        color = RING_COLOR_P1 if player == 1 else RING_COLOR_P2
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 2, 3)
        
    # Draw markers
    for x, y, player in markers:
        color = MARKER_COLOR_P1 if player == 1 else MARKER_COLOR_P2
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 3)

def get_vertices_in_line(start, end, margin=5): #returns path between start and end of move
    #margin is maximum number of pixels in the gap between expected (calculated with steps) vertex position and actual vertex position
    start_x, start_y = start
    end_x, end_y = end

    path = [start]

    dx = end_x - start_x
    dy = end_y - start_y

    step_x = 0
    step_y = 0

    if abs(dy) <= margin:  # horizontal movement
        step_x = VERTEX_SPACING * (-1 if dx < 0 else 1)
    elif abs(dx) - int(abs(dy) * (2 / math.sqrt(3))) <= margin:  # diagonal
        step_x = VERTEX_SPACING // 2 * (-1 if dx < 0 else 1)
        step_y = int(VERTEX_SPACING * math.sqrt(3) / 2 * (-1 if dy < 0 else 1))
    else:
        return []  # not valid, not a straight line move

    current_x = start_x + step_x
    current_y = start_y + step_y
    outofbounds = False
    jumped = False
    # check all positions along the line between start vertex and end vertex
    while (abs(current_x - end_x) > margin or abs(current_y - end_y) > margin):
        # find closest vertex to calculated values with the step, if not inside margin yet
        jumping = False
        closest_vertex = None
        closest_distance = max(WIDTH,HEIGHT)+1

        for x, y in vertex_positions:
            distance = math.hypot(x - current_x, y - current_y)
            if distance < closest_distance:
                closest_distance = distance
                closest_vertex = (x, y)

        ''' We need to check if it jumped over a ring (invalid), if it jumped over more than one consecutive sequence of markers (invalid) and in case of a jump, if it landed exactly after a sequence of markers '''
        if closest_vertex and closest_distance <= margin: #if vertex inside margin its the next on the path
            (vertex_x, vertex_y) = closest_vertex
            for (ring_x, ring_y, player_ring) in rings:
                if vertex_x==ring_x and vertex_y==ring_y: # found a ring, invalid move
                    print("jumped over a ring")
                    return []
            
            for (marker_x, marker_y, player_marker) in markers:
                if vertex_x==marker_x and vertex_y==marker_y: # found a marker, a jump is performed
                    jumping = True
                    jumped = True
                    break

            if jumped and not jumping: #already jumped and tried to keep going without landing right after
                print("tried to overjump")
                return []
            
            path.append(closest_vertex) #valid move so far, added vertex to path

        current_x += step_x
        current_y += step_y

        if not (current_x<=WIDTH and current_y<=HEIGHT and current_x>=0 and current_y>=0): #Check if verification finds the final vertex to place the ring at
            outofbounds = True
            break
    if outofbounds: #if it doesnt find the final vertex just return empty, not valid
        return []
    path.append(end)
    return path

def get_valid_moves(player_turn): # returns all possible moves for a turn
    valid_moves = []
    occupied_positions = {(piece_x, piece_y) for (piece_x, piece_y, piece_p) in rings + markers}

    for i, (ring_x, ring_y, ring_p) in enumerate(rings):  
        if ring_p == player_turn:  # Only move the bot's own rings
            for x, y in vertex_positions:  # Check all board positions
                if (x, y) in occupied_positions:  # Skip occupied spots
                    continue

                path = get_vertices_in_line((ring_x, ring_y), (x, y))
                if path:  # If path is valid, store the move
                    valid_moves.append((i, (ring_x, ring_y), (x, y), path))

    return valid_moves


####################################################################  ---RANDOM BOT
def random_bot_make_move(player_turn): #plays a random bot move
    valid_moves = get_valid_moves(player_turn)
    
    if not valid_moves:
        print("Bot has no valid moves!")
        return False

    ring_index, (old_x, old_y), (new_x, new_y), path = random.choice(valid_moves)
    
    # Place a marker before moving the ring
    markers.append((old_x, old_y, player_turn))

    # Flip markers along the path
    for path_x, path_y in path[1:]:  # Ignore the first position
        for j, (marker_x, marker_y, marker_p) in enumerate(markers):
            if (marker_x, marker_y) == (path_x, path_y):
                markers[j] = (marker_x, marker_y, 3 - marker_p)  # Flip marker

    # Move the ring
    rings[ring_index] = (new_x, new_y, player_turn)
    
    print(f"Bot moved ring from ({old_x}, {old_y}) to ({new_x}, {new_y})")
    return True

def bot_place_ring(player_turn):
    occupied_positions = {(x, y) for (x, y, p) in rings}  # Rings already placed
    available_positions = [pos for pos in vertex_positions if pos not in occupied_positions]

    if not available_positions:
        print("No available positions to place a ring!")
        return False

    new_x, new_y = random.choice(available_positions)
    rings.append((new_x, new_y, player_turn))

    print(f"Bot placed a ring at ({new_x}, {new_y})")
    return True

####################################################################  ---PLAYER MOVES
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
                                if path==[]: #path empty = move not good
                                    print("not a valid move")
                                    markers.remove((ring_x, ring_y, player_turn)) #remove marker we placed
                                    return False
                                else:
                                    for (path_x, path_y) in path[1:]: #flip the markers in the path, except the one we just put down
                                        for j, (marker_x, marker_y, marker_player) in enumerate(markers):
                                            if (marker_x==path_x and marker_y==path_y):
                                                markers[j] = (marker_x, marker_y, 3 - marker_player)
                                print(markers)
                                print(path)
                                rings[i] = (x, y, ring_p)
                                return True  # moved a ring
    return False  # didnt click a ring


####################################################################  ---GAME UTILS
def check_5_line(player_turn):
    #Check if there are 5 markers of the same color aligned, if so remove a ring

    directions = [ # list possible sequence directions
        (VERTEX_SPACING, 0),
        (VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)),
        (-VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2))
    ]

    marker_positions = {(x, y): player for (x, y, player) in markers} #extract marker positions by player

    sequences = []

    for (x, y, player) in markers: #for every marker
        for dx, dy in directions: #and every direction
            sequence = [(x, y)] #initialize an array with the markers in the line (already with the one we are iterating over in there)
            for i in range(1, 5): #search for 4 more markers in a row in the direction we are iterating over
                next_x, next_y = x + i * dx, y + i * dy #calculate next position
                if (next_x, next_y) in marker_positions and marker_positions[(next_x, next_y)] == player: #if marker of the correct player is found keep going
                    sequence.append((next_x, next_y))
                else: #if marker is not found stop and go next direction/marker combo
                    break

            '''TODO In case of multiple sequences player must be able to choose which sequence to select'''
            if len(sequence) == 5: # if 5 consecutive markers are found
                print(f"player {player} formed a line at {sequence}!")
                sequences.append((sequence, player)) #add sequence to a list

    if (len(sequences)>0):
        draw_board(player_turn) 
        draw_pieces()
        pygame.display.flip()
        choosing = True
        selected_sequence = None

        ################ KINDA NAIVE IMPLEMENTATION
        '''if RANDOM_BOT and player_turn == BOT_COLOR:
            if BOT_COLOR in sequences and sequences[BOT_COLOR]:  #bot made a sequence
                selected_sequence = random.choice(player_sequences[BOT_COLOR])

            # remove markers from the selected sequence
            markers[:] = [m for m in markers if (m[0], m[1]) not in selected_sequence]
            draw_board(player_turn)
            draw_pieces()
            pygame.display.flip()
            remove_ring(BOT_COLOR if BOT_COLOR in player_sequences else (3 - BOT_COLOR))  # remove the correct ring

            check_game_over(player_turn)
            return True'''

        while choosing:
            # display sequence numbers on the side if not a bot playing
            if len(set(own for _, own in sequences))==2:
                draw_board(player_turn)
                draw_pieces()
                draw_message("Both players made a sequence! Click to proceed",((255,255,255) if player==1 else (0,0,0)))

            elif RANDOM_BOT and any(own==BOT_COLOR for _, own in sequences):
                draw_message("The bot made a sequence! Click to proceed",((255,255,255) if BOT_COLOR==1 else (0,0,0)))
                
            else:
                draw_message("You made a sequence! Choose which one to eliminate",((255,255,255) if player==1 else (0,0,0)))
                font = pygame.font.Font(None, 36)
                for idx, (seq,_) in enumerate(sequences):
                    text_color = (255, 255, 0) if selected_sequence == seq else (255, 255, 255) if player_turn == 1 else (0,0,0) # goes yellow when number is selected
                    text = font.render(str(idx + 1), True, text_color)
                    screen.blit(text, (50, 10 + idx * 40))
                    

            # highlight selected sequence
            if selected_sequence is not None:
                for (x, y) in selected_sequence:  # iterate through selected sequence
                    pygame.draw.circle(screen, (255, 0, 0), (x, y), VERTEX_SPACING // 3, 3)  # goes red when highlighted

            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if len(set(own for _, own in sequences))==1: #if only one player made a sequence
                        
                        only_player = sequences[0][1]  # Get the player who formed the sequence
                        if RANDOM_BOT and only_player == BOT_COLOR:  # Bot selects automatically
                            selected_sequence = random.choice([seq for seq, _ in sequences])
                            markers[:] = [m for m in markers if (m[0], m[1]) not in selected_sequence]
                            draw_board(player_turn)
                            draw_pieces()
                            pygame.display.flip()
                            remove_ring(BOT_COLOR)
                            choosing = False
                            
                        else:
                            for idx, (seq,own) in enumerate(sequences): # check if a number is clicked
                                if 50 <= mouse_x <= 80 and 10 + idx * 40 <= mouse_y <= 40 + idx * 40:
                                    draw_board(player_turn)
                                    draw_pieces()
                                    pygame.display.flip()
                                    if selected_sequence == seq:  
                                        # if already selected, confirm removal
                                        markers[:] = [m for m in markers if (m[0], m[1]) not in seq] #eliminate markers
                                        draw_board(player_turn)
                                        draw_pieces()
                                        pygame.display.flip()
                                        remove_ring(own) #remove ring
                                        choosing = False
                                    else:
                                        # if not selected highlght it
                                        selected_sequence = seq
                                    
                    elif len(set(own for _, own in sequences))==2:
                        player_sequences = {1: [], 2: []}

                        for seq, own in sequences:
                            player_sequences[own].append(seq)

                        selected_sequences = {1: None, 2: None}

                        for player in [1, 2]:  # Each player must choose a sequence
                            
                            if RANDOM_BOT and player == BOT_COLOR:  # Bot selects a sequence automatically if its his
                                selected_sequences[player] = random.choice(player_sequences[player])
                                markers[:] = [m for m in markers if (m[0], m[1]) not in selected_sequences[player]]
                                draw_board(player_turn)
                                draw_pieces()
                                pygame.display.flip()
                                remove_ring(BOT_COLOR)
                                print(f"Bot selects sequence {selected_sequences[player]}")
                                continue
                            
                            choosing = True
                            draw_board(player_turn)
                            draw_pieces()
                            pygame.display.flip()
                            while choosing:
                                draw_message("You made a sequence! Choose which one to eliminate",((255,255,255) if player==1 else (0,0,0)))

                                font = pygame.font.Font(None, 36)
                                for idx, seq in enumerate(player_sequences[player]):
                                    text_color = (255, 255, 0) if selected_sequences[player] == seq else (255, 255, 255) if player == 1 else (0,0,0)
                                    text = font.render(str(idx + 1), True, text_color)
                                    screen.blit(text, (50, 10 + idx * 40))

                                #highlight the selected sequence
                                if selected_sequences[player] is not None:
                                    for (x, y) in selected_sequences[player]:  
                                        pygame.draw.circle(screen, (255, 0, 0), (x, y), VERTEX_SPACING // 3, 3)  # Red outline

                                pygame.display.flip()

                                for event in pygame.event.get():
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        mouse_x, mouse_y = pygame.mouse.get_pos()
                                        for idx, seq in enumerate(player_sequences[player]):
                                            if 50 <= mouse_x <= 80 and 10 + idx * 40 <= mouse_y <= 40 + idx * 40:
                                                draw_board(player_turn)
                                                draw_pieces()
                                                pygame.display.flip()
                                                if selected_sequences[player] == seq:
                                                    # Confirm removal
                                                    markers[:] = [m for m in markers if (m[0], m[1]) not in seq]  # Eliminate markers
                                                    draw_board(player_turn)
                                                    draw_pieces()
                                                    pygame.display.flip()
                                                    remove_ring(player)  # Remove ring from the correct player
                                                    choosing = False
                                                else:
                                                    # Highlight selection
                                                    selected_sequences[player] = seq

                        
        check_game_over(player_turn) #game over check
        return True
    return False

def remove_ring(player):
    draw_message("You made a sequence! Eliminate a ring",((255,255,255) if player==1 else (0,0,0)))
    while True: #eliminate ring
        if player==BOT_COLOR and RANDOM_BOT: #bot eliminate ring
            bot_rings = [(i, ring_x, ring_y) for i, (ring_x, ring_y, ring_p) in enumerate(rings) if ring_p == player]

            if bot_rings:
                i, ring_x, ring_y = random.choice(bot_rings)
                rings.pop(i)
                print(f"Bot removed ring at ({ring_x}, {ring_y})")
                return
        
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, (ring_x, ring_y, ring_p) in enumerate(rings):  # see if there is a ring where I clicked
                    if math.hypot(mouse_x - ring_x, mouse_y - ring_y) < VERTEX_SPACING // 2 and player==ring_p:
                        rings.pop(i)
                        return

def check_game_over(player_turn):
    draw_board(player_turn)
    draw_pieces()
    pygame.display.flip()
    count_white = 0
    count_black = 0
    game_over = False
    for (_,_,color) in rings:
        if color == 1:
            count_white += 1
        else:
            count_black += 1
    if count_white <= 2 and count_black <= 2:
        draw_message("Game over, it's a draw", (255,255,0))
        game_over = True
    elif count_white <= 2:
        draw_message("Game over, White wins", (255,255,255))
        game_over = True
    elif count_black <= 2:
        draw_message("Game over, Black wins", (0,0,0))
        game_over = True
    while game_over:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()

def main():
    clock = pygame.time.Clock()
    running = True
    phase1 = True
    player_turn = 1
    ring_count = {1: 0, 2: 0}
    
    while running:
        draw_board(player_turn)
        draw_pieces()
        pygame.display.flip()

        if player_turn==BOT_COLOR and RANDOM_BOT: # bot moves here as black
            if not phase1:
                random_bot_make_move(player_turn)
                check_5_line(player_turn)
                player_turn = 3 - player_turn
            else:
                bot_place_ring(player_turn)
                ring_count[player_turn] += 1
                if ring_count[1] == ring_count[2] == 5:
                    phase1 = False
                player_turn = 3 - player_turn
                
        
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
                                player_turn = 3-player_turn
                                if ring_count[1] == ring_count[2] == 5:
                                    phase1 = False
                        else:
                            #game over check
                            check_game_over(player_turn)
                            if player_move(mouse_x, mouse_y, player_turn): # calculate move
                                print("turn")
                                check_5_line(player_turn)
                                player_turn = 3 - player_turn  # switch turn
                                print(get_valid_moves(player_turn)[0])
                                print("valid moves above")
                        break
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
