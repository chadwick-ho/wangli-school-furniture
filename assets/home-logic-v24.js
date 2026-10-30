/* User-controlled photo rail and local inquiry preparation. No network or storage. */
(() => {
  const gallery = document.querySelector('#home-gallery');
  gallery?.querySelectorAll('[data-gallery-step]').forEach(button => {
    button.addEventListener('click', () => {
      const sign = button.dataset.galleryStep === 'next' ? -1 : 1;
      gallery.querySelectorAll('.wl-v24-gallery-track').forEach(track => {
        track.scrollBy({ left: sign * Math.min(420, track.clientWidth * 0.82), behavior:
          matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
      });
    });
  });
  const builder = document.querySelector('.wl-v24-brief-builder');
  if (!builder) return;
  const product = document.getElementById('brief-product');
  const output = document.getElementById('brief-output');
  const text = document.getElementById('brief-text');
  const message = document.getElementById('brief-message');
  const copyStatus = document.getElementById('brief-copy-status');
  const value = key => document.getElementById('brief-' + key).value.trim();
  document.getElementById('brief-generate').addEventListener('click', () => {
    if (!value('product')) {
      product.setAttribute('aria-invalid', 'true');
      message.textContent = builder.dataset.required;
      product.focus();
      return;
    }
    product.removeAttribute('aria-invalid');
    message.textContent = '';
    copyStatus.textContent = '';
    text.value = [
      'طلب أثاث مدرسي — WangLi',
      'صفة المشتري: ' + (value('role') || 'لم تحدد'),
      'المنتج أو الموديل: ' + value('product'),
      'الكميات: ' + (value('quantity') || 'تحتاج إلى تأكيد'),
      'وجهة التسليم: ' + (value('destination') || 'تحتاج إلى تأكيد'),
      'متطلبات إضافية: ' + (value('notes') || 'تستكمل عند المناقشة'),
      'يرجى مراجعة التوفر والمواصفات النهائية ونطاق العرض والمدة حسب هذا الطلب.'
    ].join('\n');
    output.hidden = false;
    text.focus({ preventScroll: true });
    if (matchMedia('(max-width: 800px)').matches) {
      output.scrollIntoView({ block: 'start', behavior:
        matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    }
  });
  product.addEventListener('input', () => {
    product.removeAttribute('aria-invalid');
    message.textContent = '';
  });
  document.getElementById('brief-copy').addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(text.value);
      copyStatus.textContent = builder.dataset.copied;
    } catch {
      text.focus();
      text.select();
      copyStatus.textContent = builder.dataset.copyFailed;
    }
  });
})();
