"""Build the Arabic blog and a website-only Pages artifact from Markdown.

Editorial source: content/blog/*.md, with a leading JSON metadata comment.
Run `python scripts/build_blog.py` locally; Actions runs the same command.
Existing article URLs are preserved. Drafts are excluded from the output.
"""
from pathlib import Path
from urllib.parse import urljoin, urlsplit, unquote
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape
import json,re,shutil,argparse
from xml.etree.ElementTree import Element,SubElement,tostring
import markdown
from bs4 import BeautifulSoup
import company
import home

ROOT=Path(__file__).resolve().parents[1]
DOMAIN='https://wangliarabia.com'
CATEGORIES={
 'tenders':{'name':'المناقصات وتوريد المشاريع','intro':'مقالات لمراجعة جدول الكميات والمواصفات الفنية وتجهيز ملفات توريد الأثاث المدرسي.'},
 'wholesale':{'name':'الشراء بالجملة والتوزيع','intro':'أدلة للموزعين حول مقارنة عروض الأثاث المدرسي والعينات والتعبئة وتجهيز طلبات الشراء.'},
 'specifications':{'name':'الخامات والمواصفات','intro':'شروحات لقراءة أبعاد الطاولات والكراسي ومقارنة الخامات وتوثيق المواصفات المطلوبة.'}
}
LEGACY={'school-furniture-tender-checklist','school-furniture-wholesale-guide','school-desk-chair-specifications'}

def load_posts():
    posts=[];paths=set()
    for file in sorted((ROOT/'content/blog').glob('*.md')):
        raw=file.read_text(encoding='utf-8')
        match=re.match(r'\s*<!--\s*blog\s*(\{.*?\})\s*-->\s*',raw,re.S)
        if not match:raise ValueError('Missing blog JSON metadata: '+file.name)
        post=json.loads(match.group(1))
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',post['slug']),file.name
        assert post['category'] in CATEGORIES,file.name
        assert post['title'] and post['description'] and post['image_alt']
        post['path']=post.get('path','/blog/'+post['slug']+'/')
        assert post['path']=='/blog/'+post['slug']+'/' or post['slug'] in LEGACY and post['path']=='/'+post['slug']+'/'
        assert post['path'] not in paths,'Duplicate article URL';paths.add(post['path'])
        post['date']=datetime.fromisoformat(post['published'])
        assert post['date'].tzinfo is not None,'published requires timezone'
        post['image']='/assets/'+Path(post['image']).name
        assert (ROOT/post['image'].lstrip('/')).is_file(),'Missing article image'
        body=BeautifulSoup(markdown.markdown(raw[match.end():],extensions=['tables','sane_lists']),'html.parser')
        for h1 in list(body.find_all('h1')):h1.decompose()
        assert len(body.find_all('h2'))>=2,'An article needs meaningful sections'
        assert not body.find(['script','iframe','form','style']),'Unsupported active article content'
        for el in body.find_all(True):
            assert not any(k.lower().startswith('on') for k in el.attrs),'Inline event handler rejected'
        for a in body.find_all('a',href=True):
            assert urlsplit(a['href']).scheme in ['','https','http','mailto'],'Unsupported link scheme'
        post['body']=str(body);post['source']=file.name
        if post.get('draft',False):
            output=ROOT/post['path'].lstrip('/')/'index.html'
            # Only a file explicitly owned by this post can be removed.
            if output.is_file():output.unlink()
            continue
        posts.append(post)
    assert posts,'No published blog articles'
    return sorted(posts,key=lambda p:(p['published'],p['slug']),reverse=True)

def relative_source_doc():
    return BeautifulSoup((ROOT/'templates/blog-layout.html').read_text(encoding='utf-8'),'html.parser')

def category_nav(active='all'):
    items=[('all','جميع المقالات','/blog/')]+[(key,value['name'],'/blog/'+key+'/') for key,value in CATEGORIES.items()]
    return '<nav class="wl-blog-topics" aria-label="تصنيفات المدونة">'+''.join('<a'+(' aria-current="page"' if key==active else '')+' href="'+href+'">'+escape(name)+'</a>' for key,name,href in items)+'</nav>'

def card(post):
    cat=CATEGORIES[post['category']]['name']
    image_class='wl-blog-image'+(' wl-blog-image-photo' if post.get('image_kind')=='photo' else '')
    return '<article class="wl-blog-card"><a class="'+image_class+'" href="'+post['path']+'"><img src="'+post['image']+'" alt="'+escape(post['image_alt'],quote=True)+'" width="800" height="500" loading="lazy" decoding="async"></a><div class="wl-blog-card-body"><p class="wl-eyebrow">'+escape(cat)+' · <time datetime="'+post['published']+'">'+post['published'][:10]+'</time></p><h2><a href="'+post['path']+'">'+escape(post['title'])+'</a></h2><p>'+escape(post['description'])+'</p><a class="wl-blog-read" href="'+post['path']+'">اقرأ المقال <span aria-hidden="true">←</span></a></div></article>'

def page(path,title,description,main,post=None,category=None):
    doc=relative_source_doc();doc.title.string=title
    doc.main.clear();doc.main.append(BeautifulSoup(main,'html.parser'))
    for el in doc.head.select('meta[name="keywords"],meta[name="description"],meta[name="robots"],meta[property^="og:"],meta[name^="twitter:"],link[rel="canonical"],script[type="application/ld+json"]'):el.decompose()
    def meta(key,value,property=False):doc.head.append(doc.new_tag('meta',attrs={'property' if property else 'name':key,'content':value}))
    meta('description',description);meta('robots','noindex, follow' if category else 'index, follow, max-image-preview:large')
    if post:meta('wangli-blog-source',post['source'])
    url=DOMAIN+path;doc.head.append(doc.new_tag('link',rel='canonical',href=url))
    image=DOMAIN+(post['image'] if post else POSTS[0]['image'])
    for key,value in {'og:type':'article' if post else 'website','og:locale':'ar_AR','og:site_name':'WangLi','og:title':title,'og:description':description,'og:url':url,'og:image':image}.items():meta(key,value,True)
    for key,value in {'twitter:card':'summary_large_image','twitter:title':title,'twitter:description':description,'twitter:image':image}.items():meta(key,value)
    if not doc.head.select_one('link[href="/assets/blog.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/blog.css'))
    doc.head.append(doc.new_tag('link',rel='alternate',attrs={'type':'application/rss+xml','title':'مدونة WangLi','href':DOMAIN+'/feed.xml'}))
    crumbs=[{'@type':'ListItem','position':1,'name':'الرئيسية','item':DOMAIN+'/'}]
    if path!='/blog/':crumbs.append({'@type':'ListItem','position':2,'name':'المدونة','item':DOMAIN+'/blog/'})
    if post:crumbs.append({'@type':'ListItem','position':3,'name':CATEGORIES[post['category']]['name'],'item':DOMAIN+'/blog/'+post['category']+'/'})
    crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':post['title'] if post else CATEGORIES[category]['name'] if category else 'المدونة','item':url})
    graph=[{'@type':'Organization','@id':DOMAIN+'/#organization','name':'WangLi','url':DOMAIN+'/','sameAs':['https://www.wangliedu.com/','https://zjwangli.en.alibaba.com/']},{'@type':'WebSite','@id':DOMAIN+'/#website','url':DOMAIN+'/','name':'WangLi','inLanguage':'ar'}, {'@type':'WebPage','@id':url+'#webpage','url':url,'name':title,'description':description,'inLanguage':'ar','isPartOf':{'@id':DOMAIN+'/#website'}},{'@type':'BreadcrumbList','itemListElement':crumbs}]
    if post:graph.append({'@type':'BlogPosting','@id':url+'#article','headline':post['title'],'description':description,'datePublished':post['published'],'dateModified':post.get('modified',post['published']),'inLanguage':'ar','image':image,'author':{'@id':DOMAIN+'/#organization'},'publisher':{'@id':DOMAIN+'/#organization'},'mainEntityOfPage':{'@id':url+'#webpage'},'isPartOf':{'@id':DOMAIN+'/blog/#blog'},'articleSection':CATEGORIES[post['category']]['name']})
    else:
        items=[p for p in POSTS if not category or p['category']==category]
        graph.append({'@type':'CollectionPage' if category else 'Blog','@id':url+'#blog','url':url,'name':title,'inLanguage':'ar','blogPost':[{'@id':DOMAIN+p['path']+'#article'} for p in items]} if not category else {'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'url':DOMAIN+p['path'],'name':p['title']} for i,p in enumerate(items)]})
    script=doc.new_tag('script',type='application/ld+json');script.string=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('</','<\\/');doc.head.append(script)
    target=ROOT/path.lstrip('/')/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(str(doc),encoding='utf-8')

def render_blog():
    # Remove previously generated articles when their Markdown is removed or drafted.
    active={p['path'] for p in POSTS}
    for previous in ROOT.rglob('index.html'):
        if any(x in previous.relative_to(ROOT).parts for x in ['.git','_site','templates']):continue
        old=BeautifulSoup(previous.read_text(encoding='utf-8'),'html.parser')
        path='/'+previous.parent.relative_to(ROOT).as_posix().strip('/')+'/'
        if old.find('meta',attrs={'name':'wangli-blog-source'}) and path not in active:previous.unlink()
    title='مدونة الأثاث المدرسي للموزعين وشركات التوريد | WangLi'
    description='مقالات عربية عن شراء الأثاث المدرسي بالجملة، ومواصفات الطاولات والكراسي، وتجهيز عروض المناقصات وطلبات التوريد.'
    intro='<section class="wl-blog-hero"><div class="wl-container"><p class="wl-eyebrow">WANGLI · المدونة</p><h1>مدونة الأثاث المدرسي</h1><p class="wl-lead">معرفة عملية للموزعين وشركات توريد المشاريع: قارن المواصفات، وجهز طلبات الشراء، وراجع ملفات المناقصات.</p>'+category_nav()+'</div></section>'
    page('/blog/',title,description,intro+'<section class="wl-section"><div class="wl-container"><div class="wl-blog-grid">'+''.join(card(p) for p in POSTS)+'</div><p class="wl-blog-tools"><a href="/school-furniture-buying-guides/">قوالب الاستفسار وأدلة الشراء</a> · <a href="/feed.xml" lang="en" dir="ltr">RSS</a></p></div></section>')
    for cat,info in CATEGORIES.items():
        items=[p for p in POSTS if p['category']==cat]
        main='<section class="wl-blog-hero"><div class="wl-container"><p class="wl-eyebrow"><a href="/blog/">المدونة</a></p><h1>'+info['name']+'</h1><p class="wl-lead">'+info['intro']+'</p>'+category_nav(cat)+'</div></section><section class="wl-section"><div class="wl-container wl-blog-grid">'+''.join(card(p) for p in items)+'</div></section>'
        page('/blog/'+cat+'/',info['name']+' | مدونة WangLi',info['intro'],main,category=cat)
    for post in POSTS:
        main='<nav class="wl-breadcrumb wl-container" aria-label="مسار التنقل"><a href="/">الرئيسية</a> / <a href="/blog/">المدونة</a> / <a href="/blog/'+post['category']+'/">'+CATEGORIES[post['category']]['name']+'</a></nav><article class="wl-section wl-blog-article"><div class="wl-container wl-reading"><header><p class="wl-eyebrow">'+CATEGORIES[post['category']]['name']+'</p><h1>'+escape(post['title'])+'</h1><p class="wl-blog-byline">WangLi · <time datetime="'+post['published']+'">'+post['published'][:10]+'</time></p></header><img class="wl-blog-cover" src="'+post['image']+'" alt="'+escape(post['image_alt'],quote=True)+'" width="800" height="500" loading="eager" decoding="async" fetchpriority="high"><div class="wl-blog-prose">'+post['body']+'</div><aside class="wl-blog-related"><h2>مقالات ذات صلة</h2><ul>'+''.join('<li><a href="'+p['path']+'">'+escape(p['title'])+'</a></li>' for p in POSTS if p['slug']!=post['slug'])+'</ul><a href="/blog/">جميع مقالات المدونة</a></aside></div></article>'
        if post.get('image_caption'):
            parsed=BeautifulSoup(main,'html.parser');cover=parsed.select_one('.wl-blog-cover')
            figure=parsed.new_tag('figure',attrs={'class':'wl-blog-cover-figure'});cover.wrap(figure)
            caption=parsed.new_tag('figcaption');caption.string=post['image_caption'];figure.append(caption);main=str(parsed)
        page(post['path'],post.get('seo_title',post['title']+' | WangLi'),post['description'],main,post=post)

def update_site():
    # Selected reviewed pages can enter search. Detailed product pages retain
    # their previous noindex status while specification questions remain open.
    content_routes={'/','/products/','/about-wangli/','/factory/','/packing-and-shipping/','/certificates/','/school-furniture-wholesale/','/school-furniture-tender-supply/','/school-furniture-solutions/','/school-furniture-catalog/','/blog/'}|{p['path'] for p in POSTS}
    categories={'classroom','lecture','student-chairs','cafeteria','dormitory','storage','teacher-desks','office','laboratory','whiteboards','auditorium','kindergarten'}
    content_routes|={'/products/'+c+'/' for c in categories}
    indexed=[]
    for file in sorted(ROOT.rglob('index.html')):
        if any(x in file.relative_to(ROOT).parts for x in ['.git','_site','templates']):continue
        path='/'+file.parent.relative_to(ROOT).as_posix().strip('.')
        path=path.rstrip('/')+'/'
        doc=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser')
        for menu in doc.select('.wl-nav ul,.wl-mobile-nav ul'):
            links=[a for a in menu.find_all('a') if a.get_text(strip=True) in ['المدونة','Blog']]
            for a in links:a.parent.decompose()
            li=doc.new_tag('li',attrs={'class':'menu-item'});a=doc.new_tag('a',href='/blog/');a.string='المدونة';li.append(a);menu.append(li)
        robots=doc.find('meta',attrs={'name':'robots'})
        if not robots:robots=doc.new_tag('meta',attrs={'name':'robots'});doc.head.append(robots)
        robots['content']='index, follow, max-image-preview:large' if path in content_routes else 'noindex, follow'
        if path in content_routes:indexed.append(DOMAIN+path)
        if not doc.head.select_one('link[href="/assets/blog.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/blog.css'))
        if path=='/':
            home.integrate(doc,__import__(__name__))
            existing=doc.select_one('#wangli-latest-posts')
            if existing:existing.decompose()
            section=BeautifulSoup('<section id="wangli-latest-posts" class="wl-section wl-soft"><div class="wl-container"><p class="wl-eyebrow">من المدونة</p><h2>مقالات تساعدك قبل طلب التوريد</h2><div class="wl-blog-grid">'+''.join(card(p) for p in POSTS[:3])+'</div><p class="wl-blog-tools"><a href="/blog/">استعرض جميع المقالات ←</a></p></div></section>','html.parser')
            doc.main.append(section)
        company.integrate(doc,path)
        file.write_text(str(doc),encoding='utf-8')
    urlset=Element('urlset',xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    for url in sorted(indexed):SubElement(SubElement(urlset,'url'),'loc').text=url
    (ROOT/'sitemap.xml').write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n'+tostring(urlset,encoding='utf-8'))
    (ROOT/'robots.txt').write_text('User-agent: *\nAllow: /\nDisallow: /content/\nDisallow: /scripts/\nDisallow: /templates/\nSitemap: '+DOMAIN+'/sitemap.xml\n',encoding='utf-8')
    feed=Element('rss',version='2.0');channel=SubElement(feed,'channel')
    for k,v in [('title','مدونة WangLi للأثاث المدرسي'),('link',DOMAIN+'/blog/'),('description','مقالات للموزعين وشركات توريد المشاريع'),('language','ar')]:SubElement(channel,k).text=v
    for post in POSTS:
        item=SubElement(channel,'item')
        for k,v in [('title',post['title']),('link',DOMAIN+post['path']),('guid',DOMAIN+post['path']),('description',post['description']),('pubDate',format_datetime(post['date'].astimezone(timezone.utc))),('category',CATEGORIES[post['category']]['name'])]:SubElement(item,k).text=v
    (ROOT/'feed.xml').write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n'+tostring(feed,encoding='utf-8'))
    return indexed

def validate():
    count=0
    for file in ROOT.rglob('index.html'):
        if any(x in file.relative_to(ROOT).parts for x in ['.git','_site','templates']):continue
        doc=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser');assert doc.html.get('lang')=='ar' and doc.html.get('dir')=='rtl' and len(doc.find_all('h1'))==1,file
        assert doc.find('link',rel='canonical')['href'].startswith(DOMAIN+'/')
        assert not doc.find('form')
        for el,attr in [(e,'href') for e in doc.find_all(href=True)]+[(e,'src') for e in doc.find_all(src=True)]:
            value=el[attr];parsed=urlsplit(value)
            if parsed.scheme or parsed.netloc or value.startswith('#'):continue
            target=(ROOT/unquote(parsed.path).lstrip('/')) if parsed.path.startswith('/') else (file.parent/unquote(parsed.path))
            target=target.resolve()
            assert target.is_relative_to(ROOT.resolve()),(file,value)
            if target.is_dir():target=target/'index.html'
            assert target.is_file(),(file,value)
        count+=1
    assert len({p['path'] for p in POSTS})==len(POSTS)
    return count

def artifact():
    dest=(ROOT/'_site').resolve()
    assert dest.parent==ROOT.resolve() and dest.name=='_site'
    if dest.exists():shutil.rmtree(dest)
    dest.mkdir()
    allowed={'.html','.css','.jpg','.png','.pdf','.xlsx','.csv','.xml','.txt','.ico','.webp'}
    for file in ROOT.rglob('*'):
        if not file.is_file() or any(p in {'.git','.github','_site','scripts','templates','content','__pycache__'} for p in file.relative_to(ROOT).parts):continue
        if file.suffix.lower() not in allowed and file.name not in ['CNAME','.nojekyll']:continue
        target=dest/file.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,target)
    assert not list(dest.rglob('*.md')) and not list(dest.rglob('*.py')) and not list(dest.rglob('*.zip'))

if __name__=='__main__':
    import sys
    POSTS=load_posts();render_blog();company.render_company(sys.modules[__name__]);indexed=update_site();count=validate();artifact()
    print(json.dumps({'pages':count,'posts':len(POSTS),'indexable_urls':len(indexed),'artifact':'_site','passed':True}))
