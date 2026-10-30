"""Benefit -> evidence -> mechanism -> objection -> action homepage modules."""
from html import escape as e

def why(data,builder,image):
    rows=[]
    for a in data['items']:
        s=a['evidence'];body=''
        if s['kind']=='product':
            body='<div class="wl-v24-product-proof">'+image(builder,s['image'],s['alt'])+'<dl>'+''.join('<div><dt>'+e(f['label'])+'</dt><dd><bdi dir="ltr">'+e(f['value'])+'</bdi></dd></div>' for f in s['facts'])+'</dl></div>'
        elif s['kind']=='documents':
            body='<div class="wl-v24-file-list">'+''.join('<a href="'+f['url']+'"><span class="wl-v24-file-type">'+f['format']+'</span><div><strong>'+e(f['title'])+'</strong><span>'+e(f['description'])+'</span></div><span aria-hidden="true">↗</span></a>' for f in s['files'])+'</div>'
        else:
            body='<div class="wl-v24-proof-photos">'+''.join('<figure>'+image(builder,f['image'],f['alt'])+'<figcaption>'+e(f['caption'])+'</figcaption></figure>' for f in s['photos'])+'</div>'
        benefit='<div class="wl-v24-reason"><p class="wl-v24-number">'+a['number']+'</p><h3 id="why-'+a['id']+'">'+e(a['title'])+'</h3><p>'+e(a['description'])+'</p><a href="'+a['action_url']+'">'+e(a['action_label'])+' <span aria-hidden="true">←</span></a></div>'
        evidence='<aside class="wl-v24-evidence" aria-label="'+e(s['eyebrow'],quote=True)+'"><p class="wl-v24-evidence-label">'+e(s['eyebrow'])+'</p><h4>'+e(s['title'])+'</h4>'+body+'<p class="wl-v24-evidence-note">'+e(s['note'])+'</p><a href="'+s['url']+'">'+e(s['label'])+' <span aria-hidden="true">←</span></a></aside>'
        rows.append('<article class="wl-v24-reason-pair" aria-labelledby="why-'+a['id']+'">'+benefit+evidence+'</article>')
    return '<section id="home-why" class="wl-v24-why"><div class="wl-container"><header class="wl-v24-why-head"><p class="wl-v23-kicker">'+e(data['eyebrow'])+'</p><h2>'+e(data['title'])+'</h2><p>'+e(data['description'])+'</p></header><div class="wl-v24-reason-grid">'+''.join(rows)+'</div></div></section>'

def mechanisms(data,products,builder,image,button):
    rows=[]
    for i,a in enumerate(data['items']):
        if a['visual_kind']=='range':
            visual='<div class="wl-v24-range-stage">'+''.join('<figure>'+image(builder,p['image'],p['alt'])+'<figcaption>'+e(p['title'])+'</figcaption></figure>' for p in products[:3])+'</div>'
        elif a['visual_kind']=='project':
            visual='<div class="wl-v24-project-stage"><div class="wl-v24-sheet"><p class="wl-v24-sheet-caption">مثال توضيحي لتنظيم المراجعة</p><h4>من بند المشروع إلى التكوين المقترح</h4><div class="wl-v24-sheet-row"><span>مرجع المنتج</span><bdi>ZYTJ_02</bdi></div><div class="wl-v24-sheet-row"><span>أبعاد الطاولة المتاحة</span><bdi dir="ltr">620 × 475 × 760 مم</bdi></div><div class="wl-v24-sheet-row"><span>متطلبات المشروع</span><strong>تحدد في الطلب</strong></div><div class="wl-v24-sheet-row"><span>المطابقة والوثائق</span><strong>بانتظار المراجعة</strong></div><p class="wl-v24-sheet-note">المواصفات المتاحة بداية للمقارنة؛ ليست اعتمادًا من جهة المشروع.</p></div><a href="/assets/wangli-tender-technical-response-ar.csv" class="wl-v24-sheet-tag">CSV · قالب يمكنك تنزيله ↗</a></div>'
        else:
            visual='<div class="wl-v24-supply-stage"><div class="wl-v24-supply-photos">'+image(builder,'home-v23-factory-visit-welding-01-preview.webp','ورش الإنتاج وتجهيز الهياكل في WangLi')+image(builder,'home-v23-packing-pallet-staging-preview.webp','هياكل مغلفة على منصات في منطقة التجهيز')+'</div><div class="wl-v24-supply-path"><span>الموديل والكميات</span><span aria-hidden="true">←</span><span>التعبئة</span><span aria-hidden="true">←</span><span>وجهة الطلب</span></div><p>صور من الموقع؛ ترتيبات الشحنة تؤكد حسب الطلب.</p></div>'
        copy='<div class="wl-v24-mechanism-copy"><p class="wl-v23-kicker">0'+str(i+1)+' · '+e(a['visual_label'])+'</p><h3>'+e(a['title'])+'</h3><p>'+e(a['description'])+'</p><ul>'+''.join('<li>'+e(s)+'</li>' for s in a['points'])+'</ul>'+button(a['action_label'],a['action_url'],True)+'</div>'
        rows.append('<article class="wl-v24-mechanism '+('wl-v24-reverse' if i%2 else '')+'" id="how-'+a['id']+'"><div class="wl-v24-mechanism-visual">'+visual+'</div>'+copy+'</article>')
    return '<section id="home-how" class="wl-v24-how"><div class="wl-container"><header class="wl-v24-how-head"><p class="wl-v23-kicker">'+e(data['eyebrow'])+'</p><h2>'+e(data['title'])+'</h2></header>'+''.join(rows)+'</div></section>'

def gallery(data,builder,image):
    cards=[]
    for a in data['items']:
        cards.append('<a href="'+a['url']+'" class="wl-v24-gallery-card">'+image(builder,a['image'],a['alt'])+'<div><p>'+e(a['caption'])+'</p><h3>'+e(a['title'])+'</h3><span aria-hidden="true">↗</span></div></a>')
    rows=''.join('<div class="wl-v24-gallery-track" tabindex="0" role="region" aria-label="مشاهد من WangLi، الصف '+str(i+1)+'">'+''.join(cards[i*4:(i+1)*4])+'</div>' for i in range(2))
    return '<section id="home-gallery" class="wl-v24-gallery"><div class="wl-container"><header><div><p class="wl-v23-kicker">'+e(data['eyebrow'])+'</p><h2>'+e(data['title'])+'</h2><p>'+e(data['description'])+'</p></div><div class="wl-v24-gallery-controls"><button type="button" data-gallery-step="previous" aria-label="المشاهد السابقة">→</button><button type="button" data-gallery-step="next" aria-label="المشاهد التالية">←</button></div></header></div><div class="wl-v24-gallery-window">'+rows+'</div></section>'

def faq(data):
    return '<section id="home-faq" class="wl-v24-faq"><div class="wl-container"><header><p class="wl-v23-kicker">'+e(data['eyebrow'])+'</p><h2>'+e(data['title'])+'</h2></header><div>'+''.join('<details><summary>'+e(a['question'])+'</summary><p>'+e(a['answer'])+'</p></details>' for a in data['items'])+'</div></div></section>'

def inquiry(data,button):
    d=data['brief']
    def field(key,tag='input'):
        label='<label for="brief-'+key+'">'+e(d[key+'_label'])+'</label>'
        attrs=' id="brief-'+key+'" placeholder="'+e(d[key+'_placeholder'],quote=True)+'" maxlength="'+('1500' if key=='notes' else '250')+'"'
        return '<div class="wl-v24-field'+(' wl-v24-field-wide' if key in ['product','notes'] else '')+'">'+label+('<textarea'+attrs+' rows="3"></textarea>' if tag=='textarea' else '<input'+attrs+' type="text">')+'</div>'
    options=''.join('<option value="'+('' if i==0 else e(o,quote=True))+'">'+e(o)+'</option>' for i,o in enumerate(d['role_options']))
    fields='<fieldset class="wl-v24-brief-fields"><legend>'+e('المعلومات المتاحة عن طلبك')+'</legend><div class="wl-v24-field wl-v24-field-wide"><label for="brief-role">'+e(d['role_label'])+'</label><select id="brief-role">'+options+'</select></div>'+field('product')+field('quantity')+field('destination')+field('notes','textarea')+'</fieldset>'
    widget='<div class="wl-v24-brief-builder" data-required="'+e(d['required_message'],quote=True)+'" data-copied="'+e(d['copied_message'],quote=True)+'" data-copy-failed="'+e(d['copy_failed_message'],quote=True)+'">'+fields+'<button type="button" id="brief-generate" class="wl-v23-button">'+e(d['generate_label'])+'</button><p id="brief-message" role="status" aria-live="polite"></p></div>'
    output='<div id="brief-output" class="wl-v24-brief-output" hidden><label for="brief-text">'+e(d['output_label'])+'</label><textarea id="brief-text" rows="10" readonly></textarea><button type="button" id="brief-copy" class="wl-v23-button wl-v23-outline">'+e(d['copy_label'])+'</button><p id="brief-copy-status" role="status" aria-live="polite"></p></div>'
    copy='<div class="wl-v24-brief-copy"><header class="wl-v24-brief-intro"><p class="wl-v23-kicker">'+e(data['eyebrow'])+'</p><h2>'+e(data['title'])+'</h2><p>'+e(data['description'])+'</p></header>'+output+'<div class="wl-v24-channels"><p>'+e(d['channel_note'])+'</p><div class="wl-v23-actions">'+button(data['primary_label'],data['primary_url'])+button(data['secondary_label'],data['secondary_url'],True)+'</div></div></div>'
    return '<section id="home-request" class="wl-v24-inquiry"><div class="wl-container">'+copy+widget+'</div></section>'
