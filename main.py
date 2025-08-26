#!/usr/bin/env python3
"""
MBTI Personality Test - Terminal Application
A comprehensive Myers-Briggs Type Indicator assessment tool
"""

import sys
from pathlib import Path
from typing import Dict, Optional
import questionary

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.test_engine import TestEngine
from ui.components import UIComponents
from ui.animations import Animations
from ui.themes import console
from display.reports import Reports
from utils.exporter import Exporter
from utils.helpers import (
    ensure_terminal_size, 
    validate_data_files,
    display_disclaimer,
    get_version
)
from config.settings import SETTINGS

class MBTIApp:
    """Main application class for MBTI test."""
    
    def __init__(self):
        self.test_engine = TestEngine()
        self.ui = UIComponents()
        self.current_session_id = None
    
    def run(self):
        """Main application entry point."""
        try:
            # Check terminal size
            if not ensure_terminal_size(SETTINGS['min_terminal_width']):
                console.print(
                    f"[error]Terminal width must be at least {SETTINGS['min_terminal_width']} columns[/error]"
                )
                return
            
            # Validate data files
            if not validate_data_files():
                console.print("[error]Required data files not found. Please ensure all files are present.[/error]")
                return
            
            # Clean up old sessions
            self.test_engine.cleanup_old_sessions()
            
            # Show welcome screen
            self.ui.display_welcome()
            
            # Check for resumable sessions
            sessions = self.test_engine.get_available_sessions()
            
            if sessions:
                session_id = self.ui.display_resume_option(sessions)
                if session_id:
                    # Resume existing session
                    if self.test_engine.resume_test(session_id):
                        self.ui.display_success("Session resumed successfully!")
                        self.run_test(resuming=True)
                    else:
                        self.ui.display_error("Failed to resume session")
                        self.start_new_test()
                else:
                    self.start_new_test()
            else:
                self.start_new_test()
            
        except KeyboardInterrupt:
            self.handle_interrupt()
        except Exception as e:
            console.print(f"[error]An unexpected error occurred: {e}[/error]")
            sys.exit(1)
    
    def start_new_test(self):
        """Start a new test session."""
        # Select test length
        test_length = self.ui.select_test_length()
        
        if not test_length:
            return
        
        # Initialize test
        Animations.loading_spinner("Preparing your test...", 1)
        self.current_session_id = self.test_engine.initialize_test(test_length)
        
        # Run test
        self.run_test(resuming=False)
    
    def run_test(self, resuming: bool = False):
        """
        Run the main test loop.
        
        Args:
            resuming: Whether resuming a previous session
        """
        if resuming:
            console.print("\n[primary]Resuming your test...[/primary]\n")
        
        # Main test loop
        while not self.test_engine.is_complete():
            # Get current question
            question = self.test_engine.get_current_question()
            if not question:
                break
            
            # Get progress
            progress = self.test_engine.get_progress()
            
            # Display question
            response = self.ui.display_question(
                question,
                progress['current'] + 1,
                progress['total'],
                progress
            )
            
            if response is None:
                # User wants to quit
                if self.ui.confirm_action("Save progress and quit?"):
                    console.print("[success]Progress saved. You can resume later.[/success]")
                    return
                else:
                    continue
            
            # Submit response
            self.test_engine.submit_response(response)
        
        # Test complete
        self.show_results()
    
    def show_results(self):
        """Calculate and display test results."""
        console.clear()
        
        # Validate responses
        is_valid, message = self.test_engine.validate_responses()
        if not is_valid:
            self.ui.display_error(f"Response validation failed: {message}")
            if not self.ui.confirm_action("Continue anyway?"):
                return
        
        # Calculate results with animation
        Animations.loading_spinner("Analyzing your responses...", 2)
        results = self.test_engine.calculate_results()
        
        # Reveal type dramatically
        Animations.reveal_result(results['mbti_type'])
        
        # Display full results
        Reports.display_full_results(results)
        
        # Offer export options
        self.offer_export(results)
        
        # Show disclaimer
        console.print("\n[dim]Note: This is not a clinical assessment.[/dim]")
        
        # Ask if user wants to take another test
        console.print("\n")
        if self.ui.confirm_action("Would you like to take another test?"):
            self.run()
    
    def offer_export(self, results: Dict):
        """
        Offer export options for results.
        
        Args:
            results: Test results dictionary
        """
        console.print("\n")
        console.rule("[primary]Save Your Results[/primary]")
        
        choices = [
            "📄 Save as text file",
            "📊 Save as JSON",
            "📋 Copy to clipboard",
            "❌ Don't save"
        ]
        
        choice = questionary.select(
            "How would you like to save your results?",
            choices=choices
        ).ask()
        
        if "text" in choice:
            filepath = Exporter.export_results(results, 'txt')
            if filepath:
                self.ui.display_success(f"Results saved to: {filepath}")
        elif "JSON" in choice:
            filepath = Exporter.export_results(results, 'json')
            if filepath:
                self.ui.display_success(f"Results saved to: {filepath}")
        elif "clipboard" in choice:
            if Exporter.copy_to_clipboard(results):
                self.ui.display_success("Results copied to clipboard!")
            else:
                self.ui.display_error("Failed to copy to clipboard")
    
    def handle_interrupt(self):
        """Handle Ctrl+C gracefully."""
        console.print("\n[warning]Test interrupted[/warning]")
        
        if self.current_session_id:
            console.print("[success]Your progress has been automatically saved.[/success]")
        
        console.print("[dim]Goodbye![/dim]")
        sys.exit(0)


def main():
    """Main entry point."""
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MBTI Personality Test - Terminal Application"
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'MBTI Test v{get_version()}'
    )
    parser.add_argument(
        '--disclaimer',
        action='store_true',
        help='Show disclaimer'
    )
    
    args = parser.parse_args()
    
    if args.disclaimer:
        display_disclaimer()
        return
    
    # Run application
    app = MBTIApp()
    app.run()


if __name__ == "__main__":
    main()