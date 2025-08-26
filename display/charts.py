import plotext as plt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from typing import Dict

console = Console()

class Charts:
    """Terminal-based charts and visualizations."""
    
    @staticmethod
    def create_dimension_chart(dimension_scores: Dict):
        """
        Create visual bar chart for dimensions.
        
        Args:
            dimension_scores: Dictionary of dimension scores
        """
        # Clear any previous plot data
        plt.clear_data()
        plt.clear_color()
        
        # Prepare data
        dimensions = []
        scores = []
        colors = []
        
        color_map = {
            'E_I': 'cyan',
            'S_N': 'magenta',
            'T_F': 'yellow',
            'J_P': 'green'
        }
        
        for dim_key in ['E_I', 'S_N', 'T_F', 'J_P']:
            score = dimension_scores[dim_key]
            
            # Show the preferred side
            if score['preference'] in ['E', 'N', 'T', 'J']:
                dimensions.append(score['right_label'][:3])  # Abbreviate for space
                scores.append(score['right_score'])
            else:
                dimensions.append(score['left_label'][:3])
                scores.append(score['left_score'])
            
            colors.append(color_map.get(dim_key, 'white'))
        
        # Create bar chart
        plt.bar(dimensions, scores)
        plt.title("Your Personality Dimensions")
        plt.xlabel("Dimension")
        plt.ylabel("Strength (%)")
        plt.ylim(0, 100)
        
        # Set theme and size
        plt.theme('dark')
        plt.plotsize(60, 15)
        
        # Show the plot
        plt.show()
        
        # Alternative: Create ASCII bar chart
        console.print("\n[primary]Dimension Strengths:[/primary]\n")
        
        for dim_key in ['E_I', 'S_N', 'T_F', 'J_P']:
            score = dimension_scores[dim_key]
            
            # Determine which side won
            if score['preference'] in ['E', 'N', 'T', 'J']:
                label = score['right_label']
                strength = score['right_score']
            else:
                label = score['left_label']
                strength = score['left_score']
            
            # Create bar
            bar_length = int(strength / 2)  # Max 50 chars
            bar = "█" * bar_length + "░" * (50 - bar_length)
            
            # Color based on strength
            if strength > 70:
                style = "success"
            elif strength > 55:
                style = "warning"
            else:
                style = "muted"
            
            console.print(f"{label:15} [{style}][{bar}][/{style}] {strength:.1f}%")
    
    @staticmethod
    def create_comparison_chart(dimension_scores: Dict):
        """
        Create comparison chart showing both sides of each dimension.
        
        Args:
            dimension_scores: Dictionary of dimension scores
        """
        table = Table(title="Dimension Comparison", title_style="primary")
        table.add_column("", style="cyan", width=15)
        table.add_column("←", style="dim", width=25)
        table.add_column("VS", style="white", width=4, justify="center")
        table.add_column("→", style="dim", width=25)
        table.add_column("", style="cyan", width=15)
        
        for dim_key in ['E_I', 'S_N', 'T_F', 'J_P']:
            score = dimension_scores[dim_key]
            
            left_score = score['left_score']
            right_score = score['right_score']
            
            # Create visual bars
            left_bar_length = int(left_score / 4)  # Max 25 chars
            right_bar_length = int(right_score / 4)
            
            left_bar = "█" * left_bar_length
            right_bar = "█" * right_bar_length
            
            # Determine styling
            if left_score > right_score:
                left_style = "[success]"
                right_style = "[dim]"
            else:
                left_style = "[dim]"
                right_style = "[success]"
            
            table.add_row(
                f"{left_style}{score['left_label']}[/]",
                f"{left_style}{left_bar:>25}[/]",
                "VS",
                f"{right_style}{right_bar:<25}[/]",
                f"{right_style}{score['right_label']}[/]"
            )
        
        console.print(table)
    
    @staticmethod
    def create_confidence_meter(confidence: float):
        """
        Create a confidence meter visualization.
        
        Args:
            confidence: Overall confidence percentage
        """
        # Determine confidence level and color
        if confidence > 70:
            level = "Strong"
            color = "success"
        elif confidence > 60:
            level = "Moderate"
            color = "warning"
        else:
            level = "Low"
            color = "error"
        
        # Create meter
        meter_length = 30
        filled = int((confidence / 100) * meter_length)
        meter = "█" * filled + "░" * (meter_length - filled)
        
        panel = Panel(
            f"""
[bold]Overall Confidence: {confidence:.1f}%[/bold]

[{color}][{meter}][/{color}]

Confidence Level: [{color}]{level}[/{color}]
            """.strip(),
            title="[primary]Result Confidence[/primary]",
            border_style=color
        )
        
        console.print(panel)
    
    @staticmethod
    def create_cognitive_stack_display(cognitive_stack: Dict):
        """
        Display cognitive function stack.
        
        Args:
            cognitive_stack: Dictionary of cognitive functions
        """
        table = Table(title="Your Cognitive Function Stack", title_style="primary")
        table.add_column("Position", style="cyan", width=12)
        table.add_column("Function", style="yellow", width=35)
        table.add_column("Strength", style="green", width=15)
        
        positions = ["Dominant", "Auxiliary", "Tertiary", "Inferior"]
        strengths = ["████████", "██████", "████", "██"]
        
        for pos, strength in zip(positions, strengths):
            if pos.lower() in cognitive_stack:
                function = cognitive_stack[pos.lower()]
            else:
                function = "Unknown"
            
            table.add_row(pos, function, strength)
        
        console.print(table)