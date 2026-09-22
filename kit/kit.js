/* ==========================================================================
   Shozbot studio kit.
   Drop this one line into any app, anywhere it is hosted:

     <script src="https://shozbot.com/kit/kit.js" defer></script>

   It does two things: adds a slim bar at the top with "← shozbot" linking back
   to the studio, and counts the visit. Options, all optional, set on the script
   tag itself:

     data-app="Word Ninja"     show the app's name on the right of the bar
     data-by=".brand .name"    no bar at all: put the words "by shozbot" just
                               after whatever that selector matches, usually
                               the app's own name or tagline
     data-by-block             with data-by, put the credit on its own line
                               rather than running on after the name
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

  function loadCss() {
    if (document.querySelector('link[data-shozkit]')) return;
    var css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = ORIGIN + '/kit/kit.css';
    css.setAttribute('data-shozkit', '');
    document.head.appendChild(css);
  }

  // ---- the byline -------------------------------------------------------
  // The quiet alternative to the bar: the words "by shozbot", clickable,
  // sitting beside or under the app's own name. A credit rather than a
  // navigation bar — it says who made this and happens to be the way to the
  // rest. `data-by` is a CSS selector for the app's own title or tagline and
  // the credit goes directly after it, which is why it costs the app almost
  // nothing: it borrows a line the app already draws.
  function insertBy() {
    if (document.getElementById(ID)) return;

    var host = document.querySelector(opts.by);
    if (!host) return;   // the app moved its title: say nothing rather than
                         // dropping a stray credit somewhere unintended
    loadCss();

    var block = 'byBlock' in opts;
    var wrap = document.createElement(block ? 'div' : 'span');
    wrap.id = ID;
    wrap.className = 'shozkit-by' + (block ? ' shozkit-by--block' : '');

    var a = document.createElement('a');
    a.className = 'shozkit-by-link';
    a.href = ORIGIN + '/';
    a.textContent = 'by shozbot';
    a.title = 'More handmade apps at shozbot.com';
    wrap.appendChild(a);

    host.parentNode.insertBefore(wrap, host.nextSibling);
  }

  function insert() {
    if (document.getElementById(ID)) return;
    loadCss();

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

    // The bar should cost an app its own height and not a pixel more. A column
    // flex or grid <body> puts its gap between every pair of children, so the
    // bar arrives carrying one — Better Weather's 18px gap turned a 38px bar
    // into 56px, which is what pushed its tab strip off an iPhone 14. Cancel it
    // with a matching negative margin, so the bar sits flush against the app.
    //
    // Only for a column: a row flex container's gap between items is the column
    // gap, and cancelling its row gap would take space the bar never took. And
    // only when something follows the bar, or the margin would eat the body's
    // own bottom padding instead.
    var disp = pad.display;
    var column = disp.indexOf('grid') >= 0 ||
                 (disp.indexOf('flex') >= 0 && pad.flexDirection === 'column');
    var gap = column ? parseFloat(pad.rowGap) : 0;
    if (gap && bar.nextElementSibling) bar.style.marginBottom = '-' + gap + 'px';
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
    // data-hide-standalone drops the bar, and only the bar. It used to return
    // out of the whole script, which quietly stopped the visit being counted
    // too — so an app used mostly from a home screen would have looked unused.
    var hidden = ('noBar' in opts) || ('hideStandalone' in opts && standalone);
    // data-by replaces the bar outright, and is never hidden when installed:
    // a credit line costs nothing worth hiding.
    if ('by' in opts) insertBy();
    else if (!hidden) insert();
    count();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
