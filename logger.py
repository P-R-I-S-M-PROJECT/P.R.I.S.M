from colorama import init, Fore, Back, Style
from datetime import datetime
import sys

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
            'accent': Fore.BLUE + Style.BRIGHT
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
        
    def pattern_score(self, score: float):
        """Print pattern score with visual indicator"""
        bars = int(score / 5)
        bar_str = "█" * bars + "░" * (20 - bars)
        print(f"{self._get_timestamp()} {self.colors['highlight']}Pattern Score: [{bar_str}] {score:.1f}/100{self.colors['reset']}")
        
    def _get_timestamp(self) -> str:
        """Get timestamp with colors"""
        return f"{self.colors['accent']}[{self._get_time()}]{self.colors['reset']}"
        
    def _get_time(self) -> str:
        """Get current time formatted as HH:MM:SS"""
        return datetime.now().strftime("%H:%M:%S")
        
    def debug(self, text: str, data: str = None, exc_info: bool = False):
        """Print debug message with optional data dump"""
        if not self.debug_enabled:
            return
            
        indent = "    " * self.section_level
        timestamp = self._get_timestamp()
        
        # Print the main debug message
        print(f"{timestamp} {indent}{self.colors['accent']}DEBUG: {text}{self.colors['reset']}")
        
        # If there's detailed data, print it in a formatted block
        if data:
            data_lines = data.strip().split('\n')
            for line in data_lines:
                print(f"{timestamp} {indent}{self.colors['accent']}       {line.strip()}{self.colors['reset']}")
        
        # Print stack trace if requested
        if exc_info:
            import traceback
            trace_lines = traceback.format_exc().split('\n')
            for line in trace_lines:
                print(f"{timestamp} {indent}{self.colors['accent']}TRACE: {line}{self.colors['reset']}")
        
    def video_sync_complete(self, output: str):
        """Print video sync completion message with details"""
        indent = "    " * self.section_level
        print(f"{self._get_timestamp()} {indent}{self.colors['success']}✓ Video sync completed{self.colors['reset']}")
        
        # Try to extract the video filename from the output if present
        if output and "Uploaded" in output:
            print(f"{self._get_timestamp()} {indent}{self.colors['info']}  {output.strip()}{self.colors['reset']}")
        
    def set_debug(self, enabled: bool):
        """Toggle debug logging"""
        self.debug_enabled = enabled