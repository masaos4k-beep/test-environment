import json
import re
import html
from pathlib import Path
from urllib.parse import urlparse

# このプログラムと次の2ファイルを同じフォルダに置いてください。
JSON_FILE = Path("market_analysis.json")
DASHBOARD_FILE = Path("market_dashboard.html")
OUTPUT_FILE = Path("market_report.html")


def get_source_url(value):
    """Markdown形式のURL、または通常のURLからリンク先を取り出す。"""
    if not isinstance(value, str):
        return ""

    value = value.strip()

    # 例: [https://example.com](https://example.com)
    match = re.fullmatch(r"\[([^\]]*)\]\((https?://[^)]+)\)", value)
    if match:
        value = match.group(2).strip()

    # 安全のため、http/https以外のスキームはリンクにしない
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""

    return value


def main():
    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"{JSON_FILE} が見つかりません。\n"
            "market_analysis.json をこのプログラムと同じフォルダに置いてください。"
        )

    if not DASHBOARD_FILE.exists():
        raise FileNotFoundError(
            f"{DASHBOARD_FILE} が見つかりません。\n"
            "market_dashboard.html をこのプログラムと同じフォルダに置いてください。"
        )

    with JSON_FILE.open("r", encoding="utf-8") as f:
        report = json.load(f)

    report_date = html.escape(str(report.get("report_date", "日付未設定")))
    drivers = report.get("drivers", [])

    if not isinstance(drivers, list):
        raise ValueError("market_analysis.json の drivers は配列である必要があります。")

    cards = []
    for index, driver in enumerate(drivers, start=1):
        if not isinstance(driver, dict):
            continue

        title = html.escape(str(driver.get("title", f"要因 {index}")))
        detail = html.escape(str(driver.get("detail", "")))
        source_title = html.escape(str(driver.get("source_title", "出典")))
        source_url = get_source_url(driver.get("source_url", ""))

        if source_url:
            # 属性値としてHTMLエスケープしてから埋め込む
            safe_url = html.escape(source_url, quote=True)
            source_html = (
                f'<a href="{safe_url}" target="_blank" '
                f'rel="noopener noreferrer">{source_title}（記事を開く）</a>'
            )
        else:
            source_html = f'<span class="source-unavailable">{source_title}</span>'

        cards.append(f"""
        <article class="factor-card">
          <div class="factor-number">MARKET FACTOR {index:02d}</div>
          <h2>{title}</h2>
          <p>{detail}</p>
          <div class="source">出典：{source_html}</div>
        </article>
        """)

    if not cards:
        cards_html = '<p class="empty">分析要因がありません。market_analysis.json を確認してください。</p>'
    else:
        cards_html = "\n".join(cards)

    # 既存のダッシュボードHTMLは変更せず、iframeでそのまま表示する
    output_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>米国株マーケットレポート {report_date}</title>
<style>
  :root {{
    color-scheme: dark;
    --bg: #080b12;
    --panel: #111827;
    --border: #263244;
    --text: #eef2f7;
    --muted: #9caec2;
    --accent: #60a5fa;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                 "Noto Sans JP", "Meiryo", sans-serif;
    line-height: 1.75;
  }}
  .page-header {{
    padding: 34px 20px 26px;
    text-align: center;
    background: linear-gradient(135deg, #111827, #0b1220 65%, #10233b);
    border-bottom: 1px solid var(--border);
  }}
  .eyebrow {{
    margin: 0 0 6px;
    color: var(--accent);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .16em;
  }}
  h1 {{
    margin: 0;
    font-size: clamp(25px, 4vw, 38px);
    line-height: 1.35;
  }}
  .date {{
    margin: 10px 0 0;
    color: var(--muted);
    font-size: 14px;
  }}
  main {{
    width: min(1120px, calc(100% - 32px));
    margin: 0 auto;
  }}
  .section-heading {{
    margin: 30px 0 14px;
    font-size: 22px;
  }}
  .section-intro {{
    margin: -4px 0 18px;
    color: var(--muted);
    font-size: 14px;
  }}
  .factors {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr));
    gap: 16px;
  }}
  .factor-card {{
    padding: 20px 21px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    box-shadow: 0 8px 24px rgba(0,0,0,.15);
  }}
  .factor-number {{
    color: var(--accent);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: .12em;
  }}
  .factor-card h2 {{
    margin: 8px 0 10px;
    font-size: 19px;
    line-height: 1.55;
  }}
  .factor-card p {{
    margin: 0;
    color: #d2dbe7;
    font-size: 14px;
    white-space: pre-wrap;
  }}
  .source {{
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
    color: var(--muted);
    font-size: 12px;
    overflow-wrap: anywhere;
  }}
  a {{ color: #93c5fd; }}
  a:hover {{ color: #dbeafe; }}
  .source-unavailable {{ color: var(--muted); }}
  .chart-section {{
    margin-top: 38px;
    padding-top: 8px;
    border-top: 1px solid var(--border);
  }}
  .chart-frame {{
    display: block;
    width: 100%;
    height: 2200px;
    border: 0;
    border-radius: 10px;
    background: #fff;
  }}
  .footer {{
    padding: 24px 16px 36px;
    color: var(--muted);
    text-align: center;
    font-size: 12px;
  }}
  .empty {{ color: var(--muted); }}
  @media (max-width: 600px) {{
    main {{ width: min(100% - 22px, 1120px); }}
    .page-header {{ padding: 26px 14px 22px; }}
    .factor-card {{ padding: 17px; }}
    .chart-frame {{ height: 2400px; }}
  }}
</style>
</head>
<body>
<header class="page-header">
  <p class="eyebrow">DAILY US MARKET REPORT</p>
  <h1>米国株マーケットレポート</h1>
  <p class="date">レポート日：{report_date}</p>
</header>

<main>
  <section aria-labelledby="factors-heading">
    <h2 class="section-heading" id="factors-heading">本日の相場を動かした主な要因</h2>
    <p class="section-intro">ニュース分析で抽出した要因と出典です。記載内容はニュースに基づく分析であり、株価変動との因果関係を断定するものではありません。</p>
    <div class="factors">
      {cards_html}
    </div>
  </section>

  <section class="chart-section" aria-labelledby="chart-heading">
    <h2 class="section-heading" id="chart-heading">米国株マーケット・ダッシュボード</h2>
    <p class="section-intro">下のチャートは既存の market_dashboard.html を読み込んで表示しています。</p>
    <iframe class="chart-frame" src="market_dashboard.html"
            title="米国株マーケット・ダッシュボード"
            loading="lazy"></iframe>
  </section>
</main>

<footer class="footer">
  ニュース要因と市場データを参考情報として掲載しています。投資判断はご自身で行ってください。
</footer>
</body>
</html>
"""

    OUTPUT_FILE.write_text(output_html, encoding="utf-8")
    print(f"作成しました: {OUTPUT_FILE.resolve()}")
    print("market_report.html と market_dashboard.html を同じフォルダに置いて開いてください。")


if __name__ == "__main__":
    main()
