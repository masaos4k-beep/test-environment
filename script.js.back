const chips = document.querySelectorAll('.filter-chip');
const cards = document.querySelectorAll('.content-card');
chips.forEach(chip => chip.addEventListener('click', () => {
  const selected = chip.dataset.filter;
  chips.forEach(item => item.classList.toggle('active', item === chip));
  cards.forEach(card => { card.hidden = selected !== 'すべて' && card.dataset.category !== selected; });
}));
const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');
menuButton.addEventListener('click', () => {
  const open = nav.classList.toggle('open');
  menuButton.setAttribute('aria-expanded', String(open));
});
nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
  nav.classList.remove('open');
  menuButton.setAttribute('aria-expanded', 'false');
}));
document.getElementById('year').textContent = new Date().getFullYear();
// 準備中カードはリンク先へ移動しないようにします。
document.querySelectorAll('[data-placeholder="true"]').forEach(card => {
  card.addEventListener('click', event => event.preventDefault());
});


// articles.json は scripts/build_article_index.py で生成します。
async function loadLatestArticles() {
  const container = document.getElementById('latest-articles-grid');
  if (!container) return;
  try {
    const response = await fetch('articles.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('記事一覧を取得できませんでした');
    const articles = await response.json();
    const sorted = [...articles].sort((a, b) => (b.date || '').localeCompare(a.date || '')).slice(0, 6);
    if (!sorted.length) {
      container.innerHTML = '<p class="article-empty">記事はまだありません。記事を追加すると、ここに自動表示されます。</p>';
      return;
    }
    container.innerHTML = '';
    sorted.forEach(article => {
      const card = document.createElement('article');
      card.className = 'article-card';
      const link = document.createElement('a');
      link.className = 'article-card-link';
      link.href = article.url;
      const category = document.createElement('span');
      category.className = 'tag';
      category.textContent = article.category || '記事';
      const title = document.createElement('h3');
      title.textContent = article.title || 'タイトル未設定';
      const date = document.createElement('time');
      date.className = 'article-date';
      date.dateTime = article.date || '';
      date.textContent = article.date ? article.date.replaceAll('-', '/') : '';
      const description = document.createElement('p');
      description.textContent = article.description || '';
      const more = document.createElement('span');
      more.className = 'card-link';
      more.textContent = '記事を読む ↗';
      link.append(category, title, date, description, more);
      card.appendChild(link);
      container.appendChild(card);
    });
  } catch (error) {
    container.innerHTML = '<p class="article-empty">記事一覧を読み込めませんでした。articles.json が作成されているか確認してください。</p>';
    console.error(error);
  }
}
loadLatestArticles();
