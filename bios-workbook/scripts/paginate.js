// BIOS workbook v3 — distributes #flow blocks over A4 pages.
// Rules: sections continue on the same page; headings never end a page; long cards split
// between sentences; figures shrink a little to fit, otherwise float to the top of the next
// page while the following text fills the current one (no big blank gaps).
(function () {
  const H = window.HDR;
  const MM = 96 / 25.4;
  let pageNo = 0, content = null, deferred = [];

  function frameSVG() {
    // frame: top line at y=17, corners r=9, sides at x=11.5 / 198.5, ends at y=276.5
    const L = 11.5, R = 198.5, T = 17, B = 276.5, r = 9, h = B - T;
    const y = f => (T + f * h).toFixed(2);
    const ring = (x, f) => `<circle cx="${x}" cy="${y(f)}" r="1.4" fill="#fff" stroke="var(--p2)" stroke-width=".55"/>`;
    return `<svg class="frame" viewBox="0 0 210 297" xmlns="http://www.w3.org/2000/svg">
      <path d="M${L} ${B} V${T + r} A${r} ${r} 0 0 1 ${L + r} ${T} H${R - r} A${r} ${r} 0 0 1 ${R} ${T + r} V${B}"
        fill="none" stroke="var(--p2)" stroke-width=".32"/>
      ${ring(L, .24)}${ring(L, .72)}${ring(R, .18)}${ring(R, .58)}${ring(R, .84)}
      <circle cx="${L}" cy="${B}" r="1.1" fill="var(--p2)"/><circle cx="${R}" cy="${B}" r="1.1" fill="var(--p2)"/>
      <rect x="${R - .55}" y="${y(.36)}" width="1.1" height="6" rx=".5" fill="var(--acc)"/>
      <g transform="translate(${L} ${y(.47)})">
        <circle r="4.2" fill="#fff" stroke="var(--p2)" stroke-width=".55"/>
        <circle r="3.2" fill="var(--warm)"/>
        <path d="M-1.35 .9 C-2.6 -.2 -2.3 -2.6 0 -2.6 C2.3 -2.6 2.6 -.2 1.35 .9 L1.2 1.6 H-1.2 Z" fill="var(--acc)"/>
        <rect x="-1.05" y="1.85" width="2.1" height=".55" rx=".25" fill="var(--pdk)"/>
        <rect x="-.8" y="2.6" width="1.6" height=".5" rx=".25" fill="var(--pdk)"/>
      </g></svg>`;
  }

  function newPage() {
    pageNo++;
    const s = document.createElement('section');
    s.className = 'page inner';
    let lines = '';
    for (let i = 0; i < H.notes; i++) lines += '<i></i>';
    s.innerHTML = frameSVG() +
      `<div class="hdr-mark">${H.mark}</div>` +
      `<div class="hdr-doc"><b>${H.doctor}</b><span dir="rtl">${H.line2}</span></div>` +
      `<div class="body"><div class="content"></div>` +
      (H.notes ? `<div class="notes"><div class="nh"><span class="pill">✎ Student Notes</span><span class="ar" dir="rtl">ملاحظات الطالب</span></div>${lines}</div>` : '') +
      `</div>` +
      `<div class="foot"><div class="ttl"><span>${H.foot_en}</span><span class="sep">│</span><em dir="rtl">${H.foot_ar}</em></div></div>` +
      `<div class="ptab">${pageNo}</div>`;
    document.body.appendChild(s);
    content = s.querySelector('.content');
    // floated figures go first on the fresh page
    const d = deferred; deferred = [];
    d.forEach(f => placeFigure(f, true));
  }

  const over = () => content.scrollHeight > content.clientHeight + 0.5;
  const used = () => { const l = content.lastElementChild; return l ? l.getBoundingClientRect().bottom - content.getBoundingClientRect().top : 0; };
  const room = () => content.clientHeight - used();
  const isHead = el => el && el.classList.contains('head');

  // move trailing headings of the current page onto a new page (keep-with-next)
  function breakKeepingHeads() {
    const heads = [];
    for (let el = content.lastElementChild; isHead(el); el = el.previousElementSibling) heads.unshift(el);
    if (heads.length && heads.length === content.children.length) heads.length = 0; // nothing else on page
    heads.forEach(h => h.remove());
    newPage();
    heads.forEach(h => content.appendChild(h));
  }

  function placeFigure(fig, fresh, minAbs) {
    content.appendChild(fig);
    if (!over()) return true;
    const img = fig.querySelector('img');
    const h = img.getBoundingClientRect().height;
    const need = content.scrollHeight - content.clientHeight;
    const target = h - need - 2;
    const minH = minAbs || Math.max(46 * MM, h * 0.55);
    if (target >= minH) {
      img.style.maxHeight = target + 'px';
      if (!over()) return true;
    }
    img.style.maxHeight = '';
    fig.remove();
    if (fresh || content.children.length === 0) {   // alone on an empty page: force-fit
      content.appendChild(fig);
      while (over() && img.getBoundingClientRect().height > 40 * MM) {
        img.style.maxHeight = (img.getBoundingClientRect().height - 4 * MM) + 'px';
      }
      return true;
    }
    deferred.push(fig);
    return false;
  }

  function placeSplit(blk) {
    const kids = Array.from(blk.children);
    const head = blk.dataset.head ? kids.shift() : null;
    let first = true;
    while (kids.length) {
      const shell = blk.cloneNode(false);
      if (head) shell.appendChild(head.cloneNode(true));
      if (!first) shell.classList.add('cont');
      content.appendChild(shell);
      let placed = 0;
      while (kids.length) {
        shell.appendChild(kids[0]);
        if (over()) { shell.removeChild(kids[0]); break; }
        kids.shift(); placed++;
      }
      if (placed === 0) {
        shell.remove();
        if (content.children.length === 0) {         // a single child taller than a page: accept overflow
          shell.appendChild(kids.shift()); content.appendChild(shell); first = false; continue;
        }
        breakKeepingHeads();
        continue;
      }
      first = false;
      if (kids.length) breakKeepingHeads();
    }
  }

  function placeBlock(blk) {
    if (blk.dataset.k === 'br') { newPage(); return; }
    if (blk.dataset.k === 'fig') { placeFigure(blk, false); return; }
    // a floated figure never drifts past the start of the next main section
    if (deferred.length && blk.classList.contains('sec')) {
      const f = deferred.shift();
      if (!placeFigure(f, false, 36 * MM)) newPage();   // squeeze it in, else close the page here
    }
    content.appendChild(blk);
    if (!over()) {
      // a heading needs room for at least ~22mm of what follows
      if (isHead(blk) && room() < 18 * MM) {
        blk.remove(); breakKeepingHeads(); content.appendChild(blk);
      }
      return;
    }
    blk.remove();
    if (blk.classList.contains('split')) { placeSplit(blk); return; }
    if (content.children.length === 0) { content.appendChild(blk); return; }
    breakKeepingHeads();
    content.appendChild(blk);
  }

  // short pairs: Arabic beside the English (one row); long pairs stay stacked (Arabic below).
  // Decided per pair by measuring both halves at the real column width.
  function lines(tx) {
    const cs = getComputedStyle(tx);
    let lh = parseFloat(cs.lineHeight);
    if (!cs.lineHeight.endsWith('px')) lh = lh * parseFloat(cs.fontSize);
    return Math.round(tx.getBoundingClientRect().height / lh);
  }
  // A group switches as a whole so a card never mixes the two layouts:
  // a paragraph card, one list item with its follow-up sentences, or one summary row.
  function trySide(pairs) {
    pairs.forEach(p => p.classList.add('side'));
    const ok = pairs.every(p => {
      const en = p.querySelector('.en .tx'), ar = p.querySelector('.ar .tx');
      return en && ar && lines(en) <= 2 && lines(ar) <= 2;
    });
    if (!ok) pairs.forEach(p => p.classList.remove('side'));
  }
  function sideBySide() {
    const q = (el, s) => Array.from(el.querySelectorAll(s));
    q(document, '#flow .para, #flow .note').forEach(c => trySide(q(c, '.pair')));
    q(document, '#flow .summary .srow').forEach(r => trySide(q(r, '.pair')));
    q(document, '#flow .list').forEach(list => {
      let group = [];
      Array.from(list.children).forEach(li => {
        if (!li.classList.contains('cont') && group.length) { trySide(group); group = []; }
        group.push(...q(li, '.pair'));
      });
      if (group.length) trySide(group);
    });
  }

  function run() {
    sideBySide();
    const blocks = Array.from(document.getElementById('flow').children);
    newPage();
    blocks.forEach(placeBlock);
    while (deferred.length) newPage();
    document.getElementById('flow').remove();
    // QA report
    const rep = [];
    document.querySelectorAll('.page.inner').forEach((p, i) => {
      const c = p.querySelector('.content');
      const kids = Array.from(c.children);
      const used = kids.length ? kids[kids.length - 1].getBoundingClientRect().bottom - c.getBoundingClientRect().top : 0;
      rep.push({ page: i + 1, fill: +(used / c.clientHeight).toFixed(2), overflow: c.scrollHeight > c.clientHeight + 1,
        lastIsHead: isHead(kids[kids.length - 1]) });
    });
    // horizontal overflow check
    const hx = [];
    document.querySelectorAll('.page.inner .content .tx, .page.inner .content .chip, .page.inner .content .sub').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 1) hx.push(el.textContent.slice(0, 50));
    });
    window.QA = { pages: rep, hscroll: hx };
    window.PAGINATED = true;
  }

  Promise.all([document.fonts.ready, ...Array.from(document.images).map(im => im.complete ? 0 : new Promise(r => { im.onload = im.onerror = r; }))])
    .then(() => setTimeout(run, 50));
})();
