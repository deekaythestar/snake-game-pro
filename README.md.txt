# Snake Game Pro 🐍

A feature-rich Snake game built with Pygame. Includes multiplayer, themes, difficulty scaling, and full player customization.

![Gameplay GIF](assets/gameplay.gif)

### Features
- **Single & Multi Player** - Local leaderboard with JSON save system
- **5 Eye-Strain Safe Themes** - Midnight Blue, Soft Charcoal, Forest Night, Warm Dusk, Ocean Deep
- **Dodge Timer Mechanic** - Purple food gives 3 moves to dodge instead of instant penalty
- **Full Customization** - Change resolution, block size, and speed mid-game with keybinds
- **3 Difficulty Presets** - F1 Chill, F2 Normal, F3 Insane
- **Combo System** - Dodge 3 purples in a row for guaranteed gold food

### Controls
| Key | Action |
| --- | --- |
| Arrows | Move |
| SPACE | Pause |
| W | Toggle Wrap/Solid Walls |
| S | Toggle Sound On/Off |
| +/- | Change Resolution [Paused] |
| ]/[ | Block Size [Paused] |
| =/- | Speed Control |
| M | Toggle Auto/Manual Speed |
| T | Cycle Themes |
| H | Help Screen |
| ESC | Exit/Menu |

### Installation
```bash
git clone https://github.com/deekaythestar/snake-game-pro.git
cd snake-game-pro
pip install -r requirements.txt
python snake_pro.py