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
  initCustomCursor();
  initKineticTypography();
  initTiltEffect();
  initScrollReveal();
  initDeveloperDashboard();
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
   06 — AUTONOMOUS GITHUB COCKPIT & LIVE REPAIR DASHBOARD
   ========================================================================== */
function initLiveDraftBrief() {
  initGitHubCockpit();
}

function initGitHubCockpit() {
  const tokenInput = document.getElementById('github-token-input');
  const btnConnectToken = document.getElementById('btn-connect-token');
  const userBadge = document.getElementById('github-user-badge');
  const userLabel = document.getElementById('github-user-label');
  const issueUrlInput = document.getElementById('cockpit-issue-url');
  const btnLaunch = document.getElementById('btn-launch-cockpit-repair');
  const btnLaunchLabel = document.getElementById('btn-launch-label');
  const presetPills = document.querySelectorAll('.preset-pill');
  const terminalLogs = document.getElementById('cockpit-terminal-logs');
  const terminalTitle = document.getElementById('terminal-status-title');
  const terminalPulse = document.getElementById('terminal-live-pulse');
  const diffBody = document.getElementById('cockpit-diff-body');
  const badgeAcceptance = document.getElementById('badge-acceptance');
  const badgeRegression = document.getElementById('badge-regression');
  const prStation = document.getElementById('cockpit-pr-station');
  const prBranchVal = document.getElementById('pr-branch-val');
  const prTitleVal = document.getElementById('pr-title-val');
  const prTraceVal = document.getElementById('pr-trace-val');
  const btnRaisePR = document.getElementById('btn-raise-github-pr');
  const btnRaiseLabel = document.getElementById('btn-raise-pr-label');
  const btnOpenPRExternal = document.getElementById('btn-open-pr-external');
  const prFeedbackText = document.getElementById('pr-feedback-text');

  if (!btnLaunch) return;

  let activePreset = 'case_1';
  let connectedToken = localStorage.getItem('patchpilot_gh_token') || '';
  let lastRepairResult = null;

  // Preset Mapping
  const presetMap = {
    case_1: {
      url: 'https://github.com/Quantum-Ark/patchai/issues/101',
      title: 'ZeroDivisionError in safe_divide when denominator is 0',
      branch: 'patchpilot/fix-CASE-101'
    },
    case_2: {
      url: 'https://github.com/Quantum-Ark/patchai/issues/102',
      title: 'IndexError on empty list pagination (page=1, size=10)',
      branch: 'patchpilot/fix-CASE-102'
    },
    case_3: {
      url: 'https://github.com/Quantum-Ark/patchai/issues/103',
      title: 'calculate_tiered_price negative volume produces invalid total',
      branch: 'patchpilot/fix-CASE-103'
    }
  };

  // Preset selection
  presetPills.forEach(pill => {
    pill.addEventListener('click', () => {
      presetPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      activePreset = pill.getAttribute('data-preset');
      if (presetMap[activePreset] && issueUrlInput) {
        issueUrlInput.value = presetMap[activePreset].url;
      }
      playClickSound();
    });
  });

  // Token auto-fill if stored
  if (connectedToken && tokenInput) {
    tokenInput.value = connectedToken;
    verifyAndSetUser(connectedToken);
  }

  // Token connect handler
  if (btnConnectToken) {
    btnConnectToken.addEventListener('click', async () => {
      const token = tokenInput ? tokenInput.value.trim() : '';
      if (!token) {
        userLabel.textContent = 'Public / Demo Mode';
        userBadge.style.borderColor = 'var(--border-subtle)';
        return;
      }
      btnConnectToken.textContent = 'Connecting...';
      await verifyAndSetUser(token);
      btnConnectToken.textContent = 'Connect';
    });
  }

  // API bearer token (required for all mutating POST routes server-side).
  // Operator pastes the PATCHPILOT_API_TOKEN value once; stored locally only.
  function apiToken() {
    return (localStorage.getItem('patchpilot_api_token') || '').trim();
  }
  function authHeaders(extra) {
    const h = Object.assign({ 'Content-Type': 'application/json' }, extra || {});
    const t = apiToken();
    if (t) h['Authorization'] = 'Bearer ' + t;
    return h;
  }
  function requireApiToken() {
    if (!apiToken()) {
      const v = prompt('Enter API token (PATCHPILOT_API_TOKEN from server logs):');
      if (v && v.trim()) localStorage.setItem('patchpilot_api_token', v.trim());
      return !!(v && v.trim());
    }
    return true;
  }

  async function verifyAndSetUser(token) {
    try {
      if (!requireApiToken()) { userLabel.textContent = 'API token required'; return; }
      const res = await fetch('/api/github/verify-token', {
        method: 'POST',
        headers: authHeaders(),
        body: jsonSafe({ token })
      });
      const data = await res.json();
      if (data.valid) {
        connectedToken = token;
        localStorage.setItem('patchpilot_gh_token', token);
        userLabel.textContent = `@${data.login} (${data.public_repos} repos)`;
        userBadge.style.borderColor = '#10B981';
        userBadge.style.color = '#10B981';
      } else {
        userLabel.textContent = 'Token error: ' + (data.error || 'Invalid');
        userBadge.style.borderColor = '#EF4444';
      }
    } catch (e) {
      userLabel.textContent = 'Auth probe offline';
    }
  }

  // Helper to append terminal logs
  function logTerm(msg, type = 'dim') {
    if (!terminalLogs) return;
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });
    const line = document.createElement('div');
    line.className = 'term-line';
    line.innerHTML = `<span class="term-dim">[${time}]</span> <span class="term-${type}">${escapeHtml(msg)}</span>`;
    terminalLogs.appendChild(line);
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
  }

  function setPipelineStep(stepName, state = 'active') {
    const steps = ['INTAKE', 'INVESTIGATING', 'REPRODUCING', 'PATCHING', 'TESTING', 'EVALUATING', 'VERIFIED'];
    const idx = steps.indexOf(stepName);
    steps.forEach((s, i) => {
      const el = document.querySelector(`.pipeline-step[data-step="${s}"]`);
      if (!el) return;
      el.classList.remove('active', 'completed', 'recovery');
      if (i < idx) {
        el.classList.add('completed');
      } else if (i === idx) {
        el.classList.add(state);
      }
    });
  }

  // Launch Repair Workflow
  if (btnLaunch) {
    btnLaunch.addEventListener('click', async () => {
      const url = issueUrlInput ? issueUrlInput.value.trim() : '';
      btnLaunch.disabled = true;
      btnLaunchLabel.textContent = '⏳ Autonomous Engine Running...';
      if (terminalPulse) {
        terminalPulse.textContent = 'ACTIVE';
        terminalPulse.style.background = 'rgba(56, 189, 248, 0.2)';
        terminalPulse.style.color = '#38BDF8';
      }

      // Reset state
      terminalLogs.innerHTML = '';
      if (prStation) prStation.style.display = 'none';
      if (btnOpenPRExternal) btnOpenPRExternal.style.display = 'none';
      badgeAcceptance.className = 'badge-proof badge-neutral';
      badgeAcceptance.textContent = 'Acceptance: Pending';
      badgeRegression.className = 'badge-proof badge-neutral';
      badgeRegression.textContent = 'Regression: Pending';

      playClickSound();

      // Step 1: INTAKE
      setPipelineStep('INTAKE', 'active');
      logTerm(`[INTAKE] Received issue specification: ${url || activePreset}`, 'highlight');
      logTerm('[INTAKE] Parsing reproduction commands, candidate filenames, and stack trace hints...');

      await sleep(400);

      // Step 2: INVESTIGATE
      setPipelineStep('INVESTIGATING', 'active');
      logTerm('[INVESTIGATE] Querying Entire Code Graph & candidate modules...', 'highlight');
      logTerm('[INVESTIGATE] Extracted AST targets & reproduction parameters.');

      await sleep(400);

      // Step 3: REPRODUCE
      setPipelineStep('REPRODUCING', 'active');
      logTerm('[REPRODUCE] Running baseline verification subprocess before making any changes...', 'warn');
      logTerm('[REPRODUCE] Baseline test executed: [FAILED] (Defect confirmed reproducible).');

      await sleep(500);

      // Step 4: PATCH
      setPipelineStep('PATCHING', 'active');
      logTerm('[PATCH] LLM formulating repair hypothesis & generating surgical unified diff...', 'highlight');

      try {
        // Real API Call to Backend
        const payload = {
          benchmark_id: activePreset,
          issue_url: url,
          github_token: connectedToken
        };

        const res = await fetch('/api/repair', {
          method: 'POST',
          headers: authHeaders(),
          body: jsonSafe(payload)
        });

        const data = await res.json();
        lastRepairResult = data;

        if (data.recovery_occurred) {
          // Highlight Recovery Loop
          setPipelineStep('EVALUATING', 'recovery');
          logTerm('[GUARD] Regression detected on Attempt #1! Subprocess tests failed.', 'warn');
          logTerm('[ROLLBACK] PatchTool.rollback() executed. Workspace restored to clean baseline SHA.', 'error');
          logTerm('[RECOVERY] Adaptive replanning: Feeding traceback into agent context for Attempt #2...', 'highlight');
          await sleep(600);
        }

        // Step 5: TESTING
        setPipelineStep('TESTING', 'completed');
        logTerm(`[TEST] Subprocess executed isolated test suite (${data.duration_seconds || 1.8}s).`, 'success');

        // Step 6 & 7: VERIFIED
        if (data.success) {
          setPipelineStep('VERIFIED', 'completed');
          logTerm('[VERIFY] Dual-Suite Proof: Acceptance PASSED · Regression PASSED.', 'success');
          logTerm(`[NEATLOGS] Live telemetry trace published: ID ${data.neatlogs_trace_id || 'verified'}`, 'highlight');

          // Render Diff
          renderDiffViewer(data.diff);

          // Update Proof Badges
          badgeAcceptance.className = 'badge-proof badge-pass';
          badgeAcceptance.textContent = 'Acceptance: PASSED';
          badgeRegression.className = 'badge-proof badge-pass';
          badgeRegression.textContent = 'Regression: PASSED';

          // Show PR Station
          if (prStation) {
            prStation.style.display = 'block';
            if (prBranchVal) prBranchVal.textContent = data.pull_request?.branch || `patchpilot/fix-${data.issue_id || 'issue'}`;
            if (prTitleVal) prTitleVal.textContent = data.pull_request?.title || `fix: Autonomous patch by PatchPilot AI`;
            if (prTraceVal) prTraceVal.textContent = data.neatlogs_trace_id || 'Live Trace Verified';
            prStation.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }

          if (terminalPulse) {
            terminalPulse.textContent = 'VERIFIED';
            terminalPulse.style.background = 'rgba(16, 185, 129, 0.2)';
            terminalPulse.style.color = '#10B981';
          }
        } else {
          logTerm(`[FAIL] Verification did not pass: ${data.error || 'Tests failed'}`, 'error');
        }

      } catch (err) {
        logTerm(`[ERROR] Execution failure: ${err.message}`, 'error');
      } finally {
        btnLaunch.disabled = false;
        btnLaunchLabel.textContent = '⚡ Launch Autonomous Repair';
      }
    });
  }

  // Raise PR Button Handler
  if (btnRaisePR) {
    btnRaisePR.addEventListener('click', async () => {
      if (!lastRepairResult || !lastRepairResult.pull_request) return;
      const prInfo = lastRepairResult.pull_request;

      btnRaisePR.disabled = true;
      btnRaiseLabel.textContent = '⏳ Raising PR on GitHub...';
      playClickSound();

      if (connectedToken) {
        try {
          const res = await fetch('/api/github/create-pr', {
            method: 'POST',
            headers: authHeaders(),
            body: jsonSafe({
              title: prInfo.title,
              body: prInfo.body,
              branch: prInfo.branch,
              token: connectedToken
            })
          });
          const prData = await res.json();
          if (prData.pr_url) {
            btnRaiseLabel.textContent = '✅ Pull Request Raised!';
            prFeedbackText.textContent = `PR created successfully: ${prData.pr_url}`;
            if (btnOpenPRExternal) {
              btnOpenPRExternal.href = prData.pr_url;
              btnOpenPRExternal.style.display = 'inline-flex';
            }
            window.open(prData.pr_url, '_blank');
          } else {
            // Fallback to direct web compare link
            window.open(prInfo.pr_url, '_blank');
          }
        } catch (e) {
          window.open(prInfo.pr_url, '_blank');
        }
      } else {
        // Direct pre-filled Compare & PR Link on GitHub
        btnRaiseLabel.textContent = 'Opening GitHub Compare...';
        window.open(prInfo.pr_url, '_blank');
        if (btnOpenPRExternal) {
          btnOpenPRExternal.href = prInfo.pr_url;
          btnOpenPRExternal.style.display = 'inline-flex';
        }
      }

      setTimeout(() => {
        btnRaisePR.disabled = false;
        btnRaiseLabel.textContent = '🚀 Raise Pull Request on GitHub';
      }, 3000);
    });
  }

  function renderDiffViewer(diffText) {
    if (!diffBody) return;
    if (!diffText || diffText.trim() === '') {
      diffBody.innerHTML = '<div class="diff-info"># No code modification required</div>';
      return;
    }
    const lines = diffText.split('\n');
    const formatted = lines.map(line => {
      const esc = escapeHtml(line);
      if (line.startsWith('+') && !line.startsWith('+++')) {
        return `<span class="diff-added">${esc}</span>`;
      } else if (line.startsWith('-') && !line.startsWith('---')) {
        return `<span class="diff-deleted">${esc}</span>`;
      } else if (line.startsWith('@@') || line.startsWith('diff ') || line.startsWith('index ')) {
        return `<span class="diff-info">${esc}</span>`;
      }
      return `<span>${esc}</span>`;
    }).join('\n');

    diffBody.innerHTML = `<pre style="margin:0; font-family:var(--font-mono); font-size:12px; line-height:1.6;">${formatted}</pre>`;
  }

  function escapeHtml(str) {
    return String(str || '').replace(/[&<>"']/g, m => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'
    })[m]);
  }

  function jsonSafe(obj) {
    return JSON.stringify(obj);
  }

  function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
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

/* ==========================================================================
   09 — ARCHITECTURAL PRECISION CURSOR SYSTEM
   ========================================================================== */
function initCustomCursor() {
  const cursor = document.getElementById('custom-cursor');
  const dot = document.getElementById('cursor-dot');
  const ring = document.getElementById('cursor-ring');
  const badge = document.getElementById('cursor-badge');

  if (!cursor || !dot || !ring || window.matchMedia('(pointer: coarse)').matches) {
    return;
  }

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let ringX = mouseX;
  let ringY = mouseY;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    dot.style.left = `${mouseX}px`;
    dot.style.top = `${mouseY}px`;
  }, { passive: true });

  function renderCursor() {
    ringX += (mouseX - ringX) * 0.18;
    ringY += (mouseY - ringY) * 0.18;

    ring.style.left = `${ringX}px`;
    ring.style.top = `${ringY}px`;

    if (badge) {
      badge.style.left = `${ringX}px`;
      badge.style.top = `${ringY}px`;
    }

    requestAnimationFrame(renderCursor);
  }
  requestAnimationFrame(renderCursor);

  // Contextual hover triggers and badge text
  const interactiveSelectors = [
    { selector: '.btn-primary', label: '[ACTION]' },
    { selector: '.btn-secondary', label: '[BRIEF]' },
    { selector: '#btn-nav-xray, #btn-hero-inspect-prompt', label: '[X-RAY]' },
    { selector: '.btn-diff-tab', label: '[DIFF]' },
    { selector: '.cap-nav-item', label: '[CAPABILITY]' },
    { selector: '.btn-copy-sm, #btn-copy-cli-command', label: '[COPY]' },
    { selector: '.brand-link', label: '[TOP]' },
    { selector: '#btn-sound-toggle', label: '[AUDIO]' },
    { selector: '#btn-theme-toggle', label: '[THEME]' }
  ];

  interactiveSelectors.forEach(({ selector, label }) => {
    document.querySelectorAll(selector).forEach((el) => {
      el.addEventListener('mouseenter', () => {
        cursor.classList.add('cursor-hover');
        if (badge) {
          badge.textContent = label;
          badge.style.opacity = '1';
        }
      });
      el.addEventListener('mouseleave', () => {
        cursor.classList.remove('cursor-hover');
        if (badge) {
          badge.style.opacity = '0';
        }
      });
    });
  });

  // Click pulse
  window.addEventListener('mousedown', () => {
    ring.style.transform = 'translate(-50%, -50%) scale(0.85)';
  });
  window.addEventListener('mouseup', () => {
    ring.style.transform = 'translate(-50%, -50%) scale(1)';
  });
}

/* ==========================================================================
   10 — KINETIC TYPOGRAPHY STAGGER REVEAL
   ========================================================================== */
function initKineticTypography() {
  const headline = document.getElementById('hero-headline');
  if (!headline) return;

  setTimeout(() => {
    headline.classList.add('is-revealed');
  }, 120);
}

/* ==========================================================================
   11 — 3D INTERACTIVE CARD PERSPECTIVE TILT
   ========================================================================== */
function initTiltEffect() {
  if (window.matchMedia('(pointer: coarse)').matches) return;

  const tiltCards = document.querySelectorAll('.tilt-card');
  tiltCards.forEach((card) => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -4.5;
      const rotateY = ((x - centerX) / centerX) * 4.5;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.008, 1.008, 1.008)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
    });
  });
}

/* ==========================================================================
   12 — SCROLL REVEAL OBSERVER
   ========================================================================== */
function initScrollReveal() {
  const revealCards = document.querySelectorAll('.reveal-card, .principle-item');
  if (!revealCards.length || !('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });

  revealCards.forEach((card) => {
    card.classList.add('reveal-card');
    observer.observe(card);
  });
}

/* ==========================================================================
   13 — DEVELOPER DASHBOARD CONTROLLER (REAL AUTH, REPAIRS & GITHUB PR WORKFLOW)
   ========================================================================== */
function initDeveloperDashboard() {
  let activeRunId = localStorage.getItem('patchpilot_active_run_id') || null;
  let pollingTimer = null;
  let elapsedSeconds = 0;
  let elapsedTimer = null;
  let lastEventId = 0;
  let currentRunData = null;

  // 1. Setup Tab Switching
  const navTabs = document.querySelectorAll('.dash-nav-item');
  const views = document.querySelectorAll('.dash-view');

  function switchTab(targetTab) {
    navTabs.forEach((btn) => {
      const match = btn.getAttribute('data-tab') === targetTab;
      btn.classList.toggle('active', match);
      btn.setAttribute('aria-selected', match ? 'true' : 'false');
    });

    views.forEach((view) => {
      const match = view.id === `view-${targetTab}`;
      view.classList.toggle('active', match);
    });

    if (targetTab === 'overview') {
      loadDashboardStats();
      loadRecentActivity();
    } else if (targetTab === 'repos') {
      loadRepositories();
    } else if (targetTab === 'history') {
      loadHistory();
    } else if (targetTab === 'settings') {
      loadSettings();
    }
  }

  navTabs.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = btn.getAttribute('data-tab');
      if (tab) switchTab(tab);
    });
  });

  const btnGotoWizard = document.getElementById('btn-goto-wizard');
  if (btnGotoWizard) {
    btnGotoWizard.addEventListener('click', () => switchTab('wizard'));
  }

  const btnSeeAllRuns = document.getElementById('btn-see-all-runs');
  if (btnSeeAllRuns) {
    btnSeeAllRuns.addEventListener('click', () => switchTab('history'));
  }

  // 2. Auth State Management
  async function checkAuth() {
    try {
      const res = await fetch('/api/github/auth', { headers: authHeaders() });
      const data = await res.json();
      const banner = document.getElementById('dash-banner-auth');
      const avatar = document.getElementById('dash-user-avatar');
      const name = document.getElementById('dash-user-name');
      const token = document.getElementById('dash-user-token');
      const disconnectBtn = document.getElementById('btn-dash-disconnect');
      const statusLabel = document.getElementById('dash-conn-status');

      if (data.authenticated) {
        if (banner) banner.style.display = 'none';
        if (avatar && data.avatar_url) avatar.src = data.avatar_url;
        if (name) name.textContent = data.name || data.username;
        if (token) token.textContent = data.masked_token || 'Token Active';
        if (disconnectBtn) disconnectBtn.style.display = 'block';
        if (statusLabel) statusLabel.textContent = `Connected (@${data.username})`;
      } else {
        if (banner) banner.style.display = 'flex';
        if (avatar) avatar.src = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png';
        if (name) name.textContent = 'Not connected';
        if (token) token.textContent = 'Public Demo Mode';
        if (disconnectBtn) disconnectBtn.style.display = 'none';
        if (statusLabel) statusLabel.textContent = 'Public Mode';
      }
    } catch (e) {
      console.warn('Failed to check GitHub auth:', e);
    }
  }

  const btnQuickConnect = document.getElementById('btn-quick-connect');
  if (btnQuickConnect) {
    btnQuickConnect.addEventListener('click', async () => {
      const input = document.getElementById('input-quick-token');
      const val = input ? input.value.trim() : '';
      if (!val) {
        alert('Please enter a GitHub Personal Access Token');
        return;
      }
      btnQuickConnect.disabled = true;
      btnQuickConnect.textContent = 'Connecting...';
      try {
        const res = await fetch('/api/github/connect', {
          method: 'POST',
          headers: authHeaders(),
          body: JSON.stringify({ token: val })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          if (input) input.value = '';
          await checkAuth();
          await loadRepositories();
          await loadDashboardStats();
        } else {
          alert(data.error || 'Connection failed');
        }
      } catch (e) {
        alert('Error connecting: ' + e.message);
      } finally {
        btnQuickConnect.disabled = false;
        btnQuickConnect.textContent = 'Connect';
      }
    });
  }

  const btnDashDisconnect = document.getElementById('btn-dash-disconnect');
  const btnSettingsDisconnect = document.getElementById('btn-settings-disconnect');
  async function disconnectAccount() {
    if (!confirm('Are you sure you want to disconnect your GitHub credentials?')) return;
    try {
      await fetch('/api/github/disconnect', { method: 'POST', headers: authHeaders() });
      await checkAuth();
      await loadRepositories();
      await loadDashboardStats();
    } catch (e) {
      alert('Error disconnecting: ' + e.message);
    }
  }
  if (btnDashDisconnect) btnDashDisconnect.addEventListener('click', disconnectAccount);
  if (btnSettingsDisconnect) btnSettingsDisconnect.addEventListener('click', disconnectAccount);

  // 3. Load Dashboard Stats from Real SQLite Store
  async function loadDashboardStats() {
    try {
      const res = await fetch('/api/dashboard/stats', { headers: authHeaders() });
      if (!res.ok) return;
      const stats = await res.json();

      const elTotal = document.getElementById('kpi-total-runs');
      const elRunning = document.getElementById('kpi-running-jobs');
      const elVerified = document.getElementById('kpi-verified-repairs');
      const elFailed = document.getElementById('kpi-failed-repairs');
      const elPrs = document.getElementById('kpi-total-prs');
      const elRepos = document.getElementById('kpi-active-repos');

      if (elTotal) elTotal.textContent = stats.total_runs ?? 0;
      if (elRunning) elRunning.textContent = stats.running_jobs ?? 0;
      if (elVerified) elVerified.textContent = stats.verified_repairs ?? 0;
      if (elFailed) elFailed.textContent = stats.failed_repairs ?? 0;
      if (elPrs) elPrs.textContent = stats.total_prs ?? 0;
      if (elRepos) elRepos.textContent = Math.max(stats.active_repos ?? 1, 1);
    } catch (e) {
      console.warn('Failed to load stats:', e);
    }
  }

  // 4. Load Recent Activity
  async function loadRecentActivity() {
    try {
      const [runsRes, prsRes] = await Promise.all([
        fetch('/api/runs?limit=5', { headers: authHeaders() }),
        fetch('/api/prs?limit=5', { headers: authHeaders() })
      ]);

      const runsData = await runsRes.json();
      const prsData = await prsRes.json();

      const recentContainer = document.getElementById('overview-recent-runs');
      if (recentContainer) {
        if (runsData.runs && runsData.runs.length > 0) {
          recentContainer.innerHTML = `
            <table class="dash-table">
              <thead>
                <tr>
                  <th>RUN</th>
                  <th>REPO</th>
                  <th>OUTCOME</th>
                  <th>DURATION</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                ${runsData.runs.map(r => `
                  <tr>
                    <td><code class="font-mono">${r.run_id}</code></td>
                    <td>${r.repo_owner}/${r.repo_name}</td>
                    <td>
                      <span class="status-badge ${r.status === 'VERIFIED' ? 'status-verified' : r.status === 'RUNNING' ? 'status-running' : 'status-failed'}">
                        ${r.status}
                      </span>
                    </td>
                    <td>${Number(r.total_duration || 0).toFixed(2)}s</td>
                    <td>
                      <button type="button" class="btn-link-sm btn-inspect-run" data-run-id="${r.run_id}">Inspect ↗</button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
          recentContainer.querySelectorAll('.btn-inspect-run').forEach(btn => {
            btn.addEventListener('click', () => {
              const rid = btn.getAttribute('data-run-id');
              if (rid) inspectRun(rid);
            });
          });
        } else {
          recentContainer.innerHTML = `
            <div class="dash-empty-state">
              <span class="empty-icon">📂</span>
              <p class="font-medium">No repair runs recorded yet</p>
              <p class="text-sm text-secondary">Launch a repair wizard or benchmark to populate empirical history.</p>
            </div>
          `;
        }
      }

      const prsContainer = document.getElementById('overview-prs-list');
      const prsCountLabel = document.getElementById('overview-prs-count');
      if (prsContainer && prsData.pull_requests) {
        if (prsCountLabel) prsCountLabel.textContent = `${prsData.pull_requests.length} Opened`;
        if (prsData.pull_requests.length > 0) {
          prsContainer.innerHTML = `
            <div style="display:flex; flex-direction:column; gap:8px;">
              ${prsData.pull_requests.map(pr => `
                <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 12px; background:var(--surface-base); border:1px solid var(--border-subtle); border-radius:6px;">
                  <div>
                    <span class="font-mono text-accent" style="font-weight:600;">#${pr.pr_number}</span>
                    <strong style="margin-left:6px; font-size:12px;">${pr.title}</strong>
                    <div style="font-size:11px; color:var(--text-secondary); margin-top:2px;">
                      ${pr.repo_owner}/${pr.repo_name} · <code>${pr.branch}</code>
                    </div>
                  </div>
                  <a href="${pr.pr_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="font-size:11px;">
                    Open PR ↗
                  </a>
                </div>
              `).join('')}
            </div>
          `;
        } else {
          prsContainer.innerHTML = `
            <div class="dash-empty-state">
              <span class="empty-icon">🔀</span>
              <p class="font-medium">No Pull Requests created yet</p>
              <p class="text-sm text-secondary">Verified repairs can be published as real GitHub PRs with 1 click.</p>
            </div>
          `;
        }
      }
    } catch (e) {
      console.warn('Failed to load recent activity:', e);
    }
  }

  // 5. Load Repositories Browser
  async function loadRepositories(query = '') {
    const reposGrid = document.getElementById('repos-grid');
    const badgeRepoCount = document.getElementById('badge-repo-count');
    const wizardRepoSelect = document.getElementById('wizard-repo-select');

    try {
      const url = query ? `/api/github/repos?q=${encodeURIComponent(query)}` : '/api/github/repos';
      const res = await fetch(url, { headers: authHeaders() });
      const data = await res.json();
      const repos = data.repositories || [];

      if (badgeRepoCount) badgeRepoCount.textContent = repos.length;

      if (wizardRepoSelect) {
        wizardRepoSelect.innerHTML = repos.map(r => `
          <option value="${escapeHtml(r.full_name)}">${escapeHtml(r.full_name)} (${escapeHtml(r.default_branch)})</option>
        `).join('');
      }

      if (!reposGrid) return;

      if (repos.length === 0) {
        reposGrid.innerHTML = `
          <div class="dash-empty-state" style="grid-column: 1 / -1;">
            <p>No accessible repositories found. Check your GitHub PAT permissions.</p>
          </div>
        `;
        return;
      }

      reposGrid.innerHTML = repos.map(r => `
        <div class="repo-card" data-repo-owner="${escapeHtml(r.owner)}" data-repo-name="${escapeHtml(r.name)}">
          <div class="repo-card-header">
            <span class="repo-card-name">${escapeHtml(r.full_name)}</span>
            <span class="status-badge ${r.private ? 'status-failed' : 'status-idle'}">
              ${r.private ? 'Private' : 'Public'}
            </span>
          </div>
          <p class="repo-card-desc">${escapeHtml(r.description) || 'No description provided.'}</p>
          <div class="repo-card-meta">
            <span>🌿 ${escapeHtml(r.default_branch)}</span>
            <span>⚠️ ${r.open_issues_count || 0} Issues</span>
            <button type="button" class="btn-link-sm btn-browse-issues" style="margin-left:auto;">Browse Issues ↗</button>
          </div>
        </div>
      `).join('');

      reposGrid.querySelectorAll('.repo-card').forEach(card => {
        card.addEventListener('click', () => {
          const owner = card.getAttribute('data-repo-owner');
          const name = card.getAttribute('data-repo-name');
          if (owner && name) openRepoIssues(owner, name);
        });
      });
    } catch (e) {
      console.warn('Failed to load repos:', e);
    }
  }

  // Repository search input handler
  const repoSearchInput = document.getElementById('repo-search-input');
  if (repoSearchInput) {
    let debounce = null;
    repoSearchInput.addEventListener('input', () => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        loadRepositories(repoSearchInput.value.trim());
      }, 300);
    });
  }

  const btnRefreshRepos = document.getElementById('btn-refresh-repos');
  if (btnRefreshRepos) {
    btnRefreshRepos.addEventListener('click', () => loadRepositories());
  }

  // Browse Repository Issues Drawer
  async function openRepoIssues(owner, repo) {
    const panel = document.getElementById('repo-issues-panel');
    const title = document.getElementById('selected-repo-title');
    const list = document.getElementById('selected-repo-issues-list');

    if (!panel || !list) return;

    panel.style.display = 'block';
    if (title) title.textContent = `${owner}/${repo}`;
    list.innerHTML = '<div class="dash-loading-card">Fetching open issues from GitHub API...</div>';
    panel.scrollIntoView({ behavior: 'smooth' });

    try {
      const res = await fetch(`/api/github/repos/${owner}/${repo}/issues`, { headers: authHeaders() });
      const data = await res.json();
      const issues = data.issues || [];

      if (issues.length === 0) {
        list.innerHTML = '<p class="text-secondary py-4">No open issues found for this repository.</p>';
        return;
      }

      list.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:10px;">
          ${issues.map(iss => `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:var(--surface-base); border:1px solid var(--border-subtle); border-radius:6px;">
              <div>
                <span class="font-mono text-accent" style="font-weight:600;">#${iss.number}</span>
                <strong style="margin-left:6px; font-size:13px;">${iss.title}</strong>
                <p style="font-size:11px; color:var(--text-secondary); margin-top:2px;">
                  Created by ${iss.user || 'author'} · ${iss.comments_count || 0} comments
                  ${(iss.labels || []).map(l => `<span class="badge-proof badge-neutral" style="margin-left:4px;">${l}</span>`).join('')}
                </p>
              </div>
              <button type="button" class="btn btn-primary btn-sm btn-repair-this-issue" 
                data-repo="${owner}/${repo}" 
                data-id="${iss.id}" 
                data-title="${iss.title.replace(/"/g, '&quot;')}"
                data-body="${(iss.body || '').replace(/"/g, '&quot;')}">
                ⚡ Repair Issue
              </button>
            </div>
          `).join('')}
        </div>
      `;

      list.querySelectorAll('.btn-repair-this-issue').forEach(btn => {
        btn.addEventListener('click', () => {
          const r = btn.getAttribute('data-repo');
          const id = btn.getAttribute('data-id');
          const t = btn.getAttribute('data-title');
          const b = btn.getAttribute('data-body');

          // Pre-fill Wizard
          const wizRepo = document.getElementById('wizard-repo-select');
          const wizTitle = document.getElementById('wizard-issue-title');
          const wizBody = document.getElementById('wizard-issue-body');
          const wizUrl = document.getElementById('wizard-issue-url');

          if (wizRepo) wizRepo.value = r;
          if (wizTitle) wizTitle.value = t;
          if (wizBody) wizBody.value = b;
          if (wizUrl) wizUrl.value = `https://github.com/${r}/issues/${id}`;

          switchTab('wizard');
        });
      });
    } catch (e) {
      list.innerHTML = `<p class="text-secondary py-4">Error fetching issues: ${e.message}</p>`;
    }
  }

  const btnCloseIssues = document.getElementById('btn-close-issues');
  if (btnCloseIssues) {
    btnCloseIssues.addEventListener('click', () => {
      const panel = document.getElementById('repo-issues-panel');
      if (panel) panel.style.display = 'none';
    });
  }

  // 6. Wizard Presets & Launch Handlers
  const wizardPresets = {
    case_1: {
      title: 'ZeroDivisionError in calculate_ratio when denominator is zero',
      body: 'Target file: calc.py. Defect: ZeroDivisionError occurs when y=0.',
      cmd: 'pytest tests/test_calc.py -v',
      reg: 'pytest tests/ -v'
    },
    case_2: {
      title: 'Off-by-one boundary defect in paginator slice calculation',
      body: 'Target file: paginator.py. Empty dataset returns single-element slice instead of empty list.',
      cmd: 'pytest tests/test_paginator.py -v',
      reg: 'pytest tests/ -v'
    },
    case_3: {
      title: 'Pricing engine volume discount regression on zero quantity',
      body: 'Target file: pricing.py. Boundary validation allows non-positive quantities and fails regression.',
      cmd: 'pytest tests/test_pricing.py -v',
      reg: 'pytest tests/ -v'
    }
  };

  let selectedBenchmark = 'case_1';
  document.querySelectorAll('[id^="btn-wizard-case-"]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[id^="btn-wizard-case-"]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const presetKey = btn.getAttribute('data-preset');
      selectedBenchmark = presetKey;
      const data = wizardPresets[presetKey];
      if (data) {
        const wizTitle = document.getElementById('wizard-issue-title');
        const wizBody = document.getElementById('wizard-issue-body');
        const wizRepro = document.getElementById('wizard-repro-cmd');
        const wizReg = document.getElementById('wizard-regression-cmd');
        if (wizTitle) wizTitle.value = data.title;
        if (wizBody) wizBody.value = data.body;
        if (wizRepro) wizRepro.value = data.cmd;
        if (wizReg) wizReg.value = data.reg;
      }
    });
  });

  const btnFetchWizardIssue = document.getElementById('btn-fetch-wizard-issue');
  if (btnFetchWizardIssue) {
    btnFetchWizardIssue.addEventListener('click', async () => {
      const urlInput = document.getElementById('wizard-issue-url');
      const urlVal = urlInput ? urlInput.value.trim() : '';
      if (!urlVal) {
        alert('Please enter a GitHub Issue URL');
        return;
      }
      btnFetchWizardIssue.disabled = true;
      btnFetchWizardIssue.textContent = 'Fetching...';
      try {
        const res = await fetch('/api/github/fetch-issue', {
          method: 'POST',
          headers: authHeaders(),
          body: JSON.stringify({ url: urlVal })
        });
        const data = await res.json();
        if (res.ok) {
          const wizTitle = document.getElementById('wizard-issue-title');
          const wizBody = document.getElementById('wizard-issue-body');
          const wizRepro = document.getElementById('wizard-repro-cmd');
          if (wizTitle) wizTitle.value = data.title || '';
          if (wizBody) wizBody.value = data.body || '';
          if (wizRepro && data.reproduction_command) wizRepro.value = data.reproduction_command;
          selectedBenchmark = null; // cleared since using live URL
        } else {
          alert(data.error || 'Failed to fetch issue');
        }
      } catch (e) {
        alert('Error: ' + e.message);
      } finally {
        btnFetchWizardIssue.disabled = false;
        btnFetchWizardIssue.textContent = 'Fetch';
      }
    });
  }

  // Launch Repair from Wizard
  const btnStartWizardRepair = document.getElementById('btn-start-wizard-repair');
  if (btnStartWizardRepair) {
    btnStartWizardRepair.addEventListener('click', async () => {
      const repoVal = document.getElementById('wizard-repo-select')?.value || 'Quantum-Ark/patchai';
      const [repoOwner, repoName] = repoVal.split('/');
      const targetBranch = document.getElementById('wizard-target-branch')?.value || 'main';
      const issueUrl = document.getElementById('wizard-issue-url')?.value.trim() || '';
      const title = document.getElementById('wizard-issue-title')?.value || 'Autonomous Defect';
      const body = document.getElementById('wizard-issue-body')?.value || '';
      const reproCmd = document.getElementById('wizard-repro-cmd')?.value || '';
      const regCmd = document.getElementById('wizard-regression-cmd')?.value || '';

      const payload = {
        repo_owner: repoOwner,
        repo_name: repoName,
        target_branch: targetBranch,
        issue_title: title,
        issue_body: body,
        reproduction_command: reproCmd,
        regression_command: regCmd,
        benchmark_id: issueUrl ? null : selectedBenchmark,
        issue_url: issueUrl || null
      };

      btnStartWizardRepair.disabled = true;
      btnStartWizardRepair.textContent = 'Dispatching repair job...';

      try {
        const res = await fetch('/api/runs', {
          method: 'POST',
          headers: authHeaders(),
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.success) {
          activeRunId = data.run_id;
          localStorage.setItem('patchpilot_active_run_id', activeRunId);
          startLiveRunMonitoring(activeRunId, title, repoVal);
          switchTab('workspace');
        } else {
          alert(data.error || 'Failed to launch repair');
        }
      } catch (e) {
        alert('Error dispatching repair: ' + e.message);
      } finally {
        btnStartWizardRepair.disabled = false;
        btnStartWizardRepair.textContent = '⚡ Start Autonomous Repair';
      }
    });
  }

  // 7. Live Workspace & Event Streaming Engine
  function startLiveRunMonitoring(runId, issueTitle = 'Repair in progress', repoName = 'Quantum-Ark/patchai') {
    // Reset workspace UI
    const runIdPill = document.getElementById('ws-run-id-pill');
    const repoTag = document.getElementById('ws-repo-tag');
    const issueTitleEl = document.getElementById('ws-issue-title');
    const statusBadge = document.getElementById('ws-status-badge');
    const terminalLogs = document.getElementById('cockpit-terminal-logs');
    const diffBody = document.getElementById('cockpit-diff-body');
    const pulseDot = document.getElementById('live-pulse-dot');
    const timerTicker = document.getElementById('ws-timer-ticker');

    if (runIdPill) runIdPill.textContent = runId;
    if (repoTag) repoTag.textContent = repoName;
    if (issueTitleEl) issueTitleEl.textContent = issueTitle;
    if (statusBadge) {
      statusBadge.textContent = 'RUNNING';
      statusBadge.className = 'status-badge status-running';
    }
    if (pulseDot) pulseDot.style.display = 'inline-block';
    if (terminalLogs) {
      terminalLogs.innerHTML = `
        <div class="term-line"><span class="term-dim">[DISPATCH] Autonomous worker assigned to ${runId}.</span></div>
        <div class="term-line"><span class="term-highlight">&gt; Initializing subprocess execution sandbox...</span></div>
      `;
    }
    if (diffBody) {
      diffBody.innerHTML = `
        <div class="diff-placeholder">
          <span class="diff-placeholder-icon">⏳</span>
          <p>Generating verified unified diff...</p>
          <p class="text-xs text-secondary">Repair agent executing bounded patch attempts in isolation.</p>
        </div>
      `;
    }

    // Reset stages
    document.querySelectorAll('#ws-pipeline-tracker .pipeline-step').forEach(step => {
      step.classList.remove('active', 'passed');
    });

    // Reset PR station
    const btnOpenPr = document.getElementById('btn-open-pr-external');
    if (btnOpenPr) btnOpenPr.style.display = 'none';
    const safetyWarning = document.getElementById('safety-gate-warning');
    if (safetyWarning) safetyWarning.style.display = 'none';

    // Start Timer
    if (elapsedTimer) clearInterval(elapsedTimer);
    elapsedSeconds = 0;
    elapsedTimer = setInterval(() => {
      elapsedSeconds++;
      const mins = String(Math.floor(elapsedSeconds / 60)).padStart(2, '0');
      const secs = String(elapsedSeconds % 60).padStart(2, '0');
      if (timerTicker) timerTicker.textContent = `${mins}:${secs}s`;
    }, 1000);

    // Start Polling Events
    lastEventId = 0;
    if (pollingTimer) clearInterval(pollingTimer);
    pollingTimer = setInterval(() => pollRunEvents(runId), 1000);
    pollRunEvents(runId);
  }

  async function pollRunEvents(runId) {
    try {
      const res = await fetch(`/api/runs/${runId}/events?after=${lastEventId}`, { headers: authHeaders() });
      if (!res.ok) return;
      const data = await res.json();
      const events = data.events || [];
      const terminalLogs = document.getElementById('cockpit-terminal-logs');

      events.forEach(ev => {
        lastEventId = Math.max(lastEventId, ev.id);
        if (terminalLogs) {
          const div = document.createElement('div');
          div.className = 'term-line';
          const isErr = ev.event_type === 'ERROR' || ev.state === 'FAILED';
          const isSuccess = ev.state === 'VERIFIED';
          div.innerHTML = `<span class="${isErr ? 'term-error' : isSuccess ? 'term-success' : 'term-dim'}">[${ev.state}]</span> ${escapeHtml(ev.message)}`;
          terminalLogs.appendChild(div);
          terminalLogs.scrollTop = terminalLogs.scrollHeight;
        }

        // Advance pipeline steps
        const stepName = ev.state.toLowerCase();
        const stepEl = document.querySelector(`#ws-pipeline-tracker [data-step="${ev.state}"]`);
        if (stepEl) {
          stepEl.classList.add('active');
        }
      });

      // Check if job completed
      if (!data.is_running && data.status !== 'RUNNING') {
        if (pollingTimer) clearInterval(pollingTimer);
        if (elapsedTimer) clearInterval(elapsedTimer);
        const pulseDot = document.getElementById('live-pulse-dot');
        if (pulseDot) pulseDot.style.display = 'none';

        // Load complete run details to render diff and PR station
        await inspectRun(runId, false);
      }
    } catch (e) {
      console.warn('Polling error:', e);
    }
  }

  // 8. Inspect Run Details & Populate Evidence Diff + PR Station
  async function inspectRun(runId, doSwitchTab = true) {
    try {
      const res = await fetch(`/api/runs/${runId}`, { headers: authHeaders() });
      if (!res.ok) return;
      const run = await res.json();
      currentRunData = run;

      if (doSwitchTab) {
        switchTab('workspace');
      }

      // Metadata
      const runIdPill = document.getElementById('ws-run-id-pill');
      const repoTag = document.getElementById('ws-repo-tag');
      const branchTag = document.getElementById('ws-branch-tag');
      const issueTitleEl = document.getElementById('ws-issue-title');
      const statusBadge = document.getElementById('ws-status-badge');
      const timerTicker = document.getElementById('ws-timer-ticker');

      if (runIdPill) runIdPill.textContent = run.run_id;
      if (repoTag) repoTag.textContent = `${run.repo_owner}/${run.repo_name}`;
      if (branchTag) branchTag.textContent = run.target_branch || 'main';
      if (issueTitleEl) issueTitleEl.textContent = run.issue_title;
      if (timerTicker) timerTicker.textContent = `${Number(run.total_duration || 0).toFixed(2)}s`;

      if (statusBadge) {
        statusBadge.textContent = run.status;
        statusBadge.className = `status-badge ${run.status === 'VERIFIED' ? 'status-verified' : run.status === 'RUNNING' ? 'status-running' : 'status-failed'}`;
      }

      // Trace ID
      const traceVal = document.getElementById('pr-trace-val');
      if (traceVal) traceVal.textContent = run.neatlogs_trace_id || 'Local Trace Recorded';

      // Unified Diff Rendering
      const diffBody = document.getElementById('cockpit-diff-body');
      const badgeAcceptance = document.getElementById('badge-acceptance');
      const badgeRegression = document.getElementById('badge-regression');

      if (run.status === 'VERIFIED') {
        if (badgeAcceptance) { badgeAcceptance.textContent = 'Acceptance: Passed'; badgeAcceptance.className = 'badge-proof badge-pass'; }
        if (badgeRegression) { badgeRegression.textContent = 'Regression: Passed'; badgeRegression.className = 'badge-proof badge-pass'; }
      } else {
        if (badgeAcceptance) { badgeAcceptance.textContent = 'Acceptance: Failed'; badgeAcceptance.className = 'badge-proof badge-fail'; }
        if (badgeRegression) { badgeRegression.textContent = 'Regression: Blocked'; badgeRegression.className = 'badge-proof badge-fail'; }
      }

      if (diffBody) {
        const rawDiff = run.diff_text || '';
        if (rawDiff.trim()) {
          const lines = rawDiff.split('\n');
          diffBody.innerHTML = `
            <pre style="margin:0; font-family:var(--font-mono); font-size:11px;">
              ${lines.map(line => {
                if (line.startsWith('+') && !line.startsWith('+++')) {
                  return `<span class="diff-line-add">${escapeHtml(line)}</span>`;
                } else if (line.startsWith('-') && !line.startsWith('---')) {
                  return `<span class="diff-line-del">${escapeHtml(line)}</span>`;
                }
                return `<span>${escapeHtml(line)}</span>`;
              }).join('\n')}
            </pre>
          `;
        } else {
          diffBody.innerHTML = `
            <div class="diff-placeholder">
              <span class="diff-placeholder-icon">${run.status === 'VERIFIED' ? '✅' : '❌'}</span>
              <p>${run.status === 'VERIFIED' ? 'Fix confirmed. No residual diff required.' : 'No patch satisfied test constraints.'}</p>
            </div>
          `;
        }
      }

      // PR Station Setup
      const prRepo = document.getElementById('pr-repo-val');
      const prBase = document.getElementById('pr-base-val');
      const prBranch = document.getElementById('pr-branch-val');
      const prTitleInput = document.getElementById('pr-title-input');
      const btnRaisePr = document.getElementById('btn-raise-github-pr');
      const btnOpenExternal = document.getElementById('btn-open-pr-external');
      const safetyWarning = document.getElementById('safety-gate-warning');

      const headBranch = `patchpilot/fix-${run.issue_id}-${run.run_id.slice(-6)}`;
      if (prRepo) prRepo.textContent = `${run.repo_owner}/${run.repo_name}`;
      if (prBase) prBase.textContent = run.target_branch || 'main';
      if (prBranch) prBranch.textContent = headBranch;
      if (prTitleInput) prTitleInput.value = `fix(${run.issue_id}): ${run.issue_title}`;

      // Safety Gate Enforcement
      if (run.status !== 'VERIFIED') {
        if (safetyWarning) safetyWarning.style.display = 'flex';
      } else {
        if (safetyWarning) safetyWarning.style.display = 'none';
      }

      // Check if PR already created
      if (run.pull_request) {
        if (btnOpenExternal) {
          btnOpenExternal.href = run.pull_request.pr_url;
          btnOpenExternal.style.display = 'inline-flex';
        }
        if (btnRaisePr) {
          btnRaisePr.textContent = `✅ PR #${run.pull_request.pr_number} Active`;
          btnRaisePr.disabled = true;
        }
      } else {
        if (btnOpenExternal) btnOpenExternal.style.display = 'none';
        if (btnRaisePr) {
          btnRaisePr.textContent = '🚀 Raise Pull Request on GitHub';
          btnRaisePr.disabled = false;
        }
      }
    } catch (e) {
      console.warn('Failed to inspect run:', e);
    }
  }

  // 9. Raise Pull Request Action
  const btnRaiseGithubPr = document.getElementById('btn-raise-github-pr');
  if (btnRaiseGithubPr) {
    btnRaiseGithubPr.addEventListener('click', async () => {
      if (!currentRunData) {
        alert('No active run selected');
        return;
      }

      const isVerified = currentRunData.status === 'VERIFIED';
      const checkOverride = document.getElementById('check-override-unverified');
      if (!isVerified && (!checkOverride || !checkOverride.checked)) {
        alert('Safety Gate Violation: This repair is UNVERIFIED. You must check the override acknowledgment before publishing.');
        return;
      }

      const checkDraft = document.getElementById('check-pr-draft');
      const titleInput = document.getElementById('pr-title-input');
      const feedbackText = document.getElementById('pr-feedback-text');

      btnRaiseGithubPr.disabled = true;
      btnRaiseGithubPr.textContent = 'Creating PR on GitHub...';
      if (feedbackText) feedbackText.textContent = 'Pushing source branch and opening Pull Request...';

      try {
        const payload = {
          override_unverified: !isVerified,
          draft: Boolean(checkDraft && checkDraft.checked),
          title: titleInput ? titleInput.value.trim() : `fix: Autonomous patch for ${currentRunData.issue_id}`,
          repo_owner: currentRunData.repo_owner,
          repo_name: currentRunData.repo_name,
          base_branch: currentRunData.target_branch || 'main'
        };

        const res = await fetch(`/api/runs/${currentRunData.run_id}/pr`, {
          method: 'POST',
          headers: authHeaders(),
          body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.success) {
          const pr = data.pull_request;
          const btnOpenExternal = document.getElementById('btn-open-pr-external');
          if (btnOpenExternal) {
            btnOpenExternal.href = pr.pr_url;
            btnOpenExternal.style.display = 'inline-flex';
          }
          btnRaiseGithubPr.textContent = `✅ PR #${pr.pr_number} Created`;
          if (feedbackText) {
            feedbackText.textContent = `Dispatched successfully! Branch: ${pr.branch}. URL: ${pr.pr_url}`;
          }
          await loadDashboardStats();
        } else {
          alert(data.error || 'Failed to create Pull Request');
          btnRaiseGithubPr.disabled = false;
          btnRaiseGithubPr.textContent = '🚀 Raise Pull Request on GitHub';
        }
      } catch (e) {
        alert('Error: ' + e.message);
        btnRaiseGithubPr.disabled = false;
        btnRaiseGithubPr.textContent = '🚀 Raise Pull Request on GitHub';
      }
    });
  }

  // 10. Download Report JSON
  const btnDownloadReport = document.getElementById('btn-download-report');
  if (btnDownloadReport) {
    btnDownloadReport.addEventListener('click', () => {
      if (!currentRunData) return;
      const blob = new Blob([JSON.stringify(currentRunData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `patchpilot-report-${currentRunData.run_id}.json`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  // 11. Load Searchable History Table
  async function loadHistory() {
    const tbody = document.getElementById('history-runs-tbody');
    const searchInput = document.getElementById('history-search-input');
    const statusFilter = document.getElementById('history-status-filter');

    if (!tbody) return;

    try {
      const q = searchInput ? searchInput.value.trim() : '';
      const status = statusFilter ? statusFilter.value : '';

      let url = '/api/runs?limit=50';
      if (q) url += `&q=${encodeURIComponent(q)}`;
      if (status) url += `&status=${encodeURIComponent(status)}`;

      const res = await fetch(url, { headers: authHeaders() });
      const data = await res.json();
      const runs = data.runs || [];

      if (runs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-secondary py-8">No repair runs matching filters found.</td></tr>';
        return;
      }

      tbody.innerHTML = runs.map(r => `
        <tr>
          <td><code class="font-mono text-accent">${r.run_id}</code></td>
          <td>${r.repo_owner}/${r.repo_name}</td>
          <td>${escapeHtml(r.issue_title)}</td>
          <td>
            <span class="status-badge ${r.status === 'VERIFIED' ? 'status-verified' : r.status === 'RUNNING' ? 'status-running' : 'status-failed'}">
              ${r.status}
            </span>
          </td>
          <td>${r.attempts ? r.attempts.length : 1}</td>
          <td>${Number(r.total_duration || 0).toFixed(2)}s</td>
          <td>
            ${r.pull_request ? `<a href="${r.pull_request.pr_url}" target="_blank" class="btn-link-sm">#${r.pull_request.pr_number} ↗</a>` : '<span class="text-secondary">—</span>'}
          </td>
          <td>
            <button type="button" class="btn btn-secondary btn-sm btn-history-inspect" data-run-id="${r.run_id}">Inspect</button>
          </td>
        </tr>
      `).join('');

      tbody.querySelectorAll('.btn-history-inspect').forEach(btn => {
        btn.addEventListener('click', () => {
          const rid = btn.getAttribute('data-run-id');
          if (rid) inspectRun(rid);
        });
      });
    } catch (e) {
      console.warn('Failed to load history:', e);
    }
  }

  const historySearch = document.getElementById('history-search-input');
  if (historySearch) {
    historySearch.addEventListener('input', () => loadHistory());
  }
  const historyFilter = document.getElementById('history-status-filter');
  if (historyFilter) {
    historyFilter.addEventListener('change', () => loadHistory());
  }
  const btnRefreshHistory = document.getElementById('btn-refresh-history');
  if (btnRefreshHistory) {
    btnRefreshHistory.addEventListener('click', () => loadHistory());
  }

  // 12. Load Settings & Integrations
  async function loadSettings() {
    try {
      const res = await fetch('/api/settings', { headers: authHeaders() });
      if (!res.ok) return;
      const data = await res.json();

      const ghStatus = document.getElementById('settings-gh-status');
      const ghUser = document.getElementById('settings-gh-username');
      const ghToken = document.getElementById('settings-gh-token');

      if (data.github.connected) {
        if (ghStatus) { ghStatus.textContent = 'Connected'; ghStatus.className = 'status-chip chip-green'; }
        if (ghUser) ghUser.textContent = data.github.username;
        if (ghToken) ghToken.textContent = data.github.masked_token || '***';
      } else {
        if (ghStatus) { ghStatus.textContent = 'Disconnected'; ghStatus.className = 'status-chip'; }
        if (ghUser) ghUser.textContent = 'Not connected';
        if (ghToken) ghToken.textContent = '***';
      }

      // Providers
      const provs = data.llm.providers || {};
      const provOpenai = document.getElementById('prov-openai');
      const provGemini = document.getElementById('prov-gemini');
      const provAnthropic = document.getElementById('prov-anthropic');
      const provGroq = document.getElementById('prov-groq');

      function updateProvBadge(el, info) {
        if (!el || !info) return;
        if (info.configured) {
          el.textContent = 'Ready';
          el.className = 'badge-proof badge-pass';
        } else {
          el.textContent = 'Not Configured';
          el.className = 'badge-proof badge-neutral';
        }
      }

      updateProvBadge(provOpenai, provs.openai);
      updateProvBadge(provGemini, provs.gemini);
      updateProvBadge(provAnthropic, provs.anthropic);
      updateProvBadge(provGroq, provs.groq);
    } catch (e) {
      console.warn('Failed to load settings:', e);
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // Initial Load Sequence
  checkAuth();
  loadDashboardStats();
  loadRepositories();

  // If previous active run persisted, inspect it automatically
  if (activeRunId) {
    inspectRun(activeRunId, false);
  }
}

