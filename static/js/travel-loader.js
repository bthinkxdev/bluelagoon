/**
 * Home landing page loader — once per browser session every 12 hours.
 */
(function () {
  var STORAGE_KEY = 'bluelagoon_home_loader_seen';
  var COOLDOWN_MS = 12 * 60 * 60 * 1000;
  var PROGRESS_DURATION = 4000;
  var overlay = document.getElementById('travel-loader-overlay');

  if (!overlay) {
    return;
  }

  function removeOverlay() {
    document.body.classList.remove('home-loader-active');
    if (overlay.parentNode) {
      overlay.parentNode.removeChild(overlay);
    }
  }

  function hideLoader() {
    overlay.classList.add('is-hidden');
    try {
      sessionStorage.setItem(STORAGE_KEY, String(Date.now()));
    } catch (e) { /* ignore */ }
    window.setTimeout(removeOverlay, 600);
  }

  function skipLoader() {
    removeOverlay();
  }

  function shouldSkipLoader() {
    try {
      var raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return false;
      var seenAt = parseInt(raw, 10);
      if (isNaN(seenAt)) return false;
      return Date.now() - seenAt < COOLDOWN_MS;
    } catch (e) {
      return false;
    }
  }

  if (shouldSkipLoader()) {
    skipLoader();
    return;
  }

  document.body.classList.add('home-loader-active');

  var fill = document.getElementById('travel-loader-progress-fill');
  var pct = document.getElementById('travel-loader-progress-pct');
  var planeOnBar = document.getElementById('travel-loader-progress-plane');
  var messageEl = document.getElementById('travel-loader-message');
  var plane = document.getElementById('travel-loader-plane');
  var steps = Array.prototype.slice.call(document.querySelectorAll('#travel-loader-overlay .step'));

  var messages = [
    { at: 0, text: 'Preparing your passport…' },
    { at: 20, text: 'Finding amazing destinations…' },
    { at: 40, text: 'Comparing the best prices…' },
    { at: 60, text: 'Booking trusted partners…' },
    { at: 80, text: 'Packing your memories…' },
    { at: 100, text: 'Ready to explore!' }
  ];

  var currentMsgIndex = -1;
  var currentStepIndex = -1;
  var finished = false;

  function setActiveStep(idx) {
    if (idx === currentStepIndex) return;
    currentStepIndex = idx;
    steps.forEach(function (s, i) {
      s.classList.toggle('active', i === idx);
    });
  }

  function setMessage(idx) {
    if (idx === currentMsgIndex || !messageEl) return;
    currentMsgIndex = idx;
    messageEl.classList.add('fading');
    window.setTimeout(function () {
      messageEl.textContent = messages[idx].text;
      messageEl.classList.remove('fading');
    }, 220);
  }

  function updateProgress(progressPct) {
    var clamped = Math.min(100, Math.max(0, progressPct));
    if (fill) fill.style.width = clamped + '%';
    if (pct) pct.textContent = Math.round(clamped) + '%';
    if (planeOnBar) planeOnBar.style.left = clamped + '%';

    var msgIdx = 0;
    for (var i = messages.length - 1; i >= 0; i--) {
      if (clamped >= messages[i].at) {
        msgIdx = i;
        break;
      }
    }
    setMessage(msgIdx);
    setActiveStep(Math.min(3, Math.floor(clamped / 25)));
  }

  var rx = 115;
  var ry = 55;
  var planeSize = 30;
  var orbitDuration = 9000;

  function updateOrbit(t) {
    if (!plane) return;
    var angle = (t % orbitDuration) / orbitDuration * Math.PI * 2;
    var x = Math.cos(angle) * rx;
    var y = Math.sin(angle) * ry * 0.55;
    var behind = Math.sin(angle) < -0.1;

    plane.style.transform =
      'translate(' + (x - planeSize / 2) + 'px, ' + (y - planeSize / 2 - 6) + 'px) ' +
      'scale(' + (behind ? 0.78 : 1) + ') ' +
      'rotate(' + (Math.cos(angle) >= 0 ? -18 : 18) + 'deg) ' +
      'scaleX(' + (Math.cos(angle) >= 0 ? 1 : -1) + ')';

    plane.classList.toggle('behind', behind);
    plane.classList.toggle('front', !behind);
  }

  var start = null;

  function frame(ts) {
    if (finished) return;
    if (start === null) start = ts;
    var elapsed = ts - start;
    var progressPct = Math.min(100, (elapsed / PROGRESS_DURATION) * 100);

    updateProgress(progressPct);
    updateOrbit(elapsed);

    if (progressPct >= 100) {
      finished = true;
      window.setTimeout(hideLoader, 400);
      return;
    }
    requestAnimationFrame(frame);
  }

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    updateProgress(100);
    window.setTimeout(hideLoader, 300);
    return;
  }

  requestAnimationFrame(frame);
})();
