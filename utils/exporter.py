import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from config.settings import SETTINGS
from display.reports import Reports

class Exporter:
    """Handle exporting test results in various formats."""
    
    @staticmethod
    def export_results(results: Dict, format: str = 'txt') -> Optional[str]:
        """
        Export test results to file.
        
        Args:
            results: Complete results dictionary
            format: Export format (txt/json)
            
        Returns:
            File path if successful, None otherwise
        """
        export_dir = SETTINGS['export_directory']
        export_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        mbti_type = results.get('mbti_type', 'unknown')
        
        try:
            if format == 'json':
                filepath = export_dir / f"mbti_results_{mbti_type}_{timestamp}.json"
                Exporter._export_json(results, filepath)
            else:  # txt
                filepath = export_dir / f"mbti_results_{mbti_type}_{timestamp}.txt"
                Exporter._export_text(results, filepath)
            
            return str(filepath)
            
        except Exception as e:
            print(f"Export failed: {e}")
            return None
    
    @staticmethod
    def _export_json(results: Dict, filepath: Path):
        """Export results as JSON."""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    @staticmethod
    def _export_text(results: Dict, filepath: Path):
        """Export results as formatted text."""
        summary = Reports.generate_summary_report(results)
        
        with open(filepath, 'w') as f:
            f.write(summary)
            f.write("\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    @staticmethod
    def copy_to_clipboard(results: Dict) -> bool:
        """
        Copy results summary to clipboard.
        
        Args:
            results: Complete results dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import pyperclip
            summary = Reports.generate_summary_report(results)
            pyperclip.copy(summary)
            return True
        except ImportError:
            print("Clipboard functionality requires pyperclip")
            return False
        except Exception as e:
            print(f"Clipboard copy failed: {e}")
            return False