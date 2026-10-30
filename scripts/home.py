"""Buyer-question carousel and catalog paths from editable content files."""
import json
from copy import deepcopy
from html import escape as e
from bs4 import BeautifulSoup

def hero(data):
    slides=[]
    for n,s in enumerate(data['slides']):
        priority=' loading="eager" fetchpriority="high"' if n==0 else ' loading="lazy"'
        default=(901,888) if s['kind']=='product' else (1800,900)
        w,h=s.get('width',default[0]),s.get('height',default[1])
        responsive=f''' srcset="/assets/{s['preview']} 960w, /assets/{s['image']} {w}w" sizes="(max-width: 800px) 100vw, 59vw"''' if s.get('preview') else ''
        slides.append(f'''<div id="home-slide-{s['id']}" class="wl-carousel-slide wl-slide-{s['kind']}" role="group" aria-label="{n+1} / {len(data['slides'])}" data-label="{e(s['label'],quote=True)}"><figure class="wl-slide-media"><img src="/assets/{s['image']}" alt="{e(s['alt'],quote=True)}" width="{w}" height="{h}" decoding="async"{responsive}{priority}><figcaption>{e(s['caption'])}</figcaption></figure><div class="wl-container"><div class="wl-slide-copy"><p class="wl-slide-audience">{e(s['audience'])}</p><h2>{e(s['title'])}</h2><p class="wl-slide-description">{e(s['description'])}</p><div class="wp-block-buttons wl-home-actions"><div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="{s['primary_url']}">{e(s['primary_label'])}</a></div><div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="{s['secondary_url']}">{e(s['secondary_label'])}</a></div></div></div></div></div>''')
    proof=''.join(f'''<div class="wl-home-proof-item"><figure class="wp-block-image size-full"><img src="/assets/{p['image']}" alt="{e(p['alt'],quote=True)}" width="64" height="76" loading="lazy" decoding="async"></figure><p><a href="{p['url']}">{e(p['title'])} <span aria-hidden="true">←</span></a></p></div>''' for p in data['proof'])
    return f'''<section id="wangli-home-evidence" class="wl-home-hero wl-home-carousel" aria-label="حلول شراء الأثاث المدرسي" aria-roledescription="عارض شرائح"><header class="wl-container wl-home-intro"><p class="wl-eyebrow">{e(data['kicker'])}</p><h1>{e(data['title'])}</h1></header><div class="wl-carousel-stage">{''.join(slides)}</div><div class="wl-container wl-carousel-controls" hidden></div><div class="wl-container wl-home-proof">{proof}</div></section>'''

def catalog_paths(data):
    cards=[]
    for p in data['paths']:
        cards.append(f'''<article id="{p['id']}" class="wl-catalog-task"><p class="wl-eyebrow">{p['number']}</p><h3>{e(p['title'])}</h3><p>{e(p['description'])}</p><a class="wl-catalog-main" href="{p['primary_url']}">{e(p['primary_label'])} ←</a><a href="{p['secondary_url']}">{e(p['secondary_label'])}</a></article>''')
    return f'''<section id="wangli-catalog-buyers" class="wl-section wl-soft"><div class="wl-container"><h2>{e(data['title'])}</h2><p class="wl-catalog-intro">{e(data['description'])}</p><div class="wl-catalog-tasks">{''.join(cards)}</div></div></section>'''

def integrate_catalog(doc,builder):
    data=json.loads((builder.ROOT/'content/catalog-buyers.json').read_text(encoding='utf-8'))
    old=doc.select_one('#wangli-catalog-buyers')
    if old:old.decompose()
    heading=doc.main.find('h1');assert heading
    section=heading.find_parent(class_='wl-section') or doc.main.select_one('.wl-section');assert section
    section.insert_after(BeautifulSoup(catalog_paths(data),'html.parser'))
    if not doc.head.select_one('link[href="/assets/home.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/home.css'))

def integrate(doc,builder):
    data=json.loads((builder.ROOT/'content/home.json').read_text(encoding='utf-8'))
    if (builder.ROOT/'content/home-layout.json').exists():
        import home_redesign
        home_redesign.integrate(doc,builder,data,certificate_wall)
        return
    old=doc.select_one('#wangli-home-evidence') or doc.select_one('main .wl-hero');assert old
    old.replace_with(BeautifulSoup(hero(data),'html.parser'))
    old_certificates=doc.select_one('#wangli-home-certificates')
    if old_certificates:old_certificates.decompose()
    certificates=json.loads((builder.ROOT/'content/company.json').read_text(encoding='utf-8'))['certificates']
    doc.select_one('#wangli-home-evidence').insert_after(BeautifulSoup(certificate_wall(data['certificates'],certificates),'html.parser'))
    # Reuse actual products from the maintained product page; rebuild idempotently.
    old_products=doc.select_one('#wangli-home-selected-products')
    if old_products: old_products.decompose()
    product_doc=BeautifulSoup((builder.ROOT/'products/index.html').read_text(encoding='utf-8'),'html.parser')
    product_grid=product_doc.select_one('main .wl-products')
    category_grid=doc.select_one('main .wl-catalog-grid')
    assert product_grid and category_grid
    grid=deepcopy(product_grid)
    for image in grid.select('img[src]'):
        image['src']=image['src'].replace('../assets/','/assets/')
    for link in grid.select('a[href]'):
        link['href']='/products/'+link['href']
    section=BeautifulSoup('<section id="wangli-home-selected-products" class="wl-section"><div class="wl-container"><h2>منتجات مختارة من مجموعة WangLi</h2></div></section>','html.parser')
    section.select_one('.wl-container').append(grid)
    category_grid.find_parent(class_='wl-section').insert_after(section)
    doc.title.string=data['seo_title']
    for key,val in [('description',data['seo_description']),('og:title',data['seo_title']),('og:description',data['seo_description']),('twitter:title',data['seo_title']),('twitter:description',data['seo_description']),('og:image',builder.DOMAIN+'/assets/'+data['slides'][0]['image']),('twitter:image',builder.DOMAIN+'/assets/'+data['slides'][0]['image'])]:
        tag=doc.find('meta',attrs={'property' if key.startswith('og:') else 'name':key})
        if tag:tag['content']=val
    if not doc.head.select_one('link[href="/assets/home.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/home.css'))
    if not doc.select_one('script[src="/assets/home-carousel.js"]'):doc.body.append(doc.new_tag('script',src='/assets/home-carousel.js',defer=''))
    for tag in doc.find_all('script',type='application/ld+json'):
        schema=json.loads(tag.string)
        def update(node):
            if isinstance(node,dict):
                if node.get('@type')=='WebPage':node.update(name=data['seo_title'],description=data['seo_description'])
                for val in node.values():update(val)
            elif isinstance(node,list):
                for val in node:update(val)
        update(schema);tag.string=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')

def certificate_wall(copy,certificates):
    """Reuse the certificate page's document records and unaltered originals."""
    cards=[];archives=[]
    for c in certificates:
        f=c['files'][0]
        title=copy['labels'][c['slug']]
        image=f'''<a class="wl-cert-image" href="/assets/{f['file']}" target="_blank" rel="noopener" aria-label="{e(title+' — افتح الصورة الأصلية',quote=True)}"><img src="/assets/{f['preview']}" alt="{e(c['title'],quote=True)}" width="750" height="1061" loading="lazy" decoding="async"><span>{e(copy['open_original'])} ↗</span></a>'''
        if c['kind']=='archive':
            archives.append(f'''<article class="wl-cert-archive">{image}<div><p class="wl-cert-archive-label">{e(copy['archive_label'])}</p><h3><a href="/certificates/#{c['slug']}">{e(title)}</a></h3><p>{e(copy['archive_note'])} <time datetime="{c['expires']}" dir="ltr">{c['expires']}</time></p></div><a class="wl-cert-archive-link" href="/certificates/#{c['slug']}">{e(copy['details'])} ←</a></article>''')
            continue
        annexes=''.join(f'''<a href="/assets/{a['file']}" target="_blank" rel="noopener">ملحق {i} ↗</a>''' for i,a in enumerate(c['files'][1:],1))
        cards.append(f'''<article class="wl-cert-card">{image}<div class="wl-cert-copy"><p class="wl-cert-type">{e(copy['types'][c['kind']])}</p><h3><a href="/certificates/#{c['slug']}">{e(title)}</a></h3><p class="wl-cert-expiry">{e(copy['document_until'])} <time datetime="{c['expires']}" dir="ltr">{c['expires']}</time></p><div class="wl-cert-links"><a href="/certificates/#{c['slug']}">{e(copy['details'])} ←</a>{annexes}</div></div></article>''')
    return f'''<section id="wangli-home-certificates" class="wl-certificates" aria-labelledby="wl-certificates-title"><div class="wl-container"><header class="wl-cert-header"><div><p class="wl-eyebrow">{e(copy['eyebrow'])}</p><h2 id="wl-certificates-title">{e(copy['title'])}</h2><p>{e(copy['intro'])}</p></div><a class="wl-cert-all" href="/certificates/">{e(copy['all_label'])} ←<span>{e(copy['count_label'])}</span></a></header><div class="wl-cert-grid">{''.join(cards)}</div><p class="wl-cert-scope">{e(copy['scope_note'])}</p>{''.join(archives)}</div></section>'''
