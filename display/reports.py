import pyfiglet
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich import box
from typing import Dict
from display.charts import Charts

console = Console()

class Reports:
    """Generate and display test results reports."""
    
    @staticmethod
    def display_full_results(results: Dict):
        """
        Display comprehensive results dashboard.
        
        Args:
            results: Complete results dictionary
        """
        console.clear()
        
        # Get data
        mbti_type = results['mbti_type']
        dimension_scores = results['dimension_scores']
        personality_analysis = results.get('personality_analysis', {})
        
        # 1. Type reveal with ASCII art
        Reports._display_type_reveal(mbti_type, personality_analysis.get('title', ''))
        
        # 2. Confidence meter
        Charts.create_confidence_meter(results['confidence'])
        console.print()
        
        # 3. Dimension visualization
        console.rule("[primary]Personality Dimensions[/primary]")
        Charts.create_dimension_chart(dimension_scores)
        console.print()
        
        # 4. Dimension comparison
        Charts.create_comparison_chart(dimension_scores)
        console.print()
        
        # 5. Personality overview
        if personality_analysis:
            Reports._display_personality_overview(personality_analysis)
        
        # 6. Strengths and weaknesses
        if 'strengths' in personality_analysis and 'weaknesses' in personality_analysis:
            Reports._display_strengths_weaknesses(personality_analysis)
        
        # 7. Cognitive functions
        if 'cognitive_stack' in personality_analysis:
            console.rule("[primary]Cognitive Functions[/primary]")
            Charts.create_cognitive_stack_display(personality_analysis['cognitive_stack'])
            console.print()
        
        # 8. Career matches
        if 'career_matches' in personality_analysis:
            Reports._display_career_matches(personality_analysis['career_matches'])
        
        # 9. Famous examples
        if 'famous_examples' in personality_analysis:
            Reports._display_famous_examples(personality_analysis['famous_examples'])
        
        # 10. Test metadata
        if 'test_metadata' in results:
            Reports._display_test_metadata(results['test_metadata'])
    
    @staticmethod
    def _display_type_reveal(mbti_type: str, title: str):
        """Display dramatic type reveal."""
        console.rule()
        
        # ASCII art for the type
        type_ascii = pyfiglet.figlet_format(mbti_type, font="standard")
        console.print(f"[primary]{type_ascii}[/primary]", justify="center")
        
        if title:
            console.print(f"[bold]{title}[/bold]", justify="center")
        
        console.rule()
        console.print()
    
    @staticmethod
    def _display_personality_overview(personality_analysis: Dict):
        """Display personality overview panel."""
        overview_panel = Panel(
            personality_analysis.get('overview', 'No overview available'),
            title="[primary]Personality Overview[/primary]",
            border_style="cyan",
            padding=(1, 2),
            box=box.ROUNDED
        )
        console.print(overview_panel)
        console.print()
    
    @staticmethod
    def _display_strengths_weaknesses(personality_analysis: Dict):
        """Display strengths and weaknesses side by side."""
        console.rule("[primary]Strengths & Growth Areas[/primary]")
        
        strengths_content = "\n".join([
            f"• {s}" for s in personality_analysis['strengths'][:5]
        ])
        
        weaknesses_content = "\n".join([
            f"• {w}" for w in personality_analysis['weaknesses'][:5]
        ])
        
        strengths_panel = Panel(
            strengths_content,
            title="[success]💪 Strengths[/success]",
            border_style="green",
            box=box.ROUNDED
        )
        
        weaknesses_panel = Panel(
            weaknesses_content,
            title="[warning]🌱 Growth Areas[/warning]",
            border_style="yellow",
            box=box.ROUNDED
        )
        
        console.print(Columns([strengths_panel, weaknesses_panel], equal=True))
        console.print()
    
    @staticmethod
    def _display_career_matches(career_matches: list):
        """Display career matches."""
        console.rule("[primary]Career Matches[/primary]")
        
        # Split into two columns for better display
        mid = len(career_matches) // 2
        col1 = career_matches[:mid]
        col2 = career_matches[mid:]
        
        table = Table(show_header=False, box=None)
        table.add_column("", style="cyan")
        table.add_column("", style="cyan")
        
        for c1, c2 in zip(col1, col2):
            table.add_row(f"• {c1}", f"• {c2}")
        
        # Handle odd number of items
        if len(col1) > len(col2):
            table.add_row(f"• {col1[-1]}", "")
        
        career_panel = Panel(
            table,
            title="[primary]💼 Recommended Careers[/primary]",
            border_style="cyan"
        )
        console.print(career_panel)
        console.print()
    
    @staticmethod
    def _display_famous_examples(famous_examples: list):
        """Display famous people with same type."""
        examples_text = ", ".join(famous_examples[:4])
        
        famous_panel = Panel(
            f"[cyan]{examples_text}[/cyan]",
            title="[primary]🌟 Famous {mbti_type}s[/primary]",
            border_style="cyan",
            box=box.MINIMAL
        )
        console.print(famous_panel)
        console.print()
    
    @staticmethod
    def _display_test_metadata(metadata: Dict):
        """Display test completion information."""
        info_text = f"""
Test Length: {metadata.get('test_length', 'Unknown').title()}
Questions Answered: {metadata.get('total_questions', 0)}
Time Taken: {metadata.get('completion_time', 'Unknown')}
        """
        
        info_panel = Panel(
            info_text.strip(),
            title="[dim]Test Information[/dim]",
            border_style="dim",
            box=box.MINIMAL
        )
        console.print(info_panel)
    
    @staticmethod
    def generate_summary_report(results: Dict) -> str:
        """
        Generate text summary of results.
        
        Args:
            results: Complete results dictionary
            
        Returns:
            Text summary
        """
        mbti_type = results['mbti_type']
        dimension_scores = results['dimension_scores']
        personality_analysis = results.get('personality_analysis', {})
        
        summary = []
        summary.append("=" * 60)
        summary.append("MBTI PERSONALITY TEST RESULTS")
        summary.append("=" * 60)
        summary.append("")
        summary.append(f"Your Personality Type: {mbti_type}")
        
        if 'title' in personality_analysis:
            summary.append(f"Type Title: {personality_analysis['title']}")
        
        summary.append(f"Overall Confidence: {results['confidence']:.1f}%")
        summary.append("")
        
        summary.append("DIMENSION SCORES:")
        summary.append("-" * 40)
        
        for dim_key in ['E_I', 'S_N', 'T_F', 'J_P']:
            score = dimension_scores[dim_key]
            summary.append(f"{score['preferred_label']:20} {score['strength']:.1f}%")
        
        summary.append("")
        
        if 'overview' in personality_analysis:
            summary.append("PERSONALITY OVERVIEW:")
            summary.append("-" * 40)
            summary.append(personality_analysis['overview'])
            summary.append("")
        
        if 'strengths' in personality_analysis:
            summary.append("STRENGTHS:")
            summary.append("-" * 40)
            for strength in personality_analysis['strengths']:
                summary.append(f"• {strength}")
            summary.append("")
        
        if 'career_matches' in personality_analysis:
            summary.append("RECOMMENDED CAREERS:")
            summary.append("-" * 40)
            for career in personality_analysis['career_matches'][:8]:
                summary.append(f"• {career}")
            summary.append("")
        
        summary.append("=" * 60)
        
        return "\n".join(summary)