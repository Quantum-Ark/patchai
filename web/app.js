/**
 * PatchPilot AI — Master Creative Interaction Engine
 * Features: High-precision desktop cursor with magnetic pulling,
 * inspectable repair composition, trace explorer, and accessible keyboard controls.
 */

document.addEventListener('DOMContentLoaded', () => {
  initPrecisionCursor();
  initRepairWorkflowComposition();
  initTraceExplorer();
  initCliCopy();
  initNavScroll();
});

/* ==========================================================================
   1. Signature Desktop Precision Cursor & Magnetic Interactions
   ========================================================================== */
function initPrecisionCursor() {
  // Respect user preference or touch devices
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

  // 60fps smooth positional lag for halo
  function renderCursor() {
    haloX += (mouseX - haloX) * 0.18;
    haloY += (mouseY - haloY) * 0.18;
    halo.style.transform = `translate3d(${haloX}px, ${haloY}px, 0) translate(-50%, -50%)`;
    requestAnimationFrame(renderCursor);
  }
  renderCursor();

  // Hover states for links & buttons
  const interactiveTargets = document.querySelectorAll('a, button, .board-stage, .trace-event-row, .arch-node');
  interactiveTargets.forEach((target) => {
    target.addEventListener('mouseenter', () => document.body.classList.add('cursor-hover'));
    target.addEventListener('mouseleave', () => document.body.classList.remove('cursor-hover'));
  });

  // Magnetic button pull effect
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

  // Inspect badge when hovering over workflow stages
  const inspectableStages = document.querySelectorAll('.is-inspectable');
  inspectableStages.forEach((stage) => {
    stage.addEventListener('mouseenter', () => document.body.classList.add('cursor-inspecting'));
    stage.addEventListener('mouseleave', () => document.body.classList.remove('cursor-inspecting'));
  });
}

/* ==========================================================================
   2. Interactive Signature Repair Workflow Composition
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

  let lockedStage = 4; // Default to recovery stage

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

    // Hover previews stage
    stage.addEventListener('mouseenter', () => {
      updateExplainer(num);
    });

    // Mouseleave returns to locked stage
    stage.addEventListener('mouseleave', () => {
      updateExplainer(lockedStage);
    });

    // Click locks selection
    stage.addEventListener('click', () => {
      lockedStage = num;
      setStageActive(lockedStage);
    });

    // Accessible keyboard navigation
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
   3. Interactive Trace Explorer
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
   4. CLI Quick Copy
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
        btn.textContent = 'Copy all';
        btn.style.background = '';
        btn.style.color = '';
      }, 2000);
    });
  });
}

/* ==========================================================================
   5. Nav Bar Surface Scroll Transition
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
