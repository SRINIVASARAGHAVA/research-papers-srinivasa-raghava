"""Build the static research catalogue from docs/papers.json (standard library only)."""
from pathlib import Path
from html import escape
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/papers.json").read_text(encoding="utf-8"))
PAPERS = DATA["papers"]
REPO = "https://github.com/SRINIVASARAGHAVA/research-papers-srinivasa-raghava"
NAME = "K. Srinivasa Raghava"
BIO = "My research moves between pure and applied mathematics, guided by a recurring question: what deeper structure explains the pattern in front of us? Alongside published papers and preprints, I enjoy writing clear mathematical notes and sharing new findings in ways that invite students and researchers into the conversation."

def date(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y").lstrip("0")

def bib(p):
    fields = [f"  title = {{{{{p['title']}}}}}", f"  author = {{{NAME}}}", "  year = {2026}",
        f"  eprint = {{{p['arxiv_id']}}}", "  archivePrefix = {arXiv}",
        f"  primaryClass = {{{p['categories'][0]}}}", f"  url = {{{p['version_url']}}}",
        f"  note = {{arXiv preprint, version {p['version']}}}"]
    return "@misc{raghava" + p["arxiv_id"].replace(".", "") + ",\n" + ",\n".join(fields) + "\n}"

def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")

def pdf_url(p, context="root"):
    filename = f"{p['latest_version_id']}.pdf"
    if (ROOT / "docs/pdfs" / filename).is_file():
        prefix = {"root": "docs/pdfs/", "paper": "../../docs/pdfs/", "site": "pdfs/"}[context]
        return prefix + filename
    return p["version_pdf_url"]

def paper_links(p, directory=False):
    return f"[Read PDF ({p['latest_version_id']})]({pdf_url(p, 'paper' if directory else 'root')}) · [arXiv record & version history]({p['abstract_url']})"

cards = []
for n, p in enumerate(PAPERS, 1):
    ident, title = p["arxiv_id"], escape(p["title"])
    topics = " ".join(p["topics"])
    tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in p["topics"])
    details = f"{REPO}/tree/main/papers/{ident}"
    cards.append(f'''<article class="paper" id="paper-{ident}" data-id="{ident}" data-topics="{escape(topics)}">
      <div class="paper-number" aria-hidden="true">{n:02}</div>
      <div class="paper-body">
        <div class="paper-meta"><span>arXiv:{p['latest_version_id']}</span><span>{p['pages']} pages</span><span>Version date: {date(p['latest_version_at'])} UTC</span></div>
        <h3><a href="{p['version_url']}">{title}</a></h3>
        <p class="summary">{escape(p['summary'])}</p>
        <div class="tags" aria-label="Research topics">{tags}</div>
        <div class="paper-actions">
          <a class="pdf-link" data-local-pdf="pdfs/{p['latest_version_id']}.pdf" href="{pdf_url(p, 'site')}">Read PDF <span aria-hidden="true">↗</span><span class="sr-only">: {title}</span></a>
          <a href="{p['abstract_url']}">arXiv &amp; versions<span class="sr-only">: {title}</span></a>
          <a href="{details}">Paper details<span class="sr-only">: {title}</span></a>
          <button class="copy-citation" type="button" data-id="{ident}" hidden>Copy BibTeX<span class="sr-only">: {title}</span></button>
        </div>
        <details class="citation"><summary>BibTeX citation</summary><pre><code>{escape(bib(p))}</code></pre></details>
      </div>
    </article>''')

write("docs/index.html", f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Research papers by K. Srinivasa Raghava: number theory, partitions, special functions, modular forms and algebraic geometry. Read preprints and download citations.">
  <meta name="author" content="{NAME}">
  <meta name="theme-color" content="#17333a">
  <title>Research papers | {NAME}</title>
  <link rel="stylesheet" href="styles.css">
  <script src="app.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#papers">Skip to research papers</a>
  <header class="site-header"><a class="wordmark" href="./" aria-label="Research collection home">KSR<span>Mathematics</span></a><nav aria-label="Main navigation"><a href="#papers">Papers</a><a href="#about">About</a><a href="{REPO}">GitHub <span aria-hidden="true">↗</span></a></nav></header>
  <main>
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-copy"><p class="eyebrow">A mathematics research collection</p><h1 id="page-title">{NAME}</h1><p class="hero-subtitle">Research papers</p><p class="intro">{escape(BIO)}</p><div class="hero-links"><a class="button" href="#papers">Browse the collection <span aria-hidden="true">↓</span></a><a href="citations.bib" download>Download all citations</a></div></div>
      <figure class="hero-portrait"><img src="k-srinivasa-raghava.png" alt="Portrait of {NAME}" width="1122" height="1402" fetchpriority="high"><figcaption><span>{NAME}</span><span>{len(PAPERS)} public preprints</span></figcaption></figure>
    </section>
    <section class="collection" id="papers" aria-labelledby="collection-title">
      <div class="section-heading"><div><p class="eyebrow">The collection</p><h2 id="collection-title">Papers &amp; preprints</h2></div><p>Version-specific PDFs.<br>Original records on arXiv.</p></div>
      <div class="filters" id="filters" hidden><div class="search-group"><label for="search">Search the collection</label><input id="search" type="search" placeholder="Title, topic or arXiv number" autocomplete="off"></div><div class="topic-group"><label for="topic">Research topic</label><select id="topic"><option value="">All topics</option><option value="number-theory">Number theory</option><option value="partitions">Partitions &amp; combinatorics</option><option value="special-functions">Special functions</option><option value="modular-forms">Modular forms &amp; q-series</option><option value="algebraic-geometry">Algebraic geometry</option></select></div><button id="clear-filters" type="button" class="clear-button">Clear filters</button></div>
      <div class="collection-line"><p id="result-count" role="status" aria-live="polite">{len(PAPERS)} papers</p><span>Ordered by arXiv identifier</span></div>
      <div id="paper-list">{''.join(cards)}</div>
      <p class="empty-state" id="empty-state" hidden>No papers match your search. Try another title, topic or arXiv number.</p>
      <p id="citation-status" class="sr-only" role="status" aria-live="polite"></p>
    </section>
    <section class="about" id="about" aria-labelledby="about-title"><div><p class="eyebrow">About this collection</p><h2 id="about-title">An open reading shelf.</h2></div><div><p>This collection brings together {len(PAPERS)} public arXiv preprints by {NAME}, with short summaries, version information and citations.</p><p>Each PDF link opens the version listed here. Follow the arXiv record for its abstract, submission history and any later revisions. The summaries describe the papers; an arXiv listing does not by itself indicate journal publication or peer review.</p><p class="rights">Paper copyrights and licenses remain those stated in the individual papers and arXiv records. The repository software license does not relicense the manuscripts.</p><a href="{REPO}">View the collection on GitHub <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span>{NAME}</span><span>Public preprints · Metadata checked {date(DATA['verified_on'])}</span></footer>
</body>
</html>
''')

bibliography = "\n\n".join(bib(p) for p in PAPERS) + "\n"
write("citations.bib", bibliography)
write("docs/citations.bib", bibliography)
write("docs/.nojekyll", "")

table = "\n".join(f"| {n} | [{p['title']}](papers/{p['arxiv_id']}/) | [{p['latest_version_id']}]({p['version_url']}) | {date(p['latest_version_at'])} | [PDF]({pdf_url(p)}) |" for n,p in enumerate(PAPERS,1))
summaries = "\n\n".join(f"### {n}. {p['title']}\n\n{p['summary']}\n\n{paper_links(p)} · [Details & citation](papers/{p['arxiv_id']}/)" for n,p in enumerate(PAPERS,1))
mirror_count = sum((ROOT / 'docs/pdfs' / f"{p['latest_version_id']}.pdf").is_file() for p in PAPERS)
mirror_note = (f"This collection includes {mirror_count} versioned PDF copies in `docs/pdfs/`. The original arXiv records remain linked for source information and version history." if mirror_count else "PDF links currently point to the official version-specific arXiv files. The archive workflow can add checked copies in `docs/pdfs/` and rebuild the links to those copies.")
write("README.md", f'''# Research papers

## {NAME}

<img src="docs/k-srinivasa-raghava.png" alt="Portrait of {NAME}" width="280">

{BIO}

A public collection of mathematics preprints covering number theory, partitions, special functions, modular forms, and algebraic geometry.

**{len(PAPERS)} public arXiv preprints** · Metadata checked **{date(DATA['verified_on'])}**

[Research website](https://srinivasaraghava.github.io/research-papers-srinivasa-raghava/) · [Browse all citations](citations.bib) · [arXiv author search]({DATA['author_search_url']})

PDF links below open the exact versions listed. Each arXiv record provides the full abstract, submission history, and access to later revisions. Papers are described as preprints; no journal publication status is implied.

## Paper index

| # | Paper | arXiv version | Version date (UTC) | Read |
| --- | --- | --- | --- | --- |
{table}

## Paper summaries

{summaries}

## Citing these papers

Use the BibTeX entry on each paper's detail page, or download [citations.bib](citations.bib) for the complete collection. Entries identify the version represented here. For example, the rational-partitions paper has its own [citation and version details](papers/2609.18945/).

## Rights

Paper copyrights and licenses remain those stated in the individual papers and their arXiv records. The repository software license does not relicense the manuscripts. The arXiv records in this collection use the [arXiv non-exclusive distribution license](https://arxiv.org/licenses/nonexclusive-distrib/1.0/), which is not a general Creative Commons license.

## Maintaining this collection

The public metadata is in [`docs/papers.json`](docs/papers.json). Check the individual arXiv records before changing titles, version numbers, dates, or PDF URLs. Keep submission dates distinct from version dates and label preprints accurately.

After updating the metadata, regenerate the catalogue with Python 3:

```sh
python scripts/build.py
```

The script creates the main index, paper detail pages, citations and static HTML. The website files are in [`docs/`](docs/) and are deployed by the GitHub Pages workflow. Search and filters run in the browser; all papers and citations remain readable without JavaScript.

{mirror_note} The builder selects a local PDF link only when the corresponding file is present. Archive only verified versions selected for public release.
''')

for p in PAPERS:
    doi = f"\n- DOI: [{p['doi_url']}]({p['doi_url']})" if "pending" not in p["doi_registration_status"] else "\n- DOI registration: marked pending by the arXiv record when checked."
    write(f"papers/{p['arxiv_id']}/README.md", f'''# {p['title']}

**{NAME}**

{p['summary']}

{paper_links(p, directory=True)}

## Publication record

- Status: arXiv preprint
- Version in this collection: **{p['latest_version_id']}**
- First submitted: {date(p['submitted_at'])} UTC
- Version submitted: {date(p['latest_version_at'])} UTC
- Length reported by arXiv: {p['pages']} pages
- arXiv categories: {', '.join(p['categories'])}
- Metadata checked: {date(DATA['verified_on'])}{doi}

## Citation

```bibtex
{bib(p)}
```

## Rights and versions

The PDF link opens the version specified above. The [arXiv record]({p['abstract_url']}) contains the abstract, full version history and any subsequent revisions.

Paper copyrights and licenses remain those stated in the paper and its [arXiv license record]({p['license_url']}). The repository software license does not relicense the manuscript.

[Back to the research collection](../../README.md) · [All citations](../../citations.bib)
''')

print(f"Built catalogue, {len(PAPERS)} paper pages and citations.")
