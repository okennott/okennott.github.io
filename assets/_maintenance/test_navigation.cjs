const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.join(__dirname, '../..');
const pages = ['index.html', 'research.html', 'publications.html', 'fieldwork.html', 'cv.html', 'contact.html'];
const html = name => fs.readFileSync(path.join(root, name), 'utf8');
const navigation = source => {
  const match = source.match(/<ul class="nav-links" id="primary-nav-links">[\s\S]*?\n  <\/ul>\n<\/nav>/);
  assert.ok(match, 'Expected the primary navigation');
  return match[0];
};

const menu = navigation(html(pages[0]));
for (const page of pages) {
  assert.equal(navigation(html(page)), menu, `Navigation differs in ${page}`);
}
assert.match(menu, /<li><a href="fieldwork\.html" id="nav-field">Fieldwork<\/a><\/li>\s*<\/ul>/);
assert.doesNotMatch(menu, /\n    <li><a href="fieldwork\.html" id="nav-field">/);

for (const match of menu.matchAll(/aria-controls="([^"]+)"/g)) {
  assert.match(menu, new RegExp(`id="${match[1]}"`), `Missing submenu ${match[1]}`);
}
const years = [...menu.matchAll(/href="publications\.html#year-(\d{4})"/g)].map(match => match[1]);
assert.equal(years.length, 9);
for (const year of years) {
  assert.match(html('publications.html'), new RegExp(`id="year-${year}"`));
}
assert.match(menu, /class="nav-submenu nav-submenu--columns" id="nav-publications-years"/);
console.log('Navigation checks passed: shared markup, nested Fieldwork, submenu targets and year links.');
