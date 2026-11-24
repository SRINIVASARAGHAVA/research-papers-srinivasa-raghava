(() => {
  'use strict';
  const search = document.getElementById('search');
  const topic = document.getElementById('topic');
  const cards = Array.from(document.querySelectorAll('.paper'));
  const topicNames = {
    'mathematical-physics': 'Mathematical physics',
    'number-theory': 'Number theory',
    partitions: 'Partitions & combinatorics',
    'special-functions': 'Special functions',
    'modular-forms': 'Modular forms & q-series',
    'algebraic-geometry': 'Algebraic geometry'
  };
  function filter() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const selected = topicNames[topic.value];
    let total = 0;
    cards.forEach(card => {
      const haystack = (card.querySelector('h3').textContent + ' ' + card.querySelector('.summary').textContent + ' ' + card.dataset.id + ' ' + card.dataset.topics).toLocaleLowerCase();
      const shown = terms.every(term => haystack.includes(term)) && (!selected || card.dataset.topics.includes(selected));
      card.hidden = !shown;
      if (shown) total++;
    });
    document.getElementById('result-count').textContent = `${total} ${total === 1 ? 'paper' : 'papers'}${total < cards.length ? ` of ${cards.length}` : ''}`;
    document.getElementById('empty-state').hidden = total !== 0;
  }
  document.getElementById('filters').hidden = false;
  search.addEventListener('input', filter);
  topic.addEventListener('change', filter);
  document.getElementById('clear-filters').addEventListener('click', () => {
    search.value = '';
    topic.value = '';
    filter();
    search.focus();
  });
  document.querySelectorAll('.copy-citation').forEach(button => {
    button.hidden = false;
    button.addEventListener('click', async () => {
      const card = button.closest('.paper');
      const code = card.querySelector('.citation code');
      const status = document.getElementById('citation-status');
      try {
        if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(code.textContent);
        status.textContent = `BibTeX citation copied for ${card.querySelector('h3').textContent.trim()}.`;
        const previous = button.innerHTML;
        button.textContent = 'Copied';
        window.setTimeout(() => { button.innerHTML = previous; }, 1800);
      } catch (_) {
        card.querySelector('.citation').open = true;
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(code);
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = 'Copy is unavailable. The citation is expanded and selected so you can copy it manually.';
      }
    });
  });
})();
