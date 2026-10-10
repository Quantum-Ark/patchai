/**
 * PatchPilot AI — The Code Forge
 * Master Interaction, 3D Particle Sculpture & Motion Engine
 * 
 * Art Direction:
 * - 3D Particle Mesh with Perspective Projection, Curved Strands, & Broken Node Branch
 * - Interactive Local Displacement & Spring Recovery Physics
 * - Defect Investigation State Machine (Idle -> Inspecting -> Rollback -> Verified Green)
 * - Precision Desktop Custom Cursor with Magnetic Attraction & "INSPECT" Badge
 * - Continuous Scroll-Linked Scene Narrative Detection (Scenes A - F)
 * - Interactive Code Diff Showcase (Before / Attempt #1 Regression / Attempt #2 Verified)
 * - Telemetry Trace Explorer with Working Clipboard Utility
 */

document.addEventListener('DOMContentLoaded', () => {
  initPrecisionCursor();
  init3DParticleSculpture();
  initScrollNarrative();
  initDiffShowcase();
  initTraceExplorer();
  initMagneticButtons();
});

/* ==========================================================================
   01 — PRECISION CUSTOM DESKTOP CURSOR
   ========================================================================== */
function initPrecisionCursor() {
  const halo = document.getElementById('cursor-halo');
  const point = document.getElementById('cursor-point');
  const badge = document.getElementById('cursor-badge');

  if (!halo || !point) return;

  // Disable custom cursor on touch/coarse devices
  if (window.matchMedia('(pointer: coarse)').matches) {
    if (halo) halo.style.display = 'none';
    if (point) point.style.display = 'none';
    if (badge) badge.style.display = 'none';
    return;
  }

  let mouseX = -100;
  let mouseY = -100;
  let haloX = -100;
  let haloY = -100;
  let isHoveringInspect = false;
  let isHoveringInteractive = false;

  window.addEventListener('mousemove', (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    point.style.transform = `translate3d(${mouseX}px, ${mouseY}px, 0)`;

    // Detect if hovering over inspectable target or defect
    const target = e.target;
    const isCanvas = target && (target.id === 'forge-sculpture-canvas' || target.closest('#sculpture-container'));
    const isInteractive = target && (target.closest('a, button, .diff-tab-btn, .trace-node-item, .seq-step-card'));

    if (isCanvas) {
      isHoveringInspect = true;
      halo.classList.add('cursor-inspect-active');
      if (badge) {
        badge.classList.add('visible');
        badge.style.transform = `translate3d(${mouseX + 16}px, ${mouseY - 12}px, 0)`;
      }
    } else {
      isHoveringInspect = false;
      halo.classList.remove('cursor-inspect-active');
      if (badge) badge.classList.remove('visible');
    }

    if (isInteractive) {
      isHoveringInteractive = true;
      halo.classList.add('cursor-hover-active');
    } else {
      isHoveringInteractive = false;
      halo.classList.remove('cursor-hover-active');
    }
  });

  // Smooth halo lag using RAF
  function renderCursor() {
    const ease = 0.18;
    haloX += (mouseX - haloX) * ease;
    haloY += (mouseY - haloY) * ease;

    const scale = isHoveringInspect ? 1.6 : (isHoveringInteractive ? 1.3 : 1);
    halo.style.transform = `translate3d(${haloX}px, ${haloY}px, 0) scale(${scale})`;

    requestAnimationFrame(renderCursor);
  }
  requestAnimationFrame(renderCursor);
}

/* ==========================================================================
   02 — THE SIGNATURE HERO: LIVING 3D PARTICLE CODE STRUCTURE
   ========================================================================== */
function init3DParticleSculpture() {
  const canvas = document.getElementById('forge-sculpture-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  const defectIndicator = document.getElementById('defect-indicator');
  const defectLabel = document.getElementById('defect-label');
  const meshStateTag = document.getElementById('mesh-state-tag');
  const triggerBtn = document.getElementById('trigger-investigate-btn');

  // Check prefers-reduced-motion
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  let width = (canvas.width = canvas.offsetWidth * window.devicePixelRatio || 800);
  let height = (canvas.height = canvas.offsetHeight * window.devicePixelRatio || 600);

  function resizeCanvas() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = canvas.width = canvas.offsetWidth * dpr;
    height = canvas.height = canvas.offsetHeight * dpr;
  }
  window.addEventListener('resize', resizeCanvas);

  // Simulation State
  let simState = 'IDLE'; // 'IDLE' | 'INVESTIGATING' | 'ROLLBACK' | 'VERIFIED'
  let stateProgress = 0; // 0..1 during transitions

  // 3D Math Configuration
  const FOCAL_LENGTH = 550;
  let rotX = 0.15;
  let rotY = 0.35;
  let targetRotX = 0.15;
  let targetRotY = 0.35;
  let zoom = 1.0;
  let targetZoom = 1.0;

  // Pointer Interaction
  const mouse = {
    x: -9999,
    y: -9999,
    canvasX: -9999,
    canvasY: -9999,
    isDown: false,
    hoverDefect: false
  };

  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    mouse.canvasX = (e.clientX - rect.left) * dpr;
    mouse.canvasY = (e.clientY - rect.top) * dpr;
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;

    // Slight parallax rotation on hover
    const nx = (mouse.x / rect.width) * 2 - 1;
    const ny = (mouse.y / rect.height) * 2 - 1;
    targetRotY = 0.35 + nx * 0.45;
    targetRotX = 0.15 - ny * 0.35;
  });

  canvas.addEventListener('mouseleave', () => {
    mouse.x = -9999;
    mouse.y = -9999;
    mouse.canvasX = -9999;
    mouse.canvasY = -9999;
    targetRotX = 0.15;
    targetRotY = 0.35;
  });

  // Generate 3D Particle Structure (Interwoven curved code paths + defect node)
  const NODE_COUNT = 140;
  const nodes = [];
  const connections = [];

  // 1. Primary Spine & Branches (Simulates AST & call paths)
  const BRANCHES = 5;
  for (let b = 0; b < BRANCHES; b++) {
    const thetaBase = (b / BRANCHES) * Math.PI * 2;
    const branchNodes = [];

    const nodesPerBranch = 24;
    for (let i = 0; i < nodesPerBranch; i++) {
      const t = i / (nodesPerBranch - 1);
      const radius = 90 + t * 140 + Math.sin(t * Math.PI * 3 + b) * 35;
      const angle = thetaBase + t * 1.8 + Math.sin(t * 4) * 0.3;
      const z = (t - 0.5) * 320 + Math.cos(t * Math.PI * 2 + b) * 50;

      const x = Math.cos(angle) * radius;
      const y = Math.sin(angle) * radius;

      const isDefect = (b === 2 && i === 16); // Node #103 Defect Location

      const node = {
        id: nodes.length,
        origX: x,
        origY: y,
        origZ: z,
        x: x,
        y: y,
        z: z,
        vx: 0,
        vy: 0,
        vz: 0,
        branch: b,
        index: i,
        isDefect: isDefect,
        isRepaired: false,
        size: isDefect ? 4.5 : (Math.random() * 1.6 + 1.2),
        brightness: Math.random() * 0.4 + 0.6,
        pulseOffset: Math.random() * Math.PI * 2
      };
      nodes.push(node);
      branchNodes.push(node);

      // Connect along branch
      if (i > 0) {
        connections.push({
          from: branchNodes[i - 1],
          to: node,
          isDefectPath: isDefect || (b === 2 && i === 15),
          weight: 1
        });
      }
    }
  }

  // 2. Cross-connect between adjacent branches to form the living lattice
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const n1 = nodes[i];
      const n2 = nodes[j];
      const dx = n1.origX - n2.origX;
      const dy = n1.origY - n2.origY;
      const dz = n1.origZ - n2.origZ;
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz);

      if (dist < 46 && Math.random() < 0.28) {
        connections.push({
          from: n1,
          to: n2,
          isDefectPath: (n1.isDefect || n2.isDefect),
          weight: 0.6
        });
      }
    }
  }

  // Diagnostic Pulses flowing across connections
  const PULSE_COUNT = 16;
  const pulses = [];
  for (let p = 0; p < PULSE_COUNT; p++) {
    const conn = connections[Math.floor(Math.random() * connections.length)];
    pulses.push({
      connection: conn,
      progress: Math.random(),
      speed: 0.006 + Math.random() * 0.008,
      size: 2.2
    });
  }

  // The Defect Node & Targeted Inspection Trigger
  const defectNode = nodes.find(n => n.isDefect);

  function triggerInvestigationSequence() {
    if (simState === 'INVESTIGATING' || simState === 'ROLLBACK') return;

    simState = 'INVESTIGATING';
    stateProgress = 0;
    targetZoom = 1.35;
    if (meshStateTag) {
      meshStateTag.textContent = 'DIAGNOSTIC SURGERY ACTIVE';
      meshStateTag.classList.add('tag-active');
    }
    if (defectLabel) {
      defectLabel.textContent = 'REPRODUCING FAILURE · ATTEMPT #1';
    }

    // Sequence timeline:
    // 0s: Zoom into defect node, pulses speed up along broken path
    // 1.8s: Attempt #1 regression encountered (red warning flash)
    // 3.2s: Atomic rollback to clean Git state
    // 4.6s: Attempt #2 precision fix applied, illuminated in lime (#C7FF4A)
    // 6.0s: Verification complete (Dual suites exit 0)

    setTimeout(() => {
      simState = 'ROLLBACK';
      if (defectLabel) defectLabel.textContent = 'REGRESSION CAUGHT · ROLLING BACK TO e4f892a';
      if (defectIndicator) {
        defectIndicator.classList.remove('pulse-defect');
        defectIndicator.classList.add('pulse-rollback');
      }
    }, 1800);

    setTimeout(() => {
      simState = 'VERIFIED';
      targetZoom = 1.05;
      if (defectNode) defectNode.isRepaired = true;
      if (defectLabel) defectLabel.textContent = 'NODE #103 · VERIFIED GREEN (DUAL-SUITE PASS)';
      if (meshStateTag) {
        meshStateTag.textContent = 'VERIFIED · SYSTEM SECURE';
        meshStateTag.classList.remove('tag-active');
        meshStateTag.classList.add('tag-verified');
      }
      if (defectIndicator) {
        defectIndicator.classList.remove('pulse-rollback');
        defectIndicator.classList.add('pulse-verified');
      }
    }, 3800);
  }

  if (triggerBtn) {
    triggerBtn.addEventListener('click', (e) => {
      e.preventDefault();
      triggerInvestigationSequence();
    });
  }

  // Allow clicking directly on canvas near defect node
  canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const clickX = (e.clientX - rect.left) * dpr;
    const clickY = (e.clientY - rect.top) * dpr;

    if (defectNode && defectNode.projX !== undefined) {
      const d = Math.hypot(clickX - defectNode.projX, clickY - defectNode.projY);
      if (d < 36 * dpr) {
        triggerInvestigationSequence();
      }
    }
  });

  // Pause simulation if scrolled out of view to preserve 60-120fps efficiency
  let isCanvasVisible = true;
  const observer = new IntersectionObserver((entries) => {
    isCanvasVisible = entries[0].isIntersecting;
  }, { threshold: 0.05 });
  observer.observe(canvas);

  // Main 3D Render Loop
  let lastTime = performance.now();

  function animate(now) {
    requestAnimationFrame(animate);
    if (!isCanvasVisible) return;

    const dt = Math.min((now - lastTime) / 1000, 0.1);
    lastTime = now;

    // Smooth camera rotation
    const rotSpeed = prefersReducedMotion ? 0 : 0.04;
    rotX += (targetRotX - rotX) * 0.06;
    rotY += (targetRotY - rotY) * 0.06 + rotSpeed * dt;
    zoom += (targetZoom - zoom) * 0.05;

    // Clear Canvas with subtle trail persistence
    ctx.clearRect(0, 0, width, height);

    const cx = width / 2;
    const cy = height / 2;

    const cosY = Math.cos(rotY);
    const sinY = Math.sin(rotY);
    const cosX = Math.cos(rotX);
    const sinX = Math.sin(rotX);

    // Project & Update Nodes
    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];

      // Physical drift + Mouse local displacement field
      let curX = n.origX;
      let curY = n.origY;
      let curZ = n.origZ;

      // 3D Rotation (Y axis then X axis)
      const x1 = curX * cosY - curZ * sinY;
      const z1 = curZ * cosY + curX * sinY;
      const y2 = curY * cosX - z1 * sinX;
      const z2 = z1 * cosX + curY * sinX;

      // Perspective Projection
      const scale = (FOCAL_LENGTH / (FOCAL_LENGTH + z2 + 250)) * zoom;
      n.projX = cx + x1 * scale;
      n.projY = cy + y2 * scale;
      n.projScale = scale;
      n.projZ = z2;

      // Mouse Displacement in screen space with elastic spring recovery
      if (mouse.canvasX > 0) {
        const dx = n.projX - mouse.canvasX;
        const dy = n.projY - mouse.canvasY;
        const dist = Math.hypot(dx, dy);
        const radius = 110 * window.devicePixelRatio;

        if (dist < radius && dist > 0.01) {
          const force = (1 - dist / radius) * 22;
          n.projX += (dx / dist) * force;
          n.projY += (dy / dist) * force;
        }
      }
    }

    // Render Connections (Hairline SVG-like wireframe paths)
    for (let i = 0; i < connections.length; i++) {
      const c = connections[i];
      const from = c.from;
      const to = c.to;

      // Depth fade
      const avgZ = (from.projZ + to.projZ) / 2;
      const alpha = Math.max(0.06, Math.min(0.75, (FOCAL_LENGTH + avgZ) / (FOCAL_LENGTH * 1.5))) * c.weight;

      ctx.beginPath();
      ctx.moveTo(from.projX, from.projY);
      ctx.lineTo(to.projX, to.projY);

      if (c.isDefectPath) {
        if (defectNode && defectNode.isRepaired) {
          // Repaired state: Vibrant Lime Proof Line
          ctx.strokeStyle = `rgba(199, 255, 74, ${Math.min(1, alpha * 2.2)})`;
          ctx.lineWidth = 1.8 * from.projScale;
        } else if (simState === 'INVESTIGATING' || simState === 'ROLLBACK') {
          // Warning/Diagnostic state: Flashing Cyan/Red
          const pulseBright = 0.5 + Math.sin(now * 0.008) * 0.4;
          ctx.strokeStyle = simState === 'ROLLBACK' 
            ? `rgba(255, 102, 91, ${pulseBright})` 
            : `rgba(130, 223, 255, ${pulseBright})`;
          ctx.lineWidth = 2.0 * from.projScale;
        } else {
          // Broken Defect Path: Visible structural break in coral red
          ctx.setLineDash([4, 6]);
          ctx.strokeStyle = `rgba(255, 102, 91, ${Math.min(0.85, alpha * 1.8)})`;
          ctx.lineWidth = 1.4 * from.projScale;
        }
      } else {
        // Standard code path: Fine warm-white hairline
        ctx.setLineDash([]);
        ctx.strokeStyle = `rgba(243, 241, 234, ${alpha * 0.22})`;
        ctx.lineWidth = 0.8 * from.projScale;
      }

      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Render Diagnostic Pulses travelling along edges
    for (let i = 0; i < pulses.length; i++) {
      const p = pulses[i];
      p.progress += p.speed;
      if (p.progress >= 1) {
        p.progress = 0;
        p.connection = connections[Math.floor(Math.random() * connections.length)];
      }

      const c = p.connection;
      const px = c.from.projX + (c.to.projX - c.from.projX) * p.progress;
      const py = c.from.projY + (c.to.projY - c.from.projY) * p.progress;
      const scale = (c.from.projScale + c.to.projScale) / 2;

      ctx.beginPath();
      ctx.arc(px, py, p.size * scale, 0, Math.PI * 2);

      if (c.isDefectPath && defectNode && defectNode.isRepaired) {
        ctx.fillStyle = '#C7FF4A';
      } else if (c.isDefectPath) {
        ctx.fillStyle = '#FF665B';
      } else {
        ctx.fillStyle = '#82DFFF';
      }
      ctx.fill();
    }

    // Render Nodes (Particles with dimensional depth)
    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i];
      const radius = Math.max(1, n.size * n.projScale);

      ctx.beginPath();
      ctx.arc(n.projX, n.projY, radius, 0, Math.PI * 2);

      if (n.isDefect) {
        if (n.isRepaired) {
          // Repaired Verified Node
          ctx.fillStyle = '#C7FF4A';
          ctx.shadowColor = '#C7FF4A';
          ctx.shadowBlur = 12 * n.projScale;
          ctx.fill();
          ctx.shadowBlur = 0;

          // Outlined confirmation ring
          ctx.beginPath();
          ctx.arc(n.projX, n.projY, radius + 4 * n.projScale, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(199, 255, 74, 0.4)';
          ctx.lineWidth = 1;
          ctx.stroke();
        } else {
          // Defective Node #103
          const pulse = Math.sin(now * 0.006 + n.pulseOffset);
          ctx.fillStyle = '#FF665B';
          ctx.shadowColor = '#FF665B';
          ctx.shadowBlur = (8 + pulse * 6) * n.projScale;
          ctx.fill();
          ctx.shadowBlur = 0;

          // Pulsing halo
          ctx.beginPath();
          ctx.arc(n.projX, n.projY, radius + (6 + pulse * 4) * n.projScale, 0, Math.PI * 2);
          ctx.strokeStyle = `rgba(255, 102, 91, ${0.35 + pulse * 0.25})`;
          ctx.lineWidth = 1.2;
          ctx.stroke();

          // Technical annotation label next to defect
          ctx.font = `${Math.floor(10 * n.projScale)}px 'JetBrains Mono', monospace`;
          ctx.fillStyle = '#FF665B';
          ctx.fillText('ERR: NODE #103', n.projX + 12 * n.projScale, n.projY - 4 * n.projScale);
        }
      } else {
        // Standard neural lattice particles
        const nodeAlpha = Math.max(0.18, Math.min(0.85, (FOCAL_LENGTH + n.projZ) / (FOCAL_LENGTH * 1.4)));
        ctx.fillStyle = `rgba(243, 241, 234, ${nodeAlpha * n.brightness})`;
        ctx.fill();
      }
    }
  }

  requestAnimationFrame(animate);
}

/* ==========================================================================
   03 — SCROLL-LINKED TRANSFORMATION NARRATIVE (SCENE A - SCENE F)
   ========================================================================== */
function initScrollNarrative() {
  const sceneCards = document.querySelectorAll('.scene-card');
  if (!sceneCards.length) return;

  const sceneObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        sceneCards.forEach((c) => c.classList.remove('is-active'));
        entry.target.classList.add('is-active');
      }
    });
  }, {
    rootMargin: '-20% 0px -25% 0px',
    threshold: 0.35
  });

  sceneCards.forEach((card) => sceneObserver.observe(card));
}

/* ==========================================================================
   04 — INTERACTIVE CODE DIFF SHOWCASE
   ========================================================================== */
function initDiffShowcase() {
  const codeBody = document.getElementById('diff-code-body');
  const statText = document.getElementById('diff-stat-text');
  const tabBefore = document.getElementById('tab-diff-before');
  const tabPatch1 = document.getElementById('tab-diff-patch1');
  const tabPatch2 = document.getElementById('tab-diff-patch2');

  if (!codeBody) return;

  const diffViews = {
    before: {
      stat: '0 changes · Unhandled volume < 0',
      html: `
<div class="diff-line diff-ctx"><span class="diff-num">12</span><span class="diff-sign"> </span><span class="diff-text">def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -&gt; float:</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">13</span><span class="diff-sign"> </span><span class="diff-text">    """Calculates final price with tiered volume discounts."""</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">14</span><span class="diff-sign"> </span><span class="diff-text">    if base_price &lt; 0:</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">15</span><span class="diff-sign"> </span><span class="diff-text">        raise ValueError("base_price cannot be negative")</span></div>
<div class="diff-line diff-del"><span class="diff-num">16</span><span class="diff-sign">-</span><span class="diff-text">    # Missing check: volume &lt; 0 produces negative total</span></div>
<div class="diff-line diff-del"><span class="diff-num">17</span><span class="diff-sign">-</span><span class="diff-text">    multiplier = 0.80 if is_vip else 1.0</span></div>
<div class="diff-line diff-del"><span class="diff-num">18</span><span class="diff-sign">-</span><span class="diff-text">    return base_price * volume * multiplier</span></div>
`
    },
    patch1: {
      stat: '+1 -1 lines · Regression in test_vip_discount',
      html: `
<div class="diff-line diff-ctx"><span class="diff-num">12</span><span class="diff-sign"> </span><span class="diff-text">def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -&gt; float:</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">13</span><span class="diff-sign"> </span><span class="diff-text">    """Calculates final price with tiered volume discounts."""</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">14</span><span class="diff-sign"> </span><span class="diff-text">    if base_price &lt; 0:</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">15</span><span class="diff-sign"> </span><span class="diff-text">        raise ValueError("base_price cannot be negative")</span></div>
<div class="diff-line diff-del"><span class="diff-num">16</span><span class="diff-sign">-</span><span class="diff-text">    multiplier = 0.80 if is_vip else 1.0</span></div>
<div class="diff-line diff-del"><span class="diff-num">17</span><span class="diff-sign">-</span><span class="diff-text">    return base_price * volume * multiplier</span></div>
<div class="diff-line diff-add diff-warning"><span class="diff-num">16</span><span class="diff-sign">+</span><span class="diff-text">    # Naive Clamp Attempt #1 (Violates VIP multiplier)</span></div>
<div class="diff-line diff-add diff-warning"><span class="diff-num">17</span><span class="diff-sign">+</span><span class="diff-text">    return base_price * max(0, volume)</span></div>
`
    },
    patch2: {
      stat: '+3 -0 lines · Verified 100% Pass Rate',
      html: `
<div class="diff-line diff-ctx"><span class="diff-num">12</span><span class="diff-sign"> </span><span class="diff-text">def calculate_tiered_price(base_price: float, volume: int, is_vip: bool = False) -&gt; float:</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">13</span><span class="diff-sign"> </span><span class="diff-text">    """Calculates final price with tiered volume discounts."""</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">14</span><span class="diff-sign"> </span><span class="diff-text">    if base_price &lt; 0:</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">15</span><span class="diff-sign"> </span><span class="diff-text">        raise ValueError("base_price cannot be negative")</span></div>
<div class="diff-line diff-add"><span class="diff-num">16</span><span class="diff-sign">+</span><span class="diff-text">    if volume &lt; 0:</span></div>
<div class="diff-line diff-add"><span class="diff-num">17</span><span class="diff-sign">+</span><span class="diff-text">        raise ValueError("volume cannot be negative")</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">18</span><span class="diff-sign"> </span><span class="diff-text">    multiplier = 0.80 if is_vip else 1.0</span></div>
<div class="diff-line diff-ctx"><span class="diff-num">19</span><span class="diff-sign"> </span><span class="diff-text">    return base_price * volume * multiplier</span></div>
`
    }
  };

  function setView(viewKey) {
    [tabBefore, tabPatch1, tabPatch2].forEach((btn) => {
      if (btn) btn.classList.remove('active');
    });

    if (viewKey === 'before' && tabBefore) tabBefore.classList.add('active');
    if (viewKey === 'patch1' && tabPatch1) tabPatch1.classList.add('active');
    if (viewKey === 'patch2' && tabPatch2) tabPatch2.classList.add('active');

    const data = diffViews[viewKey];
    if (data) {
      if (statText) statText.textContent = data.stat;
      codeBody.innerHTML = data.html;
    }
  }

  if (tabBefore) tabBefore.addEventListener('click', () => setView('before'));
  if (tabPatch1) tabPatch1.addEventListener('click', () => setView('patch1'));
  if (tabPatch2) tabPatch2.addEventListener('click', () => setView('patch2'));

  // Default to Verified fix (Attempt #2)
  setView('patch2');
}

/* ==========================================================================
   05 — TELEMETRY TRACE EXPLORER
   ========================================================================== */
function initTraceExplorer() {
  const items = document.querySelectorAll('.trace-node-item');
  const detType = document.getElementById('det-type');
  const detTime = document.getElementById('det-time');
  const detTrace = document.getElementById('det-trace');
  const detCmd = document.getElementById('det-cmd');
  const detLog = document.getElementById('det-log');
  const copyBtn = document.getElementById('copy-trace-btn');

  const traceEvents = [
    {
      type: 'INTAKE & BASELINE DISCOVERY',
      time: '2026-10-10T19:48:50.412Z',
      trace: '16578e5ee3829a5a6f053c7cbeabd88f',
      cmd: 'git clone --no-hardlinks . .worktrees/patchpilot_sandbox_916d',
      log: 'Cloned clean worktree at commit e4f892a. Mapped abstract syntax tree for pricing.py. Discovered 1 candidate defect and 3 associated regression test cases.'
    },
    {
      type: 'REPRODUCTION EXECUTION',
      time: '2026-10-10T19:48:51.844Z',
      trace: '16578e5ee3829a5a6f053c7cbeabd88f',
      cmd: 'pytest -q tests/test_pricing.py::test_negative_volume',
      log: 'FAILED tests/test_pricing.py::test_negative_volume - ValueError expected but got -100.0. Process exited with Exit Code 1. Defect reproduction mathematically proven.'
    },
    {
      type: 'ATTEMPT #1 TEST EXECUTION',
      time: '2026-10-10T19:48:53.109Z',
      trace: '16578e5ee3829a5a6f053c7cbeabd88f',
      cmd: 'pytest -q tests/test_pricing.py',
      log: 'FAILED tests/test_pricing.py::test_vip_discount - AssertionError: 80.0 != 100.0. Acceptance passed, but existing VIP regression check failed. Halting promotion immediately.'
    },
    {
      type: 'ATOMIC ROLLBACK & REPLANNING',
      time: '2026-10-10T19:48:54.430Z',
      trace: '16578e5ee3829a5a6f053c7cbeabd88f',
      cmd: 'git reset --hard e4f892a && git clean -fd',
      log: 'Rolled back ephemeral worktree to baseline commit e4f892a. Injected failure traceback into context for Attempt #2. Zero dirty artifacts left in repository.'
    },
    {
      type: 'VERIFICATION GATE PASSED',
      time: '2026-10-10T19:48:56.891Z',
      trace: '16578e5ee3829a5a6f053c7cbeabd88f',
      cmd: 'pytest -q tests/test_pricing.py && pytest -q tests/test_regression.py',
      log: 'PASSED (2 suites, 14 passed in 0.42s). Exit Code 0 across all checks. Telemetry span committed to Neatlogs. Draft PR patch generated.'
    }
  ];

  items.forEach((item, idx) => {
    item.addEventListener('click', () => {
      items.forEach((it) => it.classList.remove('is-active'));
      item.classList.add('is-active');

      const data = traceEvents[idx];
      if (data) {
        if (detType) detType.textContent = data.type;
        if (detTime) detTime.textContent = data.time;
        if (detTrace) detTrace.textContent = data.trace;
        if (detCmd) detCmd.textContent = data.cmd;
        if (detLog) detLog.textContent = data.log;
      }
    });
  });

  // Working copy utility for Neatlogs trace ID
  if (copyBtn) {
    copyBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const traceId = detTrace ? detTrace.textContent.trim() : '16578e5ee3829a5a6f053c7cbeabd88f';
      try {
        await navigator.clipboard.writeText(traceId);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = 'COPIED!';
        copyBtn.classList.add('copied');
        setTimeout(() => {
          copyBtn.textContent = originalText;
          copyBtn.classList.remove('copied');
        }, 2000);
      } catch (err) {
        console.warn('Clipboard write error:', err);
      }
    });
  }
}

/* ==========================================================================
   06 — SUBTLE MAGNETIC BUTTON REACTIONS
   ========================================================================== */
function initMagneticButtons() {
  const magnets = document.querySelectorAll('.magnetic');
  if (window.matchMedia('(pointer: coarse)').matches) return;

  magnets.forEach((btn) => {
    btn.addEventListener('mousemove', (e) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate3d(${x * 0.16}px, ${y * 0.16}px, 0)`;
    });

    btn.addEventListener('mouseleave', () => {
      btn.style.transform = 'translate3d(0, 0, 0)';
    });
  });
}
