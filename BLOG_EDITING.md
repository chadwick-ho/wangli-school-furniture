# 添加和修改 Blog 文章

1. 在 GitHub 打开 `content/blog`，参考现有文章新建一个英文小写文件名，例如 `choosing-school-desks.md`。
2. 文件开头的 JSON 注释提供标题、简述、分类、发布日期、图片和状态。正文使用 Markdown，二级标题用 `##`。图片放在 `assets/`，使用真实产品或工厂资料。
3. 分类只能选择 `tenders`（招投标）、`wholesale`（经销商批发）、`specifications`（材料与规格）。
4. 新文章默认网址为 `/blog/文章slug/`。既有三篇文章保留原网址，修改时请保留原 `path`。
5. `draft: true` 是草稿，不进入文章列表、RSS、sitemap 或部署页面；`draft: false` 才发布。删除源文件也会撤下由它生成的文章页。更改已发布网址前应处理旧链接。
6. 提交到 main 后，在 Actions 查看 “Build and deploy WangLi website”。只有部署步骤成功，网站才已更新。不要直接编辑生成的文章 HTML。

新文章开头示例（JSON 必须用英文双引号，日期包含时区）：

```json
{"slug":"choosing-school-desks","title":"كيف تختار الطاولات المدرسية لمشروعك؟","seo_title":"اختيار الطاولات المدرسية للمشاريع | WangLi","description":"دليل عملي لمقارنة المقاسات والخامات وتجهيز طلب التوريد.","category":"specifications","published":"2026-10-24T09:00:00+08:00","image":"/assets/factory-showroom-01.jpg","image_alt":"نماذج طاولات مدرسية في صالة عرض WangLi","draft":true}
```

实际文件中请将 JSON 放在 `<!-- blog {这里放上述 JSON 对象内部的完整字段} -->` 注释格式内，可直接复制现有 `.md` 文件的首段，修改字段。正文至少包含两个有实际内容的 `##` 小节，不要重复堆砌关键词。

本地验证：安装 `scripts/requirements.txt`，运行 `python scripts/build_blog.py`。它会更新文章、列表、首页推荐、RSS 和 sitemap，并检查阿语 RTL、H1 和站内链接。`_site/` 是生成目录，请勿手动维护或提交。

页面具备参与搜索的技术条件不等于已收录或获得排名。证书、测试和材料声明必须符合实际适用范围；未核实的参数、认证状态和项目案例请勿写成已确认事实。
