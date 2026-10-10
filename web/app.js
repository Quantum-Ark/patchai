/**
 * PatchPilot AI — Interactive Web Engine & Motion Graphics Controller
 * Handles particle mesh canvas, magnetic cursor, live state machine simulator,
 * diff inspector, and dynamic ROI calculator.
 */

document.addEventListener('DOMContentLoaded', () => {
  initParticleCanvas();
  initCustomCursor();
  initSimulator();
  initDiffInspector();
  initRoiCalculator();
  initQuickstartCopy();
});

/* ==========================================================================
   1. Interactive Particle Background Canvas
   ========================================================================== */
function initParticleCanvas() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const mouse = { x: -1000, y: -1000, radius: 140 };

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
  });

  const particleCount = Math.min(Math.floor((width * height) / 16000), 75);
  const particles = [];

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.7;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.radius = Math.random() * 1.8 + 1;
      this.color = Math.random() > 0.4 ? 'rgba(0, 245, 212, 0.6)' : 'rgba(139, 92, 246, 0.5)';
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;

      if (this.x < 0 || this.x > width) this.vx *= -1;
      if (this.y < 0 || this.y > height) this.vy *= -1;

      // Mouse repulsion
      const dx = mouse.x - this.x;
      const dy = mouse.y - this.y;
      const dist = Math.hypot(dx, dy);
      if (dist < mouse.radius) {
        const force = (mouse.radius - dist) / mouse.radius;
        this.x -= (dx / dist) * force * 3;
        this.y -= (dy / dist) * force * 3;
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.fill();
    }
  }

  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle());
  }

  function render() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();

      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.hypot(dx, dy);

        if (dist < 110) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 245, 212, ${0.18 * (1 - dist / 110)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }
    requestAnimationFrame(render);
  }

  render();
}

/* ==========================================================================
   2. Custom Magnetic Trailing Cursor
   ========================================================================== */
function initCustomCursor() {
  const dot = document.getElementById('cursor-dot');
  const glow = document.getElementById('cursor-glow');
  if (!dot || !glow) return;

  let mouseX = -100;
  let mouseY = -100;
  let glowX = -100;
  let glowY = -100;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) translate(-50%, -50%)`;
  });

  function animateCursorGlow() {
    glowX += (mouseX - glowX) * 0.16;
    glowY += (mouseY - glowY) * 0.16;
    glow.style.transform = `translate3d(${glowX}px, ${glowY}px, 0) translate(-50%, -50%)`;
    requestAnimationFrame(animateCursorGlow);
  }
  animateCursorGlow();

  const interactiveElements = document.querySelectorAll('a, button, input, .case-tab, .diff-tab, .metric-card, .pipeline-card, .integration-card');
  interactiveElements.forEach((el) => {
    el.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
    el.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
  });
}

/* ==========================================================================
   3. Interactive Live Agent Simulator (Verified Recovery in Action)
   ========================================================================== */
const SIMULATION_DATA = {
  case3: {
    title: 'benchmarks/case_3_regression_recovery/pricing.py',
    attemptLabel: '2 / 3 (Recovered)',
    traceId: 'fa7426780f2d4838b90a61cfb8813ecb',
    logs: [
      { step: 'inspecting', delay: 200, type: 'info', text: 'INITIATING REPAIR: Case 3 (Pricing Engine Regression)' },
      { step: 'inspecting', delay: 450, type: 'trace', text: 'Worktree cloned at /tmp/patchpilot_sandbox_916d. Git SHA: e4f892a' },
      { step: 'reproducing', delay: 850, type: 'warn', text: 'Running reproduction command: pytest test_pricing.py -k test_negative' },
      { step: 'reproducing', delay: 1250, type: 'error', text: 'FAILED (Exit Code 1): ValueError: Negative volume input unhandled in compute_total' },
      { step: 'reproducing', delay: 1450, type: 'success', text: 'BASELINE CONFIRMED: Defect successfully reproduced in isolated sandbox' },
      { step: 'patching', delay: 1800, type: 'info', text: 'ATTEMPT #1: Generating surgical AST edit via configured LLM provider' },
      { step: 'patching', delay: 2200, type: 'trace', text: 'Patch applied: clamped volume to 0 via simple ternary' },
      { step: 'testing', delay: 2600, type: 'info', text: 'Executing test acceptance suite...' },
      { step: 'testing', delay: 2900, type: 'success', text: 'Acceptance test test_negative_input: PASSED' },
      { step: 'testing', delay: 3200, type: 'warn', text: 'Executing comprehensive regression test suite...' },
      { step: 'recovering', delay: 3600, type: 'error', text: 'REGRESSION DETECTED: test_vip_discount failed! Volume clamp broke multiplier tier!' },
      { step: 'recovering', delay: 4000, type: 'warn', text: 'ROLLBACK TRIGGERED: Restoring clean baseline Git state (git reset --hard e4f892a)' },
      { step: 'recovering', delay: 4300, type: 'trace', text: 'Updating hypothesis: Must preserve volume tier before applying floor logic' },
      { step: 'patching', delay: 4700, type: 'info', text: 'ATTEMPT #2: Applying adaptive precision patch...' },
      { step: 'verifying', delay: 5100, type: 'info', text: 'Re-verifying dual test suites on Attempt #2...' },
      { step: 'verifying', delay: 5400, type: 'success', text: 'Acceptance Suite: 100% PASSED (Exit Code 0)' },
      { step: 'verifying', delay: 5700, type: 'success', text: 'Regression Suite: 100% PASSED (3/3 tests green)' },
      { step: 'completed', delay: 6100, type: 'success', text: 'REPAIR COMPLETE & VERIFIED. Trace sent to Neatlogs. PR #42 ready.' }
    ]
  },
  case1: {
    title: 'benchmarks/case_1_syntax_error/calculator.py',
    attemptLabel: '1 / 3 (First-Pass Fix)',
    traceId: 'bc83109a24414ef2898951dbcd06a121',
    logs: [
      { step: 'inspecting', delay: 200, type: 'info', text: 'INITIATING REPAIR: Case 1 (Division by Zero)' },
      { step: 'inspecting', delay: 450, type: 'trace', text: 'AST parse tree mapped. File: calculator.py' },
      { step: 'reproducing', delay: 850, type: 'warn', text: 'Running reproduction command: pytest test_calc.py::test_zero' },
      { step: 'reproducing', delay: 1250, type: 'error', text: 'FAILED (Exit Code 1): ZeroDivisionError: division by zero' },
      { step: 'patching', delay: 1700, type: 'info', text: 'ATTEMPT #1: Generating ZeroDivision guard clause' },
      { step: 'testing', delay: 2100, type: 'info', text: 'Running test validation suite...' },
      { step: 'verifying', delay: 2500, type: 'success', text: 'Acceptance: PASSED | Regressions: PASSED' },
      { step: 'completed', delay: 2900, type: 'success', text: 'VERIFIED ON ATTEMPT 1. Clean fix committed.' }
    ]
  },
  case2: {
    title: 'benchmarks/case_2_runtime_exception/pagination.py',
    attemptLabel: '1 / 3 (Boundary Resolved)',
    traceId: '89ff102b37ce436db08119df99824f11',
    logs: [
      { step: 'inspecting', delay: 200, type: 'info', text: 'INITIATING REPAIR: Case 2 (Empty Pagination IndexError)' },
      { step: 'reproducing', delay: 700, type: 'error', text: 'FAILED (Exit Code 1): IndexError: list index out of range on empty page query' },
      { step: 'patching', delay: 1200, type: 'info', text: 'ATTEMPT #1: Adding bounds check on items slice' },
      { step: 'verifying', delay: 1700, type: 'success', text: 'Acceptance & Regression suites 100% green' },
      { step: 'completed', delay: 2200, type: 'success', text: 'BOUNDARY RESOLVED. Verified and traced.' }
    ]
  }
};

let currentSimTimeout = null;

function initSimulator() {
  const terminalOutput = document.getElementById('terminal-output');
  const replayBtn = document.getElementById('play-sim-btn');
  const tabs = document.querySelectorAll('.case-tab');
  const caseTitle = document.getElementById('terminal-case-title');
  const telAttempt = document.getElementById('tel-attempt');
  const telTrace = document.getElementById('tel-trace');

  let activeCase = 'case3';

  function runSimulation(caseKey) {
    if (currentSimTimeout) {
      clearTimeout(currentSimTimeout);
    }

    const data = SIMULATION_DATA[caseKey];
    if (!data) return;

    if (caseTitle) caseTitle.textContent = data.title;
    if (telAttempt) telAttempt.textContent = data.attemptLabel;
    if (telTrace) telTrace.textContent = data.traceId;

    terminalOutput.innerHTML = '';
    resetStepper();

    data.logs.forEach((log) => {
      setTimeout(() => {
        appendLog(log.type, log.text);
        updateStepper(log.step);
      }, log.delay);
    });
  }

  function appendLog(type, text) {
    const line = document.createElement('div');
    line.className = 'log-line';

    const time = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const prefixMap = {
      info: '[INFO]',
      trace: '[TRACE]',
      warn: '[WARN]',
      error: '[FAIL]',
      success: '[PASS]'
    };

    line.innerHTML = `
      <span class="log-time">${time}</span>
      <span class="log-prefix ${type}">${prefixMap[type] || '[LOG]'}</span>
      <span class="log-text">${escapeHtml(text)}</span>
    `;

    terminalOutput.appendChild(line);
    terminalOutput.scrollTop = terminalOutput.scrollHeight;
  }

  function resetStepper() {
    const nodes = document.querySelectorAll('.step-node');
    nodes.forEach((n) => {
      n.classList.remove('active', 'recovering', 'completed-step');
    });
    const lines = document.querySelectorAll('.step-line');
    lines.forEach((l) => l.classList.remove('passed'));
  }

  function updateStepper(step) {
    const stepMap = {
      inspecting: 'step-inspecting',
      reproducing: 'step-reproducing',
      patching: 'step-patching',
      testing: 'step-testing',
      recovering: 'step-recovering',
      verifying: 'step-verifying',
      completed: 'step-completed'
    };

    const targetId = stepMap[step];
    if (!targetId) return;

    const node = document.getElementById(targetId);
    if (!node) return;

    if (step === 'recovering') {
      node.classList.add('recovering');
    } else if (step === 'completed') {
      node.classList.add('completed-step');
    } else {
      node.classList.add('active');
    }
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      activeCase = tab.dataset.case;
      runSimulation(activeCase);
    });
  });

  if (replayBtn) {
    replayBtn.addEventListener('click', () => runSimulation(activeCase));
  }

  // Start with case 3 automatically
  runSimulation('case3');
}

/* ==========================================================================
   4. Interactive Diff Inspector
   ========================================================================== */
const DIFF_DATA = {
  attempt2: {
    status: 'Passing — Precision Verified Patch',
    lines: [
      { type: 'comment', num: '14', content: '# Attempt #2: Precision Patch (Verified Dual-Suite)' },
      { type: 'ctx', num: '15', content: 'def compute_total(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del', num: '16', content: '-    if volume < 0: volume = 0  # Naive clamp destroyed discount tier!' },
      { type: 'add', num: '16', content: '+    if volume < 0:' },
      { type: 'add', num: '17', content: '+        raise ValueError("Volume cannot be negative")' },
      { type: 'ctx', num: '18', content: '    multiplier = 0.85 if is_vip else 1.0' },
      { type: 'ctx', num: '19', content: '    return base_price * volume * multiplier' }
    ]
  },
  attempt1: {
    status: 'Failed — Caused VIP Regression',
    lines: [
      { type: 'comment', num: '14', content: '# Attempt #1: Naive Blind Ternary (Triggered Rollback)' },
      { type: 'ctx', num: '15', content: 'def compute_total(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del', num: '16', content: '-    return base_price * volume * (0.85 if is_vip else 1.0)' },
      { type: 'add', num: '16', content: '+    volume = max(0, volume)  # BROKE test_vip_discount!' },
      { type: 'add', num: '17', content: '+    return base_price * volume' }
    ]
  }
};

function initDiffInspector() {
  const viewer = document.getElementById('diff-viewer-content');
  const tab2 = document.getElementById('diff-tab-attempt2');
  const tab1 = document.getElementById('diff-tab-attempt1');
  if (!viewer || !tab2 || !tab1) return;

  function renderDiff(key) {
    const diff = DIFF_DATA[key];
    viewer.innerHTML = '';

    diff.lines.forEach((line) => {
      const lineEl = document.createElement('div');
      lineEl.className = `diff-line ${line.type}`;
      lineEl.innerHTML = `
        <span class="line-num">${line.num}</span>
        <span class="line-code">${escapeHtml(line.content)}</span>
      `;
      viewer.appendChild(lineEl);
    });
  }

  tab2.addEventListener('click', () => {
    tab2.classList.add('active');
    tab1.classList.remove('active');
    renderDiff('attempt2');
  });

  tab1.addEventListener('click', () => {
    tab1.classList.add('active');
    tab2.classList.remove('active');
    renderDiff('attempt1');
  });

  renderDiff('attempt2');
}

/* ==========================================================================
   5. Interactive Financial Economics Calculator (cfo.ai Model)
   ========================================================================== */
function initRoiCalculator() {
  const slider = document.getElementById('defect-slider');
  const sliderDisplay = document.getElementById('slider-display');
  const hoursDisplay = document.getElementById('calc-hours');
  const cogsDisplay = document.getElementById('calc-cogs');
  const savingsDisplay = document.getElementById('calc-savings');

  if (!slider) return;

  function update() {
    const bugs = parseInt(slider.value, 10);
    const hoursSaved = bugs * 3.2; // 3.2 senior engineer hours saved per verified defect
    const cogs = bugs * 0.045; // $0.045 LLM inference tokens per multi-attempt repair
    const grossSavings = hoursSaved * 100; // $100/hr blended engineering rate
    const netSavings = grossSavings - cogs;

    sliderDisplay.textContent = `${bugs} fixes`;
    hoursDisplay.textContent = `${Math.round(hoursSaved)} hrs`;
    cogsDisplay.textContent = `$${cogs.toFixed(2)}`;
    savingsDisplay.textContent = `$${Math.round(netSavings).toLocaleString()}`;
  }

  slider.addEventListener('input', update);
  update();
}

/* ==========================================================================
   6. Quickstart Copy Button
   ========================================================================== */
function initQuickstartCopy() {
  const btn = document.getElementById('copy-quickstart-btn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    const textToCopy = `git clone https://github.com/Quantum-Ark/patchai.git && cd patchai
patchpilot doctor
patchpilot verify-integrations
patchpilot evaluate`;

    navigator.clipboard.writeText(textToCopy).then(() => {
      const originalText = btn.textContent;
      btn.textContent = 'Copied to Clipboard!';
      btn.style.background = 'var(--neon-emerald)';
      btn.style.color = '#000';

      setTimeout(() => {
        btn.textContent = originalText;
        btn.style.background = '';
        btn.style.color = '';
      }, 2200);
    });
  });
}

function escapeHtml(string) {
  const entityMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  return String(string).replace(/[&<>"']/g, (s) => entityMap[s]);
}
