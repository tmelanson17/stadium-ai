# Stadium AI

An AI system for Pokemon Stadium that can read game state from screen capture and make optimal move decisions using damage calculations and type effectiveness analysis.

## Features

- **Computer Vision**: Reads game state from Pokemon Stadium screenshots/video
- **State Management**: Tracks Pokemon stats, HP, status conditions, and battle state
- **Damage Calculation**: Uses Smogon damage calculator for accurate move damage prediction
- **AI Decision Making**: Chooses optimal moves based on game state analysis
- **Move Database**: Comprehensive move and Pokemon data configuration

## Install

### Prerequisites

- Python 3.x
- Node.js and npm
- OpenCV for Python
- PyTorch (for neural network models)

### Python Dependencies

```bash
pip install opencv-python torch torchvision numpy pyyaml
```

### Node.js Dependencies

```bash
npm install
```

This will install:
- @smogon/calc: For damage calculations
- js-yaml: For YAML configuration parsing
- pokemon-showdown: For Pokemon data
- commander: For CLI interface

### Additional Setup

1. Install Tesseract OCR for text recognition:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # macOS
   brew install tesseract
   ```

2. Ensure you have the required model files:
   - `cv/hp_cnn.pt` - CNN model for HP reading
   - `cv/mnist_cnn.pt` - CNN model for number recognition

## Run

### Basic Usage

1. **Damage Calculator**:
   ```bash
   npm test
   # or
   node query_calc.js
   ```

2. **Move Query**:
   ```bash
   node query_movedex.js
   ```

3. **Game State Reader**:
   ```bash
   python game_state_machine.py
   ```

### Example Usage

**TODO**

### Configuration

- Pokemon data: `config/pokemon.yaml`
- Move data: `config/moves/`
- Type effectiveness: `analysis/type_chart.csv`

## Known Bugs

- **Partial Trapping Moves**: Partial trapping moves (like Bind, Fire Spin, etc.) are automatically assumed to be successful by the state_reader, which is not always the case. In actual gameplay, these moves can miss or fail to trap the opponent, but the current implementation assumes they always succeed when detected.
- **Adjust ContinuousTask speed**: Right now, it operates a little slowly.

## Project Structure

**TODO** : This will be restructured into the RL, StadiumParser, and DeepLearning repositories, and configs will be changed 

```
├── ai/                 # AI decision making logic
├── analysis/           # Damage calculation and type effectiveness (DEPRECATED)
├── config/             # Pokemon and move configurations 
├── cv/                 # Computer vision and OCR components (DEPRECATED)
├── parse/              # Game state parsing (DEPRECATED)
├── src/                # Core source code
├── state/              # Game state management
├── test/               # Test files
└── third-party/        # External dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

ISC License - see the package.json for details.
