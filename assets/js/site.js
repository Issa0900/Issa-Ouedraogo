(function(){
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Wrap wide tables (Markdown-rendered) in a horizontal scroll container —
  // must run before reveal targets are collected, since it changes .doc-content's direct children
  document.querySelectorAll('.doc-content table').forEach(function(table){
    if(table.parentElement.classList.contains('doc-wide-table')) return;
    var wrap = document.createElement('div');
    wrap.className = 'doc-wide-table';
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });

  // Generic scroll reveal — [data-reveal] blocks and direct children of .doc-content
  var targets = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'))
    .concat(Array.prototype.slice.call(document.querySelectorAll('.doc-content > *')));

  if('IntersectionObserver' in window && !reduced && targets.length){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function(t){ io.observe(t); });
  } else {
    targets.forEach(function(t){ t.classList.add('is-visible'); });
  }

  // Animated counters (homepage stats: [data-count])
  var counters = document.querySelectorAll('[data-count]');
  function animateCount(el){
    var target = parseInt(el.getAttribute('data-count'), 10);
    if(reduced){ el.textContent = target.toLocaleString('fr-CA'); return; }
    var duration = 1400, startTime = null;
    function step(ts){
      if(!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.floor(eased * target).toLocaleString('fr-CA');
      if(progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString('fr-CA');
    }
    requestAnimationFrame(step);
  }
  if(counters.length){
    if('IntersectionObserver' in window){
      var cio = new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
          if(entry.isIntersecting){ animateCount(entry.target); cio.unobserve(entry.target); }
        });
      }, { threshold: 0.5 });
      counters.forEach(function(c){ cio.observe(c); });
    } else {
      counters.forEach(animateCount);
    }
  }
})();
