(function () {
  var current = '__DECK_VERSION__';
  var endpoint = 'https://api.github.com/repos/tentyou/anki-ielts-decks/releases/latest';
  var storageKey = 'anki-ielts-release-check-v1';
  var stateKey = '__ankiIeltsReleaseCheck';
  var state = window[stateKey] || (window[stateKey] = {});
  var elements = document.querySelectorAll('.deck-updates');
  var element = elements[elements.length - 1];
  if (!element || element.hidden) return;
  var button = element.querySelector('.check-update');
  var link = element.querySelector('.release-link');
  var status = element.querySelector('.update-status');
  var successTTL = 24 * 60 * 60 * 1000;
  var failureTTL = 60 * 60 * 1000;

  function version(value) {
    var match = /^v?(\d+)\.(\d+)\.(\d+)$/.exec(value || '');
    return match ? [Number(match[1]), Number(match[2]), Number(match[3])] : null;
  }

  function newer(candidate) {
    var latest = version(candidate), installed = version(current);
    if (!latest || !installed) return false;
    for (var i = 0; i < 3; i++) {
      if (latest[i] !== installed[i]) return latest[i] > installed[i];
    }
    return false;
  }

  function readCache() {
    try {
      var cached = JSON.parse(localStorage.getItem(storageKey));
      if (cached && typeof cached.at === 'number') state.cache = cached;
    } catch (_) { /* Some review webviews disable persistent storage. */ }
    return state.cache || {};
  }

  function saveCache(cache) {
    state.cache = cache;
    try { localStorage.setItem(storageKey, JSON.stringify(cache)); } catch (_) {}
  }

  function render(cache, manual) {
    if (!document.contains(element)) return;
    button.disabled = false;
    button.textContent = '检查更新';
    link.textContent = newer(cache.latest) ? '发现 v' + version(cache.latest).join('.') + ' · 下载' : '版本与下载';
    if (manual) {
      status.textContent = cache.ok ? (newer(cache.latest) ? '下载后导入并同步。' : '当前已是最新版本。') : '暂时无法检查，请打开“版本与下载”。';
    }
  }

  // Share one request across front/back renders in the same webview.
  function request(done) {
    if (state.pending) { state.pending.push(done); return; }
    state.pending = [done];
    var xhr, completed = false;
    function finish(latest) {
      if (completed) return;
      completed = true;
      var old = readCache();
      var cache = { at: Date.now(), latest: latest || old.latest || '', ok: !!latest };
      saveCache(cache);
      var callbacks = state.pending;
      state.pending = null;
      for (var i = 0; i < callbacks.length; i++) callbacks[i](cache);
    }
    try {
      xhr = new XMLHttpRequest();
      xhr.open('GET', endpoint, true);
      xhr.timeout = 6000;
      xhr.onload = function () {
        try {
          var data = JSON.parse(xhr.responseText);
          finish(xhr.status === 200 && !data.draft && !data.prerelease && version(data.tag_name) ? data.tag_name : '');
        } catch (_) { finish(''); }
      };
      xhr.onerror = xhr.ontimeout = xhr.onabort = function () { finish(''); };
      xhr.send();
    } catch (_) { finish(''); }
  }

  function check(manual) {
    var cache = readCache();
    render(cache, false);
    var age = Date.now() - (cache.at || 0);
    if (!manual && age >= 0 && age < (cache.ok ? successTTL : failureTTL)) return;
    button.disabled = true;
    button.textContent = '检查中…';
    request(function (result) { render(result, manual); });
  }

  button.onclick = function () { check(true); };
  check(false);
})();
