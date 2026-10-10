/**
 * PatchPilot AI — Built Under the Surface
 * Interactive Architecture & Inspection Lens Engine
 * Inspired by metic.studio design philosophy
 */

document.addEventListener('DOMContentLoaded', () => {
  initInspectionLens();
  initDiffViewer();
  initCodebaseTree();
  initDefectInteraction();
  initTraceCopy();
  initScrollAssembly();
});

/* ==========================================================================
   03 — SIGNATURE INTERACTION: THE INSPECTION LENS
   ========================================================================== */
function initInspectionLens() {
  const lensLayer = document.getElementById('inspection-lens-layer');
  const lensCircle = document.getElementById('lens-circle');
  const blueprintLayer = document.getElementById('blueprint-guide-layer');
  const blueprintSvg = document.getElementById('blueprint-svg');
  const toggleBtn = document.getElementById('btn-inspect-toggle');
  const toggleLabel = document.getElementById('inspect-toggle-label');
  const statusHint = document.getElementById('inspect-status-hint');

  const readoutCoord = document.getElementById('readout-coord');
  const readoutTarget = document.getElementById('readout-target');
  const readoutDim = document.getElementById('readout-dim');
  const readoutToken = document.getElementById('readout-token');

  if (!lensLayer || !lensCircle || !blueprintSvg) return;

  let isInspecting = false;
  let isLockedToggle = false;
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;

  // Design tokens to display dynamically in the readout
  const tokenSamples = [
    '--bg-canvas: #F4F1E9',
    '--text-primary: #151515',
    '--signal-accent: #F04438',
    '--verified-state: #1E5631',
    '--rule-fine: #D4D0C5',
    '--font-mono: JetBrains Mono',
    '--bg-dark-inspection: #171816'
  ];

  function activateLens(x, y) {
    isInspecting = true;
    lensLayer.classList.add('is-active');
    blueprintLayer.classList.add('is-visible');
    if (toggleBtn) toggleBtn.classList.add('is-active');
    if (statusHint) statusHint.textContent = 'INSPECTING ARCHITECTURAL UNDERNEATH';
    updateLensPosition(x, y);
    renderBlueprintOverlay();
  }

  function deactivateLens() {
    if (isLockedToggle) return;
    isInspecting = false;
    lensLayer.classList.remove('is-active');
    blueprintLayer.classList.remove('is-visible');
    if (toggleBtn) toggleBtn.classList.remove('is-active');
    if (statusHint) statusHint.textContent = 'Press & hold anywhere to reveal the architecture underneath';
    blueprintSvg.innerHTML = '';
  }

  function updateLensPosition(x, y) {
    mouseX = x;
    mouseY = y;
    lensCircle.style.left = `${x}px`;
    lensCircle.style.top = `${y}px`;

    if (readoutCoord) {
      readoutCoord.textContent = `X: ${Math.round(x)}  Y: ${Math.round(y)}`;
    }

    // Identify underlying element
    const elem = document.elementFromPoint(x, y);
    if (elem) {
      const inspectLabel = elem.closest('[data-inspect-label]')?.getAttribute('data-inspect-label')
        || elem.tagName.toLowerCase();
      const rect = elem.getBoundingClientRect();

      if (readoutTarget) readoutTarget.textContent = `<${inspectLabel}>`;
      if (readoutDim) readoutDim.textContent = `${Math.round(rect.width)} × ${Math.round(rect.height)} px`;

      // Pseudo-random token display based on element hash
      if (readoutToken) {
        const tokenIdx = Math.abs((Math.round(x) + Math.round(y)) % tokenSamples.length);
        readoutToken.textContent = tokenSamples[tokenIdx];
      }
    }
  }

  // Draw real DOM element boundaries and measurement hairlines into SVG
  function renderBlueprintOverlay() {
    const inspectables = document.querySelectorAll('[data-inspect-label], .stage-guide-bar, .hero-editorial-col, .hero-schematic-col, .diff-toggle-bar');
    let svgMarkup = '';

    const vw = window.innerWidth;
    const vh = window.innerHeight;

    inspectables.forEach((el) => {
      const rect = el.getBoundingClientRect();
      // Only draw if inside viewport or nearby
      if (rect.bottom >= 0 && rect.top <= vh) {
        const tag = el.getAttribute('data-inspect-label') || el.className.split(' ')[0] || el.tagName.toLowerCase();
        
        // Hairline boundary rect
        svgMarkup += `
          <rect x="${rect.left}" y="${rect.top}" width="${rect.width}" height="${rect.height}" 
                fill="rgba(44, 130, 201, 0.03)" stroke="rgba(44, 130, 201, 0.45)" stroke-width="1" stroke-dasharray="3 3"/>
          <text x="${rect.left + 6}" y="${rect.top + 14}" fill="#2C82C9" font-family="'JetBrains Mono', monospace" font-size="10">
            &lt;${tag}&gt; ${Math.round(rect.width)}×${Math.round(rect.height)}
          </text>
        `;

        // Horizontal and vertical guide lines
        svgMarkup += `
          <line x1="0" y1="${rect.top}" x2="${vw}" y2="${rect.top}" stroke="rgba(212, 208, 197, 0.25)" stroke-width="0.5"/>
          <line x1="${rect.left}" y1="0" x2="${rect.left}" y2="${vh}" stroke="rgba(212, 208, 197, 0.25)" stroke-width="0.5"/>
        `;
      }
    });

    blueprintSvg.innerHTML = svgMarkup;
  }

  // Mouse Hold Listener
  window.addEventListener('mousedown', (e) => {
    // Avoid triggering on links or buttons unless explicitly desired
    if (e.target.closest('a, button, input, textarea')) return;
    activateLens(e.clientX, e.clientY);
  });

  window.addEventListener('mousemove', (e) => {
    if (isInspecting) {
      updateLensPosition(e.clientX, e.clientY);
    }
  });

  window.addEventListener('mouseup', () => {
    deactivateLens();
  });

  // Touch Support (Press & Hold)
  let touchTimer = null;
  window.addEventListener('touchstart', (e) => {
    if (e.target.closest('a, button')) return;
    const touch = e.touches[0];
    touchTimer = setTimeout(() => {
      activateLens(touch.clientX, touch.clientY);
    }, 280);
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    if (isInspecting && e.touches[0]) {
      updateLensPosition(e.touches[0].clientX, e.touches[0].clientY);
    }
  }, { passive: true });

  window.addEventListener('touchend', () => {
    if (touchTimer) clearTimeout(touchTimer);
    deactivateLens();
  });

  // Accessible Keyboard Hold ([Space] or [KeyI])
  window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && !e.target.closest('input, textarea')) {
      e.preventDefault();
      if (!isInspecting) {
        activateLens(mouseX, mouseY);
      }
    }
  });

  window.addEventListener('keyup', (e) => {
    if (e.code === 'Space' && !isLockedToggle) {
      deactivateLens();
    }
  });

  // Toggle Button Click
  if (toggleBtn) {
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      isLockedToggle = !isLockedToggle;
      if (isLockedToggle) {
        toggleLabel.textContent = 'INSPECT MODE [ACTIVE]';
        activateLens(mouseX, mouseY);
      } else {
        toggleLabel.textContent = 'HOLD TO INSPECT [SPACE]';
        deactivateLens();
      }
    });
  }

  // Redraw blueprint guides on scroll when active
  window.addEventListener('scroll', () => {
    if (isInspecting) {
      renderBlueprintOverlay();
    }
  }, { passive: true });
}

/* ==========================================================================
   04 — STAGE 06: CODE SURGERY DIFF
   ========================================================================== */
function initDiffViewer() {
  const diffBody = document.getElementById('edc-content-body');
  const statsText = document.getElementById('edc-stats-text');
  const btnAfter = document.getElementById('btn-show-after');
  const btnBefore = document.getElementById('btn-show-before');
  const btnAttempt1 = document.getElementById('btn-show-attempt1');

  if (!diffBody) return;

  const diffData = {
    after: {
      stats: '+3 lines · Verified Surgical Validation',
      rows: [
        { num: 12, sign: ' ', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -> float:', cls: '' },
        { num: 13, sign: ' ', text: '    """Calculates final price with tiered volume discounts."""', cls: '' },
        { num: 14, sign: ' ', text: '    if base_price < 0:', cls: '' },
        { num: 15, sign: ' ', text: '        raise ValueError("base_price cannot be negative")', cls: '' },
        { num: 16, sign: '+', text: '    if volume < 0:', cls: 'diff-row-add' },
        { num: 17, sign: '+', text: '        raise ValueError("volume cannot be negative")', cls: 'diff-row-add' },
        { num: 18, sign: ' ', text: '    multiplier = 0.80 if is_vip else 1.0', cls: '' },
        { num: 19, sign: ' ', text: '    return base_price * volume * multiplier', cls: '' }
      ]
    },
    before: {
      stats: '0 changes · Defective (Missing Volume Validation)',
      rows: [
        { num: 12, sign: ' ', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -> float:', cls: '' },
        { num: 13, sign: ' ', text: '    """Calculates final price with tiered volume discounts."""', cls: '' },
        { num: 14, sign: ' ', text: '    if base_price < 0:', cls: '' },
        { num: 15, sign: ' ', text: '        raise ValueError("base_price cannot be negative")', cls: '' },
        { num: 16, sign: '-', text: '    # Missing check: volume < 0 produces negative bill total', cls: 'diff-row-del' },
        { num: 17, sign: '-', text: '    multiplier = 0.80 if is_vip else 1.0', cls: 'diff-row-del' },
        { num: 18, sign: '-', text: '    return base_price * volume * multiplier', cls: 'diff-row-del' }
      ]
    },
    attempt1: {
      stats: '+1 -1 lines · Regression in test_vip_discount',
      rows: [
        { num: 12, sign: ' ', text: 'def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -> float:', cls: '' },
        { num: 13, sign: ' ', text: '    """Calculates final price with tiered volume discounts."""', cls: '' },
        { num: 14, sign: ' ', text: '    if base_price < 0:', cls: '' },
        { num: 15, sign: ' ', text: '        raise ValueError("base_price cannot be negative")', cls: '' },
        { num: 16, sign: '-', text: '    multiplier = 0.80 if is_vip else 1.0', cls: 'diff-row-del' },
        { num: 17, sign: '-', text: '    return base_price * volume * multiplier', cls: 'diff-row-del' },
        { num: 16, sign: '+', text: '    # Naive Clamp Attempt #1 (Overwrote VIP discount)', cls: 'diff-row-del' },
        { num: 17, sign: '+', text: '    return base_price * max(0, volume)', cls: 'diff-row-del' }
      ]
    }
  };

  function renderDiff(key) {
    [btnAfter, btnBefore, btnAttempt1].forEach(b => b && b.classList.remove('active'));
    if (key === 'after' && btnAfter) btnAfter.classList.add('active');
    if (key === 'before' && btnBefore) btnBefore.classList.add('active');
    if (key === 'attempt1' && btnAttempt1) btnAttempt1.classList.add('active');

    const data = diffData[key];
    if (!data) return;

    if (statsText) statsText.textContent = data.stats;

    diffBody.innerHTML = data.rows.map(r => `
      <div class="diff-row ${r.cls}">
        <span class="diff-num">${r.num}</span>
        <span class="diff-sign">${r.sign}</span>
        <span class="diff-text">${r.text}</span>
      </div>
    `).join('');
  }

  if (btnAfter) btnAfter.addEventListener('click', () => renderDiff('after'));
  if (btnBefore) btnBefore.addEventListener('click', () => renderDiff('before'));
  if (btnAttempt1) btnAttempt1.addEventListener('click', () => renderDiff('attempt1'));

  // Default to verified after
  renderDiff('after');
}

/* ==========================================================================
   04 — STAGE 02: CODEBASE TREE INTERACTION
   ========================================================================== */
function initCodebaseTree() {
  const items = document.querySelectorAll('.tree-item');
  const roleDesc = document.getElementById('tree-role-desc');

  const descriptions = {
    'pricing.py': '<code>src/pricing.py</code> contains the defective <code>calculate_tiered_price</code> calculation. AST parser mapped 1 candidate function and 2 call sites.',
    'test_pricing.py': '<code>tests/test_pricing.py</code> provides the baseline reproduction harness. Executes <code>test_negative_input</code> and validates expected exceptions.',
    'test_regression.py': '<code>tests/test_regression.py</code> tests existing VIP volume discounts (<code>test_vip_discount</code>). Intercepts regressions before any patch is accepted.',
    'models.py': '<code>src/models.py</code> defines customer tier data classes and discount thresholds. Unaffected by this defect; isolated from modifications.'
  };

  items.forEach(item => {
    item.addEventListener('click', () => {
      items.forEach(i => i.classList.remove('is-selected'));
      item.classList.add('is-selected');

      const fileKey = item.getAttribute('data-file');
      if (roleDesc && descriptions[fileKey]) {
        roleDesc.innerHTML = descriptions[fileKey];
      }
    });
  });
}

/* ==========================================================================
   04 — STAGE 01: DEFECT MARKER INTERACTION
   ========================================================================== */
function initDefectInteraction() {
  const markerBtn = document.getElementById('defect-marker-btn');
  const cardBody = document.getElementById('defect-card-body');

  if (markerBtn && cardBody) {
    markerBtn.addEventListener('click', () => {
      cardBody.style.borderColor = 'var(--signal-accent)';
      cardBody.style.backgroundColor = 'rgba(240, 68, 56, 0.04)';
      setTimeout(() => {
        cardBody.style.borderColor = 'var(--rule-fine)';
        cardBody.style.backgroundColor = 'var(--bg-canvas)';
      }, 1200);
    });
  }
}

/* ==========================================================================
   04 — STAGE 07: TRACE ID COPY UTILITY
   ========================================================================== */
function initTraceCopy() {
  const copyBtn = document.getElementById('btn-copy-trace');
  const traceCode = document.getElementById('proof-trace-id');

  if (copyBtn && traceCode) {
    copyBtn.addEventListener('click', async () => {
      const text = traceCode.textContent.trim();
      try {
        await navigator.clipboard.writeText(text);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'Copied!';
        copyBtn.style.borderColor = 'var(--verified-state)';
        copyBtn.style.color = 'var(--verified-state)';
        setTimeout(() => {
          copyBtn.textContent = originalText;
          copyBtn.style.borderColor = 'var(--rule-fine)';
          copyBtn.style.color = 'var(--text-secondary)';
        }, 2000);
      } catch (err) {
        console.warn('Clipboard write error:', err);
      }
    });
  }
}

/* ==========================================================================
   04 — SCROLL-DRIVEN STAGE PROGRESSION
   ========================================================================== */
function initScrollAssembly() {
  const stages = document.querySelectorAll('.assembly-stage');
  if (!stages.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-active-stage');
      }
    });
  }, {
    threshold: 0.2
  });

  stages.forEach(stage => observer.observe(stage));
}
