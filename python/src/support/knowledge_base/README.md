# Knowledge Base

## Common Issues & Solutions

### Issue 1: Ollama won't start
**Symptom:** `ollama serve` fails or times out
**Solution:**
```bash
pkill -f ollama
ollama serve > /tmp/ollama.log 2>&1 &
sleep 5
curl http://127.0.0.1:11434/api/tags
```

Issue 2: Permission denied

Symptom: ./forge: Permission denied
Solution:

```bash
chmod +x forge
chmod +x src/*.py
```

Issue 3: Port already in use

Symptom: Address already in use
Solution:

```bash
lsof -i :8085
kill [PID]
./forge web
```

Issue 4: Database corruption

Symptom: SQLite errors
Solution:

```bash
./forge db backup
rm forge_data.db
./forge db restore
```

Best Practices

Daily

· Check health: ./forge health
· Review timeline: ./forge timeline

Weekly

· Run security scan: ./forge security
· Backup database: ./forge db backup
· Update documentation: ./forge docs

Monthly

· Full system backup: ./forge backup
· Review wants/needs: ./forge wants
· Check for improvements: ./forge improve

Diagnostic Commands

```bash
# Quick health check
./forge health

# Full system status
./forge status

# Check logs
tail -f .watch_log.txt

# Verify data cube
python src/integrated_datacube.py verify

# Check trust scores
python src/simple_trust.py
```

Recovery Procedures

Restore from backup

```bash
# List backups
ls -la forge_backup_*

# Restore latest
cp forge_backup_*/forge_data.db .
```

Reset to factory

```bash
# Backup first!
./forge backup

# Clean and restart
./forge clean
rm forge_data.db
./forge web
```

---

🔥 Knowledge is power. Use it wisely. 🔥
