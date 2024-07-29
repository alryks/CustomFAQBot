"""
get all the files from ./migrations directory, sort them by name without extension (pathlib) and run them in order with runpy
"""

from pathlib import Path
import runpy

migrations = sorted(Path("migrations").glob("*.py"), key=lambda x: x.stem)
for migration in migrations:
    runpy.run_path(migration)
    print(f"Migration {migration.stem} done...")

print("Full migration completed!")