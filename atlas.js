(function () {
  document.documentElement.classList.add('js');

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var deck = document.querySelector('.deck');
  var cards = Array.prototype.slice.call(deck.children);
  var bar = document.querySelector('.bar');
  var grid = document.querySelector('.index-grid');
  var ticking = false;
  var shown = -1;

  function screenAt(y) {
    var h = cards[0].offsetHeight;
    return Math.max(0, Math.min(cards.length - 1, Math.floor((y - deck.offsetTop) / h)));
  }

  var frames = Array.prototype.slice.call(grid.querySelectorAll('.tile-frame'));

  function glass() {
    var g = grid.getBoundingClientRect();
    if (g.bottom < -window.innerHeight || g.top > 2 * window.innerHeight) return;
    grid.style.setProperty('--sx', g.left + 'px');
    grid.style.setProperty('--sy', g.top + 'px');
  }

  function placeFrames() {
    var g = grid.getBoundingClientRect();
    frames.forEach(function (f) {
      var r = f.getBoundingClientRect();
      f.style.setProperty('--fx', (r.left - g.left + f.clientLeft) + 'px');
      f.style.setProperty('--fy', (r.top - g.top + f.clientTop) + 'px');
    });
    glass();
  }

  function update() {
    ticking = false;
    glass();
    var y = window.scrollY + bar.offsetHeight / 2;
    var past = y > deck.offsetTop + deck.offsetHeight;
    var k = screenAt(y);
    bar.style.setProperty('--bar', past ? '' : cards[k].dataset.t);
    bar.classList.toggle('is-past', past);
    address();
    var top = reduce.matches ? -1 : screenAt(window.scrollY);
    if (top === shown) return;
    shown = top;
    for (var i = 0; i < cards.length; i++) cards[i].classList.toggle('is-under', i < top);
  }

  /* The address bar and tab title follow the plate filling the screen, so any
     moment can be shared as /lisbon/; the globe and the index read as the home page. */
  function address() {
    var mid = window.scrollY + window.innerHeight / 2;
    var card = mid > deck.offsetTop + deck.offsetHeight ? cards[0] : cards[screenAt(mid)];
    var path = card === cards[0] ? '/' : '/' + card.id + '/';
    if (document.title !== card.dataset.title) document.title = card.dataset.title;
    if (path === location.pathname) return;
    history.replaceState(null, '', path + (card === cards[0] ? location.hash : ''));
    clearTimeout(dwell);
    if (card !== cards[0] && !viewed[card.id]) dwell = setTimeout(viewPrint, 1500, card);
  }

  /* Analytics: a print counts as viewed once it has held the screen for 1.5s, once per visit. */
  var viewed = {};
  var dwell = 0;

  function viewPrint(card) {
    viewed[card.id] = true;
    if (!window.gtag) return;
    gtag('event', 'view_print', {
      print: card.id,
      city: card.querySelector('.plate-name').textContent,
      country: card.querySelector('.plate-place').textContent.split(' · ')[0]
    });
  }

  function queue() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);
  reduce.addEventListener('change', queue);
  new ResizeObserver(placeFrames).observe(grid);
  if (document.fonts) document.fonts.ready.then(placeFrames);

  // A print's own page (/lisbon/) or an old #lisbon link opens the scroll at that plate.
  if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
  if (!jumpTo(document.body.dataset.start || location.hash.slice(1))) update();

  // Covered plates are stuck at the top, so a plain anchor jump back to one never scrolls.
  function jumpTo(id) {
    var target = id && document.getElementById(id);
    var k = cards.indexOf(target);
    if (k < 0) return false;
    window.scrollTo(0, deck.offsetTop + k * cards[0].offsetHeight);
    update();
    return true;
  }

  function cardFor(a) {
    var u = new URL(a.href, location.href);
    if (u.origin !== location.origin) return '';
    if (u.hash && u.pathname === location.pathname) return u.hash.slice(1);
    if (u.pathname === '/') return 'top';
    var m = u.pathname.match(/^\/([a-z0-9-]+)\/$/);
    return m ? m[1] : '';
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (jumpTo(cardFor(a))) e.preventDefault();
  });

  globe(document.querySelector('.intro-globe'));
  globe(document.querySelector('.foot-globe'));

  var buttons = Array.prototype.slice.call(document.querySelectorAll('[data-sort]'));
  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      var key = button.dataset.sort;
      buttons.forEach(function (b) { b.setAttribute('aria-pressed', String(b === button)); });
      var items = Array.prototype.slice.call(grid.children);
      var before = items.map(function (li) { return li.getBoundingClientRect(); });
      var moved = items.slice().sort(function (a, b) { return a.dataset[key] - b.dataset[key]; });
      moved.forEach(function (li) { grid.appendChild(li); });
      placeFrames();
      if (reduce.matches) return;
      items.forEach(function (li, i) {
        var after = li.getBoundingClientRect();
        var dx = before[i].left - after.left;
        var dy = before[i].top - after.top;
        if (!dx && !dy) return;
        li.animate(
          [{ transform: 'translate(' + dx + 'px,' + dy + 'px)' }, { transform: 'none' }],
          { duration: 720, delay: moved.indexOf(li) * 6, easing: 'cubic-bezier(.2,.7,.1,1)', fill: 'backwards' }
        );
      });
    });
  });

  /* A dot earth that turns once every 96s, one pin per city in its poster's color.
     Drag to spin it; hovering a pin names the city, clicking opens its print.
     A data-muted globe is land only: dimmer, no pins, no labels, no touch. */
  function globe(canvas) {
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var muted = 'muted' in canvas.dataset;
    var label = muted ? null : document.querySelector('.globe-label');
    var TILT = 0.36;
    var TURN = 6.2832 / 96000;
    var land = [];
    var onScreen = true;
    var cities = (canvas.dataset.cities || '').split(';').filter(Boolean).map(function (s, k) {
      var v = s.split('|');
      var p = unit(+v[0], +v[1]);
      p.c = v[2];
      p.slug = v[3];
      p.city = v[4];
      p.meta = v[5] + ' · ' + Math.abs(+v[0]).toFixed(2) + '° ' + (+v[0] >= 0 ? 'N' : 'S') +
        ' ' + Math.abs(+v[1]).toFixed(2) + '° ' + (+v[1] >= 0 ? 'E' : 'W');
      p.ph = (k * 0.618034) % 1;
      p.zz = -1;
      p.g = 0;
      return p;
    });
    var R = 0, cx = 0, cy = 0, dot = 1, raf = 0;
    var rot = muted ? 2.2 : 0.35, vel = TURN, last = 0, drag = null, hover = null, focus = 0;
    var feat = null, featAt = 0, shown = null;

    function unit(lat, lon) {
      lat /= 57.2958;
      lon /= 57.2958;
      return { x: Math.cos(lat) * Math.sin(lon), y: Math.sin(lat), z: Math.cos(lat) * Math.cos(lon) };
    }

    function size() {
      var dpr = Math.min(2, window.devicePixelRatio || 1);
      var w = canvas.clientWidth * dpr;
      canvas.width = canvas.height = Math.round(w);
      R = w * 0.46;
      cx = cy = w / 2;
      dot = Math.max(1 * dpr, R * 0.0052);
    }

    function draw(now) {
      var ca = Math.cos(rot), sa = Math.sin(rot), cb = Math.cos(TILT), sb = Math.sin(TILT);
      var quiet = (1 - 0.45 * focus) * (muted ? 0.45 : 1);
      var big;
      var buckets = [[], [], [], [], [], []];
      var i, p, x, z, y, zz, u, r;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (i = 0; i < land.length; i++) {
        p = land[i];
        x = p.x * ca + p.z * sa;
        z = -p.x * sa + p.z * ca;
        y = p.y * cb - z * sb;
        zz = p.y * sb + z * cb;
        buckets[zz < 0 ? 0 : 1 + Math.min(4, Math.floor(zz * 5))].push(cx + x * R, cy - y * R);
      }
      ctx.fillStyle = '#f2ede4';
      for (i = 0; i < buckets.length; i++) {
        ctx.globalAlpha = (i ? 0.08 + i * 0.08 : 0.04) * quiet;
        r = i ? dot : dot * 0.7;
        ctx.beginPath();
        for (p = 0; p < buckets[i].length; p += 2) ctx.rect(buckets[i][p] - r / 2, buckets[i][p + 1] - r / 2, r, r);
        ctx.fill();
      }

      for (i = 0; i < cities.length; i++) {
        p = cities[i];
        x = p.x * ca + p.z * sa;
        z = -p.x * sa + p.z * ca;
        y = p.y * cb - z * sb;
        zz = p.y * sb + z * cb;
        p.zz = zz;
        if (zz < 0.02) continue;
        x = p.sx = cx + x * R;
        y = p.sy = cy - y * R;
        big = 1 + 0.9 * p.g;
        r = Math.max(quiet, p.g);
        ctx.fillStyle = ctx.strokeStyle = p.c;
        ctx.globalAlpha = 0.12 * zz * r;
        ctx.beginPath();
        ctx.arc(x, y, dot * 3.4 * big, 0, 6.2832);
        ctx.fill();
        ctx.globalAlpha = Math.min(1, 0.35 + zz) * r;
        ctx.beginPath();
        ctx.arc(x, y, dot * 1.5 * big, 0, 6.2832);
        ctx.fill();
        if (!reduce.matches) {
          u = (now / 6400 + p.ph) % 1;
          ctx.globalAlpha = (1 - u) * (1 - u) * 0.5 * zz * r;
          ctx.lineWidth = Math.max(1, dot * 0.45);
          ctx.beginPath();
          ctx.arc(x, y, dot * (2 + 8 * u), 0, 6.2832);
          ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
    }

    /* Coasts after a throw, eases back to the slow turn, and stops under a hovered pin. */
    function frame(now) {
      var dt = Math.min(64, now - (last || now));
      var target = hover || reduce.matches ? 0 : TURN;
      last = now;
      if (!drag) {
        vel = target + (vel - target) * Math.exp(-dt / (hover ? 240 : 1100));
        rot += vel * dt;
      }
      focus += ((hover ? 1 : 0) - focus) * Math.min(1, dt / 160);
      raf = requestAnimationFrame(frame);
      if (!onScreen || canvas.parentNode.classList.contains('is-under')) return;
      if (label) feature(now);
      var lit = hover || feat;
      for (var i = 0; i < cities.length; i++) {
        cities[i].g += ((cities[i] === lit ? 1 : 0) - cities[i].g) * Math.min(1, dt / 220);
      }
      draw(now);
      if (!label) return;
      showLabel(lit);
      if (lit) place(lit);
    }

    /* The city crossing the middle of the globe lights up and is named; each holds
       for a moment so a dense region like Europe doesn't flicker through names. */
    function feature(now) {
      var best = null, bd = R * 0.14, i, p, d;
      if (hover || drag || reduce.matches) {
        feat = null;
        return;
      }
      if (feat && now - featAt < 2600 && feat.zz > 0.3) return;
      for (i = 0; i < cities.length; i++) {
        p = cities[i];
        if (p.zz < 0.45) continue;
        d = Math.abs(p.sx - cx);
        if (d < bd) { bd = d; best = p; }
      }
      if (best !== feat) {
        feat = best;
        featAt = now;
      }
    }

    function place(p) {
      var cr = canvas.getBoundingClientRect();
      var ir = canvas.parentNode.getBoundingClientRect();
      var k = cr.width / canvas.width;
      var x = cr.left - ir.left + p.sx * k;
      var y = cr.top - ir.top + p.sy * k;
      var left = p.sx > cx + R * 0.3;
      label.classList.toggle('is-left', left);
      label.style.transform = 'translate(' + Math.round(x + (left ? -20 : 20)) + 'px,' + Math.round(y) + 'px) translate(' + (left ? '-100%' : '0') + ',-50%)';
    }

    function showLabel(p) {
      if (p === shown) return;
      shown = p;
      if (p) {
        label.firstChild.textContent = p.city;
        label.lastChild.textContent = p.meta;
      }
      label.classList.toggle('is-on', !!p);
    }

    function setHover(p) {
      if (p === hover) return;
      hover = p;
      canvas.classList.toggle('is-pin', !!p);
    }

    function at(e) {
      var r = canvas.getBoundingClientRect();
      var k = canvas.width / r.width;
      return { x: (e.clientX - r.left) * k, y: (e.clientY - r.top) * k, k: k };
    }

    function onSphere(q) {
      return (q.x - cx) * (q.x - cx) + (q.y - cy) * (q.y - cy) < R * R;
    }

    function pick(q) {
      var best = null, bd = 196 * q.k * q.k, i, p, d;
      for (i = 0; i < cities.length; i++) {
        p = cities[i];
        if (p.zz < 0.08) continue;
        d = (p.sx - q.x) * (p.sx - q.x) + (p.sy - q.y) * (p.sy - q.y);
        if (d < bd) { bd = d; best = p; }
      }
      return best;
    }

    new IntersectionObserver(function (entries) {
      onScreen = entries[0].isIntersecting;
    }).observe(canvas);

    if (!muted) canvas.addEventListener('pointermove', function (e) {
      var q = at(e);
      var da;
      if (drag) {
        da = (e.clientX - drag.x) * q.k / R;
        drag.moved += Math.abs(e.clientX - drag.x);
        rot += da;
        vel = 0.6 * vel + 0.4 * da / Math.max(8, e.timeStamp - drag.t);
        drag.x = e.clientX;
        drag.t = e.timeStamp;
        return;
      }
      if (e.pointerType !== 'mouse') return;
      setHover(pick(q));
      canvas.classList.toggle('is-grab', onSphere(q));
    });

    canvas.addEventListener('pointerdown', function (e) {
      var q = at(e);
      if (muted || !onSphere(q)) return;
      drag = { x: e.clientX, t: e.timeStamp, moved: 0, pin: pick(q) };
      vel = 0;
      setHover(null);
      canvas.setPointerCapture(e.pointerId);
      canvas.classList.add('is-dragging');
    });

    function release(e) {
      if (!drag) return;
      var pin = drag.moved < 6 && e.type === 'pointerup' ? drag.pin : null;
      if (e.timeStamp - drag.t > 80 || reduce.matches) vel = 0;
      drag = null;
      canvas.classList.remove('is-dragging');
      if (pin) jumpTo(pin.slug);
    }

    canvas.addEventListener('pointerup', release);
    canvas.addEventListener('pointercancel', release);
    canvas.addEventListener('pointerleave', function () {
      if (!drag) setHover(null);
    });

    function start() {
      cancelAnimationFrame(raf);
      size();
      raf = requestAnimationFrame(frame);
    }

    var img = new Image();
    img.onload = function () {
      var c = document.createElement('canvas');
      c.width = 360;
      c.height = 180;
      var g = c.getContext('2d');
      g.drawImage(img, 0, 0);
      var px = g.getImageData(0, 0, 360, 180).data;
      var N = 20000, k, lat, lon, gx, gy;
      for (k = 0; k < N; k++) {
        lat = Math.asin(1 - 2 * (k + 0.5) / N) * 57.2958;
        lon = ((k * 137.50776) % 360) - 180;
        gx = Math.min(359, Math.floor(lon + 180));
        gy = Math.min(179, Math.floor(90 - lat));
        if (px[(gy * 360 + gx) * 4] > 127 && lat > -60) land.push(unit(lat, lon));
      }
      start();
      canvas.classList.add('is-ready');
      new ResizeObserver(start).observe(canvas);
      reduce.addEventListener('change', start);
    };
    img.src = '/land.png';
  }
})();
