/**
 * Geocoding widget for Wagtail admin.
 * Targets pages that have #id_latitude + #id_longitude fields.
 * Uses OpenStreetMap Nominatim (free, no API key, 1 req/s limit).
 */
(function () {
  'use strict';

  // Respect Nominatim's 1 req/s policy
  let lastReqTime = 0;
  const MIN_GAP = 1100;

  function nominatimFetch(url) {
    const wait = Math.max(0, MIN_GAP - (Date.now() - lastReqTime));
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        lastReqTime = Date.now();
        fetch(url, { headers: { 'Accept-Language': 'en' } })
          .then(r => r.json())
          .then(resolve)
          .catch(reject);
      }, wait);
    });
  }

  function buildWidget() {
    const div = document.createElement('div');
    div.className = 'geocode-widget';
    div.innerHTML = `
      <div class="geocode-header">
        <span class="geocode-icon">📍</span>
        <span class="geocode-title">Search location by name</span>
        <span class="geocode-badge">OpenStreetMap / Nominatim</span>
      </div>
      <div class="geocode-autocomplete">
        <div class="geocode-row">
          <input
            type="text"
            class="geocode-input"
            placeholder="e.g. Samarkand, Uzbekistan"
            autocomplete="off"
            spellcheck="false"
            aria-label="Search for a location"
            aria-autocomplete="list"
            aria-controls="geocode-results-list"
          />
          <button type="button" class="geocode-clear" title="Clear" hidden aria-label="Clear location">✕</button>
        </div>
        <ul class="geocode-results" id="geocode-results-list" role="listbox" hidden></ul>
      </div>
      <p class="geocode-hint">
        Type a city or landmark name → select a result → coordinates auto-fill below.
      </p>
    `;
    return div;
  }

  function init() {
    const latInput = document.getElementById('id_latitude');
    const lngInput = document.getElementById('id_longitude');
    if (!latInput || !lngInput) return;

    // Avoid double-init if tabs switch or DOM re-renders
    if (document.querySelector('.geocode-widget')) return;

    const widget = buildWidget();

    // Insert just before the latitude field's nearest panel/section ancestor
    const anchor =
      latInput.closest('[data-panel]') ||
      latInput.closest('.w-panel') ||
      latInput.closest('section') ||
      latInput.closest('.multiple') ||
      latInput.closest('.field') ||
      latInput.parentNode;

    anchor.insertAdjacentElement('beforebegin', widget);

    const searchInput = widget.querySelector('.geocode-input');
    const clearBtn    = widget.querySelector('.geocode-clear');
    const results     = widget.querySelector('.geocode-results');

    // --- reverse geocode existing coords on page load ---
    if (latInput.value && lngInput.value) {
      const url = `https://nominatim.openstreetmap.org/reverse?lat=${latInput.value}&lon=${lngInput.value}&format=json`;
      nominatimFetch(url)
        .then(data => {
          if (data && data.display_name) {
            searchInput.value = data.display_name;
            clearBtn.hidden = false;
          }
        })
        .catch(() => {});
    }

    // --- helpers ---
    function showResults(html) {
      results.innerHTML = html;
      results.hidden = !html;
    }

    function fillCoords(lat, lon, displayName) {
      latInput.value = lat;
      lngInput.value = lon;
      searchInput.value = displayName;
      clearBtn.hidden = false;
      results.hidden = true;
      // Tell Wagtail the form is dirty
      ['change', 'input'].forEach(ev => {
        latInput.dispatchEvent(new Event(ev, { bubbles: true }));
        lngInput.dispatchEvent(new Event(ev, { bubbles: true }));
      });
    }

    function search(q) {
      if (!q || q.length < 2) { showResults(''); return; }

      showResults('<li class="geocode-status">Searching…</li>');

      const url =
        `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=7&addressdetails=1`;

      nominatimFetch(url)
        .then(places => {
          if (!places.length) {
            showResults('<li class="geocode-status geocode-status--empty">No results found — try adding the country name.</li>');
            return;
          }

          const items = places.map(place => {
            const lat = parseFloat(place.lat).toFixed(6);
            const lon = parseFloat(place.lon).toFixed(6);
            const li = document.createElement('li');
            li.className = 'geocode-option';
            li.setAttribute('role', 'option');
            li.innerHTML = `
              <span class="geocode-option__name">${escHtml(place.display_name)}</span>
              <span class="geocode-option__coords">${lat},  ${lon}</span>
            `;
            li.addEventListener('mousedown', e => {
              e.preventDefault(); // keep focus on input until we're done
              fillCoords(lat, lon, place.display_name);
            });
            return li;
          });

          results.innerHTML = '';
          items.forEach(li => results.appendChild(li));
          results.hidden = false;
        })
        .catch(() => {
          showResults('<li class="geocode-status geocode-status--error">Request failed — check your connection.</li>');
        });
    }

    function escHtml(s) {
      return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    }

    // --- events ---
    let debounce;
    searchInput.addEventListener('input', () => {
      clearTimeout(debounce);
      clearBtn.hidden = !searchInput.value;
      debounce = setTimeout(() => search(searchInput.value.trim()), 420);
    });

    searchInput.addEventListener('keydown', e => {
      if (e.key === 'Enter')  { e.preventDefault(); clearTimeout(debounce); search(searchInput.value.trim()); }
      if (e.key === 'Escape') { results.hidden = true; }
    });

    searchInput.addEventListener('blur', () => {
      // Small delay so mousedown on result fires first
      setTimeout(() => { results.hidden = true; }, 180);
    });

    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      latInput.value    = '';
      lngInput.value    = '';
      clearBtn.hidden   = true;
      results.hidden    = true;
      latInput.dispatchEvent(new Event('change', { bubbles: true }));
      lngInput.dispatchEvent(new Event('change', { bubbles: true }));
      searchInput.focus();
    });
  }

  // Wagtail 5.x renders tabs/panels lazily; retry a few times
  function tryInit() {
    init();
    if (!document.getElementById('id_latitude')) {
      [600, 1500, 3000].forEach(ms => setTimeout(init, ms));
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', tryInit);
  } else {
    tryInit();
  }
})();
