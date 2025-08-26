from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from time import sleep
from typing import Callable, Any
import random

console = Console()

class Animations:
    """Animation effects for enhanced user experience."""
    
    @staticmethod
    def typewriter_effect(text: str, delay: float = 0.03):
        """
        Display text with typewriter effect.
        
        Args:
            text: Text to display
            delay: Delay between characters
        """
        for char in text:
            console.print(char, end="")
            sleep(delay)
        console.print()
    
    @staticmethod
    def fade_in_text(lines: list, delay: float = 0.1):
        """
        Fade in text line by line.
        
        Args:
            lines: List of text lines
            delay: Delay between lines
        """
        for line in lines:
            console.print(line, style="dim")
            sleep(delay)
    
    @staticmethod
    def loading_spinner(message: str, duration: float = 2.0):
        """
        Show loading spinner with message.
        
        Args:
            message: Loading message
            duration: Duration in seconds
        """
        with console.status(f"[primary]{message}[/primary]", spinner="dots"):
            sleep(duration)
    
    @staticmethod
    def progress_animation(task_name: str, steps: int = 100, delay: float = 0.01):
        """
        Show animated progress bar.
        
        Args:
            task_name: Name of the task
            steps: Number of steps
            delay: Delay between steps
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(task_name, total=steps)
            
            for _ in range(steps):
                progress.update(task, advance=1)
                sleep(delay)
    
    @staticmethod
    def transition_effect():
        """Display a transition effect between screens."""
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        for _ in range(10):
            char = random.choice(chars)
            console.print(f"\r[primary]{char}[/primary]", end="")
            sleep(0.05)
        console.print("\r ", end="")
    
    @staticmethod
    def countdown(seconds: int = 3):
        """
        Display countdown.
        
        Args:
            seconds: Number of seconds to count down
        """
        for i in range(seconds, 0, -1):
            console.print(f"\r[bold primary]{i}...[/bold primary]", end="")
            sleep(1)
        console.print("\r[bold success]Go![/bold success]    ")
        sleep(0.5)
    
    @staticmethod
    def reveal_result(result_text: str):
        """
        Dramatically reveal test result.
        
        Args:
            result_text: The result to reveal
        """
        console.print("\n[primary]Analyzing your responses...[/primary]")
        sleep(1)
        
        messages = [
            "Processing personality dimensions...",
            "Calculating cognitive functions...",
            "Determining your type..."
        ]
        
        for msg in messages:
            Animations.loading_spinner(msg, 0.8)
        
        console.print("\n[bold primary]Your personality type is...[/bold primary]")
        sleep(1)
        
        # Dramatic reveal
        for _ in range(3):
            console.print(".", end="")
            sleep(0.5)
        
        console.print(f"\n\n[bold success]{result_text}[/bold success]\n")
    
    @staticmethod
    def pulse_text(text: str, times: int = 3):
        """
        Make text pulse.
        
        Args:
            text: Text to pulse
            times: Number of pulses
        """
        for _ in range(times):
            console.print(f"\r[dim]{text}[/dim]", end="")
            sleep(0.3)
            console.print(f"\r[bold]{text}[/bold]", end="")
            sleep(0.3)
        console.print()
    
    @staticmethod
    def animated_task(func: Callable, message: str = "Processing...") -> Any:
        """
        Run a function with loading animation.
        
        Args:
            func: Function to run
            message: Loading message
            
        Returns:
            Function result
        """
        result = None
        
        with console.status(f"[primary]{message}[/primary]", spinner="dots"):
            result = func()
        
        return result