/* ==========================================================================
   Shozbot studio kit.
   Drop this one line into any app, anywhere it is hosted:

     <script src="https://shozbot.com/kit/kit.js" defer></script>

   It does two things: adds a slim bar at the top with "← shozbot" linking back
   to the studio, and counts the visit. Options, all optional, set on the script
   tag itself:

     data-app="Word Ninja"     show the app's name on the right of the bar
     data-hide-standalone      hide the bar when the app has been installed to
                               a phone home screen and is running full-screen
     data-no-bar               count the visit but add no bar, for an app whose
                               layout a bar would spoil
     data-no-count             the bar, but no counting

   Everything is namespaced `shozkit-`; the script touches nothing else on the
   page and is safe to include twice.
   ========================================================================== */
(function () {
  'use strict';

  var ORIGIN = 'https://shozbot.com';
  var ID = 'shozkit-bar';

  if (document.getElementById(ID)) return;          // already inserted

  var tag = document.currentScript ||
            document.querySelector('script[src*="/kit/kit.js"]');
  var opts = (tag && tag.dataset) || {};

  var standalone =
    (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) ||
    window.navigator.standalone === true;

  if ('hideStandalone' in opts && standalone) return;

  function insert() {
    if (document.getElementById(ID)) return;

    if (!document.querySelector('link[data-shozkit]')) {
      var css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = ORIGIN + '/kit/kit.css';
      css.setAttribute('data-shozkit', '');
      document.head.appendChild(css);
    }

    var bar = document.createElement('div');
    bar.id = ID;
    bar.className = 'shozkit-bar';

    var home = document.createElement('a');
    home.className = 'shozkit-home';
    home.href = ORIGIN + '/';
    // The wordmark, in the studio's own casing.
    home.innerHTML = '<span class="shozkit-arrow" aria-hidden="true">&#8592;</span>' +
                     '<span>shozbot</span>';
    home.setAttribute('aria-label', 'Back to shozbot.com');
    bar.appendChild(home);

    if (opts.app) {
      var name = document.createElement('span');
      name.className = 'shozkit-app';
      name.textContent = opts.app;
      bar.appendChild(name);
    }

    document.body.insertBefore(bar, document.body.firstChild);

    // Apps pad their own <body>, which would leave the bar floating inside that
    // padding with a strip of the app's background above and beside it. Pull it
    // back out to the edges. Measured rather than assumed, because every app
    // uses a different value — and only ever pulled up and sideways, never
    // bottom, so nothing below it moves.
    var pad = window.getComputedStyle(document.body);
    if (parseFloat(pad.paddingTop) || parseFloat(pad.paddingLeft)) {
      bar.style.width = 'auto';
      bar.style.marginTop = '-' + pad.paddingTop;
      bar.style.marginLeft = '-' + pad.paddingLeft;
      bar.style.marginRight = '-' + pad.paddingRight;
    }
  }

  // ---- visitor counting -------------------------------------------------
  // GoatCounter: cookieless, stores nothing on the visitor's machine and
  // identifies nobody. Injected here rather than pasted into seven apps, so the
  // day it needs changing it changes once.
  //
  // count.js finds its own endpoint by looking for a script tag carrying
  // data-goatcounter, which is why the attribute goes on the element rather
  // than into a variable. Loaded async: if it is slow or blocked, the app does
  // not wait and does not care.
  function count() {
    if ('noCount' in opts) return;
    if (document.querySelector('script[data-goatcounter]')) return;   // twice is once

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://gc.zgo.at/count.js';
    s.setAttribute('data-goatcounter', 'https://shozbot.goatcounter.com/count');
    document.head.appendChild(s);
  }

  function start() {
    if (!('noBar' in opts)) insert();
    count();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
