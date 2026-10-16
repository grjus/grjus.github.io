(function () {
  var button = document.querySelector('.theme-toggle');
  var preference = window.matchMedia('(prefers-color-scheme: dark)');

  function savedTheme() {
    try { return localStorage.getItem('theme'); } catch (error) { return null; }
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    button.setAttribute('aria-pressed', String(theme === 'dark'));
  }

  applyTheme(document.documentElement.dataset.theme);
  button.hidden = false;
  button.addEventListener('click', function () {
    var theme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(theme);
    try { localStorage.setItem('theme', theme); } catch (error) {}
  });
  preference.addEventListener('change', function (event) {
    var saved = savedTheme();
    if (saved !== 'dark' && saved !== 'light') applyTheme(event.matches ? 'dark' : 'light');
  });
  window.addEventListener('storage', function (event) {
    if (event.key === 'theme' || event.key === null) {
      var saved = savedTheme();
      applyTheme(saved === 'dark' || saved === 'light' ? saved : (preference.matches ? 'dark' : 'light'));
    }
  });
}());
