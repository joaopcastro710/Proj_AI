# YINSH - G138

## Prerequisites

To run this program, you need to have the following installed:

1. **Python 3.8 or higher**  
   Download and install Python from [python.org](https://www.python.org/).

2. **Pygame library**  
   Install Pygame by running the following command in your terminal:
   ```
   pip install pygame
   ```

## Run the Game

To run the program, execute the command: 
```
python game.py
```


## How to use the Program

### Menu Instructions

- When opening the application you will find a menu with some options:
   - From the top down you will see the "START GAME" button which starts a new game with the selected configurations.
   - Below a "HINTS" button you can toggle, if green then move hints will appear on the righthand side of the screen between every move played
   - Below a "DEBUG" button you can toggle, if green then the console from where the game was launched will print debug information regarding the game
   - In the middle of the screen you will find a blue "CHANGE BOARD" button, when you press it you will see the board in the background change. There are 4 boards to choose from, only the main board saves and loads the game state.
   - On the sides you will see two boxes with "P1" and "P2", here you can choose the players that will take part by clicking and iterating through them, they can be human players or bots. Player 1 plays white, player 2 plays black. If a box has selected the Monte Carlo bot or the Minimax bot, below three difficulty levels will appear, the coloured one is the selected one, you can click them to change.
   - On the bottom of the screen you will find a "LOAD GAME" button which you can press to load the contents of the game_state.txt file in the directory this application was launched from. This is useful to load board configurations and game states.

### Gameplay Instructions

> The goal of the game is to form lines of 5 markers of your color (either white or black). Once a line is formed, you can remove one of your rings. The first player to remove 3 rings wins.

- Game Phases:
    - **Phase 1: Placing Rings**: The players take turns placing their rings on the board. Just click on a valid position to palce the ring.
    - **Phase 2: Moving Rings**: After all rings are placed, players will take turns moving their rings. Moves must follow YINSH rules:
        - Rings must move in a straight line;
        - Rings can jump over markers but must land in the first empty space they find;
        - Markers jumped over will flip to the opposite color.
    - **Phase 3: Player Turns**: Player 1 (White) and Player 2 (Black) alternate turns moving rings to empty spaces and placing markers.
    - **Phase 4: Winning the Game**: To win the game, it is needed to form a line of 5 markers of the player's color to remove a ring. As mentioned before, the first player to remove 3 rings wins.
 
- UI:
   - When playing the game you will be shown the board in the center, the scoreboard above, contextual messages to help understanding what is happening on the top, and board evaluation / move hints on the right.
   - In phase 1, to place a ring, simply click one of the empty vertices of the board.
   - In phase 2, to play a move, click the desired ring (it should light green) and the destination you want it to go to. If the move is valid the game continues, if it is not then the ring is de-selected.
   - When a move is made and a sequence is formed a few things may happen. If the sequence is of a human player, a few numbers will appear on the left of the screen, these are all the valid sequences you may remove from the board. To select one of them click the number and the corresponding markers will light red, if you click it again then you remove that sequence and you will be prompted to remove a ring afterwards. If a random bot is the one that made the sequence the game will wait for a click of the user before continuing. In any other case the game will simply continue upon the deletion of a sequence.
   - When the game ends, it will wait for a click on the screen to load back into the menu.
   - To exit the game at any stage you can press the top right X button of the game window.

