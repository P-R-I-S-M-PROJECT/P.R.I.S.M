from colorama import init, Fore, Back, Style
from datetime import datetime
import sys
import re

# Initialize colorama for Windows support
init()

class ArtLogger:
    def __init__(self, debug_enabled: bool = False):
        self.section_level = 0
        self.debug_enabled = debug_enabled
        self.colors = {
            'title': Fore.MAGENTA + Style.BRIGHT,
            'success': Fore.GREEN + Style.BRIGHT,
            'error': Fore.RED + Style.BRIGHT,
            'info': Fore.CYAN,
            'warning': Fore.YELLOW,
            'highlight': Fore.WHITE + Style.BRIGHT,
            'reset': Style.RESET_ALL,
            'accent': Fore.BLUE + Style.BRIGHT,
            'analysis': Fore.MAGENTA,
            'metric': Fore.CYAN + Style.BRIGHT,
            'insight': Fore.GREEN,
            'evolution': Fore.YELLOW + Style.BRIGHT,
            'technique': Fore.BLUE + Style.BRIGHT,
            'dim': Style.DIM,
            'sync': Fore.BLUE
        }
        
    def separator(self):
        """Print a separator line"""
        print(f"\n{self.colors['title']}{'═' * 80}{self.colors['reset']}\n")
        
    def title(self, text: str):
        """Print a title with double borders"""
        if text == "PRISM GENERATION SYSTEM":
            self._print_welcome()
        else:
            border = "═" * 80
            print(f"\n{self.colors['title']}{border}")
            print(f"║ {text}")
            print(f"{border}{self.colors['reset']}")
            
    def _print_welcome(self):
        """Print fancy welcome message"""
        print(f"\n{self.colors['accent']}")
        print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██████╗ ██████╗ ██╗███████╗███╗   ███╗                                 ║
║   ██╔══██╗██╔══██╗██║██╔════╝████╗ ████║                                 ║
║   ██████╔╝██████╔╝██║███████╗██╔████╔██║                                 ║
║   ██╔═══╝ ██╔══██╗██║╚════██║██║╚██╔╝██║                                 ║
║   ██║     ██║  ██║██║███████║██║ ╚═╝ ██║                                 ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚═╝                                 ║
║                                                                           ║
║   Pattern Recognition & Interactive Sketch Machine                        ║
║   [ Generative Art System v1.0 ]                                         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
        """)
        print(f"{self.colors['reset']}")
        
    def start_section(self, text: str):
        """Start a new section with title"""
        self.section_level += 1
        print(f"\n{self._get_timestamp()}{self.colors['highlight']}┌─ {text} {'─' * (76 - len(text))}{self.colors['reset']}")
        
    def end_section(self):
        """End the current section"""
        if self.section_level > 0:
            print(f"{self._get_timestamp()}{self.colors['highlight']}└─ Complete {'─' * 69}{self.colors['reset']}")
            self.section_level -= 1
            
    def info(self, text: str):
        """Print info message"""
        indent = "    " * self.section_level
        print(f"{self._get_timestamp()} {indent}{self.colors['info']}ℹ {text}{self.colors['reset']}")
        
    def success(self, text: str):
        """Print success message"""
        indent = "    " * self.section_level
        print(f"{self._get_timestamp()} {indent}{self.colors['success']}✓ {text}{self.colors['reset']}")
        
    def warning(self, text: str):
        """Print warning message"""
        indent = "    " * self.section_level
        print(f"{self._get_timestamp()} {indent}{self.colors['warning']}⚠ {text}{self.colors['reset']}")
        
    def error(self, text: str):
        """Print error message"""
        indent = "    " * self.section_level
        print(f"{self._get_timestamp()} {indent}{self.colors['error']}✖ {text}{self.colors['reset']}")
        
    def pattern_score(self, score: float, metrics: dict = None):
        """Enhanced pattern score display with optional metrics"""
        bars = int(score / 5)
        bar_str = "█" * bars + "░" * (20 - bars)
        
        # Color gradient based on score
        score_color = (
            self.colors['error'] if score < 30 else
            self.colors['warning'] if score < 60 else
            self.colors['success']
        )
        
        print(f"\n{score_color}┌{'─' * 40}┐")
        print(f"│ Pattern Score [{bar_str}] {score:>5.1f}/100 │")
        if metrics:
            print(f"├{'─' * 40}┤")
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"│ {key:<20}: {value:>15.2f} │")
                else:
                    print(f"│ {key:<15}: {str(value):>20} │")
        print(f"└{'─' * 40}┘{self.colors['reset']}")
        
    def _get_timestamp(self) -> str:
        """Get timestamp with colors"""
        return f"{self.colors['accent']}[{self._get_time()}]{self.colors['reset']}"
        
    def _get_time(self) -> str:
        """Get current time formatted as HH:MM:SS"""
        return datetime.now().strftime("%H:%M:%S")
        
    def debug(self, text: str, data: str = None, exc_info: bool = False):
        """Enhanced debug message with better formatting"""
        if not self.debug_enabled:
            return
            
        indent = "    " * self.section_level
        timestamp = self._get_timestamp()
        
        # Print the main debug message with a more subtle style
        print(f"{timestamp} {indent}{self.colors['accent']}┌─ DEBUG: {text}{self.colors['reset']}")
        
        # If there's detailed data, print it in an indented block
        if data:
            data_lines = data.strip().split('\n')
            for line in data_lines:
                print(f"{timestamp} {indent}{self.colors['accent']}│  {line.strip()}{self.colors['reset']}")
        
        # Print stack trace if requested
        if exc_info:
            import traceback
            trace_lines = traceback.format_exc().split('\n')
            for line in trace_lines:
                print(f"{timestamp} {indent}{self.colors['accent']}│  {line}{self.colors['reset']}")
        
        if data or exc_info:
            print(f"{timestamp} {indent}{self.colors['accent']}└─{self.colors['reset']}")
        
    def video_sync_complete(self, output: str):
        """Print concise video sync status"""
        indent = "    " * self.section_level
        
        # Only extract and show essential information
        if "CDN response (200)" in output and "verification successful" in output:
            # Extract version number from the output
            version_match = re.search(r'animation_v(\d+)-\d+\.mp4', output)
            version = version_match.group(1) if version_match else ""
            print(f"{self._get_timestamp()} {indent}{self.colors['sync']}◈ Synced v{version}{self.colors['reset']} {self.colors['success']}✓{self.colors['reset']}")
        else:
            print(f"{self._get_timestamp()} {indent}{self.colors['sync']}◈ Sync Failed{self.colors['reset']} {self.colors['error']}✖{self.colors['reset']}")
        
    def set_debug(self, enabled: bool):
        """Toggle debug logging"""
        self.debug_enabled = enabled

    def analysis_header(self, text: str):
        """Print a stylized analysis header"""
        print(f"\n{self.colors['analysis']}╔{'═' * 78}╗")
        print(f"║ {text:<77}║")
        print(f"╚{'═' * 78}╝{self.colors['reset']}")

    def metric_block(self, metrics: dict):
        """Display a block of metrics in a stylized format"""
        print(f"\n{self.colors['metric']}┌{'─' * 40}┐")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"│ {key:<20}: {value:>15.2f} │")
            else:
                print(f"│ {key:<20}: {str(value):>15} │")
        print(f"└{'─' * 40}┘{self.colors['reset']}")

    def insight(self, category: str, text: str):
        """Log an insight with category-specific styling and emoji"""
        indent = "    " * self.section_level
        category_color = self.colors.get(category.lower(), self.colors['info'])
        category_emoji = {
            'Technical': '🔧',
            'Aesthetic': '🎨',
            'Evolution': '🔄',
            'Performance': '📊',
            'Innovation': '💡'
        }.get(category, '⚡')
        
        print(f"{self._get_timestamp()} {indent}{category_color}{category_emoji} {text}{self.colors['reset']}")

    def technique_analysis(self, technique: str, stats: dict):
        """Display technique analysis in a modern box"""
        # Fixed width for consistent display
        width = 45
        
        # Remove duplicate entries from stats
        cleaned_stats = {}
        for key, value in stats.items():
            if key not in cleaned_stats and key != 'synergies':
                cleaned_stats[key] = value
        
        # Print box header
        print(f"\n{self.colors['technique']}╭{'─' * width}╮")
        print(f"│ {technique} Analysis{' ' * (width - len(technique) - 9)}│")
        print(f"├{'─' * width}┤")
        
        # Print stats with consistent formatting
        for key, value in cleaned_stats.items():
            # Format the value based on its type
            if isinstance(value, float):
                formatted_value = f"{value:>10.2f}"
            elif isinstance(value, int):
                formatted_value = f"{value:>10d}"
            elif isinstance(value, datetime):
                formatted_value = f"{value.strftime('%Y-%m'):>10}"
            else:
                formatted_value = f"{str(value)[:10]:>10}"
            
            # Format key
            key_display = key.replace('_', ' ').title()
            
            # Print line with exact spacing
            # Left side takes 20 chars (including bullet and spaces), value gets 10 chars, rest is padding
            line = f"│ • {key_display:<16}: {formatted_value} {' ' * (width - 31)}│"
            print(line)
        
        # Print box footer
        print(f"╰{'─' * width}╯{self.colors['reset']}")

    def evolution_trace(self, steps: list):
        """Display evolution steps with visual improvements"""
        print(f"\n{self.colors['evolution']}╭─ Evolution Trace ─{'─' * 30}╮")
        for i, step in enumerate(steps):
            if i < len(steps) - 1:
                print(f"│  ├─ {step}")
            else:
                # Remove duplicate (Current) marker if it exists
                step_text = step.replace(" (Current) (Current)", " (Current)")
                print(f"│  └─ {step_text} {self.colors['accent']}(Current){self.colors['evolution']}")
        print(f"╰{'─' * 46}╯{self.colors['reset']}")

    def processing_step(self, step: str, status: str = None):
        """Display a processing step with improved styling"""
        indent = "    " * self.section_level
        timestamp = self._get_timestamp()
        status_color = {
            'complete': self.colors['success'],
            'error': self.colors['error'],
            'warning': self.colors['warning']
        }.get(status, self.colors['info'])
        
        status_icon = {
            'complete': '◆',
            'error': '◇',
            'warning': '◈',
            None: '◇'
        }.get(status, '◇')
        
        print(f"{timestamp} {indent}{status_color}{status_icon} {step}{self.colors['reset']}")