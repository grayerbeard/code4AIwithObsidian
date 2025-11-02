#!/usr/bin/env python3
"""
Frontmatter Progress Manager
Quick utility to view and manage progress tracking
"""

import json
import os
from pathlib import Path

# Match your configuration
PROGRESS_LOG = r"C:\code\code4AIwithObsidian\logs\frontmatter_progress.json"

def load_progress():
    """Load progress file."""
    if not os.path.exists(PROGRESS_LOG):
        print("❌ No progress file found!")
        return None
    
    with open(PROGRESS_LOG, 'r') as f:
        return json.load(f)

def show_status():
    """Show current progress status."""
    progress = load_progress()
    if not progress:
        return
    
    print("\n" + "="*60)
    print("CURRENT PROGRESS STATUS")
    print("="*60)
    print(f"Started: {progress.get('started_at', 'Unknown')}")
    print(f"Last updated: {progress.get('last_updated', 'Unknown')}")
    print(f"Current mode: {progress.get('current_mode', 'Unknown')}")
    print(f"\nDry run tested: {len(progress.get('processed_list_dry_run', []))} files")
    print(f"Live updated: {len(progress.get('processed_list_live', []))} files")
    print(f"Errors: {len(progress.get('error_list', []))} files")
    
    if progress.get('last_processed_file'):
        print(f"\nLast processed: {Path(progress['last_processed_file']).name}")
    
    print("="*60 + "\n")

def clear_dry_run():
    """Clear dry run list (to retest in dry run mode)."""
    progress = load_progress()
    if not progress:
        return
    
    count = len(progress.get('processed_list_dry_run', []))
    progress['processed_list_dry_run'] = []
    
    with open(PROGRESS_LOG, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print(f"✓ Cleared {count} files from dry run list")
    print("  You can now retest them in dry run mode")

def clear_live():
    """Clear live list (to reprocess in live mode)."""
    progress = load_progress()
    if not progress:
        return
    
    count = len(progress.get('processed_list_live', []))
    
    response = input(f"⚠️  This will mark {count} files as not updated. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return
    
    progress['processed_list_live'] = []
    
    with open(PROGRESS_LOG, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print(f"✓ Cleared {count} files from live list")
    print("  These files will be reprocessed in live mode")

def clear_errors():
    """Clear error list."""
    progress = load_progress()
    if not progress:
        return
    
    count = len(progress.get('error_list', []))
    progress['error_list'] = []
    progress['error_files'] = 0
    
    with open(PROGRESS_LOG, 'w') as f:
        json.dump(progress, f, indent=2)
    
    print(f"✓ Cleared {count} files from error list")

def reset_all():
    """Reset all progress (start fresh)."""
    response = input("⚠️  This will reset ALL progress. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled")
        return
    
    if os.path.exists(PROGRESS_LOG):
        # Backup old progress
        backup = PROGRESS_LOG.replace('.json', '_backup.json')
        os.rename(PROGRESS_LOG, backup)
        print(f"✓ Old progress backed up to: {backup}")
        print("✓ Progress reset - next run will start fresh")
    else:
        print("No progress file to reset")

def main():
    """Main menu."""
    while True:
        print("\nFrontmatter Progress Manager")
        print("="*40)
        print("1. Show current status")
        print("2. Clear dry run list (retest in dry run)")
        print("3. Clear live list (reprocess in live mode)")
        print("4. Clear error list")
        print("5. Reset all progress")
        print("6. Exit")
        print("="*40)
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            show_status()
        elif choice == '2':
            clear_dry_run()
        elif choice == '3':
            clear_live()
        elif choice == '4':
            clear_errors()
        elif choice == '5':
            reset_all()
        elif choice == '6':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()