#!/usr/bin/env python3
"""
Obsidian Frontmatter Population Script - Phase 2
Version 1.0 - November 2025

This script uses Ollama to intelligently populate frontmatter fields
based on note content. Features:
- Progress logging and resume capability
- Processes files systematically
- Handles interruptions gracefully
- Detailed logging of all changes
- Can process specific folders or entire vault
"""

import os
import re
import yaml
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil
from dataclasses import dataclass, asdict

# ============================================================================
# CONFIGURATION
# ============================================================================

# Your vault path
VAULT_PATH = r"C:\Obsidian\Second Brain"

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"  # Change if Ollama runs elsewhere
OLLAMA_MODEL = "llama2"  # Or your preferred model (mistral, deepseek-r1, etc.)

# Folders to process (relative to vault Notes directory)
# Leave empty [] to process all folders
FOLDERS_TO_PROCESS = [
    r"Notes\AANext",
    r"Notes\Local AI", 
    r"Notes\Cara"
]

# Or set to process entire Notes directory
PROCESS_ALL_NOTES = False  # Set to True to process all Notes

# Progress tracking
PROGRESS_LOG = r"C:\Code\frontmatter\frontmatter_progress.json"
DETAILED_LOG = r"C:\Code\frontmatter\frontmatter_changes.log"

# Dry run mode
DRY_RUN = True  # Set to False to actually modify files

# Batch size (save progress after this many files)
BATCH_SIZE = 10

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ProcessingProgress:
    """Track processing progress."""
    total_files: int = 0
    processed_files: int = 0
    skipped_files: int = 0
    error_files: int = 0
    last_processed_file: str = ""
    processed_list: List[str] = None
    error_list: List[str] = None
    started_at: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if self.processed_list is None:
            self.processed_list = []
        if self.error_list is None:
            self.error_list = []


# ============================================================================
# OLLAMA INTEGRATION
# ============================================================================

class OllamaAnalyzer:
    """Uses Ollama to analyze note content and suggest frontmatter."""
    
    def __init__(self, model: str, ollama_url: str):
        self.model = model
        self.ollama_url = ollama_url
    
    def test_connection(self) -> bool:
        """Test if Ollama is accessible."""
        try:
            response = requests.get(self.ollama_url.replace('/api/generate', '/api/tags'))
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {e}")
            return False
    
    def analyze_note(self, title: str, content: str, existing_fm: Dict) -> Dict:
        """Analyze note content and suggest frontmatter values."""
        
        # Build prompt
        prompt = self._build_analysis_prompt(title, content, existing_fm)
        
        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower temperature for more consistent results
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                suggestions = self._parse_ollama_response(result.get('response', ''))
                return suggestions
            else:
                print(f"⚠ Ollama request failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"⚠ Error calling Ollama: {e}")
            return {}
    
    def _build_analysis_prompt(self, title: str, content: str, existing_fm: Dict) -> str:
        """Build the analysis prompt for Ollama."""
        
        # Truncate content if too long (keep first 2000 chars)
        content_preview = content[:2000] if len(content) > 2000 else content
        
        prompt = f"""Analyze this Obsidian note and suggest metadata values.

Note Title: {title}

Note Content:
{content_preview}

Existing Metadata:
Project: {existing_fm.get('project', 'None')}
Tags: {existing_fm.get('tags', [])}

Instructions:
Based on the content, suggest appropriate values for these metadata fields.
Respond ONLY with a valid JSON object (no markdown, no explanation):

{{
  "category": "one of: Technical, Personal, Project, Reference, Learning, Health, Financial, Maritime, History, AI_ML",
  "note_type": "one of: note, documentation, idea, task, research, log, guide, reference",
  "topics": ["list", "of", "relevant", "topics"],
  "tags": ["list", "of", "tags"],
  "technology_stack": ["if technical, list technologies"],
  "tools_used": ["software or tools mentioned"],
  "ai_model": "if AI-related, which model",
  "project": "project name if mentioned or keep existing",
  "status": "one of: new, in-progress, completed, archived, needs-review"
}}

Only include fields where you have confidence. Return empty arrays [] for lists if nothing appropriate found.
"""
        return prompt
    
    def _parse_ollama_response(self, response: str) -> Dict:
        """Parse Ollama's JSON response."""
        try:
            # Try to find JSON in response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                suggestions = json.loads(json_str)
                return suggestions
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠ Could not parse Ollama response as JSON: {e}")
            print(f"Response was: {response[:200]}")
            return {}


# ============================================================================
# FRONTMATTER PROCESSOR
# ============================================================================

class FrontmatterPopulator:
    """Populates frontmatter fields using Ollama analysis."""
    
    def __init__(self, vault_path: str, dry_run: bool = True):
        self.vault_path = Path(vault_path)
        self.dry_run = dry_run
        self.progress = self._load_progress()
        self.analyzer = OllamaAnalyzer(OLLAMA_MODEL, OLLAMA_URL)
        
        # Initialize detailed log
        self.detail_log = open(DETAILED_LOG, 'a', encoding='utf-8')
        self._log(f"\n{'='*80}")
        self._log(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        self._log(f"{'='*80}\n")
    
    def _load_progress(self) -> ProcessingProgress:
        """Load existing progress or create new."""
        if os.path.exists(PROGRESS_LOG):
            try:
                with open(PROGRESS_LOG, 'r') as f:
                    data = json.load(f)
                    return ProcessingProgress(**data)
            except Exception as e:
                print(f"⚠ Could not load progress file: {e}")
        
        progress = ProcessingProgress()
        progress.started_at = datetime.now().isoformat()
        return progress
    
    def _save_progress(self):
        """Save current progress to file."""
        self.progress.last_updated = datetime.now().isoformat()
        
        with open(PROGRESS_LOG, 'w') as f:
            json.dump(asdict(self.progress), f, indent=2)
        
        print(f"💾 Progress saved: {self.progress.processed_files}/{self.progress.total_files} files")
    
    def _log(self, message: str):
        """Write to detailed log file."""
        self.detail_log.write(message + '\n')
        self.detail_log.flush()
    
    def get_files_to_process(self) -> List[Path]:
        """Get list of files to process based on configuration."""
        all_files = []
        
        if PROCESS_ALL_NOTES:
            notes_dir = self.vault_path / "Notes"
            all_files = list(notes_dir.rglob("*.md"))
        else:
            for folder in FOLDERS_TO_PROCESS:
                folder_path = self.vault_path / folder
                if folder_path.exists():
                    all_files.extend(list(folder_path.rglob("*.md")))
                else:
                    print(f"⚠ Folder not found: {folder_path}")
        
        # Filter out already processed files
        files_to_process = [
            f for f in all_files 
            if str(f) not in self.progress.processed_list
        ]
        
        return files_to_process
    
    def extract_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
        """Extract existing YAML frontmatter."""
        if not content.startswith('---'):
            return None, content
        
        end_match = re.search(r'\n---\n', content[3:])
        if not end_match:
            return None, content
        
        yaml_content = content[3:end_match.start() + 3]
        remaining_content = content[end_match.end() + 3:]
        
        try:
            frontmatter = yaml.safe_load(yaml_content)
            return frontmatter, remaining_content
        except yaml.YAMLError as e:
            print(f"⚠ Could not parse frontmatter: {e}")
            return None, content
    
    def merge_suggestions(self, existing: Dict, suggestions: Dict) -> Dict:
        """Merge AI suggestions with existing frontmatter."""
        merged = existing.copy()
        
        # Only update fields that are empty or have default values
        for key, value in suggestions.items():
            existing_value = merged.get(key)
            
            # Update if:
            # - Field is empty/None
            # - Field is empty list
            # - Field has default value like "new"
            # - Value is more specific than existing
            
            if key in ['tags', 'topics', 'technology_stack', 'tools_used']:
                # For lists, merge and deduplicate
                if value and isinstance(value, list):
                    existing_list = existing_value if isinstance(existing_value, list) else []
                    merged[key] = list(set(existing_list + value))
            
            elif not existing_value or existing_value in [None, "", [], "new"]:
                # Update empty or default fields
                if value and value not in [None, "", []]:
                    merged[key] = value
            
            elif key == 'status' and existing_value == 'new':
                # Update status if it's still "new"
                if value and value != 'new':
                    merged[key] = value
        
        return merged
    
    def update_frontmatter_in_content(self, content: str, new_fm: Dict) -> str:
        """Update frontmatter in file content."""
        existing_fm, body = self.extract_frontmatter(content)
        
        # Format new frontmatter
        yaml_str = yaml.dump(new_fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        # Reconstruct file
        new_content = f"---\n{yaml_str}---\n\n{body}"
        
        return new_content
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single file."""
        try:
            self._log(f"\n--- Processing: {filepath.name} ---")
            
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract existing frontmatter
            existing_fm, body = self.extract_frontmatter(content)
            
            if not existing_fm:
                self._log(f"⚠ No frontmatter found, skipping")
                return False
            
            # Get AI suggestions
            print(f"🤖 Analyzing: {filepath.name}...")
            suggestions = self.analyzer.analyze_note(filepath.stem, body, existing_fm)
            
            if not suggestions:
                self._log(f"⚠ No suggestions from AI")
                print(f"⚠ Could not get suggestions for {filepath.name}")
                return False
            
            # Merge suggestions
            updated_fm = self.merge_suggestions(existing_fm, suggestions)
            
            # Log changes
            changes = []
            for key in suggestions.keys():
                old_val = existing_fm.get(key)
                new_val = updated_fm.get(key)
                if old_val != new_val:
                    changes.append(f"  {key}: {old_val} → {new_val}")
            
            if changes:
                self._log(f"Changes suggested:")
                for change in changes:
                    self._log(change)
                
                if not self.dry_run:
                    # Update file
                    new_content = self.update_frontmatter_in_content(content, updated_fm)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self._log(f"✓ File updated")
                    print(f"✓ Updated: {filepath.name}")
                else:
                    self._log(f"[DRY RUN] Would update file")
                    print(f"[DRY RUN] Would update: {filepath.name}")
            else:
                self._log(f"No changes needed")
                print(f"• No changes: {filepath.name}")
            
            return True
            
        except Exception as e:
            self._log(f"❌ Error: {str(e)}")
            print(f"❌ Error processing {filepath.name}: {e}")
            return False
    
    def process_all(self):
        """Process all files with progress tracking."""
        
        # Test Ollama connection
        print("\n🔍 Testing Ollama connection...")
        if not self.analyzer.test_connection():
            print("❌ Cannot connect to Ollama. Make sure it's running.")
            print(f"   Trying to connect to: {OLLAMA_URL}")
            return
        print(f"✓ Connected to Ollama (model: {OLLAMA_MODEL})")
        
        # Get files to process
        files = self.get_files_to_process()
        self.progress.total_files = len(files)
        
        if not files:
            print("\n✓ All files already processed!")
            return
        
        print(f"\n📊 Progress: {self.progress.processed_files} done, {len(files)} remaining")
        print(f"{'='*80}\n")
        
        # Process files
        for i, filepath in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] Processing: {filepath.name}")
            
            success = self.process_file(filepath)
            
            if success:
                self.progress.processed_files += 1
                self.progress.processed_list.append(str(filepath))
            else:
                self.progress.error_files += 1
                self.progress.error_list.append(str(filepath))
            
            self.progress.last_processed_file = str(filepath)
            
            # Save progress after each batch
            if i % BATCH_SIZE == 0:
                self._save_progress()
        
        # Final save
        self._save_progress()
        self.print_summary()
    
    def print_summary(self):
        """Print processing summary."""
        print(f"\n{'='*80}")
        print("PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"Total files: {self.progress.total_files}")
        print(f"Processed: {self.progress.processed_files}")
        print(f"Errors: {self.progress.error_files}")
        
        if self.progress.error_list:
            print(f"\nFiles with errors ({len(self.progress.error_list)}):")
            for filepath in self.progress.error_list[:10]:  # Show first 10
                print(f"  - {Path(filepath).name}")
            if len(self.progress.error_list) > 10:
                print(f"  ... and {len(self.progress.error_list) - 10} more")
        
        print(f"\n📊 Progress saved to: {PROGRESS_LOG}")
        print(f"📝 Detailed log: {DETAILED_LOG}")
        print(f"{'='*80}\n")
        
        if self.dry_run:
            print("ℹ This was a DRY RUN - no files were modified.")
            print("Set DRY_RUN = False to actually update files.")
    
    def __del__(self):
        """Clean up."""
        if hasattr(self, 'detail_log'):
            self.detail_log.close()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║  Obsidian Frontmatter Population - Phase 2                      ║
║  Intelligent population using Ollama                            ║
║  Version 1.0 - November 2025                                    ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Create populator
    populator = FrontmatterPopulator(VAULT_PATH, dry_run=DRY_RUN)
    
    # Process files
    try:
        populator.process_all()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        populator._save_progress()
        print("💾 Progress saved. You can resume by running the script again.")


if __name__ == "__main__":
    main()
