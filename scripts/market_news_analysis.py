import json
import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

from google import genai

# Gemini APIの設定
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=api_key)

# 日本時間
JST = timezone(timedelta(hours=9))


def fetch_google_news(query, max_items=15):
    """GoogleニュースのRSSからニュースを取得する。"""

    encoded_query = urllib.parse.quote(query)
    url = (
        "https://news.google.com/rss/search?"
        f"q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    )

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    news_items = []

    for item in root.findall(".//item")[:max_items]:
        title = item.findtext("title", default="")
        description = item.findtext("description", default="")
        link = item.findtext("link", default="")
        pub_date = item.findtext("pubDate", default="")

        news_items.append({
            "title": title,
            "description": description,
            "link": link,
            "published": pub_date
        })

    return news_items


def analyze_market_news(news_items):
    """ニュースから市場変動の主要因を3つ抽出する。"""

    news_text = json.dumps(
        news_items,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
あなたは米国株市場を分析するアナリストです。

以下のニュース情報を分析し、前日の米国ハイテク株市場の
値動きに関連する主要な材料を3つ抽出してください。

【重要なルール】
- ニュースに書かれていない事実を作らない。
- ニュースだけでは因果関係を確認できない場合は、断定しない。
- 市場全体の動きと個別企業のニュースを区別する。
- 同じ内容のニュースを重複して数えない。
- ニュースが十分でない場合は、無理に3つの要因を作らない。
- ニュースの見出しや概要は、信頼できる情報とは限らないため、
  確認できない内容は「可能性」「示唆」などの表現を使う。
- titleは日本語18～22文字。
- detailは日本語90～110文字。
- source_titleには根拠に使ったニュースの見出しを入れる。
- source_urlには根拠に使ったニュースのURLを入れる。
- 3つの要因を十分に裏付けられない場合は、
  driversを確認できた件数だけにする。

【JSON形式】
{{
  "report_date": "YYYY-MM-DD",
  "drivers": [
    {{
      "title": "要因のタイトル",
      "detail": "要因の説明",
      "source_title": "根拠となるニュース見出し",
      "source_url": "根拠となるニュースURL"
    }}
  ]
}}

【分析対象のニュース】
{news_text}
"""

    # モデル名は環境変数で変更できるようにする
    model = os.environ.get(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={"response_mime_type": "application/json"}
    )

    result = json.loads(response.text)

    # 日付は日本時間で記録
    result["report_date"] = datetime.now(JST).strftime("%Y-%m-%d")

    return result


def main():
    # 米国株・ハイテク市場に関するニュースを検索
    queries = [
        "US stock market Nasdaq technology stocks",
        "US semiconductor stocks Nvidia AI",
        "US megacap technology earnings"
    ]

    all_news = []

    for query in queries:
        try:
            items = fetch_google_news(query, max_items=15)
            all_news.extend(items)
            print(f"取得成功: {query} ({len(items)}件)")
        except Exception as exc:
            print(f"ニュース取得失敗: {query}: {exc}", file=sys.stderr)

    # URLで重複排除
    unique_news = {}
    for item in all_news:
        if item["link"]:
            unique_news[item["link"]] = item

    news_items = list(unique_news.values())

    if not news_items:
        raise RuntimeError(
            "ニュースを取得できませんでした。"
            "分析結果は生成せず、処理を終了します。"
        )

    print(f"ニュース取得合計: {len(news_items)}件")

    result = analyze_market_news(news_items)

    # 結果をJSONとして保存
    output_file = "market_analysis.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"分析結果を保存しました: {output_file}")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
