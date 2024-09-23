"""
get all the files from ./migrations directory, sort them by name without extension (pathlib) and run them in order with runpy
"""

from pathlib import Path
import runpy

migration_input = input("What migration do you want to run? (ex.: all, 0001, 0003-0005): ")
if migration_input == "all":
    migrations = sorted(Path("migrations").glob("*.py"), key=lambda x: x.stem)
elif "-" in migration_input:
    start, end = migration_input.split("-")
    migrations = sorted(Path("migrations").glob("*.py"), key=lambda x: x.stem)[int(start) - 1:int(end)]
else:
    migrations = [Path(f"migrations/{migration_input}.py")]

for migration in migrations:
    runpy.run_path(migration)
    print(f"Migration {migration.stem} done...")

print("Full migration completed!")