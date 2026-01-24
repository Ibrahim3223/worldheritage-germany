"""
Test Pipeline Runner
Runs entire pipeline on 10-site test dataset
"""

import subprocess
import sys
from pathlib import Path
import shutil
import time

def run_test_pipeline():
    """Run complete pipeline on test data"""

    scripts_dir = Path(__file__).parent
    data_dir = scripts_dir.parent / 'data'

    # Backup original sites.json
    original_sites = data_dir / 'raw' / 'sites.json'
    test_sites = data_dir / 'raw' / 'sites_test.json'
    backup_sites = data_dir / 'raw' / 'sites_backup.json'

    print("=" * 70)
    print("WORLDHERITAGE.GUIDE - TEST PIPELINE")
    print("=" * 70)
    print(f"Running on 10-site test dataset...")
    print()

    # Check if test file exists
    if not test_sites.exists():
        print("ERROR: sites_test.json not found!")
        print("Run: python -c 'from test_pipeline import create_test_data; create_test_data()'")
        return False

    # Backup and swap
    print("Step 0: Preparing test environment...")
    if original_sites.exists():
        shutil.copy(original_sites, backup_sites)
        print(f"  [OK] Backed up original sites.json")

    shutil.copy(test_sites, original_sites)
    print(f"  [OK] Using test dataset (10 sites)")
    print()

    try:
        # Script 2: Fetch Images
        print("Step 1: Fetching images (Script 2)...")
        print("-" * 70)
        result = subprocess.run(
            [sys.executable, "2_fetch_images.py"],
            cwd=scripts_dir,
            capture_output=False
        )
        if result.returncode != 0:
            print("ERROR in Script 2")
            return False
        print()
        time.sleep(2)

        # Script 3: Generate Content
        print("Step 2: Generating content with GPT-4o-mini (Script 3)...")
        print("-" * 70)
        print("WARNING: This will use OpenAI API credits!")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Skipped Script 3")
            print("You can run manually: python 3_generate_content.py")
        else:
            result = subprocess.run(
                [sys.executable, "3_generate_content.py"],
                cwd=scripts_dir,
                capture_output=False
            )
            if result.returncode != 0:
                print("ERROR in Script 3")
                return False
        print()
        time.sleep(2)

        # Script 4: Validate Quality
        print("Step 3: Validating quality (Script 4)...")
        print("-" * 70)
        result = subprocess.run(
            [sys.executable, "4_validate_quality.py"],
            cwd=scripts_dir,
            capture_output=False
        )
        if result.returncode != 0:
            print("ERROR in Script 4")
            return False
        print()
        time.sleep(2)

        # Script 5: Generate Hugo Site
        print("Step 4: Generating Hugo markdown (Script 5)...")
        print("-" * 70)
        result = subprocess.run(
            [sys.executable, "5_generate_site.py"],
            cwd=scripts_dir,
            capture_output=False
        )
        if result.returncode != 0:
            print("ERROR in Script 5")
            return False
        print()

        # Hugo Build
        print("Step 5: Building Hugo site...")
        print("-" * 70)
        result = subprocess.run(
            ["hugo", "--cleanDestinationDir"],
            cwd=scripts_dir.parent,
            capture_output=False
        )
        if result.returncode != 0:
            print("ERROR in Hugo build")
            return False
        print()

        print("=" * 70)
        print("TEST PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Start Hugo server: hugo server")
        print("  2. Open: http://localhost:1313")
        print("  3. Test all 10 pages")
        print()
        print("To restore original data:")
        print("  python -c 'from test_pipeline import restore_original'")
        print()

        return True

    finally:
        # Option to restore
        pass

def restore_original():
    """Restore original sites.json from backup"""
    scripts_dir = Path(__file__).parent
    data_dir = scripts_dir.parent / 'data'

    original_sites = data_dir / 'raw' / 'sites.json'
    backup_sites = data_dir / 'raw' / 'sites_backup.json'

    if backup_sites.exists():
        shutil.copy(backup_sites, original_sites)
        print("[OK] Restored original sites.json")
        backup_sites.unlink()
        print("[OK] Removed backup file")
    else:
        print("No backup found")

if __name__ == '__main__':
    success = run_test_pipeline()
    sys.exit(0 if success else 1)
