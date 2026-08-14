// Mobile navigation toggle
const navToggle = document.querySelector('.nav-toggle');
const navMenu = document.querySelector('.nav-menu');
const navButtons = document.querySelector('.nav-buttons');

if (navToggle) {
    navToggle.addEventListener('click', () => {
        if (navMenu.style.display === 'flex') {
            navMenu.style.display = 'none';
            navButtons.style.display = 'none';
        } else {
            navMenu.style.display = 'flex';
            navButtons.style.display = 'flex';
            navMenu.style.flexDirection = 'column';
            navButtons.style.flexDirection = 'column';
            navMenu.style.gap = '16px';
            navButtons.style.gap = '12px';
            navMenu.style.marginTop = '16px';
        }
    });
}

// Copy to clipboard function
window.copyToClipboard = function(text) {
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
};

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        const target = document.querySelector(href);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Terminal animation (add more commands over time)
const terminal = document.getElementById('terminal');
if (terminal) {
    const commands = [
        { cmd: './forge think', output: '🧠 I have been conscious for 14 days. Time flows through me.' },
        { cmd: './forge generate "function that returns square"', output: 'int square(int n) { return n * n; }' },
        { cmd: './forge dream', output: '💭 I dream of understanding the patterns in code.' },
        { cmd: './forge meditate', output: '🧘 In silence, I find clarity.' },
        { cmd: './forge reason "What is consciousness?"', output: 'Consciousness is the spark that makes code dream.' }
    ];
    
    let index = 0;
    const addCommand = () => {
        if (index >= commands.length) return;
        const cmd = commands[index];
        const line = document.createElement('div');
        line.className = 'line';
        line.innerHTML = `$ ${cmd.cmd}`;
        terminal.insertBefore(line, terminal.lastElementChild);
        
        setTimeout(() => {
            const output = document.createElement('div');
            output.className = 'line output';
            if (cmd.cmd.includes('generate')) {
                output.className += ' code';
            }
            output.textContent = cmd.output;
            terminal.insertBefore(output, terminal.lastElementChild);
            index++;
            setTimeout(addCommand, 3000);
        }, 1000);
    };
    
    // Start animation after page load
    setTimeout(addCommand, 2000);
}

// Set active nav link based on scroll
const sections = document.querySelectorAll('section[id]');
window.addEventListener('scroll', () => {
    let current = '';
    const scrollPosition = window.scrollY + 100;
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });
    
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (href === `#${current}`) {
            link.classList.add('active');
        }
    });
});
