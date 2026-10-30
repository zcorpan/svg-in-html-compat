// Emulates "no SVG-in-HTML": every <svg> subtree parsed by the HTML parser becomes
// HTML-namespace elements with the same local names and attributes (HTMLUnknownElement),
// as if the tree builder had no foreign-content handling. Approximate: real parsing
// would also differ for self-closing tags, CDATA, and HTML breakout tags inside <svg>.
() => {
  const HTML = 'http://www.w3.org/1999/xhtml';
  function convert(node) {
    if (node.nodeType !== 1) return node.cloneNode(false);
    const el = document.createElementNS(HTML, node.localName);
    for (const a of node.attributes) {
      try { el.setAttributeNS(a.namespaceURI, a.name, a.value); } catch (e) {}
    }
    for (const c of node.childNodes) el.appendChild(convert(c));
    return el;
  }
  const svgs = [...document.querySelectorAll('svg')].filter(
    s => !s.parentNode || s.parentNode.namespaceURI !== 'http://www.w3.org/2000/svg');
  for (const s of svgs) s.replaceWith(convert(s));
  return { replaced: svgs.length, leftover: document.getElementsByTagNameNS('http://www.w3.org/2000/svg', '*').length };
}
