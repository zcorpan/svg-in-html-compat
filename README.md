# Compat impact of removing SVG-in-HTML

Proposed change: the HTML parser stops creating SVG elements for inline `<svg>` in `text/html`, so inline SVG no longer renders. SVG in `<img>`, CSS, and standalone `image/svg+xml` documents is out of scope.

This was a quick check (under 5 minutes), not a full study. Partial data already rules the change out, so it stopped there.

## Issue comment

I checked how common inline `<svg>` is in Common Crawl and emulated the removal in Firefox Nightly on a sampled page. It's not web compatible: about half of HTML pages use inline SVG, and the first page tested loses its menu button's icon.

AI summary of the research ([zcorpan/svg-in-html-compat](https://github.com/zcorpan/svg-in-html-compat)):

> Method: one Common Crawl WARC (CC-MAIN-2026-39, 21,419 HTTP 200 `text/html` responses, all crawled URLs, not only root pages), counting documents with an `<svg>` start tag outside `<script>`. Removal was emulated in Firefox Nightly 161 by replacing each `<svg>` subtree with HTML-namespace elements of the same names and attributes (`HTMLUnknownElement`), checked on a test page. One seeded sampled page was compared before and after.
>
> | | Pages |
> |---|---|
> | HTML responses | 21,419 |
> | With inline `<svg>` | 10,432 (48.7%) |
>
> Affected pages:
>
> - larepublica.net: the header's menu/search button becomes a blank box, and the logo shifts ([before above, after below](https://github.com/zcorpan/svg-in-html-compat/blob/main/out/review/larepublica.png)).
>
> Inline SVG is a common way to ship icons (buttons, social links, logos), often without a text fallback, so I think removal would leave icon-only controls invisible on a large share of pages. Details: [README](https://github.com/zcorpan/svg-in-html-compat#readme).

## Method

- `count_svg.py` scans one local Common Crawl WARC (`CC-MAIN-20260906045500-20260906075500-00336.warc.gz`, from the seeded pick in `~/git/commoncrawl/cc-data/CC-MAIN-2026-39/`) with `cc.html_responses()`, prefilters on `<svg[\s>/]`, then counts `svg` start tags with Python's `html.parser`, which skips `<script>` and `<style>` text. Output: `out/cc-svg-count.json`, hits in `out/cc-svg-hits.jsonl` (URL queries stripped; not committed, regenerate with `count_svg.py`). `html.parser` doesn't run the tree builder, so `<svg>` inside `<template>` or `<noscript>` counts too.
- `emulate.js` is the emulation, run by hand in Firefox Nightly 161 after `load`. On a test page (`<p>icon:<svg width=40 height=40><circle …/><text …>Hi</text></svg>end`) the `<svg>` became an `HTMLUnknownElement`, its box went from 40×40 to an inline text box, and only the text "Hi" rendered. It's approximate: a parser without foreign content would also treat self-closing tags, CDATA sections, and HTML breakout tags inside `<svg>` differently, and scripts that ran before `load` saw real SVG elements.
- Sample: the hits sorted by URL and shuffled with `random.Random(1)`; the 5th entry was tested. Viewport screenshots at device scale 2 before and after; `out/review/larepublica.png` is a crop of the header, before on top, after below.

## Not covered

Root-page rates and rank (HTTP Archive), more than one sampled page, scripts that query or create SVG elements (`createElementNS`, `querySelector('svg path')`), SVG charts and maps, and other engines.

## Reproduce

This run was done with the [`httparchive` skill](https://github.com/zcorpan/web-platform-skills/blob/main/docs/httparchive.md). The steps above are standalone and rerun the same analysis without the skill.
