Procedural Jump & Run Game
This is a procedural jump-and-run game developed using Python and Pygame for a Hackclub project. It features dynamically generated levels, multiple enemy types, and player abilities like wall-running and wall-jumping. The "art" and music are also procedurally generated, offering a unique experience with every new game!

Demo
You can download the latest Windows executable (.exe) to play the game:
Download the Game Executable Here
(Note: You will need to click on "Releases" on the right side of the GitHub page to find the .exe file if the direct link does not work or if there are multiple releases.)

To run the .exe file, simply download it and double-click. If Windows SmartScreen or your antivirus warns you, you might need to click "More info" or "Run anyway" as it's an unsigned executable from an unknown developer.

Features
Procedural Level Generation: Every game (and every time you press 'R') generates a completely new, random world of platforms and walls using Perlin Noise.

Dynamic Difficulty: The game gets progressively harder as your score increases, with enemies becoming faster and more frequent, and platforming challenges subtly evolving.

Player Abilities:

Run & Jump: Standard platformer movement.

Wall Run: Slows your descent when moving against a vertical surface in the air.

Wall Jump: Leap off walls to gain height or cross difficult gaps.

Diverse Enemies: Encounter three types of enemies with distinct behaviors:

Standard: Basic, stationary obstacles.

Flying: Moves horizontally in the air.

Rolling: Patrols platforms.

Jumping: Periodically leaps from platforms.

Mouse Aim & Shoot: Control your laser attack precisely with the mouse.

Procedural Music: A unique, randomized chiptune-like melody accompanies each new map.

In-Game "Art" Customization: Press the C key during gameplay to cycle through different color themes, changing the visual style of the player, enemies, and environment.

Persistent Progress: Your score and health carry over when you regenerate the world in place (R key).

Interactive Menus: Buttons provide visual and auditory feedback on hover and click.

In-Game Tutorial & Details: Access "HOW TO PLAY" and "GAME DETAILS" from the main menu for controls and generation information.

Controls
Move Left: Left Arrow / A

Move Right: Right Arrow / D

Jump: Up Arrow / W / SPACEBAR

Shoot Laser: LEFT MOUSE CLICK (aim with mouse cursor)

New Random Map: R (during gameplay or game over screen)

Change Colors: C (during gameplay)

Back / Quit: ESC (from any screen)

Project Structure
The game is built as a single Python script (generate_noise_image.py) leveraging the pygame, perlin-noise, and numpy libraries.

generate_noise_image.py: Contains all the game logic, rendering, procedural generation algorithms, and state management.

How to Run (From Source)
If you have Python and Pygame installed, you can run the game from the source code:

Clone the repository:

git clone https://github.com/FaresAl-jaar/landscape-image-generator.git
cd landscape-image-generator

Install dependencies:

pip install pygame perlin-noise numpy

(Note: Ensure you are using the correct Python environment if you have multiple installations.)

Run the game:

python generate_noise_image.py

Contributing / Ideas
Feel free to explore the code, suggest improvements, or even fork the repository to build your own variations!
