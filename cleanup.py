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
            self._reset_database()
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

        # Create snapshots directory if it doesn't exist
        snapshots_dir = renders_path / "snapshots"
        snapshots_dir.mkdir(parents=True, exist_ok=True)

        # Find all sketch files in render directories
        sketch_files = []
        for render_dir in renders_path.glob("render_v*"):
            if render_dir.is_dir():
                for sketch_file in render_dir.glob("render_v*.pde"):
                    sketch_files.append(sketch_file)

        if not sketch_files:
            return

        # Create timestamped snapshot folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_dir = snapshots_dir / timestamp
        snapshot_dir.mkdir(exist_ok=True)

        self.log.info(f"Archiving {len(sketch_files)} sketch files...")
        for sketch_file in sketch_files:
            try:
                shutil.copy2(str(sketch_file), str(snapshot_dir / sketch_file.name))
                self.log.success(f"Archived {sketch_file.name}")
            except Exception as e:
                self.log.error(f"Failed to archive {sketch_file.name}: {e}")
    
    def _cleanup_renders(self):
        """Clear renders directory while preserving snapshots and .gitkeep"""
        renders_path = self.config.base_path / "renders"
        if renders_path.exists():
            self.log.info("Clearing renders directory...")
            for item in renders_path.iterdir():
                try:
                    # Skip the snapshots directory and .gitkeep
                    if item.name == "snapshots" or item.name == ".gitkeep":
                        continue
                        
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
    
    def _reset_database(self):
        """Reset database to initial state"""
        self.db.init_db(force=True)
    
    def _reset_metadata(self):
        """Reset metadata to initial state"""
        self.config.initialize_metadata() 