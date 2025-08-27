import pyfiglet
import questionary
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from time import sleep
from typing import Dict, List, Optional
from ui.themes import console, question_style, DIMENSION_COLORS

class UIComponents:
    """Reusable UI components for the MBTI test."""
    
    @staticmethod
    def display_welcome():
        """Display animated welcome screen."""
        console.clear()
        
        # ASCII art with animation
        ascii_title = pyfiglet.figlet_format("MBTI", font="slant")
        lines = ascii_title.split('\n')
        
        # Animated reveal
        for line in lines:
            if line.strip():  # Only print non-empty lines
                console.print(f"[primary]{line}[/primary]", justify="center")
                sleep(0.03)  # Fast, smooth animation
        
        # Subtitle
        console.print(
            "[bold white]Personality Type Assessment[/bold white]",
            justify="center"
        )
        console.print(
            "[muted]Discover your cognitive preferences[/muted]",
            justify="center"
        )
        
        # Welcome panel
        welcome_text = """
[bold white]Welcome to the MBTI Personality Assessment[/bold white]

This scientifically-designed test will help you:
• Understand your personality type
• Discover your cognitive functions
• Explore career matches
• Learn about your strengths and growth areas

[warning]Press Enter to begin your journey...[/warning]
        """
        
        panel = Panel(
            Align.center(welcome_text.strip()),
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
            title="[bold primary]About This Test[/bold primary]"
        )
        
        console.print("\n")
        console.print(panel)
        
        input()  # Wait for user
    
    @staticmethod
    def select_test_length() -> str:
        """
        Interactive test length selection.
        
        Returns:
            Selected test length key
        """
        console.clear()
        console.rule("[primary]Choose Your Test Length[/primary]")
        console.print("\n")
        
        # Create info panels for each option
        options_data = [
            {
                "title": "⚡ Quick Assessment",
                "key": "short",
                "questions": "16 questions",
                "time": "~5 minutes",
                "description": "Get a basic overview of your personality type",
                "accuracy": "★★☆☆☆"
            },
            {
                "title": "⚖️  Balanced Test",
                "key": "medium", 
                "questions": "44 questions",
                "time": "~12 minutes",
                "description": "Recommended for accurate results",
                "accuracy": "★★★★☆"
            },
            {
                "title": "🔬 Comprehensive Analysis",
                "key": "long",
                "questions": "88 questions",
                "time": "~25 minutes",
                "description": "Most detailed and accurate assessment",
                "accuracy": "★★★★★"
            }
        ]
        
        # Display option panels
        for opt in options_data:
            content = f"""
[bold]{opt['questions']}[/bold] • {opt['time']}
{opt['description']}
Accuracy: {opt['accuracy']}
            """
            
            panel = Panel(
                content.strip(),
                title=opt['title'],
                border_style="cyan" if opt['key'] == 'medium' else "dim",
                box=box.ROUNDED
            )
            console.print(panel)
            console.print()
        
        # Create choice list
        choices = [
            "⚡ Quick (16 questions)",
            "⚖️  Balanced (44 questions) - Recommended",
            "🔬 Comprehensive (88 questions)"
        ]
        
        choice = questionary.select(
            "Select your preferred test length:",
            choices=choices,
            style=question_style,
            pointer="▶",
            use_shortcuts=True,
            default=choices[1]  # Default to balanced
        ).ask()
        
        # Map choice to key
        if "Quick" in choice:
            return "short"
        elif "Balanced" in choice:
            return "medium"
        else:
            return "long"
    
    @staticmethod
    def display_question(question_data: Dict, current: int, total: int, progress_data: Dict = None):
        """
        Display question with progress and styling.
        
        Args:
            question_data: Question dictionary
            current: Current question number
            total: Total questions
            progress_data: Optional progress information
            
        Returns:
            User's response value (1-5)
        """
        console.clear()
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="progress", size=5),
            Layout(name="question", size=8),
            Layout(name="footer", size=2)
        )
        
        # Header
        header_text = f"[bold primary]MBTI Assessment[/bold primary] • Question {current} of {total}"
        layout["header"].update(Panel(header_text, box=box.MINIMAL))
        
        # Progress bar
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )
        
        task = progress.add_task(
            f"Overall Progress",
            total=total,
            completed=current-1
        )
        
        # Add dimension indicator
        dimension = question_data['dimension']
        dim_color = DIMENSION_COLORS.get(dimension, 'white')
        dim_name = {
            'E_I': 'Extraversion/Introversion',
            'S_N': 'Sensing/Intuition',
            'T_F': 'Thinking/Feeling',
            'J_P': 'Judging/Perceiving'
        }.get(dimension, dimension)
        
        progress_panel = Panel(
            progress,
            title=f"[{dim_color}]Measuring: {dim_name}[/{dim_color}]",
            border_style=dim_color,
            box=box.ROUNDED
        )
        layout["progress"].update(progress_panel)
        
        # Question panel
        question_type = question_data.get('type', 'general').replace('_', ' ').title()
        
        question_panel = Panel(
            f"\n[bold white]{question_data['text']}[/bold white]\n",
            title=f"[dim]Question Type: {question_type}[/dim]",
            border_style=dim_color,
            padding=(2, 4),
            box=box.DOUBLE
        )
        layout["question"].update(question_panel)
        
        # Footer
        footer_text = "[dim]Use arrow keys or number keys to select • Press 'q' to save and quit[/dim]"
        layout["footer"].update(Panel(footer_text, box=box.MINIMAL))
        
        # Display layout
        console.print(layout)
        console.print()
        
        # Get response with custom options
        choices = [
            "1️⃣  Strongly Disagree",
            "2️⃣  Disagree", 
            "3️⃣  Neutral",
            "4️⃣  Agree",
            "5️⃣  Strongly Agree"
        ]
        
        # Show options based on question wording
        if question_data.get('options'):
            # Use custom options if provided
            choices = [
                f"{i+1}️⃣  {opt['text']}" 
                for i, opt in enumerate(question_data['options'])
            ]
        
        answer = questionary.select(
            "",
            choices=choices,
            style=question_style,
            pointer="▶",
            use_shortcuts=True,
            instruction="(Use arrow keys or press 1-5)"
        ).ask()
        
        if answer is None:  # User pressed Ctrl+C or quit
            return None
        
        # Extract value from answer
        # The value is the first character (the number emoji)
        return int(answer[0])
    
    @staticmethod
    def display_progress_summary(progress_data: Dict):
        """Display progress summary panel."""
        console.clear()
        console.rule("[primary]Test Progress[/primary]")
        
        # Overall progress
        overall = Panel(
            f"""
[bold]Questions Completed:[/bold] {progress_data['current']}/{progress_data['total']}
[bold]Percentage:[/bold] {progress_data['percentage']:.1f}%
[bold]Time Elapsed:[/bold] {progress_data['time_elapsed']}
[bold]Questions Remaining:[/bold] {progress_data['questions_remaining']}
            """.strip(),
            title="[primary]Overall Progress[/primary]",
            border_style="cyan"
        )
        console.print(overall)
        console.print()
        
        # Dimension progress
        if 'dimension_progress' in progress_data:
            table = Table(title="Progress by Dimension", title_style="primary")
            table.add_column("Dimension", style="cyan")
            table.add_column("Progress", style="green")
            table.add_column("Status", style="yellow")
            
            for dim_key, dim_data in progress_data['dimension_progress'].items():
                progress_bar = UIComponents._create_text_progress_bar(
                    dim_data['answered'], 
                    dim_data['total']
                )
                status = "✓ Complete" if dim_data['answered'] == dim_data['total'] else "In Progress"
                
                table.add_row(
                    dim_data['name'],
                    f"{dim_data['answered']}/{dim_data['total']} {progress_bar}",
                    status
                )
            
            console.print(table)
    
    @staticmethod
    def _create_text_progress_bar(current: int, total: int, width: int = 20) -> str:
        """Create a text-based progress bar."""
        if total == 0:
            return "░" * width
        
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    @staticmethod
    def display_resume_option(sessions: List[Dict]) -> Optional[str]:
        """
        Display resume session option.
        
        Args:
            sessions: List of resumable sessions
            
        Returns:
            Selected session ID or None for new test
        """
        console.clear()
        console.rule("[primary]Resume Previous Test?[/primary]")
        
        # Create table of sessions
        table = Table(title="Available Sessions", title_style="primary")
        table.add_column("Test Type", style="cyan")
        table.add_column("Progress", style="green")
        table.add_column("Last Updated", style="yellow")
        
        for session in sessions[:5]:  # Show max 5 recent sessions
            table.add_row(
                session['test_length'].title(),
                session['progress'],
                session['last_updated']
            )
        
        console.print(table)
        console.print()
        
        # Create choices
        choices = ["🆕 Start New Test"]
        session_map = {}
        
        for i, session in enumerate(sessions[:5]):
            choice_text = f"📂 Resume {session['test_length'].title()} test ({session['progress']})"
            choices.append(choice_text)
            session_map[choice_text] = session['id']
        
        choice = questionary.select(
            "What would you like to do?",
            choices=choices,
            style=question_style,
            pointer="▶"
        ).ask()
        
        if "Start New" in choice:
            return None
        
        return session_map.get(choice)
    
    @staticmethod
    def display_error(message: str):
        """Display error message."""
        error_panel = Panel(
            f"[error]❌ {message}[/error]",
            border_style="red",
            box=box.ROUNDED
        )
        console.print(error_panel)
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
    
    @staticmethod
    def display_success(message: str):
        """Display success message."""
        success_panel = Panel(
            f"[success]✓ {message}[/success]",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(success_panel)
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """
        Display confirmation prompt.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if confirmed, False otherwise
        """
        return questionary.confirm(
            message,
            style=question_style,
            default=False
        ).ask()
    
    @staticmethod
    def display_loading(message: str = "Processing..."):
        """Display loading animation."""
        with console.status(f"[primary]{message}[/primary]", spinner="dots"):
            sleep(1)  # Simulated loading