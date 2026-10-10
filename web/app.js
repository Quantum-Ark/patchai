/**
 * PatchPilot AI — Built Under the Surface
 * Reverse-Engineered Interactive Engine (Inspired by metic.studio)
 * 
 * Features:
 * 1. 8-Stage Stable Scroll Build Engine with unified narrative & visual canvas
 * 2. Signature Inspection Lens (X-Ray) backed by actual DOM geometry and SVG projection
 * 3. Refined Master-Detail Capabilities Explorer with deep technical specs
 * 4. Live Draft Brief Generator that draws CLI command as developer types
 * 5. Light/Dark Theme Switcher with localStorage persistence
 * 6. Interactive Code Diff & Telemetry Dossier Explorer
 * 7. Audio click synthesizer on sound toggle
 */

document.addEventListener('DOMContentLoaded', () => {
  initThemeSystem();
  initAudioFeedback();
  initBuildScrollSequence();
  initInspectionLens();
  initCapabilitiesMasterDetail();
  initLiveDraftBrief();
  initDiffShowcase();
  initTraceCopy();
});

/* ==========================================================================
   01 — THEME SYSTEM (Light / Dark)
   ========================================================================== */
function initThemeSystem() {
  const toggleBtn = document.getElementById('btn-theme-toggle');
  const label = document.getElementById('theme-icon-label');
  const root = document.documentElement;

  const storedTheme = localStorage.getItem('patchpilot-theme');
  const initialTheme = storedTheme || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('patchpilot-theme', theme);
    if (label) {
      label.textContent = theme === 'dark' ? 'Light' : 'Dark';
    }
  }

  applyTheme(initialTheme);

  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const current = root.getAttribute('data-theme') || 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      applyTheme(next);
      playClickSound();
    });
  }
}

/* ==========================================================================
   02 — AUDIO FEEDBACK SYNTHESIZER
   ========================================================================== */
let audioCtx = null;
let soundEnabled = false;

function initAudioFeedback() {
  const soundBtn = document.getElementById('btn-sound-toggle');
  if (!soundBtn) return;

  soundBtn.addEventListener('click', (e) => {
    e.preventDefault();
    soundEnabled = !soundEnabled;
    soundBtn.setAttribute('aria-pressed', soundEnabled);
    if (soundEnabled) {
      soundBtn.classList.add('sound-active');
      playClickSound();
    } else {
      soundBtn.classList.remove('sound-active');
    }
  });
}

function playClickSound() {
  if (!soundEnabled) return;
  try {
    if (!audioCtx) {
      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    }
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(800, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(320, audioCtx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.04);
  } catch (err) {
    // Audio context may be restricted before user gesture
  }
}

/* ==========================================================================
   03 — 8-STAGE SCROLL-DRIVEN CONSTRUCTION STORY
   ========================================================================== */
function initBuildScrollSequence() {
  const section = document.getElementById('build-sequence');
  const pctDisplay = document.getElementById('build-pct-num');
  const stageRailFill = document.getElementById('stage-rail-fill');
  const stageBadgeNum = document.getElementById('stage-badge-num');
  const stageEyebrow = document.getElementById('stage-eyebrow');
  const stageHeadline = document.getElementById('stage-headline');
  const stageDesc = document.getElementById('stage-desc');
  const skipBtn = document.getElementById('btn-skip-build');
  const stageVisuals = document.querySelectorAll('.stage-visual');

  const navCenterReadout = document.getElementById('nav-center-readout');
  const navProgressFill = document.getElementById('nav-progress-fill');
  const navStepLabel = document.getElementById('nav-step-label');

  if (!section || !pctDisplay) return;

  const stages = [
    { num: '01', eyebrow: '01 · REPO DISCOVERY', title: 'A line.', desc: 'Every repair starts somewhere. Where code breaks is pinpointed, not guessed.' },
    { num: '02', eyebrow: '02 · CODEBASE MAPPING', title: 'A grid.', desc: 'Understand the structure. Columns, modules, and worktree boundaries establish the repository scaffolding.' },
    { num: '03', eyebrow: '03 · FAULT LOCALIZATION', title: 'A layout.', desc: 'Find the part that matters. Connect the bug report, candidate AST function, and reproduction test in one frame.' },
    { num: '04', eyebrow: '04 · HYPOTHESIS SPECIFICATION', title: 'A typeface.', desc: 'Make the diagnosis clear. Formulate an explicit, testable repair hypothesis before writing any code.' },
    { num: '05', eyebrow: '05 · SIGNAL INTERCEPTION', title: 'A colour.', desc: 'Every signal has a purpose. Red halts execution immediately when a test regression occurs.' },
    { num: '06', eyebrow: '06 · MINIMAL SURGERY', title: 'A line of code.', desc: 'Change the code. Inspect the diff. Bounded edits that touch only what is necessary.' },
    { num: '07', eyebrow: '07 · EMPIRICAL GATE', title: 'Online.', desc: 'Run it. Check it. Report it. Dual-suite verification gates success with zero simulated fallback.' },
    { num: '08', eyebrow: '08 · VERIFIED CONVERGENCE', title: 'Your turn.', desc: 'Make every fix earn your trust. All evidence converges into one decisive product action.' }
  ];

  let currentStageIdx = 1;

  function onScroll() {
    const rect = section.getBoundingClientRect();
    const sectionTop = rect.top;
    const sectionHeight = rect.height;
    const windowHeight = window.innerHeight;

    // Determine if user is actively in the build sequence section
    const isInBuildSection = rect.top <= windowHeight * 0.5 && rect.bottom >= windowHeight * 0.2;
    if (navCenterReadout) {
      if (isInBuildSection) {
        navCenterReadout.classList.add('is-active');
      } else {
        navCenterReadout.classList.remove('is-active');
      }
    }

    // Normalized progress (0..1)
    const totalScrollable = sectionHeight - windowHeight;
    let progress = -sectionTop / totalScrollable;
    progress = Math.max(0, Math.min(1, progress));

    const pct = Math.round(progress * 100);
    pctDisplay.textContent = String(pct).padStart(3, '0');

    if (stageRailFill) {
      stageRailFill.style.width = `${pct}%`;
    }
    if (navProgressFill) {
      navProgressFill.style.width = `${pct}%`;
    }

    // Current stage index (1 to 8)
    const stage = Math.min(8, Math.max(1, Math.floor(progress * 8) + 1));
    if (stage !== currentStageIdx) {
      currentStageIdx = stage;
      const data = stages[stage - 1];

      if (stageBadgeNum) {
        stageBadgeNum.textContent = `STAGE ${data.num} / 08`;
      }

      if (navStepLabel) {
        navStepLabel.textContent = `${data.num} / 08 · ${data.title}`;
      }

      // Smoothly update narrative text in place
      if (stageEyebrow) stageEyebrow.textContent = data.eyebrow;
      if (stageHeadline) {
        stageHeadline.style.opacity = '0.3';
        setTimeout(() => {
          stageHeadline.textContent = data.title;
          stageHeadline.style.opacity = '1';
        }, 80);
      }
      if (stageDesc) {
        stageDesc.style.opacity = '0.3';
        setTimeout(() => {
          stageDesc.textContent = data.desc;
          stageDesc.style.opacity = '1';
        }, 80);
      }

      // Update visuals
      stageVisuals.forEach((vis) => {
        const visIdx = parseInt(vis.getAttribute('data-stage-vis'), 10);
        if (visIdx === stage) {
          vis.classList.add('is-active');
        } else {
          vis.classList.remove('is-active');
        }
      });
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Skip the build button
  if (skipBtn) {
    skipBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const principleSection = document.getElementById('principle-section');
      if (principleSection) {
        principleSection.scrollIntoView({ behavior: 'smooth' });
      }
      playClickSound();
    });
  }
}

/* ==========================================================================
   04 — SIGNATURE INTERACTION: THE INSPECTION LENS (X-RAY)
   ========================================================================== */
function initInspectionLens() {
  const lensLayer = document.getElementById('inspection-lens-layer');
  const lensCircle = document.getElementById('lens-circle');
  const blueprintLayer = document.getElementById('blueprint-guide-layer');
  const blueprintSvg = document.getElementById('blueprint-svg');
  const btnNavXray = document.getElementById('btn-nav-xray');
  const btnHeroInspect = document.getElementById('btn-hero-inspect-prompt');

  const coordEl = document.getElementById('readout-coord');
  const targetEl = document.getElementById('readout-target');
  const dimEl = document.getElementById('readout-dim');
  const tokenEl = document.getElementById('readout-token');

  let isInspecting = false;
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;

  function activateLens() {
    if (isInspecting) return;
    isInspecting = true;
    document.body.classList.add('is-inspecting');
    if (lensLayer) lensLayer.classList.add('is-active');
    if (blueprintLayer) blueprintLayer.classList.add('is-active');
    if (btnNavXray) btnNavXray.classList.add('active');
    drawBlueprintGeometry();
    playClickSound();
  }

  function deactivateLens() {
    if (!isInspecting) return;
    isInspecting = false;
    document.body.classList.remove('is-inspecting');
    if (lensLayer) lensLayer.classList.remove('is-active');
    if (blueprintLayer) blueprintLayer.classList.remove('is-active');
    if (btnNavXray) btnNavXray.classList.remove('active');
  }

  function toggleLens() {
    if (isInspecting) deactivateLens();
    else activateLens();
  }

  // Header Nav Button
  if (btnNavXray) {
    btnNavXray.addEventListener('click', (e) => {
      e.preventDefault();
      toggleLens();
    });
  }

  // Hero prompt
  if (btnHeroInspect) {
    btnHeroInspect.addEventListener('click', (e) => {
      e.preventDefault();
      activateLens();
    });
  }

  // Spacebar toggle / hold
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
      e.preventDefault();
      activateLens();
    }
    if (e.key === 'Escape' && isInspecting) {
      deactivateLens();
    }
  });

  window.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
      deactivateLens();
    }
  });

  // Mouse tracking
  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    if (isInspecting) {
      if (lensCircle) {
        lensCircle.style.left = `${mouseX}px`;
        lensCircle.style.top = `${mouseY}px`;
      }
      if (blueprintLayer) {
        blueprintLayer.style.clipPath = `circle(140px at ${mouseX}px ${mouseY}px)`;
      }

      // Query element under crosshair
      const el = document.elementFromPoint(mouseX, mouseY);
      if (el && !el.closest('#inspection-lens-layer') && !el.closest('#blueprint-guide-layer')) {
        const rect = el.getBoundingClientRect();
        if (coordEl) coordEl.textContent = `X: ${Math.round(mouseX)}  Y: ${Math.round(mouseY)}`;
        if (targetEl) targetEl.textContent = `<${el.tagName.toLowerCase()}${el.id ? '#' + el.id : el.className ? '.' + el.className.split(' ')[0] : ''}>`;
        if (dimEl) dimEl.textContent = `${Math.round(rect.width)} × ${Math.round(rect.height)} px`;
        if (tokenEl) {
          const comp = window.getComputedStyle(el);
          tokenEl.textContent = `font: ${comp.fontSize} ${comp.fontFamily.split(',')[0]}`;
        }
      }
    }
  }, { passive: true });

  // Draw SVG blueprint outlines
  function drawBlueprintGeometry() {
    if (!blueprintSvg) return;
    blueprintSvg.innerHTML = '';
    const inspectables = document.querySelectorAll('[data-inspect-label], .shell, h1, h2, h3, button, .btn');
    
    inspectables.forEach((el) => {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        const rectSvg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rectSvg.setAttribute('x', r.left);
        rectSvg.setAttribute('y', r.top);
        rectSvg.setAttribute('width', r.width);
        rectSvg.setAttribute('height', r.height);
        rectSvg.setAttribute('fill', 'none');
        rectSvg.setAttribute('stroke', '#2C82C9');
        rectSvg.setAttribute('stroke-width', '1');
        rectSvg.setAttribute('stroke-dasharray', '4 3');
        rectSvg.setAttribute('opacity', '0.65');
        blueprintSvg.appendChild(rectSvg);
      }
    });
  }
}

/* ==========================================================================
   05 — MASTER-DETAIL CAPABILITIES SYSTEM
   ========================================================================== */
function initCapabilitiesMasterDetail() {
  const navItems = document.querySelectorAll('.cap-nav-item');
  const numEl = document.getElementById('cap-detail-num');
  const badgeEl = document.getElementById('cap-detail-badge');
  const tagEl = document.getElementById('cap-detail-tag');
  const titleEl = document.getElementById('cap-detail-title');
  const descEl = document.getElementById('cap-detail-desc');
  const mechEl = document.getElementById('cap-spec-mechanism');
  const isoEl = document.getElementById('cap-spec-isolation');
  const guarEl = document.getElementById('cap-spec-guarantee');
  const chipsEl = document.getElementById('cap-detail-chips');

  if (!navItems.length) return;

  const capabilitiesData = {
    1: {
      num: '01 / CAPABILITY',
      tag: 'Entire Graph AST',
      badge: 'OPERATIONAL',
      title: 'Repository Inspection',
      desc: 'PatchPilot traverses the codebase tree using AST symbols and dependency graphs. It indexes functions, references, and test locations to establish an isolated surgical scope without hallucinating unreferenced modules.',
      mechanism: 'Entire Graph code graph & AST symbol resolution',
      isolation: 'Read-only candidate discovery in working tree',
      guarantee: 'Zero file modifications during intake stage',
      chips: ['Entire Graph AST', 'Candidate Resolver', 'Symbol Cross-ref']
    },
    2: {
      num: '02 / CAPABILITY',
      tag: 'Exit Code 1 Confirmed',
      badge: 'OPERATIONAL',
      title: 'Baseline Reproduction',
      desc: 'Executes targeted reproduction commands in an isolated environment. PatchPilot strictly requires confirming that a test fails with exit code != 0 before generating any patch code.',
      mechanism: 'Subprocess runner with stdout/stderr capture',
      isolation: 'Non-destructive environment isolation',
      guarantee: 'Prevents false-positive repairs on already-passing suites',
      chips: ['Exit Code 1 Confirmed', 'Subprocess Runner', 'Traceback Capture']
    },
    3: {
      num: '03 / CAPABILITY',
      tag: 'Traversal Guard Active',
      badge: 'OPERATIONAL',
      title: 'Patch Synthesis',
      desc: 'Synthesizes bounded surgical diffs using authenticated LLM models. File path boundaries are verified to prevent path traversal, and changes are kept strictly minimal.',
      mechanism: 'Targeted code diff synthesis via LLM provider',
      isolation: 'File path sandboxing (no escapes outside repo)',
      guarantee: 'Minimal surgical edits without indiscriminate rewrites',
      chips: ['Traversal Guard', 'Minimal Surgery', 'AST Boundaries']
    },
    4: {
      num: '04 / CAPABILITY',
      tag: '60s Timeout Budget',
      badge: 'OPERATIONAL',
      title: 'Isolated Test Runner',
      desc: 'Executes acceptance tests first, then triggers existing regression suites. Applies a strict 60-second execution budget with scrubbed environment variables.',
      mechanism: 'Ephemeral subprocess execution with timeout budgets',
      isolation: 'Scrubbed environment variables (prevents secret leaks)',
      guarantee: 'Deterministic execution with non-zero exit code tracking',
      chips: ['60s Timeout Budget', 'Env Scrubbing', 'Sandbox Worktree']
    },
    5: {
      num: '05 / CAPABILITY',
      tag: 'Atomic Rollback Ready',
      badge: 'OPERATIONAL',
      title: 'Failure Recovery',
      desc: 'When a test regression or error occurs, PatchPilot performs an immediate atomic git rollback to the baseline SHA e4f892a, extracts traceback diagnostics, and replans Attempt #2.',
      mechanism: 'Atomic git reset --hard to baseline commit SHA',
      isolation: 'Prevents dirty state accumulation across retry loops',
      guarantee: 'Zero corrupted intermediate state committed to branch',
      chips: ['Atomic Rollback', 'Traceback Injection', 'Loop Circuit Breaker']
    },
    6: {
      num: '06 / CAPABILITY',
      tag: 'Dual Gate Required',
      badge: 'OPERATIONAL',
      title: 'Dual Gate Verification',
      desc: 'A repair is never marked successful on test output alone. Both the reproduction test and the existing full regression suite must pass with exit code 0 simultaneously.',
      mechanism: 'Compound verification gate (Repro + Regression == 0)',
      isolation: 'Clean worktree verification before packaging',
      guarantee: 'Zero regressions introduced to existing functionality',
      chips: ['Dual-Suite Gate', '100% Pass Required', 'Exit Code 0']
    },
    7: {
      num: '07 / CAPABILITY',
      tag: 'Neatlogs Telemetry',
      badge: 'OPERATIONAL',
      title: 'Cryptographic Evidence',
      desc: 'Generates an immutable audit dossier with Neatlogs span identifiers, archived git patch diffs, and prepares a draft PR ready for human peer review.',
      mechanism: 'Neatlogs telemetry export + structured run dossier',
      isolation: 'Cryptographic execution hashes and logs',
      guarantee: 'Every repair is verifiable by third-party reviewers',
      chips: ['Neatlogs Telemetry', 'Draft PR Dossier', 'Audit Trail']
    }
  };

  function selectCapability(capId) {
    const data = capabilitiesData[capId];
    if (!data) return;

    navItems.forEach((btn) => {
      const isMatch = btn.getAttribute('data-cap-id') === String(capId);
      btn.classList.toggle('is-active', isMatch);
      btn.setAttribute('aria-selected', isMatch ? 'true' : 'false');
    });

    if (numEl) numEl.textContent = data.num;
    if (badgeEl) badgeEl.textContent = data.badge;
    if (tagEl) tagEl.textContent = data.tag;
    if (titleEl) titleEl.textContent = data.title;
    if (descEl) descEl.textContent = data.desc;
    if (mechEl) mechEl.textContent = data.mechanism;
    if (isoEl) isoEl.textContent = data.isolation;
    if (guarEl) guarEl.textContent = data.guarantee;

    if (chipsEl) {
      chipsEl.innerHTML = '';
      data.chips.forEach((c) => {
        const span = document.createElement('span');
        span.className = 'fan-chip';
        span.textContent = c;
        chipsEl.appendChild(span);
      });
    }

    playClickSound();
  }

  navItems.forEach((btn) => {
    const capId = btn.getAttribute('data-cap-id');
    btn.addEventListener('click', () => selectCapability(capId));
    btn.addEventListener('mouseenter', () => selectCapability(capId));
  });
}

/* ==========================================================================
   06 — LIVE DRAFT BRIEF GENERATOR
   ========================================================================== */
function initLiveDraftBrief() {
  const fRepo = document.getElementById('f-repo');
  const fIssue = document.getElementById('f-issue');
  const fTest = document.getElementById('f-test-cmd');
  const fAttempts = document.getElementById('f-max-attempts');
  const livePreview = document.getElementById('live-cli-preview');
  const pctDisplay = document.getElementById('draft-pct-display');
  const copyBtn = document.getElementById('btn-copy-cli-command');
  const copyLabel = document.getElementById('btn-copy-label');
  const statusFeedback = document.getElementById('form-feedback-status');

  if (!livePreview) return;

  function updateDraft() {
    const repoVal = fRepo ? fRepo.value.trim() : 'https://github.com/Quantum-Ark/patchai';
    const issueVal = fIssue ? fIssue.value.trim() : 'Defect description';
    const testVal = fTest ? fTest.value.trim() : 'pytest tests/';
    const attemptsVal = fAttempts ? fAttempts.value : '3';

    // Calculate completion score
    let score = 0;
    if (repoVal.length > 3) score += 35;
    if (issueVal.length > 10) score += 40;
    if (testVal.length > 5) score += 15;
    if (attemptsVal) score += 10;

    if (pctDisplay) {
      pctDisplay.textContent = `${score}%`;
    }

    // Construct command
    const sanitizedIssue = issueVal.replace(/"/g, '\\"').substring(0, 100);
    const cmd = `patchpilot run \\\n  --repo "${repoVal || '.'}" \\\n  --issue "${sanitizedIssue || 'Describe the issue'}" \\\n  --test "${testVal || 'pytest'}" \\\n  --max-attempts ${attemptsVal}`;

    livePreview.textContent = cmd;
  }

  [fRepo, fIssue, fTest, fAttempts].forEach((input) => {
    if (input) {
      input.addEventListener('input', updateDraft);
      input.addEventListener('change', updateDraft);
    }
  });

  updateDraft();

  // Copy CLI command utility
  if (copyBtn) {
    copyBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const textToCopy = livePreview.textContent.trim();
      try {
        await navigator.clipboard.writeText(textToCopy);
        if (copyLabel) copyLabel.textContent = 'Command Copied!';
        if (statusFeedback) statusFeedback.textContent = 'Copied to clipboard. Paste into your terminal to execute.';
        playClickSound();

        setTimeout(() => {
          if (copyLabel) copyLabel.textContent = 'Copy CLI Command';
          if (statusFeedback) statusFeedback.textContent = 'Ready to execute locally';
        }, 2500);
      } catch (err) {
        console.warn('Clipboard write error:', err);
      }
    });
  }
}

/* ==========================================================================
   07 — INTERACTIVE CODE DIFF SHOWCASE
   ========================================================================== */
function initDiffShowcase() {
  const pane = document.getElementById('diff-view-pane');
  const indicator = document.getElementById('diff-status-indicator');
  const tabV = document.getElementById('tab-v');
  const tabD = document.getElementById('tab-d');
  const tabR = document.getElementById('tab-r');

  if (!pane) return;

  const diffContent = {
    verified: {
      meta: 'pricing.py:15 · +2 lines · Verified 100% Pass Rate',
      html: `
<div class="diff-r"><span class="d-n">12</span><span class="d-s"> </span><span>def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -&gt; float:</span></div>
<div class="diff-r"><span class="d-n">13</span><span class="d-s"> </span><span>    """Calculates final price with tiered volume discounts."""</span></div>
<div class="diff-r"><span class="d-n">14</span><span class="d-s"> </span><span>    if base_price &lt; 0: raise ValueError("base_price cannot be negative")</span></div>
<div class="diff-r diff-r-add"><span class="d-n">15</span><span class="d-s">+</span><span>    if volume &lt; 0:</span></div>
<div class="diff-r diff-r-add"><span class="d-n">16</span><span class="d-s">+</span><span>        raise ValueError("volume must be non-negative")</span></div>
<div class="diff-r"><span class="d-n">17</span><span class="d-s"> </span><span>    multiplier = 0.80 if is_vip else 1.0</span></div>
<div class="diff-r"><span class="d-n">18</span><span class="d-s"> </span><span>    return base_price * volume * multiplier</span></div>
`
    },
    defective: {
      meta: 'pricing.py:15 · 0 changes · Unhandled volume < 0',
      html: `
<div class="diff-r"><span class="d-n">12</span><span class="d-s"> </span><span>def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -&gt; float:</span></div>
<div class="diff-r"><span class="d-n">13</span><span class="d-s"> </span><span>    """Calculates final price with tiered volume discounts."""</span></div>
<div class="diff-r"><span class="d-n">14</span><span class="d-s"> </span><span>    if base_price &lt; 0: raise ValueError("base_price cannot be negative")</span></div>
<div class="diff-r diff-r-del"><span class="d-n">15</span><span class="d-s">-</span><span>    # Missing defensive volume check produces negative invoice totals</span></div>
<div class="diff-r diff-r-del"><span class="d-n">16</span><span class="d-s">-</span><span>    multiplier = 0.80 if is_vip else 1.0</span></div>
<div class="diff-r diff-r-del"><span class="d-n">17</span><span class="d-s">-</span><span>    return base_price * volume * multiplier</span></div>
`
    },
    regression: {
      meta: 'pricing.py:15 · Attempt #1 Naive Clamp · Broke VIP Tier',
      html: `
<div class="diff-r"><span class="d-n">12</span><span class="d-s"> </span><span>def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -&gt; float:</span></div>
<div class="diff-r"><span class="d-n">13</span><span class="d-s"> </span><span>    if base_price &lt; 0: raise ValueError("base_price cannot be negative")</span></div>
<div class="diff-r diff-r-del"><span class="d-n">14</span><span class="d-s">-</span><span>    multiplier = 0.80 if is_vip else 1.0</span></div>
<div class="diff-r diff-r-del"><span class="d-n">15</span><span class="d-s">-</span><span>    return base_price * volume * multiplier</span></div>
<div class="diff-r diff-r-del"><span class="d-n">14</span><span class="d-s">+</span><span>    # Attempt #1 Naive Clamp (Overwrote VIP discount multiplier)</span></div>
<div class="diff-r diff-r-del"><span class="d-n">15</span><span class="d-s">+</span><span>    return base_price * max(0, volume)</span></div>
`
    }
  };

  function setDiffView(viewKey) {
    [tabV, tabD, tabR].forEach((t) => t && t.classList.remove('active'));

    if (viewKey === 'verified' && tabV) tabV.classList.add('active');
    if (viewKey === 'defective' && tabD) tabD.classList.add('active');
    if (viewKey === 'regression' && tabR) tabR.classList.add('active');

    const data = diffContent[viewKey];
    if (data) {
      if (indicator) indicator.textContent = data.meta;
      pane.innerHTML = data.html;
      playClickSound();
    }
  }

  if (tabV) tabV.addEventListener('click', () => setDiffView('verified'));
  if (tabD) tabD.addEventListener('click', () => setDiffView('defective'));
  if (tabR) tabR.addEventListener('click', () => setDiffView('regression'));

  setDiffView('verified');
}

/* ==========================================================================
   08 — TELEMETRY TRACE COPY UTILITY
   ========================================================================== */
function initTraceCopy() {
  const copyBtn = document.getElementById('btn-copy-trace-id');
  const traceIdVal = document.getElementById('trace-id-val');

  if (copyBtn && traceIdVal) {
    copyBtn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(traceIdVal.textContent.trim());
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.borderColor = 'var(--status-verified)';
        copyBtn.style.color = 'var(--status-verified)';
        playClickSound();

        setTimeout(() => {
          copyBtn.textContent = originalText;
          copyBtn.style.borderColor = 'var(--border-default)';
          copyBtn.style.color = 'var(--text-secondary)';
        }, 2000);
      } catch (err) {
        console.warn('Clipboard write error:', err);
      }
    });
  }
}
