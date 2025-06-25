# Illusion of Thinking

A Gradio web application for exploring the experiments described in Apple's paper ["The Illusion of Thinking:
Understanding the Strengths and Limitations of Reasoning Models](https://ml-site.cdn-apple.com/papers/the-illusion-of-thinking.pdf) with locally hosted language models using Ollama. This project is designed to test and evaluate the reasoning capabilities of language models on well-defined problem-solving tasks.

## Overview

The paper evaluates on four different types of puzzles with varying difficulty levels:

### Available Puzzles

1. **Towers of Hanoi** - The classic disk-moving puzzle with three pegs
2. **Checker Jumping** - A one-dimensional board puzzle where checkers must swap positions
3. **River Crossing** - A constraint-satisfaction puzzle involving actors and agents crossing a river
4. **Blocks World** - A planning puzzle requiring rearrangement of stacked blocks

Each puzzle:

- Has configurable difficulty levels (n=1 to n=10)
- Provides structured system prompts to guide the language model
- Automatically evaluates the model's solution for correctness
- Supports real-time interaction through a web interface via Gradio

### Installing Ollama

1. Install Ollama from [https://ollama.ai](https://ollama.ai)
2. Pull at least one model (recommended models for reasoning tasks):
   ```bash
   ollama pull qwen3:8b
   ```
3. Verify Ollama is running:
   ```bash
   ollama list
   ```

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd illusion-of-thinking
   ```

2. **Install dependencies** (using uv - recommended):

   ```bash
   pip install uv
   uv sync
   ```

   Or using pip:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

1. **Ensure Ollama is running** with at least one model available
2. **Launch the Gradio interface**:

   using uv

   ```bash
   uv run main.py
   ```

   or if using a virtual environment

   ```bash
   python main.py
   ```

3. **Open your browser** to the displayed URL (typically `http://127.0.0.1:7860`)

### Using the Interface

#### Left Panel (Chat Interface)

- **Chatbot Window**: Displays the conversation between system prompts and model responses
- **Model Dropdown**: Select which Ollama model to use for solving puzzles
- **Options**: Advanced JSON configuration for model parameters (temperature, top_p, etc.)
- **Clear Button**: Reset the conversation history

#### Right Panel (Puzzle Configuration)

- **Puzzle Dropdown**: Choose from Towers of Hanoi, Checker Jumping, River Crossing, or Blocks World
- **Difficulty Slider**: Set complexity level (n=1 for easiest, n=10 for hardest)
- **Solve Button**: Start the puzzle-solving process
- **System Tab**: View/edit the system prompt that guides the model
- **User Tab**: View/edit the specific puzzle instance description

### Example Workflow

1. Select a model (e.g., "qwen3:8b")
2. Choose "Towers of Hanoi" puzzle
3. Set difficulty to 3
4. Click "Solve"
5. Watch as the model attempts to solve the puzzle
6. View the automatic evaluation of the solution

### Adding New Puzzles

To add a new puzzle:

1. Create a new class inheriting from `Puzzle` in `puzzles.py`
2. Implement required methods: `parse_solution()`, `play()`, `move()`, `user_prompt()`
3. Define `NAME`, `SYSTEM_PROMPT`, and other class attributes
4. Add the puzzle to the `puzzles` dictionary in `main.py`
