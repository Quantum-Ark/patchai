/**
 * PatchPilot AI — Interactive Infrastructure Workbench Controller
 * Handles deterministic state machine simulation, code diff inspection,
 * and SaaS unit economics calculation.
 */

document.addEventListener('DOMContentLoaded', () => {
  initWorkbench();
  initDiffViewer();
  initEconomicsCalculator();
  initQuickCopy();
});

/* ==========================================================================
   1. Interactive Simulation Workbench (State Machine & Terminal)
   ========================================================================== */
const CASES_DATABASE = {
  case3: {
    target: 'benchmarks/case_3_regression_recovery/pricing.py',
    attemptLabel: '2 / 3 (Recovered)',
    traceId: '16578e5ee3829a5a',
    auditTitle: 'State: Verified Complete',
    auditDesc: 'Dual-suite verification green. Acceptance: PASSED · Regressions: 3/3 PASSED. Baseline clean.',
    logs: [
      { step: 'inspecting', tag: 'info', delay: 100, msg: 'INTAKE: Parsing issue #103 — Invalid negative volume in calculate_tiered_price.' },
      { step: 'inspecting', tag: 'trace', delay: 350, msg: 'SANDBOX: Cloned ephemeral worktree at .worktrees/patchpilot_sandbox_916d. Git baseline: e4f892a.' },
      { step: 'reproducing', tag: 'warn', delay: 700, msg: 'REPRODUCING: Executing pytest test_pricing.py -k test_negative_input ...' },
      { step: 'reproducing', tag: 'fail', delay: 1100, msg: 'BASELINE CONFIRMED: ValueError unhandled. Reproduction exit code: 1 (FAILED).' },
      { step: 'patching', tag: 'info', delay: 1500, msg: 'ATTEMPT #1: Synthesized initial candidate patch via configured LLM provider.' },
      { step: 'patching', tag: 'trace', delay: 1850, msg: 'PATCHTOOL: Applied naive clamp: volume = max(0, volume).' },
      { step: 'testing', tag: 'info', delay: 2200, msg: 'SANDBOX TEST: Running acceptance test test_negative_input ...' },
      { step: 'testing', tag: 'pass', delay: 2500, msg: 'ACCEPTANCE SUITE: test_negative_input PASSED (Exit Code: 0).' },
      { step: 'testing', tag: 'warn', delay: 2850, msg: 'REGRESSION SUITE: Executing full regression test suite (3 existing tests) ...' },
      { step: 'recovering', tag: 'fail', delay: 3200, msg: 'REGRESSION DETECTED: test_vip_discount failed! Naive clamp violated multiplier tier calculation.' },
      { step: 'recovering', tag: 'warn', delay: 3600, msg: 'ATOMIC ROLLBACK: Restoring clean Git baseline state (git reset --hard e4f892a). Zero residue.' },
      { step: 'recovering', tag: 'trace', delay: 3950, msg: 'HYPOTHESIS UPDATE: Error traceback fed to context. Strategy: Preserve discount tier before bounds check.' },
      { step: 'patching', tag: 'info', delay: 4300, msg: 'ATTEMPT #2: Applying precision adaptive patch with explicit validation raise.' },
      { step: 'verifying', tag: 'info', delay: 4650, msg: 'DUAL VERIFICATION: Re-evaluating acceptance and regression suites on Attempt #2 ...' },
      { step: 'verifying', tag: 'pass', delay: 4950, msg: 'ACCEPTANCE SUITE: PASSED (100% exit code 0).' },
      { step: 'verifying', tag: 'pass', delay: 5250, msg: 'REGRESSION SUITE: PASSED (3/3 tests green, 0 warnings).' },
      { step: 'completed', tag: 'pass', delay: 5550, msg: 'RECOVERY VERIFIED: Neatlogs trace 16578e5ee3829a5a logged. Ephemeral worktree pruned. PR #42 ready.' }
    ]
  },
  case1: {
    target: 'benchmarks/case_1_logic_bug/calc.py',
    attemptLabel: '1 / 3 (Direct Fix)',
    traceId: '9051cc67fd823b12',
    auditTitle: 'State: Verified Complete',
    auditDesc: 'Single-attempt arithmetic guard clause verified. 100% test pass rate.',
    logs: [
      { step: 'inspecting', tag: 'info', delay: 100, msg: 'INTAKE: Parsing issue #101 — ZeroDivisionError in safe_divide.' },
      { step: 'reproducing', tag: 'warn', delay: 500, msg: 'REPRODUCING: Executing pytest test_calc.py::test_zero ...' },
      { step: 'reproducing', tag: 'fail', delay: 900, msg: 'DEFECT CONFIRMED: ZeroDivisionError reproduced with exit code: 1.' },
      { step: 'patching', tag: 'info', delay: 1300, msg: 'ATTEMPT #1: Applied zero-denominator guard clause returning None.' },
      { step: 'testing', tag: 'pass', delay: 1700, msg: 'ACCEPTANCE: test_zero PASSED.' },
      { step: 'verifying', tag: 'pass', delay: 2100, msg: 'REGRESSION SUITE: 4/4 tests PASSED.' },
      { step: 'completed', tag: 'pass', delay: 2400, msg: 'VERIFIED ON ATTEMPT #1. Neatlogs trace recorded.' }
    ]
  },
  case2: {
    target: 'benchmarks/case_2_boundary_bug/paginator.py',
    attemptLabel: '1 / 3 (Boundary Resolved)',
    traceId: 'd966f503a1441b80',
    auditTitle: 'State: Verified Complete',
    auditDesc: 'Off-by-one boundary defect on empty query response resolved safely.',
    logs: [
      { step: 'inspecting', tag: 'info', delay: 100, msg: 'INTAKE: Parsing issue #102 — IndexError on empty list pagination.' },
      { step: 'reproducing', tag: 'fail', delay: 600, msg: 'DEFECT CONFIRMED: IndexError: list index out of range reproduced.' },
      { step: 'patching', tag: 'info', delay: 1100, msg: 'ATTEMPT #1: Bound check applied to items slice indexing.' },
      { step: 'verifying', tag: 'pass', delay: 1600, msg: 'ACCEPTANCE & REGRESSION: 100% tests green.' },
      { step: 'completed', tag: 'pass', delay: 2000, msg: 'BOUNDARY RESOLVED. Neatlogs trace recorded.' }
    ]
  }
};

let currentSimulationTimer = null;

function initWorkbench() {
  const terminal = document.getElementById('terminal-screen');
  const replayBtn = document.getElementById('replay-btn');
  const tabs = document.querySelectorAll('.tab-item');
  const targetLabel = document.getElementById('terminal-target-label');
  const telAttempt = document.getElementById('tel-attempt');
  const telTrace = document.getElementById('tel-trace');
  const auditTitle = document.getElementById('audit-title');
  const auditDesc = document.getElementById('audit-desc');

  let activeCase = 'case3';

  function runSimulation(caseKey) {
    if (currentSimulationTimer) {
      clearTimeout(currentSimulationTimer);
    }

    const data = CASES_DATABASE[caseKey];
    if (!data) return;

    if (targetLabel) targetLabel.textContent = data.target;
    if (telAttempt) telAttempt.textContent = data.attemptLabel;
    if (telTrace) telTrace.textContent = data.traceId;
    if (auditTitle) auditTitle.textContent = data.auditTitle;
    if (auditDesc) auditDesc.textContent = data.auditDesc;

    terminal.innerHTML = '';
    resetStepper();

    data.logs.forEach((log) => {
      setTimeout(() => {
        appendTerminalLine(log.tag, log.msg);
        updateStepper(log.step);
      }, log.delay);
    });
  }

  function appendTerminalLine(tag, msg) {
    const row = document.createElement('div');
    row.className = 'log-entry';

    const now = new Date();
    const timeStr = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;

    const tagLabels = {
      info: 'INFO',
      trace: 'TRACE',
      warn: 'WARN',
      fail: 'FAIL',
      pass: 'PASS'
    };

    row.innerHTML = `
      <span class="log-time">${timeStr}</span>
      <span class="log-tag ${tag}">[${tagLabels[tag] || 'LOG'}]</span>
      <span class="log-msg">${escapeHtml(msg)}</span>
    `;

    terminal.appendChild(row);
    terminal.scrollTop = terminal.scrollHeight;
  }

  function resetStepper() {
    const steps = document.querySelectorAll('.step-item');
    steps.forEach((s) => s.classList.remove('active', 'completed-step'));
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

    const el = document.getElementById(targetId);
    if (!el) return;

    if (step === 'completed') {
      el.classList.add('completed-step');
    } else {
      el.classList.add('active');
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

  runSimulation('case3');
}

/* ==========================================================================
   2. Precision Code Diff Viewer
   ========================================================================== */
const DIFF_DATA = {
  attempt2: {
    stats: '+3 -1 lines',
    rows: [
      { type: 'meta', num: '14', text: '# Attempt #2: Precision Patch — Preserves VIP tier, validates invalid negative volume' },
      { type: 'ctx',  num: '15', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del',  num: '16', text: '-    if volume < 0: volume = 0  # Naive clamp destroyed discount calculation tier' },
      { type: 'add',  num: '16', text: '+    if volume < 0:' },
      { type: 'add',  num: '17', text: '+        raise ValueError("Volume must be non-negative")' },
      { type: 'ctx',  num: '18', text: '    multiplier = 0.80 if is_vip else 1.0' },
      { type: 'ctx',  num: '19', text: '    return base_price * volume * multiplier' }
    ]
  },
  attempt1: {
    stats: '+1 -1 lines (Broken)',
    rows: [
      { type: 'meta', num: '14', text: '# Attempt #1: Naive Blind Clamp — Caused regression in test_vip_discount' },
      { type: 'ctx',  num: '15', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool) -> float:' },
      { type: 'del',  num: '16', text: '-    return base_price * volume * (0.80 if is_vip else 1.0)' },
      { type: 'add',  num: '16', text: '+    return base_price * max(0, volume)  # BROKE VIP DISCOUNT RULE' }
    ]
  }
};

function initDiffViewer() {
  const container = document.getElementById('diff-content');
  const btn2 = document.getElementById('btn-attempt2');
  const btn1 = document.getElementById('btn-attempt1');
  const statsLabel = document.getElementById('diff-stats');

  if (!container || !btn2 || !btn1) return;

  function renderDiff(key) {
    const diff = DIFF_DATA[key];
    if (statsLabel) statsLabel.textContent = diff.stats;
    container.innerHTML = '';

    diff.rows.forEach((row) => {
      const lineEl = document.createElement('div');
      lineEl.className = `diff-row ${row.type}`;
      lineEl.innerHTML = `
        <span class="diff-num">${row.num}</span>
        <span class="diff-code">${escapeHtml(row.text)}</span>
      `;
      container.appendChild(lineEl);
    });
  }

  btn2.addEventListener('click', () => {
    btn2.classList.add('active');
    btn1.classList.remove('active');
    renderDiff('attempt2');
  });

  btn1.addEventListener('click', () => {
    btn1.classList.add('active');
    btn2.classList.remove('active');
    renderDiff('attempt1');
  });

  renderDiff('attempt2');
}

/* ==========================================================================
   3. SaaS Unit Economics & ROI Calculator (cfo.ai Model)
   ========================================================================== */
function initEconomicsCalculator() {
  const slider = document.getElementById('bug-slider');
  const sliderVal = document.getElementById('slider-val');
  const hoursVal = document.getElementById('res-hours');
  const cogsVal = document.getElementById('res-cogs');
  const savingsVal = document.getElementById('res-savings');

  if (!slider) return;

  function recalculate() {
    const bugs = parseInt(slider.value, 10);
    const hours = bugs * 3.2; // 3.2 dev hours saved per defect
    const cogs = bugs * 0.045; // $0.045 inference COGS
    const netSavings = (hours * 100) - cogs; // $100/hr blended engineering rate

    sliderVal.textContent = `${bugs} fixes`;
    hoursVal.textContent = `${Math.round(hours)} hrs`;
    cogsVal.textContent = `$${cogs.toFixed(2)}`;
    savingsVal.textContent = `$${Math.round(netSavings).toLocaleString()}`;
  }

  slider.addEventListener('input', recalculate);
  recalculate();
}

/* ==========================================================================
   4. Quick Copy Button
   ========================================================================== */
function initQuickCopy() {
  const container = document.getElementById('quick-copy-cmd');
  if (!container) return;

  container.addEventListener('click', () => {
    const text = 'pip install -e . && patchpilot evaluate';
    navigator.clipboard.writeText(text).then(() => {
      const cmdText = container.querySelector('.cmd-text');
      const original = cmdText.textContent;
      cmdText.textContent = 'Copied to clipboard!';
      cmdText.style.color = 'var(--accent-emerald)';

      setTimeout(() => {
        cmdText.textContent = original;
        cmdText.style.color = '';
      }, 2000);
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
