/**
 * PatchPilot AI — Built Under the Surface
 * Reverse-Engineered Interactive Engine (Inspired by metic.studio)
 * 
 * Features:
 * 1. 8-Stage Sticky Scroll Build Engine with real scroll-driven percentages (000% - 100%)
 * 2. Signature Inspection Lens (X-Ray) backed by actual DOM geometry and SVG projection
 * 3. Pointer-Responsive Capabilities Fan with dynamic flex expansion
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
  initCapabilitiesFan();
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

  // Retrieve stored theme or match system preference
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
   02 — SUBTLE AUDIO FEEDBACK SYNTHESIZER
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
   03 — PHASE 4: 8-STAGE SCROLL-DRIVEN CONSTRUCTION STORY
   ========================================================================== */
function initBuildScrollSequence() {
  const section = document.getElementById('build-sequence');
  const pctDisplay = document.getElementById('build-pct-num');
  const navProgressFill = document.getElementById('nav-progress-fill');
  const navStepLabel = document.getElementById('nav-step-label');
  const skipBtn = document.getElementById('btn-skip-build');

  const stageVisuals = document.querySelectorAll('.stage-visual');
  const captionSlides = document.querySelectorAll('.caption-slide');

  if (!section || !pctDisplay) return;

  const stageTitles = [
    '01 / 08 · A line',
    '02 / 08 · A grid',
    '03 / 08 · A layout',
    '04 / 08 · A typeface',
    '05 / 08 · A colour',
    '06 / 08 · A line of code',
    '07 / 08 · Online',
    '08 / 08 · Your turn'
  ];

  let currentStageIdx = 1;

  function onScroll() {
    const rect = section.getBoundingClientRect();
    const sectionTop = rect.top;
    const sectionHeight = rect.height;
    const windowHeight = window.innerHeight;

    // Calculate normalized scroll progress through sticky section (0..1)
    const totalScrollable = sectionHeight - windowHeight;
    let progress = -sectionTop / totalScrollable;
    progress = Math.max(0, Math.min(1, progress));

    const pct = Math.round(progress * 100);
    pctDisplay.textContent = String(pct).padStart(3, '0');

    if (navProgressFill) {
      navProgressFill.style.width = `${pct}%`;
    }

    // Determine current stage index (1 to 8)
    const stage = Math.min(8, Math.max(1, Math.floor(progress * 8) + 1));
    if (stage !== currentStageIdx) {
      currentStageIdx = stage;

      if (navStepLabel) {
        navStepLabel.textContent = stageTitles[stage - 1];
      }

      // Update center visual
      stageVisuals.forEach((vis) => {
        const visIdx = parseInt(vis.getAttribute('data-stage-vis'), 10);
        vis.classList.toggle('is-active', visIdx === stage);
      });

      // Update bottom caption
      captionSlides.forEach((slide) => {
        const slideIdx = parseInt(slide.getAttribute('data-step-index'), 10);
        slide.classList.toggle('is-active', slideIdx === stage);
      });

      playClickSound();
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Accessible Skip the Build button
  if (skipBtn) {
    skipBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const target = document.getElementById('principle-section');
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  }
}

/* ==========================================================================
   04 — PHASE 3: SIGNATURE INSPECTION LENS (X-RAY LAYER)
   ========================================================================== */
function initInspectionLens() {
  const lensLayer = document.getElementById('inspection-lens-layer');
  const lensCircle = document.getElementById('lens-circle');
  const blueprintLayer = document.getElementById('blueprint-guide-layer');
  const blueprintSvg = document.getElementById('blueprint-svg');
  
  const navXrayBtn = document.getElementById('btn-nav-xray');
  const floatingXrayBtn = document.getElementById('btn-floating-xray');
  const floatingLabel = document.getElementById('floating-xray-label');
  const statusBubble = document.getElementById('xray-status-bubble');
  const heroPrompt = document.getElementById('btn-hero-inspect-prompt');

  const readoutCoord = document.getElementById('readout-coord');
  const readoutTarget = document.getElementById('readout-target');
  const readoutDim = document.getElementById('readout-dim');
  const readoutToken = document.getElementById('readout-token');

  if (!lensLayer || !lensCircle || !blueprintSvg) return;

  let isInspecting = false;
  let isLockedToggle = false;
  let isMouseDown = false;
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let rafId = null;

  function activateLens(x, y) {
    isInspecting = true;
    document.body.classList.add('is-inspecting');
    lensLayer.classList.add('is-active');
    blueprintLayer.classList.add('is-visible');
    
    if (navXrayBtn) navXrayBtn.classList.add('is-active');
    if (floatingXrayBtn) floatingXrayBtn.classList.add('is-active');
    if (statusBubble) statusBubble.textContent = 'INSPECTING ARCHITECTURAL UNDERNEATH';

    updateLensPosition(x, y);
    renderBlueprintOverlay();
    playClickSound();
  }

  function deactivateLens() {
    if (isLockedToggle) return;
    isInspecting = false;
    document.body.classList.remove('is-inspecting');
    lensLayer.classList.remove('is-active');
    blueprintLayer.classList.remove('is-visible');

    if (navXrayBtn) navXrayBtn.classList.remove('is-active');
    if (floatingXrayBtn) floatingXrayBtn.classList.remove('is-active');
    if (statusBubble) statusBubble.textContent = 'Hold mouse or Space to reveal the architecture underneath';

    blueprintSvg.innerHTML = '';
  }

  function updateLensPosition(x, y) {
    mouseX = x;
    mouseY = y;

    lensCircle.style.left = `${x}px`;
    lensCircle.style.top = `${y}px`;

    // Clip dark blueprint layer so only the 280px circular window shows underneath!
    const clipStyle = `circle(140px at ${x}px ${y}px)`;
    blueprintLayer.style.clipPath = clipStyle;
    blueprintLayer.style.webkitClipPath = clipStyle;

    if (readoutCoord) {
      readoutCoord.textContent = `X: ${Math.round(x)}  Y: ${Math.round(y)}`;
    }

    // Inspect underlying element
    const elem = document.elementFromPoint(x, y);
    if (elem) {
      const inspectLabel = elem.closest('[data-inspect-label]')?.getAttribute('data-inspect-label')
        || elem.getAttribute('id')
        || elem.tagName.toLowerCase();
      const rect = elem.getBoundingClientRect();
      const cs = window.getComputedStyle(elem);

      if (readoutTarget) readoutTarget.textContent = `<${inspectLabel}>`;
      if (readoutDim) readoutDim.textContent = `W: ${Math.round(rect.width)}px  H: ${Math.round(rect.height)}px`;

      if (readoutToken) {
        if (cs.fontSize && cs.fontSize !== '0px') {
          readoutToken.textContent = `font: ${cs.fontSize} / pad: ${cs.padding.split(' ')[0]}`;
        } else {
          readoutToken.textContent = '--surface-base: #F4F1E9';
        }
      }
    }

    scheduleBlueprintRedraw();
  }

  function scheduleBlueprintRedraw() {
    if (rafId) return;
    rafId = requestAnimationFrame(() => {
      rafId = null;
      if (isInspecting) {
        renderBlueprintOverlay();
      }
    });
  }

  // Draw real DOM element boundaries, guides, and technical measurements in SVG
  function renderBlueprintOverlay() {
    const inspectables = document.querySelectorAll('[data-inspect-label], .rule, .btn, .stage-visual, .fan-card, .diff-card-box');
    let svgMarkup = '';

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    // Crosshairs through cursor
    svgMarkup += `
      <line x1="0" y1="${mouseY}" x2="${vw}" y2="${mouseY}" stroke="rgba(255, 255, 255, 0.2)" stroke-width="0.8"/>
      <line x1="${mouseX}" y1="0" x2="${mouseX}" y2="${vh}" stroke="rgba(255, 255, 255, 0.2)" stroke-width="0.8"/>
    `;

    // Real element boundaries
    inspectables.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.bottom >= 0 && rect.top <= vh) {
        const tag = el.getAttribute('data-inspect-label') || el.id || el.tagName.toLowerCase();
        
        const isHovered = (mouseX >= rect.left && mouseX <= rect.right && mouseY >= rect.top && mouseY <= rect.bottom);
        const strokeColor = isHovered ? '#F04438' : 'rgba(130, 223, 255, 0.65)';
        const strokeWidth = isHovered ? '1.5' : '0.8';
        const fillCol = isHovered ? 'rgba(240, 68, 56, 0.08)' : 'rgba(44, 130, 201, 0.04)';

        svgMarkup += `
          <rect x="${rect.left}" y="${rect.top}" width="${rect.width}" height="${rect.height}" 
                fill="${fillCol}" stroke="${strokeColor}" stroke-width="${strokeWidth}" stroke-dasharray="${isHovered ? 'none' : '4 4'}"/>
          <text x="${rect.left + 6}" y="${rect.top + 14}" fill="${isHovered ? '#F04438' : '#82DFFF'}" font-family="'JetBrains Mono', monospace" font-size="10">
            &lt;${tag}&gt; ${Math.round(rect.width)}×${Math.round(rect.height)}px
          </text>
        `;
      }
    });

    blueprintSvg.innerHTML = svgMarkup;
  }

  function toggleLockInspection() {
    isLockedToggle = !isLockedToggle;
    if (isLockedToggle) {
      if (floatingLabel) floatingLabel.textContent = 'X-RAY [LOCKED]';
      activateLens(mouseX, mouseY);
    } else {
      if (floatingLabel) floatingLabel.textContent = 'X-RAY [HOLD SPACE]';
      deactivateLens();
    }
  }

  // Bind Buttons
  [navXrayBtn, floatingXrayBtn, heroPrompt].forEach((btn) => {
    if (btn) {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        toggleLockInspection();
      });
    }
  });

  // Mouse Hold Listeners
  window.addEventListener('mousedown', (e) => {
    if (e.target.closest('a, button, input, textarea, select, .fan-card, .btn-diff-tab')) return;
    isMouseDown = true;
    activateLens(e.clientX, e.clientY);
  });

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    if (isInspecting && (isMouseDown || isLockedToggle)) {
      updateLensPosition(mouseX, mouseY);
    }
  });

  window.addEventListener('mouseup', () => {
    isMouseDown = false;
    if (!isLockedToggle) {
      deactivateLens();
    }
  });

  // Touch Support
  window.addEventListener('touchstart', (e) => {
    if (e.target.closest('a, button, input, textarea, select, .fan-card')) return;
    const touch = e.touches[0];
    isMouseDown = true;
    activateLens(touch.clientX, touch.clientY);
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    if (isInspecting && e.touches[0]) {
      updateLensPosition(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  window.addEventListener('touchend', () => {
    isMouseDown = false;
    if (!isLockedToggle) {
      deactivateLens();
    }
  });

  // Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    if (e.target.closest('input, textarea')) return;
    if (e.code === 'Space') {
      e.preventDefault();
      if (!isInspecting) {
        activateLens(mouseX, mouseY);
      }
    } else if (e.key === 'x' || e.key === 'X') {
      toggleLockInspection();
    } else if (e.code === 'Escape' && isLockedToggle) {
      toggleLockInspection();
    }
  });

  window.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && !isLockedToggle) {
      deactivateLens();
    }
  });

  window.addEventListener('scroll', () => {
    if (isInspecting) {
      scheduleBlueprintRedraw();
    }
  }, { passive: true });
}

/* ==========================================================================
   05 — PHASE 5: POINTER-RESPONSIVE CAPABILITIES FAN
   ========================================================================== */
function initCapabilitiesFan() {
  const fanCards = document.querySelectorAll('.fan-card');
  if (!fanCards.length) return;

  fanCards.forEach((card) => {
    // Desktop hover & focus activation
    card.addEventListener('mouseenter', () => {
      fanCards.forEach((c) => c.classList.remove('is-active'));
      card.classList.add('is-active');
      playClickSound();
    });

    card.addEventListener('focus', () => {
      fanCards.forEach((c) => c.classList.remove('is-active'));
      card.classList.add('is-active');
    });

    // Mobile / click toggle
    card.addEventListener('click', () => {
      fanCards.forEach((c) => c.classList.remove('is-active'));
      card.classList.add('is-active');
    });
  });
}

/* ==========================================================================
   06 — PHASE 7: LIVE DRAFT BRIEF GENERATOR
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

  if (!fRepo || !livePreview) return;

  function updateDraft() {
    const repo = fRepo.value.trim() || 'https://github.com/Quantum-Ark/patchai';
    const rawIssue = fIssue.value.trim() || 'Describe issue';
    const testCmd = fTest.value.trim() || 'pytest';
    const attempts = fAttempts.value || '3';

    // Sanitize issue string for CLI
    const issueSummary = rawIssue.replace(/[\r\n]+/g, ' ').slice(0, 60);

    const generatedCmd = `patchpilot run --repo ${repo} --issue "${issueSummary}" --test "${testCmd}" --max-attempts ${attempts}`;
    livePreview.textContent = generatedCmd;

    // Calculate real completion percentage
    let score = 0;
    if (fRepo.value.trim()) score += 35;
    if (fIssue.value.trim().length > 10) score += 35;
    if (fTest.value.trim()) score += 20;
    if (fAttempts.value) score += 10;

    if (pctDisplay) {
      pctDisplay.textContent = `${score}%`;
    }
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
   07 — PHASE 6C: INTERACTIVE CODE DIFF SHOWCASE
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
