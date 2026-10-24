"""Render supplied factory photographs and clearly scoped company documents."""
import json
from html import escape as e
from bs4 import BeautifulSoup

def photo(p):
    return '<figure class="wl-factory-photo"><a href="/assets/'+p['file']+'" target="_blank" rel="noopener" aria-label="'+e(p['title']+' — افتح الصورة الكبيرة',quote=True)+'"><img src="/assets/'+p.get('preview',p['file'])+'" width="'+str(p.get('preview_width',p['width']))+'" height="'+str(p.get('preview_height',p['height']))+'" loading="lazy" decoding="async" alt="'+e(p['title'],quote=True)+'"></a><figcaption><h3>'+e(p['title'])+'</h3><p>'+e(p['caption'])+'</p></figcaption></figure>'

def document(c):
    images=''
    for i,f in enumerate(c['files']):
        label='الوثيقة الرئيسية' if i==0 else 'ملحق نطاق المنتجات '+str(i)
        images+='<figure><a href="/assets/'+f['file']+'" target="_blank" rel="noopener"><img src="/assets/'+f['preview']+'" width="750" height="1061" loading="lazy" decoding="async" alt="'+e(c['title']+' — '+label,quote=True)+'"><span>'+label+' · افتح الصورة الكاملة ↗</span></a></figure>'
    note=''
    if c['kind']=='management':note='تخص نظام الإدارة ضمن النطاق المدون. تتطلب متابعة دورية؛ اطلب التحقق من الحالة الحالية عند تجهيز ملف المشروع.'
    if c['slug'].startswith('udem'):note='عنوان الوثيقة: General Product Safety Directive — Attestation of Conformity. يقتصر النطاق على الموديلات المذكورة فيها.'
    if len(c['files'])>1:note='تقرأ الشهادة مع ملحقي نطاق المنتجات؛ لا تستخدم الملاحق منفصلة عن الوثيقة الرئيسية.'
    if c['kind']=='archive':note='وثيقة مؤرشفة — انتهت الفترة المدونة في 2026-07-30. ليست دليلًا على اعتماد حالي؛ تطلب نسخة محدثة عند الحاجة.'
    return '<article class="wl-doc-card" id="'+c['slug']+'"><div class="wl-doc-heading"><p class="wl-eyebrow">'+('أرشيف الوثائق' if c['kind']=='archive' else 'وثائق الشركة')+'</p><h3>'+c['title']+'</h3><p class="wl-doc-number" dir="ltr">'+e(c['number'])+'</p><dl><dt>الجهة المصدرة</dt><dd dir="ltr">'+e(c['issuer'])+'</dd><dt>الفترة المدونة في الوثيقة</dt><dd dir="ltr">'+c['issued']+' — '+c['expires']+'</dd><dt>النطاق</dt><dd>'+e(c['scope'])+'</dd></dl>'+('<p class="wl-doc-note">'+note+'</p>' if note else '')+'</div><div class="wl-doc-images">'+images+'</div></article>'

def section(title,content,cls=''):
    return '<section class="wl-section '+cls+'"><div class="wl-container"><h2>'+title+'</h2>'+content+'</div></section>'

def links():
    return '<p class="wl-company-links"><a href="/factory/">جولة في المصنع</a><a href="/packing-and-shipping/">التعبئة والتحميل</a><a href="/certificates/">الشهادات والوثائق</a><a href="/request-a-quote/">اطلب ملفًا لمشروعك</a></p>'

def render_company(builder):
    data=json.loads((builder.ROOT/'content/company.json').read_text(encoding='utf-8'))
    photos=data['photos'];certs=data['certificates']
    hero='<section class="wl-company-hero"><div class="wl-container wl-company-hero-grid"><div><p class="wl-eyebrow">WANGLI · من داخل المصنع</p><h1>مصنع الأثاث المدرسي: صور من الموقع</h1><p class="wl-lead">تعرف على موقع WangLi وورش تشغيل المعادن والمستودع وصالات عرض الأثاث المدرسي، قبل تجهيز طلب الشراء أو عرض توريد المشروع.</p>'+links()+'</div><img src="/assets/factory-gate.jpg" alt="واجهة مصنع WangLi ومدخل الموقع" width="1800" height="900" fetchpriority="high" decoding="async"></div></section>'
    main=hero+section('ورش الإنتاج والمستودع','<p class="wl-section-intro">صور من مناطق القطع واللحام وثني الأنابيب والثقب والتخزين. حدد الموديلات والكميات المطلوبة لطلب معلومات الإنتاج والتعبئة الخاصة بطلبك.</p><div class="wl-factory-grid">'+''.join(photo(p) for p in photos[1:6])+'</div>')
    if data.get('additional_factory_photos'):
        main+=section('من تجهيز المكونات إلى تخزين الكراتين','<p class="wl-section-intro">صور إضافية للمقاعد قبل التجميع والهياكل المعدنية والكراتين داخل المصنع.</p><div class="wl-factory-grid wl-photo-grid">'+''.join(photo(p) for p in data['additional_factory_photos'])+'</div>','wl-soft')
    main+=section('الاستقبال وصالات العرض','<p class="wl-section-intro">استعرض نماذج من الطاولات والكراسي والأسرّة والأثاث التعليمي في صالات عرض WangLi.</p><div class="wl-factory-grid">'+''.join(photo(p) for p in photos[6:])+'</div>','wl-soft')
    main+=section('جهز طلبك مع فريق WangLi','<p>للموزعين: أرسل فئات المنتجات والموديلات والكميات وبلد الوصول. ولشركات توريد المشاريع: أرفق جدول الكميات والمواصفات والوثائق المطلوبة للمراجعة.</p>'+links())
    builder.page('/factory/','مصنع الأثاث المدرسي WangLi | صور الإنتاج وصالات العرض','صور حقيقية من مصنع WangLi تشمل ورش تشغيل المعادن والمستودع وصالات العرض، للموزعين وشركات توريد الأثاث المدرسي في الأسواق العربية.',main)
    intro='<section class="wl-company-hero"><div class="wl-container"><p class="wl-eyebrow">WANGLI · ملف الشركة</p><h1>الشهادات والوثائق</h1><p class="wl-lead">استعرض وثائق نظم الإدارة وسلسلة الحيازة ووثائق المنتجات، مع أرقامها والفترات المدونة ونطاق كل وثيقة.</p><p>اسم الجهة الوارد في الوثائق: <bdi>Zhejiang Wangli Teaching Equipment Co., Ltd</bdi>.</p><p class="wl-section-intro">حدد بلد المشروع والموديل والبند المطلوب، ليطابق الفريق الوثيقة المناسبة مع متطلبات ملف التوريد.</p>'+links()+'</div></section>'
    main=intro+section('وثائق نظم الإدارة','<div class="wl-doc-grid">'+''.join(document(c) for c in certs if c['kind']=='management')+'</div>')
    main+=section('سلسلة الحيازة ووثائق المنتجات','<p class="wl-section-intro">يراجع نطاق كل وثيقة على حدة. بيانات FSC ترتبط بالمنتجات ومستندات الطلب المعنية، ووثائق الموديلات تقرأ مع أرقام الموديلات والملاحق المذكورة.</p><div class="wl-doc-grid">'+''.join(document(c) for c in certs if c['kind'] not in ['management','archive'])+'</div>','wl-soft')
    main+=section('أرشيف الوثائق','<div class="wl-doc-grid">'+''.join(document(c) for c in certs if c['kind']=='archive')+'</div>')
    main+=section('وثائق لمراجعة متطلبات المناقصة','<p>أرسل قائمة الشهادات والمعايير والموديلات المطلوبة مع جدول الكميات، واطلب نسخًا واضحة والتحقق من الحالة الحالية للوثائق قبل اعتماد ملف العرض.</p>'+links(),'wl-soft')
    builder.page('/certificates/','شهادات ووثائق WangLi للأثاث المدرسي | نطاق الوثائق وصورها','وثائق ISO 9001 وISO 14001 وISO 45001 وFSC ووثائق منتجات WangLi مع الصور الأصلية والأرقام ونطاق الوثيقة والفترة المدونة فيها.',main)
    shipping=data.get('shipping_photos',[])
    if shipping:
        intro='<section class="wl-company-hero"><div class="wl-container wl-company-hero-grid"><div><p class="wl-eyebrow">WANGLI · تجهيز طلبات التوريد</p><h1>تعبئة الأثاث المدرسي وتحميل الحاويات</h1><p class="wl-lead">استعرض صورًا من تجهيز المكونات وتغليف الهياكل ومناولة المنصات وتحميل الحاويات، مع مجموعة صور من ملف العراق.</p><p>للموزعين وشركات توريد المشاريع: أرسل الموديلات والكميات وبلد الوجهة والميناء المطلوب لمراجعة التعبئة وترتيب التحميل الخاص بطلبك.</p><nav class="wl-blog-topics" aria-label="أقسام صور التعبئة"><a href="#packaging">التعبئة والمنصات</a><a href="#loading">تحميل الحاويات</a><a href="#iraq">صور ملف العراق</a></nav></div><img src="/assets/packing-pallet-staging-preview.jpg" alt="منصات من هياكل الأثاث المغلفة في منطقة التجهيز" width="675" height="900" fetchpriority="high" decoding="async"></div></section>'
        main=intro
        groups=[('packaging','التعبئة وترتيب المنصات','صور للكراتين والمكونات المنفصلة والهياكل المغلفة أثناء التجهيز والمناولة.'),('loading','التحميل ومناولة الحاويات','صور من منطقة التحميل واستخدام الرافعات في مناولة المنصات والكراتين.'),('iraq','صور من ملف تجهيزات العراق','مجموعة من صور تجهيز الهياكل وتغليف المكونات وترتيب الحمولات في ملف العراق لدى WangLi.')]
        for group,title,description in groups:
            main+='<section id="'+group+'" class="wl-section'+(' wl-soft' if group=='loading' else '')+'"><div class="wl-container"><h2>'+title+'</h2><p class="wl-section-intro">'+description+'</p><div class="wl-factory-grid wl-photo-grid">'+''.join(photo(p) for p in shipping if p['group']==group)+'</div></div></section>'
        main+=section('ما المعلومات اللازمة لمراجعة التعبئة والتحميل؟','<p>حدد الموديل والكمية ومقاسات المكونات والوجهة ومتطلبات الاستلام. اطلب توضيح عدد القطع في الكرتون وأبعاده ووزنه وطريقة حماية الأجزاء وترتيب المنصات ضمن عرض السعر الخاص بطلبك.</p><p>إذا كنت تجهز ملف مناقصة، أرفق متطلبات ترقيم الكراتين والملصقات والتسليم للمراجعة قبل اعتماد الطلب.</p>'+links(),'wl-soft')
        builder.page('/packing-and-shipping/','تعبئة الأثاث المدرسي وتحميل الحاويات | صور WangLi','صور تعبئة الأثاث المدرسي وترتيب المنصات وتحميل الحاويات لدى WangLi، مع صور من ملف العراق ومعلومات تجهيز الطلب للموزعين وشركات توريد المشاريع.',main)
    routes=[('factory','factory-gate.jpg','مصنع WangLi'),('certificates','certificate-iso9001-preview.jpg','الشهادات والوثائق')]
    if shipping:routes.append(('packing-and-shipping','packing-pallet-staging-preview.jpg','التعبئة والتحميل'))
    for route,image,title in routes:
        file=builder.ROOT/route/'index.html';doc=BeautifulSoup(file.read_text(encoding='utf-8'),'html.parser')
        for meta in doc.select('meta[property="og:image"],meta[name="twitter:image"]'):meta['content']=builder.DOMAIN+'/assets/'+image
        script=doc.find('script',type='application/ld+json');schema=json.loads(script.string)
        schema['@graph']=[g for g in schema['@graph'] if g['@type'] not in ['Blog','ItemList']]
        for g in schema['@graph']:
            if g['@type']=='BreadcrumbList':g['itemListElement']=[{'@type':'ListItem','position':1,'name':'الرئيسية','item':builder.DOMAIN+'/'},{'@type':'ListItem','position':2,'name':title,'item':builder.DOMAIN+'/'+route+'/'}]
        script.string=json.dumps(schema,ensure_ascii=False).replace('</','<\\/')
        file.write_text(str(doc),encoding='utf-8')

def integrate(doc,path):
    if not doc.head.select_one('link[href="/assets/company.css"]'):doc.head.append(doc.new_tag('link',rel='stylesheet',href='/assets/company.css'))
    footer=doc.find('footer')
    if footer:
        old=footer.select_one('#wangli-company-footer')
        if old:old.decompose()
        footer.append(BeautifulSoup('<div id="wangli-company-footer" class="wl-container">'+links()+'</div>','html.parser'))
    if path in ['/','/about-wangli/','/school-furniture-tender-supply/','/school-furniture-wholesale/']:
        old=doc.select_one('#wangli-company-preview')
        if old:old.decompose()
        html='<section id="wangli-company-preview" class="wl-section wl-company-preview"><div class="wl-container"><p class="wl-eyebrow">تعرف على WangLi</p><h2>من المصنع إلى ملف التوريد</h2><p>جولة مصورة في المصنع وصالات العرض، ووثائق الشركة لمراجعة نطاقها ضمن متطلبات الشراء والتوريد.</p><div class="wl-company-strip">'+''.join('<a href="/factory/"><img src="/assets/'+f+'" alt="'+alt+'" width="1800" height="900" loading="lazy" decoding="async"></a>' for f,alt in [('factory-gate.jpg','مدخل مصنع WangLi'),('factory-welding.jpg','ورشة اللحام في مصنع WangLi'),('factory-showroom-01.jpg','نماذج الأثاث المدرسي في صالة عرض WangLi')])+'</div>'+links()+'</div></section>'
        doc.main.append(BeautifulSoup(html,'html.parser'))
