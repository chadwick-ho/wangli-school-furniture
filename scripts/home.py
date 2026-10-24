"""Evidence-led Arabic homepage hero; copy and supplied photos are editable data."""
import json
from html import escape as e
from bs4 import BeautifulSoup

def hero(data):
    proof=''.join('<div class="wl-home-proof-item"><figure class="wp-block-image size-full"><img src="/assets/'+p['image']+'" alt="'+e(p['alt'],quote=True)+'" width="64" height="76" loading="eager" decoding="async"></figure><p><a href="'+p['url']+'">'+e(p['title'])+' <span aria-hidden="true">←</span></a></p></div>' for p in data['proof'])
    return '<section id="wangli-home-evidence" class="wl-home-hero"><div class="wl-container wl-home-grid"><div class="wl-home-copy"><p class="wl-eyebrow">'+e(data['kicker'])+'</p><h1 class="wp-block-heading">'+e(data['title'])+'</h1><p class="wl-home-subtitle">'+e(data['subtitle'])+'</p><p class="wl-home-description">'+e(data['description'])+'</p><div class="wp-block-buttons wl-home-actions"><div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/request-a-quote/">'+e(data['primary_cta'])+'</a></div><div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/products/">'+e(data['secondary_cta'])+'</a></div></div><p class="wl-home-buyers"><a href="/school-furniture-wholesale/">'+e(data['distributor_label'])+'</a><span aria-hidden="true"> · </span><a href="/school-furniture-tender-supply/">'+e(data['tender_label'])+'</a></p></div><div class="wl-home-proof">'+proof+'</div><div class="wl-home-media"><figure class="wp-block-image size-full"><a href="/factory/"><img src="/assets/'+data['factory_image']+'" alt="'+e(data['factory_alt'],quote=True)+'" width="1800" height="900" loading="eager" decoding="async" fetchpriority="high"></a></figure><p><a href="/factory/">'+e(data['factory_caption'])+' <span aria-hidden="true">←</span></a></p></div></div></section>'

def integrate(doc,builder):
    data=json.loads((builder.ROOT/'content/home.json').read_text(encoding='utf-8'))
    old=doc.select_one('#wangli-home-evidence') or doc.select_one('main .wl-hero')
    assert old,'Homepage hero to replace was not found'
    old.replace_with(BeautifulSoup(hero(data),'html.parser'))
    doc.title.string=data['seo_title']
    for key,val in [('description',data['seo_description']),('og:title',data['seo_title']),('og:description',data['seo_description']),('twitter:title',data['seo_title']),('twitter:description',data['seo_description']),('og:image',builder.DOMAIN+'/assets/'+data['factory_image']),('twitter:image',builder.DOMAIN+'/assets/'+data['factory_image'])]:
        tag=doc.find('meta',attrs={'property' if key.startswith('og:') else 'name':key})
        if tag:tag['content']=val
    if not doc.head.select_one('link[href="/assets/home.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/home.css'))
    for tag in doc.find_all('script',type='application/ld+json'):
        schema=json.loads(tag.string)
        def update(node):
            if isinstance(node,dict):
                if node.get('@type')=='WebPage':node.update(name=data['seo_title'],description=data['seo_description'])
                for val in node.values():update(val)
            elif isinstance(node,list):
                for val in node:update(val)
        update(schema);tag.string=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
