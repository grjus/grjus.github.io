const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const source = readFileSync(join(__dirname, '../assets/theme.js'), 'utf8');

function page(theme, { saved = null, systemDark = false, storageBlocked = false } = {}) {
  const button = {
    hidden: true,
    attributes: {},
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, handler) { this[name] = handler; },
  };
  const preference = {
    matches: systemDark,
    addEventListener(name, handler) { this[name] = handler; },
  };
  const document = { documentElement: { dataset: { theme } }, querySelector: () => button };
  const window = {
    matchMedia: () => preference,
    addEventListener(name, handler) { this[name] = handler; },
  };
  const localStorage = {
    getItem() {
      if (storageBlocked) throw new Error('Storage blocked');
      return saved;
    },
    setItem(key, value) {
      if (storageBlocked) throw new Error('Storage blocked');
      saved = value;
    },
  };
  vm.runInNewContext(source, { document, window, localStorage });
  return { button, document, preference, window, save: value => { saved = value; } };
}

function expectTheme(context, theme) {
  const target = theme === 'dark' ? 'light' : 'dark';
  assert.equal(context.document.documentElement.dataset.theme, theme);
  assert.equal(context.button.textContent, `${target[0].toUpperCase()}${target.slice(1)} mode`);
  assert.equal(context.button.attributes['aria-label'], `Switch to ${target} mode`);
  assert.equal(context.button.hidden, false);
}

test('initial label offers the opposite of the active theme', () => {
  expectTheme(page('dark'), 'dark');
  expectTheme(page('light'), 'light');
});

test('clicks update the theme, label, and saved preference', () => {
  const context = page('dark', { systemDark: true });
  context.button.click();
  expectTheme(context, 'light');
  context.preference.change({ matches: true });
  expectTheme(context, 'light');
  context.button.click();
  expectTheme(context, 'dark');
});

test('system changes and cross-tab updates keep the label in sync', () => {
  const context = page('light');
  context.preference.matches = true;
  context.preference.change({ matches: true });
  expectTheme(context, 'dark');
  context.save('light');
  context.window.storage({ key: 'theme' });
  expectTheme(context, 'light');
  context.save('dark');
  context.window.storage({ key: 'theme' });
  expectTheme(context, 'dark');
  context.save(null);
  context.window.storage({ key: null });
  expectTheme(context, 'dark');
});

test('switching still works when storage is unavailable', () => {
  const context = page('dark', { storageBlocked: true });
  context.button.click();
  expectTheme(context, 'light');
});
