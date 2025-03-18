# 🚀 Coadmap

Coadmap is a powerful code roadmap generator that helps developers plan their projects with ease. Simply describe your application idea, and Coadmap will create a comprehensive development roadmap tailored to your project needs.

## ✨ Features

- Generate detailed technical roadmaps from simple text descriptions
- Interactive mode with customization questions
- Save generated roadmaps to markdown files
- Beautiful terminal interface with progress animations

## 📋 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/coadmap.git
cd coadmap
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp env.example .env
```
Then edit the .env file to add your Anthropic API key.

## 🔧 Usage

### Generate a roadmap and display it in the terminal:

```bash
python main.py generate "A web application for tracking daily habits and visualizing progress"
```

### Generate a roadmap interactively:

```bash
python main.py interactive "A mobile app for finding nearby hiking trails"
```

### Generate and save a roadmap to a file:

```bash
python main.py save "A CLI tool for organizing photo collections" --output-file my_photo_app.md
```

All saved roadmaps are stored in the `roadmaps` directory.

## 📝 License

MIT

## 🙏 Acknowledgements

- Built with [Anthropic's Claude](https://www.anthropic.com/claude) API
- Terminal interface powered by [Rich](https://github.com/Textualize/rich)
- CLI functionality by [Typer](https://typer.tiangolo.com/)