/**
 * PatchPilot AI — Master Creative Interaction & Motion Engine
 * Features:
 * - "The Repair Current": High-performance technical circuit canvas simulation with cursor displacement
 * - Precision desktop cursor with magnetic pulling and contextual "INSPECT" badge
 * - Interactive Code Diff Showcase (Before / Patch #1 / Patch #2)
 * - Hero Workflow Composition stage lock & preview
 * - Trace Explorer with working copy utilities
 */

document.addEventListener('DOMContentLoaded', () => {
  initRepairCurrentCanvas();
  initPrecisionCursor();
  initRepairWorkflowComposition();
  initDiffShowcase();
  initTraceExplorer();
  initCliCopy();
  initNavScroll();
});

/* ==========================================================================
   1. "The Repair Current" Interactive Technical Canvas Simulation
   ========================================================================== */
function initRepairCurrentCanvas() {
  const canvas = document.getElementById('repair-current-canvas');
  if (!canvas) return;

  // Honor prefers-reduced-motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return;
  }

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = canvas.offsetWidth);
  let height = (canvas.height = canvas.offsetHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = canvas.offsetWidth;
    height = canvas.height = canvas.offsetHeight;
  });

  const mouse = { x: -1000, y: -1000, active: false };

  window.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
    mouse.active = true;
  });

  window.addEventListener('mouseleave', () => {
    mouse.active = false;
  });

  // Grid points with spring displacement
  const cols = 28;
  const rows = 14;
  const grid = [];

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      grid.push({
        baseX: (c / (cols - 1)) * width,
        baseY: (r / (rows - 1)) * height,
        x: (c / (cols - 1)) * width,
        y: (r / (rows - 1)) * height,
        vx: 0,
        vy: 0
      });
    }
  }

  // Diagnostic signal pulses traveling along technical paths toward defect
  const pulses = [];
  const maxPulses = 16;

  class SignalPulse {
    constructor() {
      this.reset();
    }

    reset() {
      this.progress = 0;
      this.speed = 0.004 + Math.random() * 0.006;
      this.startX = Math.random() * width * 0.4;
      this.startY = Math.random() * height;
      this.targetX = width * 0.75;
      this.targetY = height * 0.45;
      this.color = Math.random() > 0.3 ? 'rgba(200, 255, 85, 0.65)' : 'rgba(118, 215, 255, 0.5)';
      this.size = Math.random() * 1.6 + 1.2;
    }

    update() {
      this.progress += this.speed;
      if (this.progress >= 1) {
        this.reset();
      }
    }

    draw() {
      // Curved circuit bezier path
      const cx = this.startX + (this.targetX - this.startX) * 0.5;
      const cy = this.startY;

      const t = this.progress;
      const inv = 1 - t;
      const px = inv * inv * this.startX + 2 * inv * t * cx + t * t * this.targetX;
      const py = inv * inv * this.startY + 2 * inv * t * cy + t * t * this.targetY;

      ctx.beginPath();
      ctx.arc(px, py, this.size, 0, Math.PI * 2);
      ctx.fillStyle = this.color;
      ctx.fill();
    }
  }

  for (let i = 0; i < maxPulses; i++) {
    pulses.push(new SignalPulse());
  }

  // Defect pulse coordinates
  let defectPulseTime = 0;
  let isRunning = true;

  // Pause when out of viewport
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      isRunning = entry.isIntersecting;
      if (isRunning) requestAnimationFrame(render);
    });
  });
  observer.observe(canvas);

  function render() {
    if (!isRunning) return;

    ctx.clearRect(0, 0, width, height);

    // 1. Draw delicate grid with spring displacement
    ctx.fillStyle = 'rgba(37, 43, 53, 0.45)';
    for (let i = 0; i < grid.length; i++) {
      const p = grid[i];

      // Mouse displacement
      if (mouse.active) {
        const dx = mouse.x - p.baseX;
        const dy = mouse.y - p.baseY;
        const dist = Math.hypot(dx, dy);
        if (dist < 120) {
          const force = (120 - dist) / 120;
          p.vx -= (dx / dist) * force * 1.5;
          p.vy -= (dy / dist) * force * 1.5;
        }
      }

      // Spring back to base position
      p.vx += (p.baseX - p.x) * 0.08;
      p.vy += (p.baseY - p.y) * 0.08;
      p.vx *= 0.82;
      p.vy *= 0.82;
      p.x += p.vx;
      p.y += p.vy;

      ctx.fillRect(p.x - 1, p.y - 1, 2, 2);
    }

    // 2. Draw signal pulses traveling toward defect
    for (let i = 0; i < pulses.length; i++) {
      pulses[i].update();
      pulses[i].draw();
    }

    // 3. Defect node pulse indicator
    defectPulseTime += 0.035;
    const defX = width * 0.75;
    const defY = height * 0.45;
    const rad = 6 + Math.sin(defectPulseTime) * 3;

    ctx.beginPath();
    ctx.arc(defX, defY, rad, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(200, 255, 85, 0.5)';
    ctx.lineWidth = 1.2;
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(defX, defY, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#C8FF55';
    ctx.fill();

    requestAnimationFrame(render);
  }

  render();
}

/* ==========================================================================
   2. Desktop Signature Precision Cursor & Magnetic Interactions
   ========================================================================== */
function initPrecisionCursor() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || 
      window.matchMedia('(pointer: coarse)').matches) {
    return;
  }

  const point = document.getElementById('cursor-point');
  const halo = document.getElementById('cursor-halo');
  const badge = document.getElementById('cursor-badge');

  if (!point || !halo) return;

  let mouseX = -100;
  let mouseY = -100;
  let haloX = -100;
  let haloY = -100;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    point.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) translate(-50%, -50%)`;
    if (badge) {
      badge.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0) translate(22px, -50%)`;
    }
  });

  function renderCursor() {
    haloX += (mouseX - haloX) * 0.18;
    haloY += (mouseY - haloY) * 0.18;
    halo.style.transform = `translate3d(${haloX}px, ${haloY}px, 0) translate(-50%, -50%)`;
    requestAnimationFrame(renderCursor);
  }
  renderCursor();

  const interactiveTargets = document.querySelectorAll('a, button, .board-stage, .trace-event-row, .pipeline-card, .diff-view-btn');
  interactiveTargets.forEach((target) => {
    target.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
    target.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
  });

  const magneticButtons = document.querySelectorAll('.magnetic');
  magneticButtons.forEach((btn) => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate3d(${x * 0.18}px, ${y * 0.18}px, 0)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate3d(0, 0, 0)';
    });
  });

  const inspectableStages = document.querySelectorAll('.is-inspectable');
  inspectableStages.forEach((stage) => {
    stage.addEventListener('mouseenter', () => document.body.classList.add('cursor-inspecting'));
    stage.addEventListener('mouseleave', () => document.body.classList.remove('cursor-inspecting'));
  });
}

/* ==========================================================================
   3. Interactive Signature Repair Workflow Composition
   ========================================================================== */
const STAGE_EXPLANATIONS = {
  1: {
    tag: 'STAGE 01 / DEFECT SPECIFICATION',
    status: 'Defect Intake & Scope Isolation',
    text: 'A defect report indicates unhandled negative quantities in calculate_tiered_price. Before proposing any patch, PatchPilot clones a clean disposable worktree to guarantee your active branch remains untouched.'
  },
  2: {
    tag: 'STAGE 02 / REPRODUCTION PROOF',
    status: 'Baseline Failure Execution',
    text: 'PatchPilot executes a targeted reproduction command in an isolated subprocess with scrubbed secrets. It confirms the baseline failure exits with code 1, establishing genuine proof that the bug reproduces.'
  },
  3: {
    tag: 'STAGE 03 / CANDIDATE ATTEMPT & REGRESSION',
    status: 'Regression Detection in Sandbox',
    text: 'Attempt #1 used a naive clamp (max(0, volume)). While the input acceptance test passed, the comprehensive regression suite failed! The naive clamp broke existing VIP tiered discounts. PatchPilot caught this before any merge.'
  },
  4: {
    tag: 'STAGE 04 / FAILURE-DRIVEN RECOVERY',
    status: 'Atomic Git Rollback & Hypothesis Update',
    text: 'PatchPilot instantly triggers an atomic rollback to baseline SHA e4f892a. Zero residue is left. It injects the failure traceback into its context, determining that volume tier calculations must be preserved before bounds guards.'
  },
  5: {
    tag: 'STAGE 05 / PRECISION VERIFICATION',
    status: 'Dual-Suite Acceptance (100% Exit Code 0)',
    text: 'Attempt #2 applies an explicit validation raise. Both the targeted acceptance test AND all regression test cases pass with 100% exit code 0. Telemetry trace 16578e5e is exported to Neatlogs.'
  }
};

function initRepairWorkflowComposition() {
  const stages = document.querySelectorAll('.board-stage');
  const explainerTag = document.getElementById('explainer-tag');
  const explainerStatus = document.getElementById('explainer-status');
  const explainerText = document.getElementById('explainer-text');

  let lockedStage = 4; // Default to recovery

  function updateExplainer(stageNum) {
    const data = STAGE_EXPLANATIONS[stageNum];
    if (!data) return;

    if (explainerTag) explainerTag.textContent = data.tag;
    if (explainerStatus) explainerStatus.textContent = data.status;
    if (explainerText) explainerText.textContent = data.text;
  }

  function setStageActive(stageNum) {
    stages.forEach((s) => {
      const num = parseInt(s.dataset.stage, 10);
      s.classList.toggle('is-locked', num === stageNum);
    });
    updateExplainer(stageNum);
  }

  stages.forEach((stage) => {
    const num = parseInt(stage.dataset.stage, 10);

    stage.addEventListener('mouseenter', () => updateExplainer(num));
    stage.addEventListener('mouseleave', () => updateExplainer(lockedStage));
    stage.addEventListener('click', () => {
      lockedStage = num;
      setStageActive(lockedStage);
    });

    stage.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        lockedStage = num;
        setStageActive(lockedStage);
      }
    });
  });

  setStageActive(lockedStage);
}

/* ==========================================================================
   4. Interactive Code-Diff Showcase (Before / Patch #1 / Patch #2)
   ========================================================================== */
const DIFF_VIEWS = {
  before: {
    stats: 'Baseline Defect (calc_tiered_price unhandled)',
    rows: [
      { type: 'comment', num: '14', text: '# Original baseline code in pricing.py' },
      { type: 'ctx',     num: '15', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del',     num: '16', text: '    return base_price * volume * (0.80 if is_vip else 1.0)  # Defect: negative volume unhandled' }
    ]
  },
  patch1: {
    stats: '+1 -1 lines (Caused VIP Regression)',
    rows: [
      { type: 'comment', num: '14', text: '# Attempt #1: Naive Blind Clamp (Failed regression suite)' },
      { type: 'ctx',     num: '15', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del',     num: '16', text: '-    return base_price * volume * (0.80 if is_vip else 1.0)' },
      { type: 'add',     num: '16', text: '+    return base_price * max(0, volume)  # BROKE VIP DISCOUNT RULE (80.0 != 100.0)' }
    ]
  },
  patch2: {
    stats: '+3 -1 lines (Verified Precision Fix)',
    rows: [
      { type: 'comment', num: '14', text: '# Attempt #2: Precision Adaptive Patch (Verified 100% exit code 0)' },
      { type: 'ctx',     num: '15', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del',     num: '16', text: '-    if volume < 0: volume = 0  # Replaced naive volume clamp' },
      { type: 'add',     num: '16', text: '+    if volume < 0:' },
      { type: 'add',     num: '17', text: '+        raise ValueError("Volume must be non-negative")' },
      { type: 'ctx',     num: '18', text: '    multiplier = 0.80 if is_vip else 1.0' },
      { type: 'ctx',     num: '19', text: '    return base_price * volume * multiplier' }
    ]
  }
};

function initDiffShowcase() {
  const screen = document.getElementById('diff-screen');
  const tabs = document.querySelectorAll('.diff-view-btn');
  const statsLabel = document.getElementById('diff-stats-label');

  if (!screen) return;

  function renderView(viewKey) {
    const data = DIFF_VIEWS[viewKey];
    if (!data) return;

    if (statsLabel) statsLabel.textContent = data.stats;
    screen.innerHTML = '';

    data.rows.forEach((row) => {
      const lineEl = document.createElement('div');
      lineEl.className = `diff-row ${row.type}`;
      lineEl.innerHTML = `
        <span class="diff-num">${row.num}</span>
        <span class="diff-text">${escapeHtml(row.text)}</span>
      `;
      screen.appendChild(lineEl);
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener('click', () => {
      tabs.forEach((t) => t.classList.remove('active'));
      tab.classList.add('active');
      renderView(tab.dataset.view);
    });
  });

  renderView('patch2');
}

/* ==========================================================================
   5. Interactive Trace Explorer
   ========================================================================== */
const TRACE_EVENTS_DATA = [
  {
    type: 'INTAKE & BASELINE DISCOVERY',
    time: '2026-10-10T19:48:50.412Z',
    trace: '16578e5ee3829a5a6f053c7cbeabd88f',
    cmd: 'git clone --no-hardlinks . .worktrees/patchpilot_sandbox_916d',
    log: 'Cloned clean worktree at commit e4f892a. Mapped abstract syntax tree for pricing.py. Discovered 1 candidate defect and 3 associated regression test cases.'
  },
  {
    type: 'REPRODUCTION EXECUTION',
    time: '2026-10-10T19:48:51.842Z',
    trace: '16578e5ee3829a5a6f053c7cbeabd88f',
    cmd: 'pytest tests/test_pricing.py -k test_negative_input',
    log: 'FAILED: ValueError unhandled in calculate_tiered_price.\nExit code: 1\nDuration: 0.42s\nDefect confirmed present in clean repository.'
  },
  {
    type: 'ATTEMPT #1 TEST REGRESSION',
    time: '2026-10-10T19:48:53.119Z',
    trace: '16578e5ee3829a5a6f053c7cbeabd88f',
    cmd: 'pytest tests/test_pricing.py',
    log: 'PASSED: test_negative_input\nFAILED: test_vip_discount (AssertionError: 80.0 != 100.0)\nRegression detected: Naive volume clamp violated discount multiplier!'
  },
  {
    type: 'ATOMIC BASELINE ROLLBACK',
    time: '2026-10-10T19:48:54.004Z',
    trace: '16578e5ee3829a5a6f053c7cbeabd88f',
    cmd: 'git reset --hard e4f892a && git clean -fd',
    log: 'Restored clean working tree state. Injected failure traceback to RetryPolicy. Strategy pivoted: preserve tier multipliers before applying bounds guard.'
  },
  {
    type: 'ATTEMPT #2 DUAL VERIFICATION',
    time: '2026-10-10T19:48:56.772Z',
    trace: '16578e5ee3829a5a6f053c7cbeabd88f',
    cmd: 'pytest tests/test_pricing.py -v',
    log: 'test_negative_input PASSED [ 25%]\ntest_standard_price PASSED [ 50%]\ntest_vip_discount PASSED [ 75%]\ntest_bulk_tier PASSED [100%]\n===================== 4 passed in 0.81s =====================\nExit code: 0. Fixed & Verified.'
  }
];

function initTraceExplorer() {
  const eventRows = document.querySelectorAll('.trace-event-row');
  const detType = document.getElementById('det-type');
  const detTime = document.getElementById('det-time');
  const detTrace = document.getElementById('det-trace');
  const detCmd = document.getElementById('det-cmd');
  const detLog = document.getElementById('det-log');
  const copyTraceBtn = document.getElementById('copy-trace-btn');

  function renderEvent(idx) {
    const data = TRACE_EVENTS_DATA[idx];
    if (!data) return;

    if (detType) detType.textContent = data.type;
    if (detTime) detTime.textContent = data.time;
    if (detTrace) detTrace.textContent = data.trace;
    if (detCmd) detCmd.textContent = data.cmd;
    if (detLog) detLog.textContent = data.log;

    eventRows.forEach((row, i) => {
      row.classList.toggle('is-active', i === idx);
    });
  }

  eventRows.forEach((row, idx) => {
    row.addEventListener('click', () => renderEvent(idx));
    row.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        renderEvent(idx);
      }
    });
  });

  if (copyTraceBtn) {
    copyTraceBtn.addEventListener('click', () => {
      const traceId = '16578e5ee3829a5a6f053c7cbeabd88f';
      navigator.clipboard.writeText(traceId).then(() => {
        const span = copyTraceBtn.querySelector('span');
        const orig = span.textContent;
        span.textContent = 'Copied!';
        copyTraceBtn.style.color = 'var(--accent-lime)';

        setTimeout(() => {
          span.textContent = orig;
          copyTraceBtn.style.color = '';
        }, 2000);
      });
    });
  }
}

/* ==========================================================================
   6. CLI Quick Copy
   ========================================================================== */
function initCliCopy() {
  const btn = document.getElementById('btn-copy-cli');
  if (!btn) return;

  btn.addEventListener('click', () => {
    const text = `git clone https://github.com/Quantum-Ark/patchai.git && cd patchai
pip install -e ".[dev]"
patchpilot doctor
patchpilot verify-integrations
patchpilot evaluate
patchpilot serve --port 3000`;

    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = 'Copied to clipboard!';
      btn.style.background = 'var(--accent-lime)';
      btn.style.color = '#090B0F';

      setTimeout(() => {
        btn.textContent = 'Copy commands';
        btn.style.background = '';
        btn.style.color = '';
      }, 2000);
    });
  });
}

/* ==========================================================================
   7. Navigation Scroll Transition
   ========================================================================== */
function initNavScroll() {
  const nav = document.getElementById('nav-bar');
  if (!nav) return;

  window.addEventListener('scroll', () => {
    if (window.scrollY > 25) {
      nav.classList.add('scrolled');
    } else {
      nav.classList.remove('scrolled');
    }
  }, { passive: true });
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
