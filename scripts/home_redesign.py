"""Homepage v23: reference-informed composition, supplied WangLi evidence."""
import json
from html import escape as e
from bs4 import BeautifulSoup
import home_logic

def image(builder,name,alt,cls='',preview=None,eager=False,sizes='(max-width: 700px) 100vw, 50vw'):
    # Recorded dimensions avoid adding an image library to the Pages build.
    manifest=json.loads((builder.ROOT/'content/home-images.json').read_text(encoding='utf8'))
    w,h=manifest[name]['dimensions']
    responsive=''
    if preview:
        pw=manifest[preview]['dimensions'][0]
        responsive=f' srcset="/assets/{preview} {pw}w, /assets/{name} {w}w" sizes="{sizes}"'
    return f'<img class="{cls}" src="/assets/{name}" alt="{e(alt,quote=True)}" width="{w}" height="{h}" decoding="async" loading="'+('eager' if eager else 'lazy')+'"'+(' fetchpriority="high"' if eager else '')+responsive+'>'

def button(label,url,outline=False):return '<a class="wl-v23-button'+(' wl-v23-outline' if outline else '')+'" href="'+e(url,quote=True)+'">'+e(label)+'</a>'
def section_head(kicker,title,description='',link=None):
    return '<header class="wl-v23-section-head"><div><p class="wl-v23-kicker">'+e(kicker)+'</p><h2>'+e(title)+'</h2>'+('<p>'+e(description)+'</p>' if description else '')+'</div>'+('<a class="wl-v23-text-link" href="'+link[1]+'">'+e(link[0])+' <span aria-hidden="true">←</span></a>' if link else '')+'</header>'

def render(data,old,builder,cert_wall):
    d=data['hero'];slides=[]
    for i,s in enumerate(d['slides']):
        slides.append('<figure class="wl-v23-scene" id="scene-'+s['id']+'"'+(' hidden' if i else '')+'>'+image(builder,s['image'],s['alt'],preview=s['preview'],eager=i==0,sizes='100vw')+'<figcaption>'+e(s['caption'])+'</figcaption></figure>')
    tabs=''.join('<button type="button" aria-controls="scene-'+s['id']+'" aria-pressed="'+str(i==0).lower()+'" data-scene="'+s['id']+'"><span aria-hidden="true">0'+str(i+1)+'</span> '+e(s['label'])+'</button>' for i,s in enumerate(d['slides']))
    main='<section id="wangli-home-evidence" class="wl-v23-hero" aria-label="WangLi · الأثاث المدرسي">'+''.join(slides)+'<div class="wl-v23-hero-shade"></div><div class="wl-container wl-v23-hero-copy"><p class="wl-v23-kicker">'+e(d['eyebrow'])+'</p><h1>'+e(d['title'])+'</h1><p class="wl-v23-hero-description">'+e(d['description'])+'</p><div class="wl-v23-actions">'+button(d['primary_label'],d['primary_url'])+button(d['secondary_label'],d['secondary_url'],True)+'</div></div><div class="wl-container wl-v23-scene-nav" aria-label="اختر مشهدًا من WangLi">'+tabs+'</div><p class="wl-v23-sr-status" aria-live="polite"></p></section>'
    main+=home_logic.why(data['why'],builder,image)
    main+=home_logic.mechanisms(data['mechanisms'],data['products']['items'],builder,image,button)
    d=data['products'];cards=''.join('<a href="'+a['url']+'" class="wl-v23-category">'+'<div class="wl-v23-category-image">'+image(builder,a['image'],a['alt'])+'</div><div class="wl-v23-category-copy"><div><h3>'+e(a['title'])+'</h3><p>'+e(a['description'])+'</p></div><span aria-hidden="true">↗</span></div></a>' for a in d['items'])
    main+='<section id="home-products" class="wl-v23-section wl-v23-products"><div class="wl-container">'+section_head(d['eyebrow'],d['title'],d['description'],('كل المنتجات','/products/'))+'<div class="wl-v23-category-grid">'+cards+'</div></div></section>'
    d=data['catalog'];steps=''.join('<li><span>'+a['number']+'</span><div><h3>'+e(a['title'])+'</h3><p>'+e(a['text'])+'</p></div></li>' for a in d['steps'])
    main+='<section id="home-catalog" class="wl-v23-section wl-v23-catalog"><div class="wl-container wl-v23-catalog-grid"><div>'+section_head(d['eyebrow'],d['title'],d['description'])+'<div class="wl-v23-actions">'+button('تنزيل الكتالوج · PDF',d['pdf'])+button('المواصفات بالعربية · Excel',d['spreadsheet'],True)+'</div><a class="wl-v23-text-link" href="/school-furniture-catalog/">دليل الكتالوج بالعربية ←</a></div><ol>'+steps+'</ol></div></section>'
    main+=home_logic.gallery(data['gallery'],builder,image)
    certs=json.loads((builder.ROOT/'content/company.json').read_text(encoding='utf8'))['certificates']
    main+=cert_wall(old['certificates'],certs)
    main+=home_logic.faq(data['faq'])
    main+=home_logic.inquiry(data['contact'],button)
    return main

def integrate(doc,builder,old,cert_wall):
    data=json.loads((builder.ROOT/'content/home-layout.json').read_text(encoding='utf8'))
    doc.main.clear();doc.main.append(BeautifulSoup(render(data,old,builder,cert_wall),'html.parser'))
    classes=doc.body.get('class',[])
    if 'wl-home-v23' not in classes:classes.append('wl-home-v23')
    doc.body['class']=classes
    for script in doc.select('script[src="/assets/home-carousel.js"]'):script.decompose()
    if not doc.head.select_one('link[href="/assets/home-v23.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/home-v23.css'))
    if not doc.select_one('script[src="/assets/home-v23.js"]'):doc.body.append(doc.new_tag('script',src='/assets/home-v23.js',defer=''))
    if not doc.head.select_one('link[href="/assets/home-logic-v24.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/home-logic-v24.css'))
    if not doc.select_one('script[src="/assets/home-logic-v24.js"]'):doc.body.append(doc.new_tag('script',src='/assets/home-logic-v24.js',defer=''))
    request_button=doc.select_one('.wl-header-button')
    if request_button:request_button['href']='#home-request'
    logo=doc.select_one('.wl-brand img')
    if logo:
        logo['src']='/assets/home-v23-da46d4e6d3-wangli-official-logo.webp';logo['width']='3203';logo['height']='1280'
    for key,val in [('og:image',builder.DOMAIN+'/assets/'+data['hero']['slides'][0]['image']),('twitter:image',builder.DOMAIN+'/assets/'+data['hero']['slides'][0]['image'])]:
        tag=doc.find('meta',attrs={'property' if key.startswith('og:') else 'name':key})
        if tag:tag['content']=val
    # Existing SEO title, canonical and Organization/Website graph stay authoritative.
