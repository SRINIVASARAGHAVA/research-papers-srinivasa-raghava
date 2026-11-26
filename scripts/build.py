"""Build the research catalogue from arXiv and optional manuscript metadata."""
from pathlib import Path
from html import escape
from datetime import datetime
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "docs/papers.json").read_text(encoding="utf-8"))
PAPERS = DATA["papers"]
MANUSCRIPT_PATH = ROOT / "docs/manuscripts.json"
MANUSCRIPTS = json.loads(MANUSCRIPT_PATH.read_text(encoding="utf-8"))["manuscripts"] if MANUSCRIPT_PATH.is_file() else []
COLLECTION = MANUSCRIPTS + PAPERS
COLLECTION_DESCRIPTION = f"{len(PAPERS)} public arXiv preprints" + (f" and {len(MANUSCRIPTS)} author manuscript{'s' if len(MANUSCRIPTS) != 1 else ''}" if MANUSCRIPTS else "")
REPO = "https://github.com/SRINIVASARAGHAVA/research-papers-srinivasa-raghava"
PACKAGE_REPO = "https://github.com/SRINIVASARAGHAVA/Rational-Partitions-Package"
PACKAGE_TITLE = "Rational Partitions Package"
PACKAGE_DESCRIPTION = ("Diagonal Rational Partitions counts the ways to write a positive integer n as an unordered sum "
                       "of reduced fractions a/b with 1 ≤ a ≤ n and 2 ≤ b ≤ n. The table gives the number of eligible "
                       "fractions K(n) and the partition count R(n) for every n from 1 to 101.")
PACKAGE_FILES = [
    ("Read the paper (PDF)", "diagonal_rational_partitions.pdf"),
    ("Exact values (TXT)", "R_values.txt"),
    ("Typeset table (PDF)", "R_values_table.pdf"),
    ("Python code", "rational_partitions.py"),
    ("Mathematica code", "RationalPartitions.wl"),
]
NAME = "K. Srinivasa Raghava"
BIO = "My research moves between pure and applied mathematics, guided by a recurring question: what deeper structure explains the pattern in front of us? Alongside published papers and preprints, I enjoy writing clear mathematical notes and sharing new findings in ways that invite students and researchers into the conversation."
FEATURE_URL = "https://ictp.global/news/13119204"
FEATURE_TITLE = "Srinivasa Raghava: Patterns, Primes, and the Ramanujan Influence"
FEATURE_DESCRIPTION = "A conversation about Ramanujan's influence, mathematical intuition, experimentation, and the ideas behind my research."
FEATURE_ATTRIBUTION = "Interview by Abdulhafeez Abdulsalam for InvariantMath, shared on the ICTP Global Science Portal."
FACEBOOK = "https://www.facebook.com/SRINIVASARAGHAVA6174"
X_PROFILE = "https://x.com/SrinivasR1729"

def date(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y").lstrip("0")

def bib(p):
    if "arxiv_id" not in p:
        fields = [f"  title = {{{{{p['title']}}}}}", f"  author = {{{' and '.join(p['authors'])}}}",
            f"  note = {{Author manuscript; added to collection {date(p['added_on'])}}}",
            f"  url = {{https://srinivasaraghava.github.io/research-papers-srinivasa-raghava/pdfs/{p['pdf_filename']}}}"]
        return "@unpublished{" + p["citation_key"] + ",\n" + ",\n".join(fields) + "\n}"
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
    prefix = {"root": "docs/pdfs/", "paper": "../../docs/pdfs/", "site": "pdfs/"}[context]
    if "arxiv_id" not in p:
        return prefix + p["pdf_filename"]
    filename = f"{p['latest_version_id']}.pdf"
    if (ROOT / "docs/pdfs" / filename).is_file():
        return prefix + filename
    return p["version_pdf_url"]

def paper_links(p, directory=False):
    if "arxiv_id" not in p:
        return f"[Read PDF]({pdf_url(p, 'paper' if directory else 'root')}) · Author manuscript"
    return f"[Read PDF ({p['latest_version_id']})]({pdf_url(p, 'paper' if directory else 'root')}) · [arXiv record & version history]({p['abstract_url']})"

cards = []
for n, p in enumerate(COLLECTION, 1):
    is_arxiv = "arxiv_id" in p
    ident, title = p["arxiv_id"] if is_arxiv else p["id"], escape(p["title"])
    title_url = p["version_url"] if is_arxiv else pdf_url(p, "site")
    pdf_filename = f"{p['latest_version_id']}.pdf" if is_arxiv else p["pdf_filename"]
    record_label = f"arXiv:{p['latest_version_id']}" if is_arxiv else "Author manuscript"
    date_label = f"Version date: {date(p['latest_version_at'])} UTC" if is_arxiv else f"Added to collection: {date(p['added_on'])}"
    record_link = f'<a href="{p["abstract_url"]}">arXiv &amp; versions<span class="sr-only">: {title}</span></a>' if is_arxiv else ""
    if ident == "2609.18945":
        record_link += f' <a href="#rational-partitions-package">{PACKAGE_TITLE}</a>'
    topics = " ".join(p["topics"])
    tags = "".join(f'<span class="tag">{escape(t)}</span>' for t in p["topics"])
    details = f"{REPO}/tree/main/papers/{ident}"
    cards.append(f'''<article class="paper" id="paper-{ident}" data-id="{ident}" data-topics="{escape(topics)}">
      <div class="paper-number" aria-hidden="true">{n:02}</div>
      <div class="paper-body">
        <div class="paper-meta"><span>{record_label}</span><span>{p['pages']} pages</span><span>{date_label}</span></div>
        <h3><a href="{title_url}">{title}</a></h3>
        <p class="summary">{escape(p['summary'])}</p>
        <div class="tags" aria-label="Research topics">{tags}</div>
        <div class="paper-actions">
          <a class="pdf-link" data-local-pdf="pdfs/{pdf_filename}" href="{pdf_url(p, 'site')}">Read PDF <span aria-hidden="true">↗</span><span class="sr-only">: {title}</span></a>
          {record_link}
          <a href="{details}">Paper details<span class="sr-only">: {title}</span></a>
          <button class="copy-citation" type="button" data-id="{ident}" hidden>Copy BibTeX<span class="sr-only">: {title}</span></button>
        </div>
        <details class="citation"><summary>BibTeX citation</summary><pre><code>{escape(bib(p))}</code></pre></details>
      </div>
    </article>''')

package_links = [(label, f"{PACKAGE_REPO}/blob/main/{filename}") for label, filename in PACKAGE_FILES]
package_html = "\n          ".join(f'<a class="feature-link" href="{url}">{escape(label)}</a>' for label, url in package_links)
package_markdown = " · ".join(f"[{label}]({url})" for label, url in package_links)

write("docs/index.html", f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Research papers by K. Srinivasa Raghava: mathematical physics, number theory, partitions, special functions, modular forms and algebraic geometry. Read manuscripts and preprints, and download citations.">
  <meta name="author" content="{NAME}">
  <meta name="theme-color" content="#17333a">
  <title>Research papers | {NAME}</title>
  <link rel="stylesheet" href="styles.css">
  <script src="app.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#papers">Skip to research papers</a>
  <header class="site-header"><a class="wordmark" href="./" aria-label="Research collection home">KSR<span>Mathematics</span></a><nav aria-label="Main navigation"><a href="#rational-partitions-package">Package</a><a href="#papers">Papers</a><a href="#feature">Interview</a><a href="#about">About</a><a href="{REPO}">GitHub <span aria-hidden="true">↗</span></a></nav></header>
  <main>
    <section class="hero" aria-labelledby="page-title">
      <div class="hero-copy"><p class="eyebrow">A mathematics research collection</p><h1 id="page-title">{NAME}</h1><p class="hero-subtitle">Research papers</p><p class="intro">{escape(BIO)}</p><div class="hero-links"><a class="button" href="#papers">Browse the collection <span aria-hidden="true">↓</span></a><a href="citations.bib" download>Download all citations</a></div><p class="social-links"><span>Connect</span><a href="{FACEBOOK}">Facebook</a><a href="{X_PROFILE}">X (Twitter)</a></p></div>
      <figure class="hero-portrait"><img src="k-srinivasa-raghava.png" alt="Portrait of {NAME}" width="1122" height="1402" fetchpriority="high"><figcaption><span>{NAME}</span><span>{len(COLLECTION)} research papers</span></figcaption></figure>
    </section>
    <section class="feature" id="rational-partitions-package" aria-labelledby="package-title">
      <div class="feature-meta"><p class="eyebrow">Featured research</p><a class="feature-link" href="{PACKAGE_REPO}">Full package on GitHub</a></div>
      <div class="feature-copy"><h2 id="package-title">{PACKAGE_TITLE}</h2>
        <p class="feature-description">{escape(PACKAGE_DESCRIPTION)}</p>
        <div class="social-links">
          {package_html}
        </div>
      </div>
    </section>
    <section class="collection" id="papers" aria-labelledby="collection-title">
      <div class="section-heading"><div><p class="eyebrow">The collection</p><h2 id="collection-title">Papers &amp; preprints</h2></div><p>{COLLECTION_DESCRIPTION}.</p></div>
      <div class="filters" id="filters" hidden><div class="search-group"><label for="search">Search the collection</label><input id="search" type="search" placeholder="Title, topic or arXiv number" autocomplete="off"></div><div class="topic-group"><label for="topic">Research topic</label><select id="topic"><option value="">All topics</option><option value="mathematical-physics">Mathematical physics</option><option value="number-theory">Number theory</option><option value="partitions">Partitions &amp; combinatorics</option><option value="special-functions">Special functions</option><option value="modular-forms">Modular forms &amp; q-series</option><option value="algebraic-geometry">Algebraic geometry</option></select></div><button id="clear-filters" type="button" class="clear-button">Clear filters</button></div>
      <div class="collection-line"><p id="result-count" role="status" aria-live="polite">{len(COLLECTION)} papers</p><span>{'Author manuscripts first; arXiv papers by identifier' if MANUSCRIPTS else 'Ordered by arXiv identifier'}</span></div>
      <div id="paper-list">{''.join(cards)}</div>
      <p class="empty-state" id="empty-state" hidden>No papers match your search. Try another title, topic or arXiv number.</p>
      <p id="citation-status" class="sr-only" role="status" aria-live="polite"></p>
    </section>
    <section class="feature" id="feature" aria-labelledby="feature-title"><div class="feature-meta"><p class="eyebrow">Special feature</p><p class="feature-source">ICTP Global Science Portal</p><time datetime="2026-03-24">24 March 2026</time></div><div class="feature-copy"><h2 id="feature-title">{escape(FEATURE_TITLE)}</h2><p class="feature-description">{escape(FEATURE_DESCRIPTION)}</p><p class="feature-attribution">{escape(FEATURE_ATTRIBUTION)}</p><a class="feature-link" href="{FEATURE_URL}">Read the interview <span aria-hidden="true">↗</span></a></div></section>
    <section class="about" id="about" aria-labelledby="about-title"><div><p class="eyebrow">About this collection</p><h2 id="about-title">An open reading shelf.</h2></div><div><p>This collection brings together {COLLECTION_DESCRIPTION} by {NAME}, with short summaries, source information and citations.</p><p>Author manuscripts are shared directly by the author and labeled with the date added to the collection. For arXiv preprints, each PDF link opens the listed version; the linked arXiv record provides its abstract, submission history and later revisions. These labels do not imply journal publication or peer review.</p><p class="rights">Paper copyrights and licenses remain those stated in the individual papers and, where applicable, their arXiv records. The repository software license does not relicense the manuscripts.</p><a href="{REPO}">View the collection on GitHub <span aria-hidden="true">↗</span></a></div></section>
  </main>
  <footer><span>{NAME}</span><span>Research papers · arXiv metadata checked {date(DATA['verified_on'])}</span></footer>
</body>
</html>
''')

bibliography = "\n\n".join(bib(p) for p in COLLECTION) + "\n"
write("citations.bib", bibliography)
write("docs/citations.bib", bibliography)
write("docs/.nojekyll", "")

table_rows = []
summary_sections = []
for n, p in enumerate(COLLECTION, 1):
    is_arxiv = "arxiv_id" in p
    ident = p["arxiv_id"] if is_arxiv else p["id"]
    record = f"[{p['latest_version_id']}]({p['version_url']})" if is_arxiv else "Author manuscript"
    listed_date = f"Version: {date(p['latest_version_at'])} UTC" if is_arxiv else f"Added: {date(p['added_on'])}"
    table_rows.append(f"| {n} | [{p['title']}](papers/{ident}/) | {record} | {listed_date} | [PDF]({pdf_url(p)}) |")
    summary_sections.append(f"### {n}. {p['title']}\n\n{p['summary']}\n\n{paper_links(p)} · [Details & citation](papers/{ident}/)")
table = "\n".join(table_rows)
summaries = "\n\n".join(summary_sections)
mirror_count = sum((ROOT / 'docs/pdfs' / f"{p['latest_version_id']}.pdf").is_file() for p in PAPERS)
mirror_note = (f"This collection includes {mirror_count} versioned arXiv PDF copies in `docs/pdfs/`. The original arXiv records remain linked for source information and version history." if mirror_count else "ArXiv PDF links currently point to the official version-specific files. The archive workflow can add checked copies in `docs/pdfs/` and rebuild the links to those copies.")
manuscript_note = "Author-supplied manuscripts are recorded separately in [`docs/manuscripts.json`](docs/manuscripts.json), with their PDF filenames, collection-added dates and file checksums. Keep the supplied PDF bytes unchanged. This optional file is independent of the arXiv archive workflow." if MANUSCRIPTS else ""
write("README.md", f'''# Research papers

## {NAME}

<img src="docs/k-srinivasa-raghava.png" alt="Portrait of {NAME}" width="280">

{BIO}

[Facebook]({FACEBOOK}) · [X (Twitter)]({X_PROFILE})

A public collection of research papers covering mathematical physics, number theory, partitions, special functions, modular forms, and algebraic geometry.

**{len(COLLECTION)} papers: {COLLECTION_DESCRIPTION}** · arXiv metadata checked **{date(DATA['verified_on'])}**

[Research website](https://srinivasaraghava.github.io/research-papers-srinivasa-raghava/) · [Browse all citations](citations.bib) · [arXiv author search]({DATA['author_search_url']})

Author manuscripts are shared directly by the author and labeled with their collection-added dates. ArXiv PDF links open the exact versions listed; each arXiv record provides the full abstract, submission history, and access to later revisions. These labels do not imply journal publication or peer review.

## Featured research

### [{PACKAGE_TITLE}]({PACKAGE_REPO})

{PACKAGE_DESCRIPTION}

{package_markdown}

## Special feature

### [{FEATURE_TITLE}]({FEATURE_URL})

**ICTP Global Science Portal · 24 March 2026**

{FEATURE_DESCRIPTION}

{FEATURE_ATTRIBUTION}

[Read the interview]({FEATURE_URL})

## Paper index

| # | Paper | Record / status | Version / collection date | Read |
| --- | --- | --- | --- | --- |
{table}

## Paper summaries

{summaries}

## Citing these papers

Use the BibTeX entry on each paper's detail page, or download [citations.bib](citations.bib) for the complete collection. ArXiv entries identify the version represented here. Author manuscripts use `@unpublished` entries with their collection-added dates. For example, the rational-partitions paper has its own [citation and version details](papers/2609.18945/).

## Rights

Paper copyrights and licenses remain those stated in the individual papers and, where applicable, their arXiv records. The repository software license does not relicense the manuscripts. The arXiv records in this collection use the [arXiv non-exclusive distribution license](https://arxiv.org/licenses/nonexclusive-distrib/1.0/), which is not a general Creative Commons license.

## Maintaining this collection

The arXiv metadata is in [`docs/papers.json`](docs/papers.json). Check the individual arXiv records before changing titles, version numbers, dates, or PDF URLs. Keep submission dates distinct from version dates and label preprints accurately.

{manuscript_note}

After updating the metadata, regenerate the catalogue with Python 3:

```sh
python scripts/build.py
```

The script creates the main index, paper detail pages, citations and static HTML. The website files are in [`docs/`](docs/) and are deployed by the GitHub Pages workflow. Search and filters run in the browser; all papers and citations remain readable without JavaScript.

{mirror_note} For arXiv entries, the builder selects a local PDF link only when the corresponding file is present. Author manuscripts link to their supplied files in `docs/pdfs/`. Archive only papers selected for public release.
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

for p in MANUSCRIPTS:
    write(f"papers/{p['id']}/README.md", f'''# {p['title']}

**{', '.join(p['authors'])}**

{p['summary']}

{paper_links(p, directory=True)}

## Manuscript record

- Status: Author manuscript
- Added to collection: {date(p['added_on'])}
- Length: {p['pages']} pages
- Research topics: {', '.join(p['topics'])}

The PDF is shared directly by the author. The collection-added date records when it was added to this reading collection.

## Citation

```bibtex
{bib(p)}
```

## Rights

Paper copyrights and licenses remain those stated in the manuscript. The repository software license does not relicense the manuscript.

[Back to the research collection](../../README.md) · [All citations](../../citations.bib)
''')

print(f"Built catalogue, {len(COLLECTION)} paper pages and citations.")
