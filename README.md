# Obsidian Frontmatter Automation Suite

A collection of Python scripts to automate the creation, population, and management of standardized YAML frontmatter in Obsidian markdown notes using AI analysis via Ollama.

## Project Overview

This project was created to solve the challenge of maintaining consistent metadata across hundreds of Obsidian notes in a "second brain" knowledge management system. Rather than manually adding and populating 31 frontmatter parameters for each note, these scripts automate the process using local AI models through Ollama.

### Why This Was Created

- **Knowledge Management**: Organizing 400+ notes across multiple projects, topics, and interests
- **Cognitive Support**: Creating a searchable, well-categorized system for information retention
- **Scalability**: Manual frontmatter entry is not practical for large note collections
- **Privacy**: Using local AI (Ollama) keeps all note content and analysis private
- **Consistency**: Ensures all notes follow the same 31-parameter frontmatter structure

## The Three Scripts

### 1. Phase 1: Frontmatter Structure Insertion (`front.py`)

**Purpose**: Inserts the standardized 31-parameter frontmatter template into all markdown files.

**What it does**:
- Scans specified directories for markdown files
- Preserves any existing frontmatter data
- Extracts and converts Dataview inline fields (e.g., `Project::`)
- Extracts wikilink tags (e.g., `[[tag]]`)
- Inserts full frontmatter structure with proper YAML formatting
- Creates backups before making changes

**When to use**: Run this first on new notes or notes without proper frontmatter structure.

### 2. Phase 2: AI-Powered Value Population (`setfront.py`)

**Purpose**: Uses Ollama to intelligently analyze note content and populate frontmatter fields.

**What it does**:
- Reads note content and existing frontmatter
- Sends content to Ollama for analysis
- Receives AI-generated suggestions for:
  - Category (Technical, Personal, Project, etc.)
  - Note type (documentation, idea, task, etc.)
  - Topics and tags
  - Technology stack
  - Tools used
  - AI models mentioned
  - Project association
  - Status
- Merges suggestions with existing data (doesn't overwrite)
- Tracks progress separately for dry-run and live modes
- Resumes from where it left off if interrupted

**When to use**: After Phase 1, to intelligently populate the empty frontmatter fields.

### 3. Progress Manager (`progress_manager.py`)

**Purpose**: Utility to view and manage progress tracking.

**What it does**:
- Shows current processing status
- Displays counts of files in dry-run vs live mode
- Allows clearing progress lists to reprocess files
- Resets all progress to start fresh
- Backs up progress data before resets

**When to use**: To check status, troubleshoot, or reset progress between runs.

## Installation & Setup

### Prerequisites

1. **Python 3.8+** with required packages:
   ```bash
   pip install pyyaml requests
   ```

2. **Ollama** installed and running:
   - Download from: https://ollama.ai
   - Pull a model: `ollama pull mistral:7b` (or llama2, gemma3, etc.)

3. **Git** for repository management

### Repository Structure

```
your-repo/
├── front_01_Nov_fixed.py        # Phase 1: Structure insertion
├── setFronts_fixed.py            # Phase 2: AI population
├── progress_manager.py           # Progress utility
├── logs/                         # Log files directory
│   ├── frontmatter_progress.json
│   └── frontmatter_changes.log
├── config.local.py               # Local configuration (not in git)
└── README.md                     # This file
```

### Configuration for Multiple Computers

**IMPORTANT**: Different computers may have different paths to your Obsidian vault.

#### Recommended Approach: Local Configuration File

1. Create a `config.local.py` file (add to `.gitignore`):

```python
# config.local.py - DO NOT COMMIT THIS FILE
# Each computer should have its own version

# Obsidian vault path
VAULT_PATH = r"C:\Obsidian\Second Brain"  # Adjust for your machine

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral:7b"  # Adjust based on what you have installed

# Log directory (relative to script location is better)
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
PROGRESS_LOG = os.path.join(LOG_DIR, "frontmatter_progress.json")
DETAILED_LOG = os.path.join(LOG_DIR, "frontmatter_changes.log")
```

2. Update `.gitignore`:
```
# Local configuration - each machine has its own
config.local.py

# Optional: ignore log files if they get too large
logs/frontmatter_changes.log
```

3. Modify scripts to import from config:

At the top of `setFronts_fixed.py`, replace the configuration section with:
```python
try:
    from config_local import *
except ImportError:
    # Fallback defaults if config_local doesn't exist
    VAULT_PATH = r"C:\Obsidian\Second Brain"
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "mistral:7b"
    import os
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(SCRIPT_DIR, "logs")
    PROGRESS_LOG = os.path.join(LOG_DIR, "frontmatter_progress.json")
    DETAILED_LOG = os.path.join(LOG_DIR, "frontmatter_changes.log")
```

#### Example Configurations for Your Setup

**Desktop (32GB RAM, GPU):**
```python
# config.local.py
VAULT_PATH = r"K:\Obsidian Vaults\Second Brain"
OLLAMA_MODEL = "gemma3:12b"  # Use larger model
```

**AI Server (N150, 16GB RAM, Always-On):**
```python
# config.local.py
VAULT_PATH = r"C:\Obsidian\Second Brain"
OLLAMA_MODEL = "mistral:7b"  # Smaller, efficient model
```

**Other PCs:**
```python
# config.local.py
VAULT_PATH = r"C:\Obsidian\Second Brain"
OLLAMA_MODEL = "llama2:7b"
```

## Usage Guide

### Phase 1: Adding Frontmatter Structure

1. **Configure folders to process** in `front_01_Nov_fixed.py`:
   ```python
   NOTES_DIR_NAME = r"Notes\Cara"  # Or your folder
   ```

2. **Test with dry run**:
   ```bash
   python front_01_Nov_fixed.py
   ```
   Review the output to see what would be changed.

3. **Run live**:
   Set `DRY_RUN = False` in the script and run again.

4. **Verify**:
   Check a few notes in Obsidian to ensure frontmatter was added correctly.

### Phase 2: Populating Values with AI

1. **Ensure Ollama is running**:
   ```bash
   ollama list  # Check available models
   ollama run mistral:7b  # Test the model (Ctrl+D to exit)
   ```

2. **Configure folders** in `setFronts_fixed.py`:
   ```python
   FOLDERS_TO_PROCESS = [
       r"Notes\AANext",
       r"Notes\Local AI"
   ]
   ```

3. **Test with dry run first**:
   ```python
   DRY_RUN = True
   ```
   ```bash
   python setFronts_fixed.py
   ```

4. **Review suggestions** in the log:
   ```bash
   type logs\frontmatter_changes.log  # Windows
   cat logs/frontmatter_changes.log   # Linux/Mac
   ```

5. **Run live mode**:
   ```python
   DRY_RUN = False
   ```
   ```bash
   python setFronts_fixed.py
   ```

6. **Monitor progress**:
   - Check console output
   - View `logs/frontmatter_progress.json`
   - Review `logs/frontmatter_changes.log`

7. **Resume if interrupted**:
   Just run the script again - it picks up where it left off!

### Managing Progress

```bash
python progress_manager.py
```

Menu options:
1. **Show current status** - See what's been done
2. **Clear dry run list** - Retest files in dry run mode
3. **Clear live list** - Reprocess files in live mode
4. **Clear error list** - Retry files that had errors
5. **Reset all progress** - Start completely fresh
6. **Exit**

## Frontmatter Structure (31 Parameters)

The scripts maintain this standardized structure:

```yaml
---
# Core Metadata (6)
created: 2025-11-01
modified: 2025-11-01
status: in-progress
migration_date: 2025-11-01
reviewed: false
needs_attention: false

# Classification (4)
project: Cara Robot
category: Technical
topics: [AI, Robotics, Raspberry Pi]
tags: [raspberrypi, ollama, docker]

# Note Characteristics (2)
note_type: documentation
source: research

# People (2)
person: 
collaborators: []

# Technology (3)
technology_stack: [Python, Docker, MCP]
tools_used: [Ollama, Obsidian]
ai_model: mistral:7b

# Location (2)
location: 
region: 

# Historical (2)
historical_period: 
historical_context: 

# Health (2)
health_category: 
adhd_relevant: false

# External (2)
url: 
external_id: 

# Task Management (3)
priority: 
actionable: false
due_date: 

# Financial (1)
financial_category: 

# Flexible (2)
metadata: 
notes: 
---
```

## Workflow for Multiple Machines

### Scenario: Start on Desktop, Continue on AI Server

**On Desktop:**
1. Run Phase 2 on some folders
2. Commit and push:
   ```bash
   git add logs/frontmatter_progress.json
   git commit -m "Progress: Completed Local AI folder"
   git push
   ```

**On AI Server:**
1. Pull latest:
   ```bash
   git pull
   ```
2. Update `config.local.py` with server-specific paths
3. Continue processing:
   ```bash
   python setFronts_fixed.py
   ```
4. Push progress periodically:
   ```bash
   git add logs/frontmatter_progress.json
   git commit -m "Progress: 200/473 files in AANext"
   git push
   ```

### Best Practices for Multi-Machine Use

1. **Always pull before running** - Get latest progress
2. **Don't run on multiple machines simultaneously** - Progress conflicts
3. **Push progress regularly** - Every 50-100 files or daily
4. **Keep config.local.py machine-specific** - Don't commit it
5. **Monitor logs** - Check for errors or issues

## Troubleshooting

### "All files already processed!" but I want to reprocess

Use the progress manager:
```bash
python progress_manager.py
# Choose option 2 (dry run) or 3 (live)
```

### Ollama connection failed

1. Check Ollama is running: `ollama list`
2. Verify URL in config: `http://localhost:11434/api/generate`
3. Test model: `ollama run mistral:7b`

### Different vault paths on different machines

Create a `config.local.py` file on each machine (see Configuration section above).

### Script crashes mid-run

No problem! Just run it again - progress is saved every 10 files (BATCH_SIZE).

### AI suggestions are poor quality

Try a different model:
- Larger models: `gemma3:12b`, `mistral:latest`
- Smaller/faster: `llama2:7b`, `phi-2`
- Adjust temperature in script (lower = more consistent)

### Path errors with logs

Ensure the `logs/` directory exists:
```bash
mkdir logs
```

Or use relative paths in your config:
```python
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
```

## Performance Notes

### Model Recommendations by Hardware

| Hardware | Recommended Model | Speed | Quality |
|----------|------------------|-------|---------|
| 32GB+ RAM, GPU | gemma3:12b, mistral:latest | Fast | Excellent |
| 16GB RAM (AI Server) | mistral:7b, llama2:7b | Moderate | Good |
| 8GB RAM | phi-2, tinyllama | Fast | Acceptable |

### Processing Times (Approximate)

- **Phase 1** (Structure): ~1-2 seconds per file
- **Phase 2** (AI Analysis):
  - Large models (12B): ~5-10 seconds per file
  - Medium models (7B): ~3-5 seconds per file
  - Small models (3B): ~1-2 seconds per file

For 400 files with a 7B model: ~20-30 minutes
Perfect for running overnight on the AI server!

## Advanced Configuration

### Adjusting AI Prompt

Edit the `_build_analysis_prompt` method in `setFronts_fixed.py` to:
- Add more categories
- Change field options
- Adjust instructions for better results

### Custom Frontmatter Fields

Edit `FRONTMATTER_TEMPLATE` dictionary in both scripts to:
- Add new fields
- Remove unwanted fields
- Change default values

### Batch Size

Adjust how often progress is saved:
```python
BATCH_SIZE = 5   # Save every 5 files (more frequent)
BATCH_SIZE = 20  # Save every 20 files (less I/O)
```

## Contributing

This is a personal project, but suggestions welcome!

## License

Personal use project for Obsidian knowledge management.

## Version History

- **1.1** - Fixed dry run/live mode tracking (November 2025)
- **1.0** - Initial release with three scripts (November 2025)

## Acknowledgments

- Built for use with [Obsidian](https://obsidian.md)
- Uses [Ollama](https://ollama.ai) for local AI analysis
- Created as part of a "second brain" knowledge management system
- Developed with assistance from Claude (Anthropic)

---

**Author**: David (Whitchurch, Shropshire, England)  
**Purpose**: Personal knowledge management and cognitive support  
**Infrastructure**: Tailscale-connected network with synced Obsidian vault across multiple devices
