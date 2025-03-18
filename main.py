# main.py
import typer
from roadmap_generator import generate_roadmap, generate_roadmap_with_questions
import asyncio
from rich.console import Console
from rich.markdown import Markdown
from config import APP_NAME, APP_VERSION
from loading_animation import LoadingAnimation, AnimationType
import threading
import os

app = typer.Typer()
console = Console()

def status_callback(message):
    """Callback function to receive status updates from the roadmap generator."""
    # Always print the status messages from the roadmap generator
    # Style messages differently based on content and avoid duplicates
    # Don't print "Starting reflection process" since animation will show this
    if message == "Starting reflection process with your input...":
        return  # Skip this message as it's shown in the animation
    elif "✅" in message:
        console.print(f"[bold green]{message}[/bold green]")
    elif "Starting" in message:
        console.print(f"[bold yellow]{message}[/bold yellow]")
    else:
        console.print(f"[yellow]{message}[/yellow]")

@app.command()
def generate(
    idea: str = typer.Argument(..., help="Your app idea description"),
    animation: str = typer.Option("spinner", help="Loading animation type (spinner, dots, bar, typing)"),
    interactive: bool = typer.Option(True, help="Use interactive mode with customization questions")
):
    """Generate a roadmap directly from the command line."""
    console.print(f"[bold cyan]{APP_NAME} v{APP_VERSION}[/bold cyan]")
    
    # Map animation string to enum
    animation_map = {
        'spinner': AnimationType.SPINNER,
        'dots': AnimationType.DOTS,
        'bar': AnimationType.BAR,
        'typing': AnimationType.TYPING
    }
    animation_type = animation_map.get(animation, AnimationType.SPINNER)
    
    try:
        if interactive:
            # For interactive mode, the loading animations are handled within the generate_roadmap_with_questions function
            console.print("[yellow]Starting interactive roadmap generation process...[/yellow]")
            roadmap = asyncio.run(generate_roadmap_with_questions(idea, animation_type, status_callback))
        else:
            # Start loading animation in a background thread
            roadmap_animation = LoadingAnimation("Generating roadmap based on your idea", animation_type)
            animation_thread = threading.Thread(target=roadmap_animation.start)
            animation_thread.daemon = True
            animation_thread.start()
            
            # Run the generation in an event loop
            roadmap = asyncio.run(generate_roadmap(idea, status_callback))
            
            # Stop the animation
            roadmap_animation.stop()
        
        console.print("\n[bold green]Roadmap generated:[/bold green]\n")
        console.print(Markdown(roadmap))
    except Exception as e:
        # Ensure animation is stopped in case of error
        if not interactive and 'roadmap_animation' in locals():
            roadmap_animation.stop()
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

@app.command()
def interactive(
    idea: str = typer.Argument(..., help="Your app idea description"),
    animation: str = typer.Option("spinner", help="Loading animation type (spinner, dots, bar, typing)")
):
    """Generate a roadmap with interactive customization questions."""
    console.print(f"[bold cyan]{APP_NAME} v{APP_VERSION}[/bold cyan]")
    
    # Map animation string to enum
    animation_map = {
        'spinner': AnimationType.SPINNER,
        'dots': AnimationType.DOTS,
        'bar': AnimationType.BAR,
        'typing': AnimationType.TYPING
    }
    animation_type = animation_map.get(animation, AnimationType.SPINNER)
    
    try:
        # Loading animations are handled within the generate_roadmap_with_questions function
        console.print("[yellow]Starting interactive roadmap generation process...[/yellow]")
        
        # Run the interactive generation in an event loop
        roadmap = asyncio.run(generate_roadmap_with_questions(idea, animation_type, status_callback))
        
        console.print("\n[bold green]Customized roadmap generated:[/bold green]\n")
        console.print(Markdown(roadmap))
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

@app.command()
def save(
    idea: str = typer.Argument(..., help="Your app idea description"),
    output_file: str = typer.Option("roadmap.md", help="Output file name"),
    animation: str = typer.Option("spinner", help="Loading animation type (spinner, dots, bar, typing)"),
    interactive: bool = typer.Option(True, help="Use interactive mode with customization questions")
):
    """Generate a roadmap and save it to a file."""
    console.print(f"[bold cyan]{APP_NAME} v{APP_VERSION}[/bold cyan]")
    
    # Map animation string to enum
    animation_map = {
        'spinner': AnimationType.SPINNER,
        'dots': AnimationType.DOTS,
        'bar': AnimationType.BAR,
        'typing': AnimationType.TYPING
    }
    animation_type = animation_map.get(animation, AnimationType.SPINNER)
    
    try:
        if interactive:
            # For interactive mode, the loading animations are handled within the generate_roadmap_with_questions function
            console.print("[yellow]Starting interactive roadmap generation process...[/yellow]")
            roadmap = asyncio.run(generate_roadmap_with_questions(idea, animation_type, status_callback))
        else:
            # Start loading animation in a background thread
            roadmap_animation = LoadingAnimation("Generating roadmap based on your idea", animation_type)
            animation_thread = threading.Thread(target=roadmap_animation.start)
            animation_thread.daemon = True
            animation_thread.start()
            
            # Run the generation in an event loop
            roadmap = asyncio.run(generate_roadmap(idea, status_callback))
            
            # Stop the animation
            roadmap_animation.stop()
        
        # Save to file in the roadmaps directory
        os.makedirs('roadmaps', exist_ok=True)  # Ensure the directory exists
        file_path = os.path.join('roadmaps', output_file)
        with open(file_path, "w") as f:
            f.write(roadmap)
        
        console.print(f"\n[bold green]Roadmap saved to {file_path}[/bold green]")
    except Exception as e:
        # Ensure animation is stopped in case of error
        if 'roadmap_animation' in locals():
            roadmap_animation.stop()
        console.print(f"[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    app()