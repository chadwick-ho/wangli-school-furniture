/* All buyer paths exist without JS; the script adds navigation and user control. */
(() => {
  'use strict';
  document.querySelectorAll('.wl-home-carousel').forEach(root => {
    const slides = [...root.querySelectorAll('.wl-carousel-slide')];
    const controls = root.querySelector('.wl-carousel-controls');
    if (slides.length < 2 || !controls || root.dataset.carouselReady) return;
    root.dataset.carouselReady = 'true'; root.classList.add('wl-carousel-enhanced'); root.tabIndex = 0;
    const reduced = matchMedia('(prefers-reduced-motion: reduce)');
    let index = 0, autoplay = !reduced.matches, timer;
    const topics = document.createElement('div'); topics.className = 'wl-carousel-topics';
    topics.setAttribute('role', 'group'); topics.setAttribute('aria-label', 'اختر موضوع الشريحة');
    const tools = document.createElement('div'); tools.className = 'wl-carousel-tools';
    const status = document.createElement('span'); status.className = 'wl-carousel-status'; status.dir = 'ltr';
    const live = document.createElement('p'); live.className = 'wl-carousel-announcement';
    live.setAttribute('aria-live', 'polite'); live.setAttribute('aria-atomic', 'true');
    const button = (label, text, action) => { const b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', label); b.textContent = text; b.addEventListener('click', action); return b; };
    const labelFor = s => s.dataset.label || s.querySelector('h2')?.textContent || '';
    const topicsButtons = slides.map((s,n) => {
      const b = button(labelFor(s), '', () => { stop(); show(n,true); }); b.setAttribute('aria-controls',s.id);
      const number = document.createElement('span'); number.textContent = String(n+1).padStart(2,'0'); number.setAttribute('aria-hidden','true');
      b.append(number,document.createTextNode(labelFor(s))); topics.append(b); return b;
    });
    const previous = button('الشريحة السابقة','→', () => { stop(); show(index-1,true); });
    const next = button('الشريحة التالية','←', () => { stop(); show(index+1,true); });
    const toggle = button('','', () => { autoplay = !autoplay; schedule(); }); toggle.className = 'wl-carousel-toggle';
    function show(n,announce=false) {
      index = (n+slides.length)%slides.length;
      slides.forEach((s,i) => { s.hidden = i!==index; topicsButtons[i].setAttribute('aria-pressed',String(i===index)); });
      status.textContent = `${index+1} / ${slides.length}`; root.dataset.activeSlide = slides[index].id;
      if (announce) live.textContent = `${index+1} / ${slides.length} — ${labelFor(slides[index])}`;
    }
    function schedule() {
      clearTimeout(timer); toggle.textContent = autoplay?'إيقاف التلقائي':'تشغيل التلقائي';
      toggle.setAttribute('aria-label',autoplay?'إيقاف العرض التلقائي':'تشغيل العرض التلقائي');
      if (autoplay && !document.hidden) timer=setTimeout(() => { show(index+1); schedule(); },8000);
    }
    function stop() { autoplay=false; schedule(); }
    tools.append(previous,status,next,toggle); controls.append(topics,tools,live); controls.hidden=false;
    root.addEventListener('mouseenter',stop);
    root.addEventListener('focusin',event => { if (event.target!==toggle) stop(); });
    root.addEventListener('keydown',event => {
      if (event.ctrlKey || event.metaKey || event.altKey || event.target.closest('a,input,textarea,select') || !['ArrowLeft','ArrowRight','Home','End'].includes(event.key)) return;
      event.preventDefault(); stop(); show(event.key==='Home'?0:event.key==='End'?slides.length-1:index+(event.key==='ArrowLeft'?1:-1),true);
    });
    let startX=null;
    root.querySelector('.wl-carousel-stage')?.addEventListener('pointerdown',event => { startX=event.target.closest('a,button')?null:event.clientX; });
    root.addEventListener('pointerup',event => { if (startX===null) return; const distance=event.clientX-startX; startX=null; if (Math.abs(distance)>65) {stop();show(index+(distance>0?1:-1),true);} });
    root.addEventListener('pointercancel',() => {startX=null;});
    document.addEventListener('visibilitychange',schedule);
    reduced.addEventListener('change',() => {if(reduced.matches)stop();});
    show(0); schedule();
  });
})();
