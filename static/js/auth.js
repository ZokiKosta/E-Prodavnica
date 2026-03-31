(function () {
    /* ── Eye toggle ── */
    const pwInput   = document.getElementById('passwordInput');
    const toggleBtn = document.getElementById('togglePw');
    const eyeOpen   = document.getElementById('eyeOpen');
    const eyeClosed = document.getElementById('eyeClosed');

    if (toggleBtn && pwInput) {
        toggleBtn.addEventListener('click', function () {
            const hidden = pwInput.type === 'password';
            pwInput.type = hidden ? 'text' : 'password';
            eyeOpen.classList.toggle('hidden', hidden);
            eyeClosed.classList.toggle('hidden', !hidden);
        });
    }

    /* ── Strength meter (register only) ── */
    const fill  = document.getElementById('strengthFill');
    const label = document.getElementById('strengthLabel');
    if (!fill || !pwInput) return;

    function scorePassword(pw) {
        if (!pw) return 0;
        let s = 0;
        if (pw.length >= 8)          s++;
        if (pw.length >= 12)         s++;
        if (/[A-Z]/.test(pw))        s++;
        if (/[a-z]/.test(pw))        s++;
        if (/[0-9]/.test(pw))        s++;
        if (/[^A-Za-z0-9]/.test(pw)) s++;
        return s;
    }

    const grades = [
        { min: 0, max: 1, text: 'Weak',   color: '#e74c3c', pct: '22%'  },
        { min: 2, max: 3, text: 'Fair',   color: '#e67e22', pct: '50%'  },
        { min: 4, max: 4, text: 'Good',   color: '#f1c40f', pct: '72%'  },
        { min: 5, max: 6, text: 'Strong', color: '#2ecc71', pct: '100%' },
    ];

    pwInput.addEventListener('input', function () {
        const pw    = pwInput.value;
        const score = scorePassword(pw);

        if (!pw) {
            fill.style.width           = '0%';
            fill.style.backgroundColor = 'transparent';
            label.textContent          = '—';
            label.style.color          = '#fff';
            return;
        }

        const g = grades.find(g => score >= g.min && score <= g.max)
                  || grades[grades.length - 1];

        fill.style.width           = g.pct;
        fill.style.backgroundColor = g.color;
        label.textContent          = g.text;
        label.style.color          = g.color;
    });
})();