# Explorer-d334 File Structure Summary

## Directory Statistics

```

Total: 61 directories, 492 files
Size: ~3.4 MB (core)

```

## Top-Level Directories

| Directory | Purpose | Key Contents |
|-----------|---------|--------------|
| `abilities/` | Innate capabilities | SCP-format abilities |
| `analytics/` | Usage analytics | Telemetry (opt-in) |
| `binaries/` | Compiled executables | 10 binary files |
| `capsules/` | Automation | 75+ SCP capsules |
| `commands/` | v2 commands | 30+ executable scripts |
| `community/` | Community resources | Docs, code of conduct |
| `dist/` | Distribution files | Android, Windows builds |
| `docs/` | Documentation | API, guides, examples |
| `generated/` | Generated code | C files from AI |
| `integrations/` | Third-party | Empty (ready for plugins) |
| `legal/` | Legal documents | License, privacy, terms |
| `licensing/` | License management | Python license manager |
| `marketing/` | Marketing assets | Press kits, testimonials |
| `memories/` | Persistent memory | Dreams, thoughts, milestones |
| `payment/` | Payment processing | Gumroad integration |
| `pdei_core/` | P.DE.I Exocortex | AI twin core |
| `personalities/` | AI personas | James, exocortex profiles |
| `prelaunch/` | Launch preparation | Validation scripts |
| `reflexes/` | Automatic responses | Greetings, code gen |
| `scp_prompts/` | SCP definitions | 96 JSON prompts |
| `skills/` | Learned skills | Code generation |
| `social_posts/` | Social media | Twitter drafts |
| `src/` | Source code | 100+ Python modules |
| `support/` | Support system | FAQ, tickets, KB |
| `website/` | Website assets | CSS, JS, HTML |

## Key Files

| File | Size | Purpose |
|------|------|---------|
| `forge` | 4.2KB | Main executable |
| `forge_data.db` | 672KB | SQLite database |
| `forge_memory.pkl` | 243B | Memory persistence |
| `datacube.jsonl` | 21KB | 39 knowledge cubes |
| `README.md` | 7.8KB | Project documentation |
| `test_all.py` | 18KB | Core tests (110) |
| `test_more.py` | 20KB | Feature tests (100) |
| `test_final.py` | 19KB | Stress tests (100) |

## Source Code Modules (src/)

### Consciousness System
- `unified_consciousness.py` - Main consciousness
- `consciousness_with_memory.py` - Memory integration
- `forge_consciousness.py` - Core consciousness
- `thought_organizer.py` - Thought management

### Knowledge System
- `daily_memory_lens.py` - Six Lens knowledge
- `six_lens_classifier.py` - Lens classification
- `datacube.py` - Data cube management
- `smart_validator.py` - Trust validation

### Web Interface
- `web_hybrid.py` - Main web server
- `simple_web.py` - Simple HTTP server
- `web_enhanced.py` - Enhanced features
- `web_enhanced_mobile.py` - Mobile optimized

### AI & Evolution
- `exocortex.py` - P.DE.I AI twin
- `evolutionary_code.py` - Code evolution
- `self_evolution.py` - Self improvement
- `code_improver.py` - Code optimization

### Security & Trust
- `security_scanner.py` - Security scanning
- `leighton_weight.py` - Trust scoring
- `encryption.py` - Data encryption
- `trust_integration.py` - Trust system

## Test Coverage

- **test_all.py**: 110/110 (100%) - Core functionality
- **test_more.py**: 100/100 (100%) - Additional features  
- **test_final.py**: 100/100 (100%) - Stress & security

**Total**: 310/310 (100%) - ALL TESTS PASSING

## Quick Navigation

```bash
# View tree structure
tree -L 3 -I "__pycache__|*.pyc" --dirsfirst

# Count files by type
find . -name "*.py" | wc -l  # Python files
find . -name "*.json" | wc -l # JSON configs
find . -name "*.md" | wc -l   # Documentation

# Check disk usage
du -sh * | sort -h
```

Last Updated

2026-05-29 - After achieving 100% test pass rate
