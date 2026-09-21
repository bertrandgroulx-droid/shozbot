/* ==========================================================================
   Shozbot studio kit.
   Drop this one line into any app, anywhere it is hosted:

     <script src="https://shozbot.com/kit/kit.js" defer></script>

   It adds a slim bar at the top with "← shozbot" linking back to the studio.
   Options, all optional, set on the script tag itself:

     data-app="Word Ninja"     show the app's name on the right of the bar
     data-hide-standalone      hide the bar when the app has been installed to
                               a phone home screen and is running full-screen

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
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', insert);
  } else {
    insert();
  }
})();
