# Quick Reference Guide

## Initial Setup (New Machine)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd <repo-name>

# 2. Run setup
python setup.py

# 3. Verify Ollama
ollama list
ollama pull mistral:7b  # If needed

# 4. Test
python setFronts_fixed.py  # Should run in dry mode
```

## Daily Usage

### Starting Work
```bash
git pull                    # Get latest progress
python setFronts_fixed.py   # Continue processing
```

### Saving Progress
```bash
git add logs/frontmatter_progress.json
git commit -m "Progress: 300/473 files"
git push
```

### Switching Machines
**On Machine A:**
```bash
# Ctrl+C to stop script
git add logs/
git commit -m "Pausing at file 200"
git push
```

**On Machine B:**
```bash
git pull
python setFronts_fixed.py  # Continues from file 200
```

## Quick Commands

### Check Status
```bash
python progress_manager.py
# Choose option 1
```

### Reset Progress (Start Over)
```bash
python progress_manager.py
# Choose option 5
```

### Check Ollama
```bash
ollama list              # Show installed models
ollama ps                # Show running models
ollama run mistral:7b    # Test a model (Ctrl+D to exit)
```

## Configuration Quick Edit

Edit your local paths:
```bash
notepad config.local.py     # Windows
nano config.local.py        # Linux/Mac
```

Change:
- `VAULT_PATH` - Your Obsidian vault location
- `OLLAMA_MODEL` - Which AI model to use
- `FOLDERS_TO_PROCESS` - Which folders to work on

## Troubleshooting

### "Cannot connect to Ollama"
```bash
ollama serve  # Start Ollama if not running
```

### "All files already processed"
```bash
python progress_manager.py
# Option 2: Clear dry run list
# Option 3: Clear live list
```

### Different paths on different machines
Each machine should have its own `config.local.py` (not in git)

### Script stuck/crashed
Just run again - progress auto-saves every 10 files

## File Locations

| File | Purpose | In Git? |
|------|---------|---------|
| `config.local.py` | Your paths/settings | ❌ No |
| `logs/frontmatter_progress.json` | Processing state | ✅ Yes |
| `logs/frontmatter_changes.log` | Detailed log | ❌ No |
| Phase 1/2 scripts | Main programs | ✅ Yes |

## Common Workflows

### First Time Full Process
```bash
# 1. Add structure (Phase 1)
python front_01_Nov_fixed.py  # DRY_RUN = True first
# Review output, then set DRY_RUN = False and run again

# 2. Populate values (Phase 2)
python setFronts_fixed.py     # DRY_RUN = True first
# Review logs/frontmatter_changes.log
# Set DRY_RUN = False and run again
```

### Long Running Process (AI Server)
```bash
# Start it and let it run for days
python setFronts_fixed.py

# Check progress anytime
python progress_manager.py  # Option 1

# View log
tail -f logs/frontmatter_changes.log    # Linux/Mac
Get-Content logs/frontmatter_changes.log -Wait  # PowerShell
```

### Reprocess Files (Change Model)
```bash
# Clear live list to reprocess
python progress_manager.py  # Option 3

# Edit config for new model
notepad config.local.py
# Change OLLAMA_MODEL = "gemma3:12b"

# Reprocess
python setFronts_fixed.py
```

## Model Selection Guide

| Your Hardware | Best Model | Files/Hour |
|---------------|------------|------------|
| 32GB RAM + GPU | gemma3:12b | ~200-300 |
| 16GB RAM | mistral:7b | ~100-150 |
| 8GB RAM | phi-2 | ~200-300 |

## Emergency Stop

**Interrupt safely:**
- Press `Ctrl+C`
- Script saves progress automatically
- Resume by running script again

**Never:**
- Don't kill process/close terminal
- Wait for "Progress saved" message

## Maintenance

### Weekly
```bash
git pull                      # Sync progress
Check logs/ directory size    # Delete old logs if huge
```

### After Completion
```bash
# Backup progress
cp logs/frontmatter_progress.json logs/progress_backup.json

# Optionally reset to process again later
python progress_manager.py  # Option 5
```

---

**Quick Help**: See README.md for full documentation