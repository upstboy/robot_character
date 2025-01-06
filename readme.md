# Sir Blink-a-lot: An Interactive Ohbot Robot Character

Sir Blink-a-lot is an expressive robotic character built using the Ohbot platform and enhanced with AI capabilities. This robot can engage in natural conversations, display emotions through movement, and interact with humans in an engaging way.

## Features

### Interactive Capabilities
- Engages in natural conversations
- Plays trivia games
- Tells jokes
- Reads stories
- Sings songs
- Answers questions
- Describes what it sees
- Plays 'Simon Says'

### Expressive Movements
- Realistic talking animations with synchronized lip movements
- Natural head and eye movements
- Emotional gestures including:
  - Agreement (nodding)
  - Disagreement (head shaking)
  - Thinking (head tilt and upward gaze)
  - Excitement (animated head and eye movements)
- Random blinking and natural idle movements

### Display Features
- Fullscreen text display
- Adaptive font sizing for optimal readability
- High-contrast white text on black background
- Toggle fullscreen mode with F11/ESC keys

## Technical Details

### Movement Control
- Uses PID (Proportional-Integral-Derivative) controllers for smooth motor movements
- Controls 7 different motor functions:
  - Head nod
  - Head turn
  - Eye turn
  - Eye tilt
  - Top lip
  - Bottom lip
  - Lid blink

### Natural Behavior System
- Implements three types of random movements:
  1. Subtle movements (70% probability)
  2. Looking around (20% probability)
  3. Focused attention (10% probability)
- Random blinking with 30% probability during idle moments
- Smooth transitions between movements

## Usage

To run Sir Blink-a-lot:
```bash
python robot.py --config sirblinkalot.yaml [--debug]
```

### Arguments
- `--config`: Path to the configuration YAML file (required)
- `--debug`: Enable debug mode for additional console output (optional)

## Dependencies
- ohbot
- simple_pid
- tkinter
- threading
- queue
- argparse

## Safety
The program can be safely terminated using Ctrl+C, which will properly clean up resources and stop all motor movements.

## Note
This robot requires an [Ohbot hardware setup](https://www.ohbot.co.uk/store/p57/Ohbot_2.2_Kit.html) to function. The software handles the robot's movements, expressions, and interactions while maintaining natural-looking behaviors and smooth transitions between states.
