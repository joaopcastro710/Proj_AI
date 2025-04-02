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

### Gameplay Instructions

> The goal of the game is to form a line of 5 markers of your color (either white or black). Once a line is formed, you can remove one of your rings. The first player to remove 3 rings wins.

- Game Phases:
    - **Phase 1: Placing Rings**: The players take turns placing their rings on the board. Just click on a valid position to palce the ring.
    - **Phase 2: Moving Rings**: After all rings are placed, players will take turns moving their rings. Moves must follow YINSH rules:
        - Rings must move in a straight line;
        - Rings can jump over markers but must land in an empty space;
        - Markers jumped over will flip to the opposite color.
    - **Phase 3: Player Turns**: Player 1 (White) and Player 2 (Black) alternate turns. If the bot is enabled, it will play as Player 2.
    - **Phase 4: Winning the Game**: To win the game, it is needed to form a line of 5 markers of the player's color to remove a ring. As mentioned before, the first player to remove 3 rings wins.

