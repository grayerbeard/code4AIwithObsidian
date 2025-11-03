#!/usr/bin/env python3
"""
Obsidian Frontmatter Insertion Script - Phase 1
Version 3.0 - October 2025

This script inserts standardized blank frontmatter into all markdown files
in your Notes directory. It handles:
- Files with no frontmatter
- Files with existing YAML frontmatter
- Files with Dataview inline fields (Project::, tags::, etc.)
- Files with wikilink tags ([[tag]])

Phase 1: Insert blank frontmatter with proper structure
Phase 2: Use Ollama to populate values (separate script)
"""

import os
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil

# ============================================================================
# CONFIGURATION - UPDATE THIS FOR YOUR SETUP
# ============================================================================

# Your vault path - update this to match your actual vault location
VAULT_PATH = r"C:\Obsidian\Second Brain"  # CHANGE THIS!

# Notes directory (relative to vault)
NOTES_DIR_NAME = "Notes\"

# Backup directory (will be created if doesn't exist)
BACKUP_DIR_NAME = "Notes_Backup_Before_Frontmatter"

# Dry run mode - set to True to test without making changes
DRY_RUN = True  # Set to False when ready to actually modify files

# ============================================================================
# FRONTMATTER TEMPLATE (31 Parameters)
# ============================================================================

FRONTMATTER_TEMPLATE = {
    # Core Metadata (6)
    "created": None,
    "modified": None,
    "status": "new",
    "migration_date": None,
    "reviewed": False,
    "needs_attention": False,
    
    # Classification (4)
    "project": None,
    "category": None,
    "topics": [],
    "tags": [],
    
    # Note Characteristics (2)
    "note_type": None,
    "source": None,
    
    # People (2)
    "person": None,
    "collaborators": [],
    
    # Technology (3)
    "technology_stack": [],
    "tools_used": [],
    "ai_model": None,
    
    # Location (2)
    "location": None,
    "region": None,
    
    # Historical (2)
    "historical_period": None,
    "historical_context": None,
    
    # Health (2)
    "health_category": None,
    "adhd_relevant": False,
    
    # External (2)
    "url": None,
    "external_id": None,
    
    # Task Management (3)
    "priority": None,
    "actionable": False,
    "due_date": None,
    
    # Financial (1)
    "financial_category": None,
    
    # Flexible (2)
    "metadata": None,
    "notes": None,
}


class FrontmatterInserter:
    """Handles insertion of standardized frontmatter into Obsidian notes."""
    
    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path)
        self.notes_dir = self.vault_path / NOTES_DIR_NAME
        self.backup_dir = self.vault_path / BACKUP_DIR_NAME
        self.dry_run = dry_run
        self.stats = {
            "total_files": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "error_files": []
        }
    
    def validate_paths(self) -> bool:
        """Validate that vault and notes directory exist."""
        if not self.vault_path.exists():
            print(f"❌ ERROR: Vault path not found: {self.vault_path}")
            print("Please update VAULT_PATH in the script configuration.")
            return False
        
        if not self.notes_dir.exists():
            print(f"❌ ERROR: Notes directory not found: {self.notes_dir}")
            return False
        
        print(f"✓ Vault found: {self.vault_path}")
        print(f"✓ Notes directory found: {self.notes_dir}")
        return True
    
    def create_backup(self):
        """Create backup of Notes directory before processing."""
        if self.dry_run:
            print(f"\n[DRY RUN] Would create backup at: {self.backup_dir}")
            return
        
        if self.backup_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_backup = self.vault_path / f"{BACKUP_DIR_NAME}_{timestamp}"
            print(f"⚠ Backup already exists, creating new one: {new_backup}")
            self.backup_dir = new_backup
        
        print(f"📦 Creating backup: {self.backup_dir}")
        shutil.copytree(self.notes_dir, self.backup_dir)
        print("✓ Backup complete!")
    
    def extract_dataview_fields(self, content: str) -> Dict[str, any]:
        """Extract Dataview inline fields (Project::, tags::, etc.)."""
        dataview_data = {}
        
        # Pattern for Dataview inline fields: Field:: Value
        pattern = r'^(\w+)::\s*(.+)$'
        
        for line in content.split('\n')[:20]:  # Check first 20 lines
            match = re.match(pattern, line.strip())
            if match:
                field_name = match.group(1).lower()
                field_value = match.group(2).strip()
                dataview_data[field_name] = field_value
        
        return dataview_data
    
    def extract_wikilink_tags(self, content: str) -> List[str]:
        """Extract wikilink tags like [[docker]], [[ai]]."""
        # Pattern for wikilinks in the first 20 lines
        pattern = r'\[\[([^\]]+)\]\]'
        tags = []
        
        for line in content.split('\n')[:20]:
            matches = re.findall(pattern, line)
            for match in matches:
                # Only consider short single words as tags (not full note titles)
                if len(match) < 30 and ' ' not in match:
                    tags.append(match)
        
        return tags
    
    def extract_existing_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
        """Extract existing YAML frontmatter if present."""
        # Check if file starts with frontmatter delimiter
        if not content.startswith('---'):
            return None, content
        
        # Find the closing delimiter
        end_match = re.search(r'\n---\n', content[3:])
        if not end_match:
            return None, content
        
        # Extract and parse YAML
        yaml_content = content[3:end_match.start() + 3]
        remaining_content = content[end_match.end() + 3:]
        
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return frontmatter, remaining_content
        except yaml.YAMLError as e:
            print(f"⚠ Warning: Could not parse existing frontmatter: {e}")
            return None, content
    
    def merge_frontmatter(self, existing: Optional[Dict], 
                         dataview: Dict, wikilinks: List[str]) -> Dict:
        """Merge existing data with new template."""
        # Start with template
        merged = FRONTMATTER_TEMPLATE.copy()
        
        # Set migration date
        merged["migration_date"] = datetime.now().strftime("%Y-%m-%d")
        
        # Merge existing YAML frontmatter
        if existing:
            for key, value in existing.items():
                key_lower = key.lower()
                if key_lower in merged:
                    merged[key_lower] = value
        
        # Merge Dataview fields
        if "project" in dataview:
            merged["project"] = dataview["project"]
        
        # Merge wikilink tags
        if wikilinks:
            existing_tags = merged.get("tags", [])
            if isinstance(existing_tags, str):
                existing_tags = [existing_tags]
            merged["tags"] = list(set(existing_tags + wikilinks))
        
        # Add note about conversion if Dataview or wikilinks were found
        notes_parts = []
        if dataview:
            notes_parts.append(f"Converted from Dataview fields: {', '.join(dataview.keys())}")
        if wikilinks:
            notes_parts.append(f"Extracted wikilink tags: {', '.join(wikilinks)}")
        if notes_parts:
            merged["notes"] = " | ".join(notes_parts)
        
        return merged
    
    def format_frontmatter(self, data: Dict) -> str:
        """Format frontmatter as clean YAML with comments."""
        lines = ["---"]
        
        # Core Metadata
        lines.append("# Core Metadata")
        lines.append(f"created: {self._format_value(data['created'])}")
        lines.append(f"modified: {self._format_value(data['modified'])}")
        lines.append(f"status: {self._format_value(data['status'])}")
        lines.append(f"migration_date: {self._format_value(data['migration_date'])}")
        lines.append(f"reviewed: {self._format_value(data['reviewed'])}")
        lines.append(f"needs_attention: {self._format_value(data['needs_attention'])}")
        lines.append("")
        
        # Classification
        lines.append("# Classification")
        lines.append(f"project: {self._format_value(data['project'])}")
        lines.append(f"category: {self._format_value(data['category'])}")
        lines.append(f"topics: {self._format_value(data['topics'])}")
        lines.append(f"tags: {self._format_value(data['tags'])}")
        lines.append("")
        
        # Note Characteristics
        lines.append("# Note Characteristics")
        lines.append(f"note_type: {self._format_value(data['note_type'])}")
        lines.append(f"source: {self._format_value(data['source'])}")
        lines.append("")
        
        # People
        lines.append("# People")
        lines.append(f"person: {self._format_value(data['person'])}")
        lines.append(f"collaborators: {self._format_value(data['collaborators'])}")
        lines.append("")
        
        # Technology
        lines.append("# Technology")
        lines.append(f"technology_stack: {self._format_value(data['technology_stack'])}")
        lines.append(f"tools_used: {self._format_value(data['tools_used'])}")
        lines.append(f"ai_model: {self._format_value(data['ai_model'])}")
        lines.append("")
        
        # Location
        lines.append("# Location")
        lines.append(f"location: {self._format_value(data['location'])}")
        lines.append(f"region: {self._format_value(data['region'])}")
        lines.append("")
        
        # Historical
        lines.append("# Historical")
        lines.append(f"historical_period: {self._format_value(data['historical_period'])}")
        lines.append(f"historical_context: {self._format_value(data['historical_context'])}")
        lines.append("")
        
        # Health
        lines.append("# Health")
        lines.append(f"health_category: {self._format_value(data['health_category'])}")
        lines.append(f"adhd_relevant: {self._format_value(data['adhd_relevant'])}")
        lines.append("")
        
        # External
        lines.append("# External")
        lines.append(f"url: {self._format_value(data['url'])}")
        lines.append(f"external_id: {self._format_value(data['external_id'])}")
        lines.append("")
        
        # Task Management
        lines.append("# Task Management")
        lines.append(f"priority: {self._format_value(data['priority'])}")
        lines.append(f"actionable: {self._format_value(data['actionable'])}")
        lines.append(f"due_date: {self._format_value(data['due_date'])}")
        lines.append("")
        
        # Financial
        lines.append("# Financial")
        lines.append(f"financial_category: {self._format_value(data['financial_category'])}")
        lines.append("")
        
        # Flexible
        lines.append("# Flexible")
        lines.append(f"metadata: {self._format_value(data['metadata'])}")
        if data['notes']:
            lines.append(f"notes: {self._format_value(data['notes'])}")
        else:
            lines.append(f"notes:")
        
        lines.append("---")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _format_value(self, value) -> str:
        """Format value for YAML output."""
        if value is None:
            return ""
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, list):
            if not value:
                return "[]"
            return yaml.dump(value, default_flow_style=True).strip()
        if isinstance(value, str):
            # Quote strings that contain special characters
            if ':' in value or '#' in value:
                return f'"{value}"'
            return value
        return str(value)
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single markdown file."""
        try:
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract existing data
            existing_fm, body_content = self.extract_existing_frontmatter(content)
            dataview_fields = self.extract_dataview_fields(body_content)
            wikilink_tags = self.extract_wikilink_tags(body_content)
            
            # Merge data
            merged_fm = self.merge_frontmatter(existing_fm, dataview_fields, wikilink_tags)
            
            # Get file timestamps
            stat = filepath.stat()
            if not merged_fm["created"]:
                merged_fm["created"] = datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d")
            if not merged_fm["modified"]:
                merged_fm["modified"] = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d")
            
            # Format new frontmatter
            new_frontmatter = self.format_frontmatter(merged_fm)
            
            # Remove Dataview inline fields from body (first 20 lines)
            body_lines = body_content.split('\n')
            cleaned_lines = []
            dataview_pattern = r'^(\w+)::\s*(.+)$'
            
            for i, line in enumerate(body_lines):
                if i < 20 and (re.match(dataview_pattern, line.strip()) or 
                              (line.strip().startswith('[[') and line.strip().endswith(']]') and 
                               len(line.strip()) < 30)):
                    continue  # Skip Dataview fields and simple wikilink tags
                cleaned_lines.append(line)
            
            # Reconstruct file
            new_content = new_frontmatter + '\n'.join(cleaned_lines).lstrip()
            
            # Write file (or show what would be written in dry run)
            if self.dry_run:
                print(f"\n[DRY RUN] Would process: {filepath.relative_to(self.notes_dir)}")
                if dataview_fields:
                    print(f"  - Found Dataview fields: {list(dataview_fields.keys())}")
                if wikilink_tags:
                    print(f"  - Found wikilink tags: {wikilink_tags}")
                return True
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✓ Processed: {filepath.relative_to(self.notes_dir)}")
                return True
                
        except Exception as e:
            print(f"❌ Error processing {filepath.name}: {str(e)}")
            self.stats["error_files"].append(str(filepath))
            return False
    
    def process_all_files(self):
        """Process all markdown files in Notes directory and subdirectories."""
        print(f"\n{'='*60}")
        print(f"Processing files in: {self.notes_dir}")
        print(f"Mode: {'DRY RUN (no changes will be made)' if self.dry_run else 'LIVE (files will be modified)'}")
        print(f"{'='*60}\n")
        
        # Find all markdown files
        md_files = list(self.notes_dir.rglob("*.md"))
        self.stats["total_files"] = len(md_files)
        
        print(f"Found {len(md_files)} markdown files to process\n")
        
        if not self.dry_run:
            response = input("⚠ This will modify your files. Continue? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return
        
        # Process each file
        for filepath in md_files:
            if self.process_file(filepath):
                self.stats["processed"] += 1
            else:
                self.stats["errors"] += 1
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print processing summary."""
        print(f"\n{'='*60}")
        print("PROCESSING SUMMARY")
        print(f"{'='*60}")
        print(f"Total files found: {self.stats['total_files']}")
        print(f"Successfully processed: {self.stats['processed']}")
        print(f"Errors: {self.stats['errors']}")
        
        if self.stats["error_files"]:
            print("\nFiles with errors:")
            for filepath in self.stats["error_files"]:
                print(f"  - {filepath}")
        
        print(f"{'='*60}\n")
        
        if self.dry_run:
            print("ℹ This was a DRY RUN - no files were modified.")
            print("Set DRY_RUN = False in the script to actually process files.")
        else:
            print(f"✓ Backup created at: {self.backup_dir}")
            print("✓ All files processed successfully!")
            print("\nNext step: Run Phase 2 with Ollama to populate frontmatter values")


def main():
    """Main execution function."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  Obsidian Frontmatter Insertion - Phase 1                       ║
║  Version 3.0 - October 2025                                      ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Create inserter instance
    inserter = FrontmatterInserter(VAULT_PATH, dry_run=DRY_RUN)
    
    # Validate paths
    if not inserter.validate_paths():
        return
    
    # Create backup (if not dry run)
    inserter.create_backup()
    
    # Process files
    inserter.process_all_files()


if __name__ == "__main__":
    main()