# 記事HTMLの保存場所

ここに記事のHTMLファイルを保存します。記事を追加したら `python scripts/build_article_index.py` を実行してください。
記事一覧はHTML内の `title`、`meta name="article-date"`、`meta name="article-category"`、`meta name="description"` から自動生成されます。

`templates/article-template.html` をコピーして新しい記事を作ると簡単です。記事ファイル名は英数字とハイフンを推奨します。
