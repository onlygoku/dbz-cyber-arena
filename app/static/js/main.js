/**
 * Dragon Ball Z Cyber Arena — Main JS
 */

// ── Countdown Timer ─────────────────────────────────────────────────────────
function startCountdown(targetISOString, elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;

  const target = new Date(targetISOString).getTime();

  function tick() {
    const now  = Date.now();
    const diff = target - now;

    if (diff <= 0) {
      el.textContent = '00:00:00';
      return;
    }

    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);

    el.textContent =
      String(h).padStart(2, '0') + ':' +
      String(m).padStart(2, '0') + ':' +
      String(s).padStart(2, '0');

    setTimeout(tick, 1000);
  }

  tick();
}

// ── Clipboard helper ─────────────────────────────────────────────────────────
function copyToClipboard(text, feedback) {
  navigator.clipboard.writeText(text).then(() => {
    if (feedback) {
      const orig = feedback.textContent;
      feedback.textContent = 'Copied!';
      setTimeout(() => { feedback.textContent = orig; }, 1500);
    }
  }).catch(() => {
    // Fallback
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity  = '0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
  });
}

// ── Flash auto-dismiss ───────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const flashes = document.querySelectorAll('[class^="flash-"]');
  flashes.forEach(el => {
    setTimeout(() => {
      el.style.transition = 'opacity 0.5s';
      el.style.opacity    = '0';
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });
});

// ── Category filter state persistence ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const saved = sessionStorage.getItem('ctf_cat_filter');
  if (saved) {
    const btn = document.querySelector(`.filter-btn[data-cat="${saved}"]`);
    if (btn) btn.click();
  }

  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      sessionStorage.setItem('ctf_cat_filter', btn.dataset.cat);
    });
  });
});
