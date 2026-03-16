/**
 * Shenron animation — triggered when the boss challenge is solved.
 * Creates a full-screen canvas dragon animation.
 */
function triggerShenron() {
  const existing = document.getElementById('shenronCanvas');
  if (existing) return;

  const canvas = document.createElement('canvas');
  canvas.id = 'shenronCanvas';
  canvas.style.cssText = `
    position: fixed;
    inset: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 9998;
  `;
  document.body.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;

  const W = canvas.width;
  const H = canvas.height;

  // Dragon body segments
  const segments = [];
  const SEGS = 40;
  const cx = W / 2;
  const cy = H / 2;

  for (let i = 0; i < SEGS; i++) {
    segments.push({ x: cx, y: cy + i * 12, angle: -Math.PI / 2 });
  }

  // Particles (energy orbs)
  const particles = [];
  for (let i = 0; i < 80; i++) {
    particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 3 + 1,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2 - 1,
      life: 1,
      hue: Math.random() * 60 + 80, // green-yellow range
    });
  }

  let t = 0;
  let alpha = 0;
  const DURATION = 300; // frames

  function drawSegment(x, y, size, hue, lightness) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(x, y, size, 0, Math.PI * 2);
    ctx.fillStyle = `hsla(${hue}, 90%, ${lightness}%, 0.85)`;
    ctx.shadowBlur = 20;
    ctx.shadowColor = `hsla(${hue}, 100%, 60%, 0.7)`;
    ctx.fill();
    ctx.restore();
  }

  function animate() {
    if (t > DURATION) {
      // Fade out
      alpha -= 0.02;
      if (alpha <= 0) {
        canvas.remove();
        return;
      }
    } else if (t < 20) {
      alpha += 0.05;
    } else {
      alpha = 1;
    }

    ctx.clearRect(0, 0, W, H);
    ctx.globalAlpha = Math.min(alpha, 1);

    // Background vignette
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * 0.7);
    grad.addColorStop(0, 'rgba(0,40,0,0.3)');
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, W, H);

    // Move head in sinusoidal path
    const speed = 3;
    const headX = cx + Math.sin(t * 0.04) * W * 0.35;
    const headY = cy + Math.sin(t * 0.025) * H * 0.25 - t * 0.3;

    // Update segments to follow head
    segments[0].x = headX;
    segments[0].y = headY;
    for (let i = 1; i < SEGS; i++) {
      const prev = segments[i - 1];
      const curr = segments[i];
      const dx = curr.x - prev.x;
      const dy = curr.y - prev.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const targetDist = 14;
      if (dist > targetDist) {
        curr.x = prev.x + (dx / dist) * targetDist;
        curr.y = prev.y + (dy / dist) * targetDist;
      }
    }

    // Draw body
    for (let i = SEGS - 1; i >= 0; i--) {
      const seg = segments[i];
      const ratio = 1 - i / SEGS;
      const size = 4 + ratio * 14;
      const hue = 100 + ratio * 40; // tail=green, head=yellow-green
      const light = 40 + ratio * 25;
      drawSegment(seg.x, seg.y, size, hue, light);
    }

    // Draw head details
    const head = segments[0];
    // Eyes
    ctx.save();
    ctx.beginPath();
    ctx.arc(head.x - 6, head.y - 4, 3, 0, Math.PI * 2);
    ctx.fillStyle = '#ff4444';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#ff0000';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(head.x + 6, head.y - 4, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Particles
    for (let p of particles) {
      p.x  += p.vx;
      p.y  += p.vy;
      p.vy -= 0.02;
      p.life -= 0.005;
      if (p.life <= 0 || p.y < 0) {
        p.x    = Math.random() * W;
        p.y    = H + 10;
        p.life = 1;
        p.vy   = -(Math.random() * 2 + 0.5);
        p.vx   = (Math.random() - 0.5) * 1.5;
      }
      ctx.save();
      ctx.globalAlpha = p.life * alpha;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `hsla(${p.hue}, 100%, 70%, 1)`;
      ctx.shadowBlur = 8;
      ctx.shadowColor = `hsla(${p.hue}, 100%, 60%, 0.8)`;
      ctx.fill();
      ctx.restore();
    }

    // Shenron title text
    if (t > 30 && t < DURATION) {
      ctx.save();
      ctx.globalAlpha = Math.min((t - 30) / 20, 1) * alpha;
      ctx.font = 'bold 28px "Orbitron", sans-serif';
      ctx.textAlign = 'center';
      ctx.fillStyle = '#fbbf24';
      ctx.shadowBlur = 30;
      ctx.shadowColor = 'rgba(251,191,36,0.8)';
      ctx.fillText('SHENRON AWAKENS', W / 2, H * 0.75);
      ctx.font = '14px "Share Tech Mono", monospace';
      ctx.fillStyle = '#a3e635';
      ctx.shadowColor = 'rgba(163,230,53,0.6)';
      ctx.fillText('Your wish has been granted...', W / 2, H * 0.75 + 36);
      ctx.restore();
    }

    t++;
    requestAnimationFrame(animate);
  }

  animate();
}
document.addEventListener("mousemove", function(e){

  const dragon = document.querySelector(".hero-dragon img")

  if(!dragon) return

  const x = (window.innerWidth / 2 - e.clientX) / 40
  const y = (window.innerHeight / 2 - e.clientY) / 40

  dragon.style.transform = `translate(${x}px, ${y}px)`
})