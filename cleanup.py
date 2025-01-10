import shutil
from config import Config
from logger import ArtLogger
from datetime import datetime

class SystemCleaner:
    def __init__(self, config: Config, logger: ArtLogger = None):
        self.config = config
        self.db = config.db_manager
        self.log = logger or ArtLogger()
        
    def cleanup_system(self):
        """Reset system to template state"""
        self.log.title("SYSTEM CLEANUP")
        self.log.start_section("Cleaning Up")
        
        try:
            # Archive sketches before cleanup
            self._archive_sketches()
            self._cleanup_renders()
            self._cleanup_web_videos()
            self._reset_database()
            self._reset_documentation()
            self._reset_metadata()
            
        except Exception as e:
            self.log.error(f"Error during cleanup: {e}")
            
        self.log.end_section()
        self.log.title("Cleanup Complete")
    
    def _archive_sketches(self):
        """Archive sketch files from render directories"""
        renders_path = self.config.base_path / "renders"
        if not renders_path.exists():
            return

        # Create archives directory if it doesn't exist
        archives_dir = renders_path / "archives"
        archives_dir.mkdir(parents=True, exist_ok=True)

        # Find all sketch files in render directories
        sketch_files = []
        for render_dir in renders_path.glob("render_v*"):
            if render_dir.is_dir():
                for sketch_file in render_dir.glob("sketch_v*.pde"):
                    sketch_files.append(sketch_file)

        if not sketch_files:
            return

        # Create timestamped archive folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_dir = archives_dir / timestamp
        archive_dir.mkdir(exist_ok=True)

        self.log.info(f"Archiving {len(sketch_files)} sketch files...")
        for sketch_file in sketch_files:
            try:
                shutil.copy2(str(sketch_file), str(archive_dir / sketch_file.name))
                self.log.success(f"Archived {sketch_file.name}")
            except Exception as e:
                self.log.error(f"Failed to archive {sketch_file.name}: {e}")
    
    def _cleanup_renders(self):
        """Clear renders directory"""
        renders_path = self.config.base_path / "renders"
        if renders_path.exists():
            self.log.info("Clearing renders directory...")
            for item in renders_path.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    self.log.success(f"Removed {item.name}")
                except Exception as e:
                    self.log.error(f"Failed to remove {item.name}: {e}")
        else:
            # Create renders directory if it doesn't exist
            renders_path.mkdir(exist_ok=True)
            self.log.info("Created renders directory")
    
    def _cleanup_web_videos(self):
        """Clear web videos directory including metadata files"""
        web_videos_path = self.config.base_path / "web" / "public" / "videos"
        if web_videos_path.exists():
            # Clean both video and metadata files
            for file in web_videos_path.glob("*"):
                if file.suffix in ['.mp4', '.json']:  # Clean both video and metadata files
                    try:
                        file.unlink()
                        self.log.success(f"Removed {file.name}")
                    except Exception as e:
                        self.log.error(f"Failed to remove {file.name}: {e}")
    
    def _reset_database(self):
        """Reset database to initial state"""
        self.db.init_db(force=True)
    
    def _reset_documentation(self):
        """Reset documentation to initial state"""
        history_template = """Most Recent Version: v0

# Animation Experiment History (2024)

## Current Version: v0
**Focus:** Black background with mainly monochrome and white lines/shapes/elements/patterns for subtle layering and variation.

## Version Entry Format
Each version documents:
- **Score**: Overall performance metrics
- **Innovation**: Measure of creative approach
- **Aesthetic**: Visual appeal assessment
- **Complexity**: Implementation sophistication
- **Techniques**: Applied creative methods

## Historical Record

### v0: Initial Setup
- **Score**: 75.0
- **Innovation**: 85.0
- **Aesthetic**: 75.0
- **Complexity**: 75.0
- **Techniques**: Basic geometric framework
"""
        with open(self.config.paths['docs']['history'], 'w') as f:
            f.write(history_template)
    
    def _reset_metadata(self):
        """Reset metadata to initial state"""
        self.config.initialize_metadata() 