import pygame
import sys
import math
import random

# Options
RANDOM_BOT = False #single player / dev start
MINIMAX_BOT = False
MC_BOT = False

RANDOM_BOT1 = False #multiplayer, bot vs bot
MINIMAX_BOT1 = False
MC_BOT1 = False

RANDOM_BOT2 = False
MINIMAX_BOT2 = False
MC_BOT2 = False

DIFFICULTY1 = 2 #default difficulty is medium, can be 1, 2, 3
DIFFICULTY2 = 2

BOT_COLOR = 1 #1 for white, 2 for black

LOAD_GAME = 0 #LOADS GAME FROM FILE IF 1
HINTS = 1 #SHOWS HINTS IF 1
DEBUG = 0 #SHOWS DEBUG INFO IF 1

# Other Constants
WIDTH, HEIGHT = 800, 800
BG_COLOR = (96, 96, 96)
LINE_COLOR = (192, 192, 192)
RING_COLOR_P1 = (255, 255, 255)  # Player 1 Rings (White)
RING_COLOR_P2 = (0, 0, 0)        # Player 2 Rings (Black)
MARKER_COLOR_P1 = (255, 255, 255)  # Player 1 Markers (White)
MARKER_COLOR_P2 = (0, 0, 0)        # Player 2 Markers (Black)
VERTEX_SPACING = 50

# Define board structure based on vertex counts per row, modifiable
BOARD1 = [4, 7, 8, 9, 10, 9, 10 , 9, 8, 7, 4]
BOARD2 = [2,5,6,7,8,7,8,7,6,5,2]
BOARD3 = [3,4,5,6,7,8,7,6,5,4,3]
BOARD4 = [6,9,10,11,12,11,12,11,10,9,6]
VERTEX_ROWS = BOARD1

rings = []
markers = []
bot_moves_played = 0
best_move = "---"

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT-200))
pygame.display.set_caption("Yinsh!")
font = pygame.font.SysFont("Courier", 14)
font2 = pygame.font.SysFont("Courier", 20)

class GameState:
    def __init__(self):
        self.rings = []  # List of rings on the board
        self.markers = []  # List of markers on the board
        self.player_turn = 1  # Current player's turn (1 or 2)
        self.phase1 = True  # Whether the game is in the initial ring placement phase
        self.ring_count = {1: 0, 2: 0}  # Number of rings placed by each player

    def clone(self):
        new_state = GameState()
        new_state.rings = [ring for ring in self.rings]  # Deep copy of rings
        new_state.markers = [marker for marker in self.markers]  # Deep copy of markers
        new_state.player_turn = self.player_turn
        new_state.phase1 = self.phase1
        new_state.ring_count = self.ring_count.copy()  # Copy ring count dictionary
        return new_state

class MCNode: # Monte Carlo Tree Node
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.visits = 0
        self.wins = 0
        self.parent = parent
        self.children = []
        self.move = move

    def is_expanded(self): # Check if all children are expanded
        return len(self.children)==len(get_valid_moves(self.game_state.player_turn, self.game_state.rings, self.game_state.markers))
    
    def best_child(self, exploration_weight=0.75): # Select the best child based on UCT (Upper Confidence Bound for Trees) with a modifiable exploration_weight value
        return max(self.children, key=lambda child: child.wins / child.visits + exploration_weight * math.sqrt(math.log(self.visits) / child.visits))


############################################################################################################################################# UI
def draw_board(player_turn, menu=False):
    screen.fill(BG_COLOR)
    pixel_positions = [pos for _, pos in vertex_positions.items()]  # Extract pixel coordinates
    for (q, r), (x, y) in vertex_positions.items():
        # Draw triangular grid by connecting each vertex appropriately
        for dx, dy in [(VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)), 
                        (-VERTEX_SPACING // 2, int(VERTEX_SPACING * math.sqrt(3) / 2)),
                        (VERTEX_SPACING, 0)]:
            if (x + dx, y + dy) in pixel_positions:  # Check against extracted pixel positions
                pygame.draw.line(screen, LINE_COLOR, (x, y), (x + dx, y + dy), 1)
    if player_turn == 1:
        label = font.render("White", 1, (255,255,255))
        screen.blit(label,(int(WIDTH/2-60),int(HEIGHT/15)))
    elif player_turn == 2:
        label = font.render("Black", 1, (0,0,0))
        screen.blit(label,(int(WIDTH/2-60),int(HEIGHT/15)))
    if player_turn != None:
        label = font.render("playing...", 1, (255,255,255))
        screen.blit(label,(int(WIDTH/2-10),int(HEIGHT/15)))

    scorewhite = scoreblack = 5 # Scoreboard
    for (ring_x, ring_y, player_ring) in rings:
        if player_ring==1:
            scorewhite-=1
        else:
            scoreblack-=1

    if not menu:
        label = font2.render(f"White {scorewhite} ", 1, (255,255,255))
        screen.blit(label,(int(WIDTH/2-90),int(HEIGHT/10)))
        label = font2.render(f"{scoreblack} Black", 1, (0,0,0))
        screen.blit(label,(int(WIDTH/2),int(HEIGHT/10)))
    else:
        label = font2.render("YINSH! Menu", 1, (0,0,0))
        screen.blit(label,(int(WIDTH/2-65),int(HEIGHT/8)))

def draw_message(message, color): # Display a message on the screen
    label = font2.render(message, 1, color)
    screen.blit(label,(int(WIDTH/2-6*len(message)),5))
    pygame.display.flip()

def draw_eval(eval): # Display the evaluation of the current board
    streval = str(eval)
    label = font2.render("Board eval: "+streval, 1, (255,255,255) if eval>=0 else (0,0,0))
    screen.blit(label,(int(WIDTH-250),50))

def draw_bot_eval(best_eval, best_move): # Display the minimax depth 3 evaluation of the position
    strmove = str(best_move[1]) + " to " + str(best_move[2])
    label = font.render(strmove, 1, (255,255,0))
    screen.blit(label,(int(WIDTH-180),100))
    label = font.render("Best move: ", 1, (255,255,0))
    screen.blit(label,(int(WIDTH-175),80))
    pygame.display.flip()

def draw_pieces():
    # Draw rings
    for q, r, player in rings:
        color = RING_COLOR_P1 if player == 1 else RING_COLOR_P2
        x, y = vertex_positions[(q, r)]
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 2, 3)
        
    # Draw markers
    for q, r, player in markers:
        color = MARKER_COLOR_P1 if player == 1 else MARKER_COLOR_P2
        x, y = vertex_positions[(q, r)]
        pygame.draw.circle(screen, color, (x, y), VERTEX_SPACING // 3)

def draw_menu():
    screen.fill((50, 50, 50))  # Background color

    # Draw the board for aesthetics
    draw_board(None, menu=True)

    # Menu title and options
    title_font = pygame.font.SysFont("Courier", 36)
    title_label = title_font.render("START GAME", True, (255, 215, 0))
    screen.blit(title_label, (WIDTH // 2 - title_label.get_width() // 2, 20))

    hint_label = font2.render("HINTS", True, (0, 255, 0) if HINTS else (255,0,0))
    screen.blit(hint_label, (WIDTH // 2 - hint_label.get_width() // 2, 55))

    hint_label = font2.render("DEBUG", True, (0, 255, 0) if DEBUG else (255,0,0))
    screen.blit(hint_label, (WIDTH // 2 - hint_label.get_width() // 2, 75))

    hint_label = font2.render("CHANGE BOARD", True, (0, 255, 255))
    screen.blit(hint_label, (WIDTH // 2 - hint_label.get_width() // 2, HEIGHT // 2-90))

    hint_label = font2.render("LOAD GAME", True, (0, 0, 255))
    screen.blit(hint_label, (WIDTH // 2 - hint_label.get_width() // 2, HEIGHT - 225))

    # Player 1 slot
    pygame.draw.rect(screen, (0, 128, 255), (WIDTH // 4 - 100, HEIGHT // 3, 200, 50))
    if not (MC_BOT1 or MINIMAX_BOT1 or RANDOM_BOT1):
        p1_label = font2.render("P1: Human", True, (255, 255, 255))
    elif MC_BOT1:
        p1_label = font2.render("P1: MC Bot", True, (255, 255, 255))
    elif MINIMAX_BOT1:
        p1_label = font2.render("P1: Minimax Bot", True, (255, 255, 255))
    elif RANDOM_BOT1:
        p1_label = font2.render("P1: Random Bot", True, (255, 255, 255))
    screen.blit(p1_label, (WIDTH // 4 - p1_label.get_width() // 2, HEIGHT // 3 + 10))

    # Player 2 slot
    pygame.draw.rect(screen, (255, 69, 0), (3 * WIDTH // 4 - 100, HEIGHT // 3, 200, 50))
    if not (MC_BOT2 or MINIMAX_BOT2 or RANDOM_BOT2):
        p2_label = font2.render("P2: Human", True, (255, 255, 255))
    elif MC_BOT2:
        p2_label = font2.render("P2: MC Bot", True, (255, 255, 255))
    elif MINIMAX_BOT2:
        p2_label = font2.render("P2: Minimax Bot", True, (255, 255, 255))
    elif RANDOM_BOT2:
        p2_label = font2.render("P2: Random Bot", True, (255, 255, 255))
    screen.blit(p2_label, (3 * WIDTH // 4 - p2_label.get_width() // 2, HEIGHT // 3 + 10))

    easy_label = font.render("Easy", True, (0, 0, 0))
    medium_label = font.render("Medium", True, (0, 0, 0))
    hard_label = font.render("Hard", True, (0, 0, 0))

    # Difficulty buttons for Player 1
    if (MC_BOT1 or MINIMAX_BOT1):
        pygame.draw.rect(screen, (0, 255, 0) if DIFFICULTY1 == 1 else (128, 128, 128), (WIDTH // 4 - 100, HEIGHT // 3 + 70, 60, 30))
        screen.blit(easy_label, (WIDTH // 4 - 85, HEIGHT // 3 + 75))

        pygame.draw.rect(screen, (255, 255, 0) if DIFFICULTY1 == 2 else (128, 128, 128), (WIDTH // 4 - 30, HEIGHT // 3 + 70, 60, 30))
        screen.blit(medium_label, (WIDTH // 4 - 25, HEIGHT // 3 + 75))

        pygame.draw.rect(screen, (255, 0, 0) if DIFFICULTY1 == 3 else (128, 128, 128), (WIDTH // 4 + 40, HEIGHT // 3 + 70, 60, 30))
        screen.blit(hard_label, (WIDTH // 4 + 55, HEIGHT // 3 + 75))

    # Difficulty buttons for Player 2
    if (MC_BOT2 or MINIMAX_BOT2):
        pygame.draw.rect(screen, (0, 255, 0) if DIFFICULTY2 == 1 else (128, 128, 128), (3 * WIDTH // 4 - 100, HEIGHT // 3 + 70, 60, 30))
        screen.blit(easy_label, (3 * WIDTH // 4 - 85, HEIGHT // 3 + 75))

        pygame.draw.rect(screen, (255, 255, 0) if DIFFICULTY2 == 2 else (128, 128, 128), (3 * WIDTH // 4 - 30, HEIGHT // 3 + 70, 60, 30))
        screen.blit(medium_label, (3 * WIDTH // 4 - 25, HEIGHT // 3 + 75))

        pygame.draw.rect(screen, (255, 0, 0) if DIFFICULTY2 == 3 else (128, 128, 128), (3 * WIDTH // 4 + 40, HEIGHT // 3 + 70, 60, 30))
        screen.blit(hard_label, (3 * WIDTH // 4 + 55, HEIGHT // 3 + 75))

############################################################################################################################################# BOARD UTILS
def generate_board_positions():
    # Board is generated on a square grid centered on the middle of the board, strategically positioned over the hexagonal yinsh board, this saves computation effort compared to our previous implementation, 
    # which used trigonometric functions to search through vertices, 
    # given the difficulty of representing a hexagonal board where only the vertices are playable
    # This means the possible unitary move DIRECTIONS are (1,1), (-1,1) and (2,0), as this fits both grids perfectly in this overlapping model
    positions = {}
    start_x = WIDTH // 2
    start_y = HEIGHT // 6

    y = start_y
    for row, count in enumerate(VERTEX_ROWS):
        for i in range(count):
            x = start_x - (count - 1) * (VERTEX_SPACING // 2) + i * VERTEX_SPACING
            q = int(2 * (i - (count - 1) / 2))  # Calculate x coordinate
            r = len(VERTEX_ROWS) // 2 - row # Calculate y coordinate
            positions[(q, r)] = (x, y)  # Store grid coordinate as key and pixels as value
        y += int(VERTEX_SPACING * math.sqrt(3) / 2)  # Adjust vertical spacing correctly
    return positions

vertex_positions = generate_board_positions()
if DEBUG:
    print(vertex_positions) #debug

def get_vertices_in_line(start, end, these_rings, these_markers): #gets all possible moves in a straight line from a given position
    start_q, start_r = start
    end_q, end_r = end

    path = [start]
    drow = end_q - start_q
    dcol = end_r - start_r

    step_row = 0
    step_col = 0

    # Determine movement direction
    
    if abs(drow) == abs(dcol):  # Diagonal movement
        step_row = 1 if drow > 0 else -1
        step_col = 1 if dcol > 0 else -1
    elif dcol == 0:  # Horizontal movement (Right or Left)
        step_row = 2 if drow > 0 else -2
    else:
        #print("Invalid move: not a straight line ", (start, end))
        #print(drow, dcol)
        return []  # Not a valid straight-line move

    current_q = start_q + step_row
    current_r = start_r + step_col
    jumping = False

    # Precompute occupied positions for quick lookup
    ring_positions = {(ring_q, ring_r) for ring_q, ring_r, _ in these_rings}
    marker_positions = {(marker_q, marker_r) for marker_q, marker_r, _ in these_markers}

    # Traverse the path
    while (current_q != end_q or current_r != end_r):
        # Check if the current position is a valid vertex
        if (current_q, current_r) not in vertex_positions.keys():
            #print("Invalid vertex:", (current_q, current_r))
            return []  # No valid vertex found

        # Check for rings
        if (current_q, current_r) in ring_positions:
            #print("Invalid move: jumped over a ring")
            return []  # Invalid move: jumped over a ring

        # Check for markers
        if (current_q, current_r) in marker_positions:
            jumping = True  # Mark as jumped
        elif jumping:  # If jumping and no marker found we must land
            return []

        path.append((current_q, current_r))
        current_q += step_row
        current_r += step_col

    path.append(end)
    return path

def get_valid_moves(player_turn, these_rings, these_markers, can_gameover=True): #gets all possible moves for a given player
    valid_moves = []
    occupied_positions = {(piece_q, piece_r) for piece_q, piece_r, _ in these_rings + these_markers}

    # Precompute ring positions for the current player
    player_rings = [(i, ring_q, ring_r) for i, (ring_q, ring_r, ring_p) in enumerate(these_rings) if ring_p == player_turn]

    for i, ring_q, ring_r in player_rings:
        for (q, r), _ in vertex_positions.items():  # Iterate over all valid vertices
            if (q, r) in occupied_positions:  # Skip occupied spots
                continue

            # Check if the path is valid
            path = get_vertices_in_line((ring_q, ring_r), (q, r), these_rings, these_markers)
            if path:
                valid_moves.append((i, (ring_q, ring_r), (q, r), path))

    if len(valid_moves)==0 and can_gameover:
        check_game_over(player_turn, nomoves=True)
    return valid_moves

################################################################################################### SAVE AND LOAD GAME
def save_game_state(ring_count, player_turn): #Saves game state to a file if the board is the original one
    if VERTEX_ROWS == BOARD1:
        with open("game_state.txt", "w") as f:
            # Save rings
            f.write("RINGS:\n")
            for ring in rings:
                f.write(f"{ring[0]},{ring[1]},{ring[2]}\n")
            
            # Save markers
            f.write("MARKERS:\n")
            for marker in markers:
                f.write(f"{marker[0]},{marker[1]},{marker[2]}\n")
            
            # Save ring count and player turn
            f.write("RING_COUNT:\n")
            ring_count = {1: len([r for r in rings if r[2] == 1]), 2: len([r for r in rings if r[2] == 2])}
            f.write(f"{ring_count[1]},{ring_count[2]}\n")
            # Save player turn
            f.write("PLAYER_TURN:\n")
            f.write(f"{player_turn}\n")
            # Save number of bot moves played
            f.write("BOT MOVES MADE:\n")
            f.write(f"{bot_moves_played}\n")
        if DEBUG:
            print("Game state saved!")
    elif DEBUG:
        print("Invalid board size for saving game state.")

def load_game_state(): #Loads game state from file
    global rings, markers, bot_moves_played
    rings = []
    markers = []
    
    with open("game_state.txt", "r") as f:
        lines = f.readlines()
        
        # Parse rings
        ring_section = lines.index("RINGS:\n") + 1
        marker_section = lines.index("MARKERS:\n")
        for line in lines[ring_section:marker_section]:
            q, r, player = map(int, line.strip().split(","))
            rings.append((q, r, player))
        
        # Parse markers
        marker_section = lines.index("MARKERS:\n") + 1
        ring_count_section = lines.index("RING_COUNT:\n")
        for line in lines[marker_section:ring_count_section]:
            q, r, player = map(int, line.strip().split(","))
            markers.append((q, r, player))
        
        # Parse ring count
        ring_count_section = lines.index("RING_COUNT:\n") + 1
        player_turn_section = lines.index("PLAYER_TURN:\n")
        ring_count = dict(zip([1, 2], map(int, lines[ring_count_section:player_turn_section][0].strip().split(","))))
        
        # Parse player turn
        player_turn_section = lines.index("PLAYER_TURN:\n") + 1
        player_turn = int(lines[player_turn_section].strip())

        # Parse bot moves played
        bot_moves_played_section = lines.index("BOT MOVES MADE:\n") + 1
        bot_moves_played = int(lines[bot_moves_played_section].strip())

    
    if DEBUG:
        print("Game state loaded!")
    return (ring_count, player_turn)

##########################################################################################################################  ---RANDOM BOT / BOT UTILS
def random_bot_make_move(player_turn): #plays a random bot move
    valid_moves = get_valid_moves(player_turn, rings, markers)
    
    if not valid_moves:
        return False

    ring_index, (old_q, old_r), (new_q, new_r), path = random.choice(valid_moves)
    
    # Place a marker before moving the ring
    markers.append((old_q, old_r, player_turn))

    # Flip markers along the path
    for path_q, path_r in path[1:]:  # Ignore the first position
        for j, (marker_q, marker_r, marker_p) in enumerate(markers):
            if (marker_q, marker_r) == (path_q, path_r):
                markers[j] = (marker_q, marker_r, 3 - marker_p)  # Flip marker

    # Move the ring
    rings[ring_index] = (new_q, new_r, player_turn)
    
    return True

def bot_place_ring(player_turn): #places a ring for the bot in phase 1
    occupied_positions = {(q, r) for (q, r, p) in rings}  # Rings already placed
    available_positions = [pos for pos, _ in vertex_positions.items() if pos not in occupied_positions]

    # If using a minimax bot, evaluate each position
    if MINIMAX_BOT or MC_BOT:
        max_moves = float('-inf')
        best_position = None

        for new_q, new_r in available_positions:
            # Simulate placing the ring
            rings.append((new_q, new_r, player_turn))
            a = get_valid_moves(player_turn, rings, markers)
            simulated_moves = len(a)  # Evaluate mobility
            rings.pop()  # Undo the simulated placement

            # Keep track of the position that maximizes the number of valid moves, add randomness
            if simulated_moves > max_moves and random.randint(0, 10) > 8:
                max_moves = simulated_moves
                best_position = (new_q, new_r)

        # Place the ring at the best position
        if best_position:
            rings.append((best_position[0], best_position[1], player_turn))
            return True

    # Fallback to random placement if no minimax bot is used
    new_q, new_r = random.choice(available_positions)
    rings.append((new_q, new_r, player_turn))
    return True

############################################################################################################################### MINIMAX BOT
#Uses an evaluation function to score the board and uses minimax to find the best move according to the evaluation, works quickly and plays well with depth 3 (or 4 in middle-late game)
def count_marker_sequences(game_state, player): # Count sequences of markers for a given player
    directions = [
        (2, 0),  # Horizontal
        (1, 1),  # Diagonal /
        (-1, 1),  # Diagonal \
    ]

    score = 0
    marker_positions = {(q, r): p for (q, r, p) in game_state.markers}
    scored_sequences = set()  # Keep track of scored sequences to avoid duplicates

    for (q, r, p) in game_state.markers:
        if p != player:
            continue

        for dq, dr in directions:
            sequence = [(q, r)]  # Start a new sequence with the current marker

            # Check forward direction
            nq, nr = q + dq, r + dr
            while (nq, nr) in marker_positions and marker_positions[(nq, nr)] == player:
                sequence.append((nq, nr))
                nq += dq
                nr += dr

            # Convert the sequence to a tuple for immutability and comparison
            sequence_tuple = tuple(sequence)

            # Only score the sequence if it hasn't been scored yet
            if len(sequence) >= 2 and sequence_tuple not in scored_sequences:
                scored_sequences.add(sequence_tuple)  # Mark the sequence as scored

                # Score based on sequence length, a 4 marker sequence is scored like 1 + 4 + 10 = 15 points
                if len(sequence) >= 5:
                    score += 1000
                elif len(sequence) == 4:
                    score += 10 
                elif len(sequence) == 3:
                    score += 4
                elif len(sequence) == 2:
                    score += 1

    return score

def evaluate_board(game_state): #heuristic functions, more markers is good, bigger sequences are better, less rings is even better, centrality breaks ties
    #Returns positive score if white is better, negative if black is better

    # Count rings and markers for both players
    white_rings = sum(1 for _, _, color in game_state.rings if color == 1)
    black_rings = sum(1 for _, _, color in game_state.rings if color == 2)

    white_markers = sum(1 for _, _, color in game_state.markers if color == 1)
    black_markers = sum(1 for _, _, color in game_state.markers if color == 2)

    # Count marker sequences for both players
    white_marker_sequences = count_marker_sequences(game_state, 1)
    black_marker_sequences = count_marker_sequences(game_state, 2)

    # Ring centrality measure, useful but slightly slower than ideal
    white_centrality = sum(1 / (1 + math.hypot(x - WIDTH // 2, y - HEIGHT // 2)) for x, y, p in game_state.rings if p == 1)
    black_centrality = sum(1 / (1 + math.hypot(x - WIDTH // 2, y - HEIGHT // 2)) for x, y, p in game_state.rings if p == 2)

    score = (black_rings - white_rings) * 10
    score += (white_markers - black_markers) / 5
    score += (white_centrality - black_centrality) * 15
    score += (white_marker_sequences - black_marker_sequences) / 10 #TODO check this

    # if game is over on the board players get a very high score (to incentivize winning of course)
    if black_rings<=2:
        score = -10000
    if white_rings<=2:
        score = 10000
    if white_rings<=2 and black_rings<=2:
        score = 0

    return round(score, 2)


def minimax(game_state, depth, alpha, beta, maximizing_player):
    if depth == 0 or check_game_over(game_state, eval=True):
        return evaluate_board(game_state), None

    valid_moves = get_valid_moves(game_state.player_turn, game_state.rings, game_state.markers) # Get valid moves for the current player
    if not valid_moves:
        return evaluate_board(game_state), None

    if maximizing_player: #maximizing player
        max_eval = float('-inf')
        best_move = None
        for move in valid_moves:
            new_state = game_state.clone()
            apply_move(new_state, move)
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        best_move = None
        for move in valid_moves:
            new_state = game_state.clone()
            apply_move(new_state, move)
            eval_score, _ = minimax(new_state, depth - 1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def apply_move(game_state, move): # Apply a move to the game state
    ring_index, old_pos, new_pos, path = move
    marker_positions = {(q, r): player for (q, r, player) in game_state.markers}

    # Place a marker at the old ring position
    marker_positions[old_pos] = game_state.player_turn

    # Flip markers along the path
    for path_q, path_r in path[1:]:
        if (path_q, path_r) in marker_positions:
            marker_positions[(path_q, path_r)] = 3 - marker_positions[(path_q, path_r)]  # Flip marker

    # Update the ring position
    game_state.rings[ring_index] = (new_pos[0], new_pos[1], game_state.player_turn)

    # Convert marker_positions back to a list
    game_state.markers = [(q, r, player) for (q, r), player in marker_positions.items()]

    sequences = []

    directions = [  # List possible sequence directions
        (2, 0),  # Horizontal
        (1, 1),  # Diagonal /
        (-1, 1),  # Diagonal \
    ]

    marker_positions = {(q, r): player for (q, r, player) in game_state.markers}

    for (q, r, player) in game_state.markers:  # For every marker

        for dq, dr in directions:  # And every direction
            sequence = [(q, r)]  # Initialize an array with the markers in the line
            for i in range(1, 5):  # Search for 4 more markers in a row in the direction
                next_q, next_r = q + i * dq, r + i * dr  # Calculate next position
                if (next_q, next_r) in marker_positions and marker_positions[(next_q, next_r)] == player:  # If marker of the correct player is found, keep going
                    sequence.append((next_q, next_r))
                else:  # If marker is not found, stop and go to the next direction/marker combo
                    break

            if len(sequence) == 5:  # If 5 consecutive markers are found
                # Mark all markers in the sequence as used

                # Remove the markers in the sequence
                game_state.markers = [m for m in game_state.markers if (m[0], m[1]) not in sequence]

                # Find rings of the player who made the sequence
                player_rings = [(i, ring_q, ring_r) for i, (ring_q, ring_r, ring_p) in enumerate(game_state.rings) if ring_p == player]

                # Remove a ring from the player who made the sequence
                if player_rings:
                    i, ring_q, ring_r = random.choice(player_rings)
                    game_state.rings.pop(i)
                    game_state.player_turn = 3 - game_state.player_turn  # Switch player turn and return
                    return

    game_state.player_turn = 3 - game_state.player_turn

def minimax_bot_move(game_state, depth=4):
    draw_message("Bot is thinking...", (255, 255, 255) if MINIMAX_BOT1 and game_state.player_turn==1 else (0, 0, 0))

    best_eval, best_move = minimax(game_state, depth, alpha=float('-inf'), beta=float('inf'), maximizing_player= (MINIMAX_BOT1 and game_state.player_turn==1))

    if DEBUG:
        print(best_eval)

    if best_move:
        apply_move(game_state, best_move)
        global rings, markers
        rings = game_state.rings
        markers = game_state.markers
        return (True, best_eval, best_move)
    else:
        return (False, None, None)

####################################################################  ---MONTE CARLO BOT
#The monte carlo bot struggles to play well up until the late game. This is explained by the huge state space of the yinsh board in every move.
#since the board itself is quite big, the representation of the game state is costly, which reduces the amount of iterations that can be made in the 
# traditional human/board game timeframe. This combined with the randomness of every game and huge state space results in very sparse results that sometimes dont amount into any
# palpable good moves up until the late game, where there are less states and the ~1000 iterations can cover them properly.
# We tried mitigating this using the minimax heuristic function to help priorize locally good mvoes and explore the tree this way instead of the random approach, however this increased the cost of the game_state 
# representation for every move, which in turn lowered the amount of iterations that could be made in the same time frame, which resulted in the same problem as before, with results varying.
def evaluate_move(game_state, move):
    cloned_state = game_state.clone()
    apply_move(cloned_state, move)
    return evaluate_board(cloned_state)

def simulate_random_game(game_state, hard=False):
    current_state = game_state.clone()
    while True:
        valid_moves = get_valid_moves(current_state.player_turn, current_state.rings, current_state.markers, False)
        if not valid_moves:
            break
        
        if (hard): # If difficulty is set to hard, uses evaluation to prioritize moves instead of playing random
            # Use evaluation to prioritize moves
            ranked_moves = sorted(
                valid_moves,
                key=lambda move: evaluate_move(current_state, move) * (1 if current_state.player_turn == 1 else -1),
                reverse=True
            )
            move = ranked_moves[0]
        else:
            move = random.choice(valid_moves)  # Default to random moves if difficulty not set to hard

        apply_move(current_state, move)

        if len(current_state.rings) <= 7: #checks game over

            count_white = sum(1 for _, _, color in current_state.rings if color == 1)
            count_black = sum(1 for _, _, color in current_state.rings if color == 2)
            if count_white < 3 or count_black < 3:
                break

    # Return result
    if (MC_BOT1 and game_state.player_turn==1 and sum(1 for _, _, color in current_state.rings if color == 1) <= 2) or \
       (MC_BOT2 and game_state.player_turn==2 and sum(1 for _, _, color in current_state.rings if color == 2) <= 2):  # Check if its the bot
        return 1  # bot wins
    else:
        return 0  # bot does not win
    
def mcts(game_state, iterations=700, hard=False):
    root = MCNode(game_state)

    for _ in range(iterations):
        # Node Selection
        node = root
        while node.is_expanded() and node.children:
            node = node.best_child(exploration_weight=0.75)

        # Node Expansion
        if not node.is_expanded():
            move = random.choice([
                move for move in get_valid_moves(node.game_state.player_turn, node.game_state.rings, node.game_state.markers, False)
                if move not in [child.move for child in node.children]
            ])
            new_game_state = node.game_state.clone()
            apply_move(new_game_state, move)
            child_node = MCNode(new_game_state, parent=node, move=move)
            node.children.append(child_node)
            node = child_node

        # Game Simulation
        wins = simulate_random_game(node.game_state, hard)

        # Backpropagation
        while node:
            node.visits += 1
            node.wins += wins
            node = node.parent

    if DEBUG:
        print("MCTS Data:")
        for child in root.children:
            move = child.move
            visits = child.visits
            wins = child.wins
            win_rate = wins / visits if visits > 0 else 0
            print(f"Move: {move}, Visits: {visits}, Wins: {wins}, Win Rate: {win_rate:.2f}")

        print("best move: ", max(root.children, key=lambda child: child.visits).move)
        print("visits: ", max(root.children, key=lambda child: child.visits).visits)
        print("wins: ", max(root.children, key=lambda child: child.visits).wins)

    # Return the best move from the root, the one with the most visits as per the slides, we tried combining it with win rate but this worked better
    return max(root.children, key=lambda child: child.visits).move if root.children else (None, 0)

def mcts_bot_move(game_state, iterations=700, hard=False):
    draw_message("Bot is thinking...", (255, 255, 255) if MC_BOT1 and game_state.player_turn==1 else (0, 0, 0))

    best_move = mcts(game_state, iterations, hard)

    if best_move:
        apply_move(game_state, best_move)
        global rings, markers
        rings = game_state.rings
        markers = game_state.markers
        return True
    else:
        return False

#######################################################################################################################################################  ---PLAYER MOVES
def player_move(mouse_x, mouse_y, player_turn): #If click is in my own ring, read another click. If click is in possible space, place ring and new marker there.
    #Move must be made in a straight line to a blank space, jumped markers must be flipped. Rules https://www.gipf.com/yinsh/index.html for specifics.
    #When 5 straight markers are the same color they are removed from the board, together with a ring. First to remove 3 rings wins.
    #print("player move function start")
    #print(rings)
    #print(mouse_x, mouse_y, player_turn) # check click coordinates
    occupied_positions = {(piece_q, piece_r) for (piece_q, piece_r, piece_p) in rings + markers}  # Precompute occupied positions
    for i, (ring_q, ring_r, ring_p) in enumerate(rings):  # See if there is a ring where I clicked
        if math.hypot(mouse_x - vertex_positions[(ring_q, ring_r)][0], mouse_y - vertex_positions[(ring_q, ring_r)][1]) < VERTEX_SPACING // 2 and ring_p == player_turn:  # Check if it's my ring
            markers.append((ring_q, ring_r, player_turn))  # Place marker before moving the ring
            draw_board(player_turn)
            draw_pieces()
            pygame.draw.circle(screen, (0, 255, 0), vertex_positions[(ring_q, ring_r)], VERTEX_SPACING // 2, 3)  # Paint selected ring green
            while True:
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        m_x, m_y = pygame.mouse.get_pos()  # Get space it's moving to
                        for (q, r), (x, y) in vertex_positions.items():  # Run through every vertex
                            if (q, r) in occupied_positions:  # Doesn't work if vertex is occupied by ring or marker
                                continue

                            if math.hypot(m_x - x, m_y - y) < VERTEX_SPACING // 2:  # If not occupied
                                path = get_vertices_in_line((ring_q, ring_r), (q, r), rings, markers)
                                if not path:  # Path empty = move not valid
                                    markers.remove((ring_q, ring_r, player_turn))  # Remove marker we placed
                                    return False
                                else:
                                    for (path_q, path_r) in path[1:]:  # Flip the markers in the path, except the one we just put down
                                        for j, (marker_q, marker_r, marker_player) in enumerate(markers):
                                            if (marker_q == path_q and marker_r == path_r):
                                                markers[j] = (marker_q, marker_r, 3 - marker_player)
                                    rings[i] = (q, r, ring_p)  # Move the ring
                                    return True  # Moved a ring
    return False  # didnt click a ring


##############################################################################################################################################  ---ENDGAME UTILS
def check_5_line(player_turn):
    check_game_over(player_turn)  # Check if game is over
    # Check if there are 5 markers of the same color aligned, if so remove a ring

    directions = [  # List possible sequence directions
        (2, 0),  # Horizontal
        (1, 1),  # Diagonal /
        (-1, 1)  # Diagonal \
    ]

    marker_positions = {(q, r): player for (q, r, player) in markers}  # Extract marker positions by player

    sequences = []

    for (q, r, player) in markers:  # For every marker
        for dq, dr in directions:  # And every direction
            sequence = [(q, r)]  # Initialize an array with the markers in the line
            for i in range(1, 5):  # Search for 4 more markers in a row in the direction we are iterating over
                next_q, next_r = q + i * dq, r + i * dr  # Calculate next position
                if (next_q, next_r) in marker_positions and marker_positions[(next_q, next_r)] == player:  # If marker of the correct player is found, keep going
                    sequence.append((next_q, next_r))
                else:  # If marker is not found, stop and go to the next direction/marker combo
                    break

            if len(sequence) == 5:  # If 5 consecutive markers are found
                sequences.append((sequence, player))  # Add sequence to a list

    if len(sequences) > 0:
        draw_board(player_turn)
        draw_pieces()
        pygame.display.flip()
        choosing = True
        selected_sequence = None

        while choosing:
            if len(set(own for _, own in sequences)) == 2:
                draw_board(player_turn)
                draw_pieces()
                draw_message("Both players made a sequence! Click to proceed", ((255, 255, 255) if player == 1 else (0, 0, 0)))

            elif (RANDOM_BOT1 or MINIMAX_BOT1 or MC_BOT1 or RANDOM_BOT2 or MINIMAX_BOT2 or MC_BOT2) and any(
                (own == 1 and (RANDOM_BOT1 or MINIMAX_BOT1 or MC_BOT1)) or 
                (own == 2 and (RANDOM_BOT2 or MINIMAX_BOT2 or MC_BOT2)) 
                for _, own in sequences):
                draw_message("The bot made a sequence! Click to proceed", ((255, 255, 255) if (MC_BOT1 or RANDOM_BOT1 or MINIMAX_BOT1) else (0, 0, 0)))

            else:
                font = pygame.font.Font(None, 36)
                for idx, (seq, own) in enumerate(sequences):
                    draw_message("You made a sequence! Choose which one to eliminate", ((255, 255, 255) if own == 1 else (0, 0, 0)))
                    text_color = (255, 255, 0) if selected_sequence == seq else (255, 255, 255) if own == 1 else (0, 0, 0)
                    text = font.render(str(idx + 1), True, text_color)
                    screen.blit(text, (50, 10 + idx * 40))

            if selected_sequence is not None:
                for (q, r) in selected_sequence:  # Iterate through selected sequence
                    pygame.draw.circle(screen, (255, 0, 0), vertex_positions[(q, r)], VERTEX_SPACING // 3, 3)  # Highlight in red

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if len(set(own for _, own in sequences)) == 1:  # If only one player made a sequence simply eliminate the seqeunce and a ring
                        only_player = sequences[0][1]
                        if ((RANDOM_BOT1 or MINIMAX_BOT1 or MC_BOT1) and only_player == 1) or ((RANDOM_BOT2 or MINIMAX_BOT2 or MC_BOT2) and only_player == 2):
                            selected_sequence = random.choice([seq for seq, _ in sequences])
                            markers[:] = [m for m in markers if (m[0], m[1]) not in selected_sequence]
                            draw_board(player_turn)
                            draw_pieces()
                            pygame.display.flip()
                            remove_ring(only_player)
                            choosing = False
                        else:
                            for idx, (seq, own) in enumerate(sequences):
                                if 50 <= mouse_x <= 80 and 10 + idx * 40 <= mouse_y <= 40 + idx * 40:
                                    draw_board(player_turn)
                                    draw_pieces()
                                    pygame.display.flip()
                                    if selected_sequence == seq:
                                        markers[:] = [m for m in markers if (m[0], m[1]) not in seq]
                                        draw_board(player_turn)
                                        draw_pieces()
                                        pygame.display.flip()
                                        remove_ring(own)
                                        choosing = False
                                    else:
                                        selected_sequence = seq

                    elif len(set(own for _, own in sequences)) == 2: # if both players made a sequence eliminate a ring for each player
                        player_sequences = {1: [], 2: []}
                        for seq, own in sequences:
                            player_sequences[own].append(seq)

                        selected_sequences = {1: None, 2: None}

                        for player in [1, 2]:
                            if ((RANDOM_BOT1 or MINIMAX_BOT1 or MC_BOT1) and player == 1) or ((RANDOM_BOT2 or MINIMAX_BOT2 or MC_BOT2) and player == 2):
                                selected_sequences[player] = random.choice(player_sequences[player])
                                markers[:] = [m for m in markers if (m[0], m[1]) not in selected_sequences[player]]
                                draw_board(player_turn)
                                draw_pieces()
                                pygame.display.flip()
                                remove_ring(player)
                                continue

                            choosing = True
                            draw_board(player_turn)
                            draw_pieces()
                            pygame.display.flip()
                            while choosing:
                                draw_message("You made a sequence! Choose which one to eliminate", ((255, 255, 255) if player == 1 else (0, 0, 0)))

                                font = pygame.font.Font(None, 36)
                                for idx, seq in enumerate(player_sequences[player]):
                                    text_color = (255, 255, 0) if selected_sequences[player] == seq else (255, 255, 255) if player == 1 else (0, 0, 0)
                                    text = font.render(str(idx + 1), True, text_color)
                                    screen.blit(text, (50, 10 + idx * 40))

                                if selected_sequences[player] is not None:
                                    for (q, r) in selected_sequences[player]:
                                        pygame.draw.circle(screen, (255, 0, 0), vertex_positions[(q, r)], VERTEX_SPACING // 3, 3)

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
                                                    markers[:] = [m for m in markers if (m[0], m[1]) not in seq]
                                                    draw_board(player_turn)
                                                    draw_pieces()
                                                    pygame.display.flip()
                                                    remove_ring(player)
                                                    choosing = False
                                                else:
                                                    selected_sequences[player] = seq
                        check_game_over(player_turn)
                        return True

        check_game_over(player_turn)
        return True
    return False

def remove_ring(player):
    draw_message("You made a sequence! Eliminate a ring", ((255, 255, 255) if player == 1 else (0, 0, 0)))
    while True:
        if ((RANDOM_BOT1 or MINIMAX_BOT1 or MC_BOT1) and player == 1) or ((RANDOM_BOT2 or MINIMAX_BOT2 or MC_BOT2) and player == 2):  # Bot eliminates ring
            bot_rings = [(i, ring_q, ring_r) for i, (ring_q, ring_r, ring_p) in enumerate(rings) if ring_p == player]

            if bot_rings:
                i, ring_q, ring_r = random.choice(bot_rings)
                rings.pop(i)
                return

        for event in pygame.event.get(): #Human player eliminates ring
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, (ring_q, ring_r, ring_p) in enumerate(rings):  # See if there is a ring where I clicked
                    if math.hypot(mouse_x - vertex_positions[(ring_q, ring_r)][0], mouse_y - vertex_positions[(ring_q, ring_r)][1]) < VERTEX_SPACING // 2 and player == ring_p:
                        rings.pop(i) # If there is i pop it
                        return

def check_game_over(player_turn, eval=False, nomoves=False): #Check for game over conditions, if so display message and reset game
    global rings, markers, bot_moves_played, best_move
    draw_board(player_turn)
    draw_pieces()
    count_white = 0
    count_black = 0
    game_over = False
    for (_,_,color) in rings:
        if color == 1:
            count_white += 1
        else:
            count_black += 1
    if (count_white <= 2 and count_black <= 2) or (nomoves and count_black==count_white and eval==False): #Draw if there are no moves and players are tied or if they reach 3 rings removed in the same move
        draw_message("Game over, it's a draw", (255,255,0))
        game_over = True
    elif count_white <= 2 or (nomoves and count_white<count_black and eval==False): #White win if they have 3 rings removed or if there are no moves and they are ahead
        draw_message("Game over, White wins", (255,255,255))
        game_over = True
    elif count_black <= 2 or (nomoves and count_black<count_white and eval==False): #Black win if they have 3 rings removed or if there are no moves and they are ahead
        draw_message("Game over, Black wins", (0,0,0))
        game_over = True

    while game_over: #Game over screen waits for a click before continuing
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                rings=[]
                markers=[]
                bot_moves_played = 0
                best_move = "---"
                main()


def main():
    global vertex_positions, bot_moves_played, DIFFICULTY1, DIFFICULTY2, RANDOM_BOT1, RANDOM_BOT2, MINIMAX_BOT1, MINIMAX_BOT2, MC_BOT1, MC_BOT2, HINTS, LOAD_GAME, DEBUG, VERTEX_ROWS, BOARD1, BOARD2, BOARD3, BOARD4
    running = True
    phase1 = True
    player_turn = 1
    ring_count = {1: 0, 2: 0}
    game_state = GameState()
    board_eval = 0
    best_eval = 0
    best_move = "---"

    while running: #Menu loop
        draw_menu()  # Draw the menu

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN: #Fetch click coordinates
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if Player 1 slot is clicked, if so change player
                if WIDTH // 4 - 100 <= mouse_x <= WIDTH // 4 + 100 and HEIGHT // 3 <= mouse_y <= HEIGHT // 3 + 50:
                    if not (MC_BOT1 or MINIMAX_BOT1 or RANDOM_BOT1):
                        RANDOM_BOT1 = True
                    elif RANDOM_BOT1:
                        RANDOM_BOT1 = False
                        MINIMAX_BOT1 = True
                    elif MINIMAX_BOT1:
                        MINIMAX_BOT1 = False
                        MC_BOT1 = True
                    elif MC_BOT1:
                        MC_BOT1 = False

                # Check if Player 2 slot is clicked and if so change player
                elif 3 * WIDTH // 4 - 100 <= mouse_x <= 3 * WIDTH // 4 + 100 and HEIGHT // 3 <= mouse_y <= HEIGHT // 3 + 50:
                    if not (MC_BOT2 or MINIMAX_BOT2 or RANDOM_BOT2):
                        RANDOM_BOT2 = True
                    elif RANDOM_BOT2:
                        RANDOM_BOT2 = False
                        MINIMAX_BOT2 = True
                    elif MINIMAX_BOT2:
                        MINIMAX_BOT2 = False
                        MC_BOT2 = True
                    elif MC_BOT2:
                        MC_BOT2 = False

                # Check if Player 1 difficulty buttons are clicked, if so swithc difficulty
                elif WIDTH // 4 - 100 <= mouse_x <= WIDTH // 4 - 40 and HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 100:
                    DIFFICULTY1 = 1  # Easy
                elif WIDTH // 4 - 30 <= mouse_x <= WIDTH // 4 + 30 and HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 100:
                    DIFFICULTY1 = 2  # Medium
                elif WIDTH // 4 + 40 <= mouse_x <= WIDTH // 4 + 100 and HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 100:
                    DIFFICULTY1 = 3  # Hard

                # Check if Player 2 difficulty buttons are clicked, if so switch difficulty
                elif 3 * WIDTH // 4 - 100 <= mouse_x <= 3 * WIDTH // 4 - 40 and HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 100:
                    DIFFICULTY2 = 1  # Easy
                elif 3 * WIDTH // 4 - 30 <= mouse_x <= 3 * WIDTH // 4 + 30 and HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 100:
                    DIFFICULTY2 = 2  # Medium
                elif 3 * WIDTH // 4 + 40 <= mouse_x <= 3 * WIDTH // 4 + 100 and HEIGHT // 3 + 70 <= mouse_y <= HEIGHT // 3 + 100:
                    DIFFICULTY2 = 3  # Hard

                # Check if other buttons are clicked
                elif WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and 0 <= mouse_y <= 55:
                    running = False  # Exit the menu and start the game

                elif WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and 55 <= mouse_y <= 75:
                    HINTS = not HINTS  # Toggle hints
                
                elif WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and 75 <= mouse_y <= 95:
                    DEBUG = not DEBUG  # Toggle debug

                elif WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and 575 <= mouse_y:
                    LOAD_GAME = True
                    running = False  # Exit the menu and start the game

                elif WIDTH // 2 - 100 <= mouse_x <= WIDTH // 2 + 100 and HEIGHT//2-90 <= mouse_y <= HEIGHT//2-70:
                    if VERTEX_ROWS == BOARD1: #Swap the boards and regenerate vertex positions
                        VERTEX_ROWS = BOARD2
                    elif VERTEX_ROWS == BOARD2:
                        VERTEX_ROWS = BOARD3
                    elif VERTEX_ROWS == BOARD3:
                        VERTEX_ROWS = BOARD4
                    elif VERTEX_ROWS == BOARD4:
                        VERTEX_ROWS = BOARD1
                    vertex_positions = generate_board_positions()
                    print(vertex_positions)

        pygame.display.update()
                

    running=True

    if LOAD_GAME: #If load game just load the game state and start the game
        ring_count, player_turn = load_game_state()
        phase1 = False
        game_state.rings = rings
        game_state.markers = markers
        game_state.player_turn = player_turn
        game_state.phase1 = phase1
        game_state.ring_count = ring_count
        board_eval = evaluate_board(game_state)
        VERTEX_ROWS = BOARD1
        vertex_positions = generate_board_positions()
        LOAD_GAME = False

    while running: #Main game loop
        draw_board(player_turn) #Draw screen
        draw_pieces()
        draw_eval(board_eval)
        if HINTS: #Draw hints if activated
            draw_bot_eval(best_eval, best_move)


        if (player_turn==1 and RANDOM_BOT1) or (player_turn==2 and RANDOM_BOT2): # Check for random bot moves
            if not phase1: #normal moves
                random_bot_make_move(player_turn)
                bot_moves_played += 1
                check_5_line(player_turn)
                player_turn = 3 - player_turn
                game_state.rings = rings #Game state is updated
                game_state.markers = markers
                game_state.player_turn = player_turn
                game_state.phase1 = phase1
                game_state.ring_count = ring_count
                board_eval = (evaluate_board(game_state)) #Board evaluation
                if HINTS: #Hints are a result of a depth 3 minimax search to save time and space but still be accurate
                    best_eval, best_move = minimax(game_state, 3, alpha=float('-inf'), beta=float('inf'), maximizing_player=(player_turn==1))
                save_game_state(ring_count, player_turn)
            else: #Move in phase 1, place a ring, maximize amount of possible moves on each ring
                bot_place_ring(player_turn)
                ring_count[player_turn] += 1
                if ring_count[1] == ring_count[2] == 5:
                    phase1 = False
                player_turn = 3 - player_turn
                if not phase1: #If it was the last ring get ready for phase 2
                    game_state.rings = rings
                    game_state.markers = markers
                    game_state.player_turn = player_turn
                    game_state.phase1 = phase1
                    game_state.ring_count = ring_count
                    board_eval = (evaluate_board(game_state))
                    save_game_state(ring_count, player_turn)
        elif (player_turn==1 and MINIMAX_BOT1) or (player_turn==2 and MINIMAX_BOT2): # same process for minimax bot
            if not phase1:
                game_state.rings = rings
                game_state.markers = markers
                game_state.player_turn = player_turn
                game_state.phase1 = phase1
                game_state.ring_count = ring_count
                board_eval = (evaluate_board(game_state))
                if (DIFFICULTY1==1 and MINIMAX_BOT1 and player_turn==1) or (DIFFICULTY2==1 and MINIMAX_BOT2 and player_turn==2): #difficulty and amount of moves made determine the depth
                    if DEBUG:
                        print("depth 1")
                    _, best_eval, best_move = minimax_bot_move(game_state, 1)
                elif (DIFFICULTY1==2 and MINIMAX_BOT1 and player_turn==1) or (DIFFICULTY2==2 and MINIMAX_BOT2 and player_turn==2):
                    if DEBUG:
                        print("depth 2")
                    _, best_eval, best_move = minimax_bot_move(game_state, 2)
                elif ((MINIMAX_BOT1 or RANDOM_BOT1 or MC_BOT1) and player_turn==1) and ((MINIMAX_BOT2 or RANDOM_BOT2 or MC_BOT2) and player_turn==2): #in hard difficulty we Check how many moves are played, if enough are made we can search deeper as the state space is smaller
                    if DEBUG:
                        print("depth", 3+int(bot_moves_played>12))
                    _, best_eval, best_move = minimax_bot_move(game_state, 3+int(bot_moves_played>12))
                else:
                    if DEBUG:
                        print("depth", 3+int(bot_moves_played>6))
                    if (DIFFICULTY1==3 and MINIMAX_BOT1 and player_turn==1) or (DIFFICULTY2==3 and MINIMAX_BOT2 and player_turn==2):
                        _, best_eval, best_move = minimax_bot_move(game_state, 3+int(bot_moves_played>12))
                bot_moves_played += 1
                if DEBUG:
                    print("bot moved")
                check_5_line(player_turn)

                board_eval = (evaluate_board(game_state))
                draw_board(player_turn)
                draw_pieces()
                draw_eval(board_eval)
                if HINTS:
                    best_eval, best_move = minimax(game_state, 3, alpha=float('-inf'), beta=float('inf'), maximizing_player=(3-player_turn==1))
                    draw_bot_eval(best_eval, best_move)
                pygame.display.update()

                player_turn = 3 - player_turn
                save_game_state(ring_count, player_turn)
            else:
                bot_place_ring(player_turn)
                ring_count[player_turn] += 1
                if ring_count[1] == ring_count[2] == 5:
                    phase1 = False
                player_turn = 3 - player_turn
                if not phase1:
                    game_state.rings = rings
                    game_state.markers = markers
                    game_state.player_turn = player_turn
                    game_state.phase1 = phase1
                    game_state.ring_count = ring_count
                    board_eval = (evaluate_board(game_state))
                    save_game_state(ring_count, player_turn)

        elif (player_turn==1 and MC_BOT1) or (player_turn==2 and MC_BOT2): #same process for the monte carlo bot
            if not phase1:
                game_state.rings = rings
                game_state.markers = markers
                game_state.player_turn = player_turn
                game_state.phase1 = phase1
                game_state.ring_count = ring_count
                board_eval = (evaluate_board(game_state))

                if bot_moves_played <= 6: #dynamic iteration count, depending on the stage of the game we are in
                    iters = 300
                elif bot_moves_played <= 10:
                    iters = 500
                elif bot_moves_played <= 14:
                    iters = 700
                elif bot_moves_played <= 20:
                    iters = 1000
                else:
                    iters = 1250

                if (DIFFICULTY1==1 and MC_BOT1 and player_turn==1) or (DIFFICULTY2==1 and MC_BOT2 and player_turn==2):
                    iters = 200
                elif (DIFFICULTY1==3 and MC_BOT1 and player_turn==1) or (DIFFICULTY2==3 and MC_BOT2 and player_turn==2):
                    iters = int(iters / 2)
                    
                if DEBUG:
                    print("iterations:",iters)
                if (DIFFICULTY1==3 and MC_BOT1 and player_turn==1) or (DIFFICULTY2==3 and MC_BOT2 and player_turn==2): #MC++, the mc bot in hard difficulty uses the evaluation function to priorize moves when exploring the tree, instead of playing random every time
                    if DEBUG:
                        print("hard bot playing")
                    mcts_bot_move(game_state, iterations=iters, hard=True)
                else:
                    if DEBUG:
                        print("normal bot playing")
                    mcts_bot_move(game_state, iterations=iters)
                bot_moves_played += 1
                check_5_line(player_turn)

                board_eval = (evaluate_board(game_state))
                draw_board(player_turn)
                draw_pieces()
                draw_eval(board_eval)
                if HINTS:
                    best_eval, best_move = minimax(game_state, 3, alpha=float('-inf'), beta=float('inf'), maximizing_player=(3-player_turn==1))
                    draw_bot_eval(best_eval, best_move)
                pygame.display.update()

                player_turn = 3 - player_turn
                save_game_state(ring_count, player_turn)
            else:
                bot_place_ring(player_turn)
                ring_count[player_turn] += 1
                if ring_count[1] == ring_count[2] == 5:
                    phase1 = False
                player_turn = 3 - player_turn
                if not phase1:
                    game_state.rings = rings
                    game_state.markers = markers
                    game_state.player_turn = player_turn
                    game_state.phase1 = phase1
                    game_state.ring_count = ring_count
                    board_eval = (evaluate_board(game_state))
                    save_game_state(ring_count, player_turn)
        
                
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for (q, r), (x, y) in vertex_positions.items():  # Iterate over vertex coordinates
                    if math.hypot(mouse_x - x, mouse_y - y) < VERTEX_SPACING // 2:  # Check distance using pixel coordinates
                        if ring_count[player_turn] < 5 and phase1:  # Placing starting 10 rings, phase 1
                            if all(rq != q or rr != r for rq, rr, rp in rings):  # Check if position is unoccupied
                                rings.append((q, r, player_turn))  # Add ring using vertex coordinates
                                ring_count[player_turn] += 1
                                player_turn = 3 - player_turn
                                if ring_count[1] == ring_count[2] == 5:
                                    phase1 = False
                        else:
                            # Game over check
                            check_game_over(player_turn)
                            if player_move(mouse_x, mouse_y, player_turn):  # Calculate move
                                check_5_line(player_turn)
                                player_turn = 3 - player_turn  # Switch turn
                                
                                game_state.rings = rings
                                game_state.markers = markers
                                game_state.player_turn = player_turn
                                game_state.phase1 = phase1
                                game_state.ring_count = ring_count
                                board_eval = evaluate_board(game_state)

                                if HINTS and not (RANDOM_BOT1 or MINIMAX_BOT1 or MC_BOT1 or RANDOM_BOT2 or MINIMAX_BOT2 or MC_BOT2):
                                    best_eval, best_move = minimax(game_state, 3, alpha=float('-inf'), beta=float('inf'), maximizing_player=(3-player_turn==1))
                    
                                save_game_state(ring_count, player_turn)
                        break

        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
