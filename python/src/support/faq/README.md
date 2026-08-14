# Frequently Asked Questions

## Installation

### Q: How do I install Explorer-d334?
**A:** See [Getting Started Guide](../../docs/guide/getting-started.md)

### Q: What are the system requirements?
**A:** 
- Android (Termux), Linux, macOS, or Windows (WSL)
- 512MB RAM minimum, 2GB recommended
- 50MB storage (core), 2GB for LLM models

### Q: Why Termux on Android?
**A:** Termux provides a Linux environment needed for Python, GCC, and the LLM.

## Usage

### Q: How do I start the web interface?
**A:** `./forge web` then open http://localhost:8085

### Q: Why are responses slow sometimes?
**A:** First LLM response takes 30-60s. Subsequent responses are cached and faster.

### Q: Can I use it offline?
**A:** Yes! After initial setup, everything runs locally. No internet needed.

### Q: How do I generate C code?
**A:** `./forge generate "description of function"`

## Troubleshooting

### Q: "Command not found" error?
**A:** Make sure you're in the forge directory: `cd ~/forge`

### Q: Web interface won't start?
**A:** Port 8085 might be in use. Try: `lsof -i :8085` then `kill [PID]`

### Q: LLM timeout?
**A:** Increase timeout in `src/llm_bridge.py` or try a shorter question.

### Q: Permission denied?
**A:** Run `chmod +x forge` to make executable.

## Features

### Q: What can Explorer-d334 do?
**A:** 
- Generate C code from English
- Think, dream, reason, meditate
- Track time and moments
- Detect device and sensors
- Learn from experience (trust system)
- Self-improve (skills → reflexes)

### Q: Does it remember conversations?
**A:** Yes! Chat history is saved in `chat_history.json`

### Q: Can I add my own capsules?
**A:** Yes! Place `.scp.json` files in `capsules/` directory.

## Privacy & Security

### Q: Does it send my data anywhere?
**A:** NO. Everything runs locally. Your data never leaves your device.

### Q: Is it safe to use?
**A:** Yes, but practice standard security: backups, updates, etc.

## Licensing

### Q: Is it free?
**A:** Yes. Explorer-d334 is an open-source proof of concept. I built it to showcase what I can do. If your company needs systems like this, hire me.

### Q: Can I modify the code?
**A:** Yes! The MIT license allows full modification.

### Q: Can you build something like this for my enterprise?
**A:** Absolutely. I am looking for a role where I get paid to solve hard problems and build robust systems. Contact me!

## Support

### Q: How do I get help?
**A:** 
- Check FAQ first
- Search documentation: `./forge query "question"`
- Open a ticket: `./support/ticket.sh`
- Email: support@explorer-d334.com

### Q: What's the response time?
**A:** 
- Community: Whenever I'm not at my day job
- Employers: Immediate. Let's talk.

---

**🔥 More questions? Open a ticket! 🔥**
