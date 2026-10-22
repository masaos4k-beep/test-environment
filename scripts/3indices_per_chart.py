from pathlib import Path
import datetime
import pandas as pd
import plotly.graph_objects as go

# ==========================================
# 1. ファイル設定
# ==========================================

# スクリプトの場所からGitHubリポジトリのルートを取得
BASE_DIR = Path(__file__).resolve().parent.parent

# 入力CSV
csv_file = BASE_DIR / "data" / "forward_pe_3indices_2026.csv"

# 出力HTML
output_filename = BASE_DIR / "3indices_per_chart_chart.html"


# ==========================================
# 2. CSVデータの読み込み
# ==========================================

df = pd.read_csv(csv_file)

df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values("Date")
df = df.set_index("Date")

# 現在の年を取得
current_year = datetime.datetime.now().year

# 横軸の表示範囲
x_start = f"{current_year}-01-01"
x_end = f"{current_year}-12-31"


# ==========================================
# 3. 指数ごとのチャート設定
# ==========================================

index_configs = {
    "SP500": {
        "name": "S&P 500",
        "column": "SP500_Forward_PE",
        "y_range": [15, 27],
        "line_color": "#FF9900",
        "marker_color": "#FFD700",
        "zones": [
            (15, 18, "割安"),
            (18, 20, "やや割安"),
            (20, 22, "中立"),
            (22, 24, "やや割高"),
            (24, 27, "割高"),
        ],
        "thresholds": [18, 20, 22, 24],
    },

    "NASDAQ100": {
        "name": "NASDAQ 100",
        "column": "NASDAQ100_Forward_PE",
        "y_range": [17, 32],
        "line_color": "#00CC96",
        "marker_color": "#98FB98",
        "zones": [
            (17, 20, "割安"),
            (20, 23, "やや割安"),
            (23, 26, "中立"),
            (26, 29, "やや割高"),
            (29, 32, "割高"),
        ],
        "thresholds": [20, 23, 26, 29],
    },

    "SOX": {
        "name": "SOX（半導体）",
        "column": "SOX_Forward_PE",
        "y_range": [15, 30],
        "line_color": "#3399FF",
        "marker_color": "#ADD8E6",
        "zones": [
            (15, 18, "割安"),
            (18, 21, "やや割安"),
            (21, 24, "中立"),
            (24, 27, "やや割高"),
            (27, 30, "割高"),
        ],
        "thresholds": [18, 21, 24, 27],
    },
}


# ==========================================
# 4. PERゾーンと基準線を作成
# ==========================================

def build_shapes_and_annotations(config):

    shapes = []
    annotations = []

    # 背景のPERゾーン
    for y0, y1, label in config["zones"]:

        shapes.append(
            dict(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=y0,
                y1=y1,
                fillcolor=(
                    "rgba(0, 180, 0, 0.07)"
                    if label == "割安"
                    else
                    "rgba(255, 255, 0, 0.05)"
                    if label == "中立"
                    else
                    "rgba(255, 80, 80, 0.05)"
                ),
                line=dict(width=0),
                layer="below",
            )
        )

    # PER基準線
    for value in config["thresholds"]:

        shapes.append(
            dict(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=value,
                y1=value,
                line=dict(
                    color="rgba(200, 200, 200, 0.45)",
                    width=1,
                    dash="dash",
                ),
            )
        )

        annotations.append(
            dict(
                xref="paper",
                x=1.005,
                y=value,
                yref="y",
                text=str(value),
                showarrow=False,
                font=dict(
                    color="#CCCCCC",
                    size=10,
                ),
                xanchor="left",
            )
        )

    return shapes, annotations


# ==========================================
# 5. チャートを作成
# ==========================================

fig = go.Figure()

for key, config in index_configs.items():

    column = config["column"]

    if column not in df.columns:
        raise ValueError(
            f"CSVに必要な列がありません: {column}"
        )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df[column],
            mode="lines+markers",
            name=config["name"],
            line=dict(
                color=config["line_color"],
                width=2,
            ),
            marker=dict(
                color=config["marker_color"],
                size=5,
            ),
            visible=(key == "SP500"),
            connectgaps=False,
            hovertemplate=(
                "%{x|%Y-%m-%d}<br>"
                + config["name"]
                + " 予想PER: %{y:.2f}"
                + "<extra></extra>"
            ),
        )
    )


# ==========================================
# 6. 初期表示の設定
# ==========================================

initial_config = index_configs["SP500"]

initial_shapes, initial_annotations = (
    build_shapes_and_annotations(initial_config)
)

fig.update_layout(
    title=dict(
        text=f"S&P 500 1年予想PER 推移（{current_year}年）",
        font=dict(
            color="#FFFFFF",
            size=20,
        ),
    ),

    template="plotly_dark",

    paper_bgcolor="#111111",
    plot_bgcolor="#1A1A1A",

    xaxis=dict(
        title="日付",
        range=[x_start, x_end],
        tickformat="%m月",
        dtick="M1",
        showgrid=True,
        gridcolor="#333333",
        color="#DDDDDD",
    ),

    yaxis=dict(
        title="予想PER",
        range=initial_config["y_range"],
        showgrid=True,
        gridcolor="#333333",
        color="#DDDDDD",
    ),

    shapes=initial_shapes,
    annotations=initial_annotations,

    margin=dict(
        r=65,
        t=90,
        b=70,
        l=60,
    ),

    showlegend=False,
)


# ==========================================
# 7. HTMLを出力
# ==========================================

# HTML本体を出力
fig.write_html(
    str(output_filename),
    include_plotlyjs="cdn",
    full_html=True,
    config={
        "responsive": True,
        "displaylogo": False,
    },
)

# ==========================================
# 8. 指数選択ボタンをHTMLに追加
# ==========================================

# Plotly標準ボタンでは選択中の色を自由に
# 切り替えにくいため、HTMLボタンを使用する。

html = output_filename.read_text(encoding="utf-8")

button_html = """
<style>
.index-button-area {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 15px 10px 5px 10px;
}

.index-button {
    background-color: #333333;
    color: #DDDDDD;
    border: 1px solid #666666;
    border-radius: 6px;
    padding: 10px 22px;
    font-size: 14px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.2s;
}

.index-button.active {
    background-color: #1677FF;
    color: #FFFFFF;
    border-color: #1677FF;
}

.index-button:hover {
    border-color: #66AAFF;
}
</style>

<div class="index-button-area">
    <button class="index-button active"
            data-index="0">S&P 500</button>
    <button class="index-button"
            data-index="1">NASDAQ 100</button>
    <button class="index-button"
            data-index="2">SOX（半導体）</button>
</div>

<script>
document.addEventListener("DOMContentLoaded", function () {

    const buttons = document.querySelectorAll(".index-button");

    const configs = [
        {
            title: "S&P 500 1年予想PER 推移",
            range: [15, 27],
            shapes: [
                [15, 18, "rgba(0, 180, 0, 0.07)"],
                [18, 20, "rgba(255, 255, 0, 0.05)"],
                [20, 22, "rgba(255, 255, 0, 0.05)"],
                [22, 24, "rgba(255, 80, 80, 0.05)"],
                [24, 27, "rgba(255, 80, 80, 0.05)"]
            ],
            thresholds: [18, 20, 22, 24]
        },
        {
            title: "NASDAQ 100 1年予想PER 推移",
            range: [17, 32],
            shapes: [
                [17, 20, "rgba(0, 180, 0, 0.07)"],
                [20, 23, "rgba(255, 255, 0, 0.05)"],
                [23, 26, "rgba(255, 255, 0, 0.05)"],
                [26, 29, "rgba(255, 80, 80, 0.05)"],
                [29, 32, "rgba(255, 80, 80, 0.05)"]
            ],
            thresholds: [20, 23, 26, 29]
        },
        {
            title: "SOX（半導体）1年予想PER 推移",
            range: [15, 30],
            shapes: [
                [15, 18, "rgba(0, 180, 0, 0.07)"],
                [18, 21, "rgba(255, 255, 0, 0.05)"],
                [21, 24, "rgba(255, 255, 0, 0.05)"],
                [24, 27, "rgba(255, 80, 80, 0.05)"],
                [27, 30, "rgba(255, 80, 80, 0.05)"]
            ],
            thresholds: [18, 21, 24, 27]
        }
    ];

    const plot = document.querySelector(".plotly-graph-div");

    function makeShapes(config) {
        const shapes = [];

        config.shapes.forEach(function (zone) {
            shapes.push({
                type: "rect",
                xref: "paper",
                yref: "y",
                x0: 0,
                x1: 1,
                y0: zone[0],
                y1: zone[1],
                fillcolor: zone[2],
                line: {width: 0},
                layer: "below"
            });
        });

        config.thresholds.forEach(function (value) {
            shapes.push({
                type: "line",
                xref: "paper",
                yref: "y",
                x0: 0,
                x1: 1,
                y0: value,
                y1: value,
                line: {
                    color: "rgba(200, 200, 200, 0.45)",
                    width: 1,
                    dash: "dash"
                }
            });
        });

        return shapes;
    }

    function makeAnnotations(config) {
        return config.thresholds.map(function (value) {
            return {
                xref: "paper",
                x: 1.005,
                y: value,
                yref: "y",
                text: String(value),
                showarrow: false,
                font: {
                    color: "#CCCCCC",
                    size: 10
                },
                xanchor: "left"
            };
        });
    }

    function selectIndex(index) {
        const config = configs[index];

        buttons.forEach(function (button) {
            button.classList.toggle(
                "active",
                Number(button.dataset.index) === index
            );
        });

        const visibility = [0, 1, 2].map(function (i) {
            return i === index;
        });

        Plotly.restyle(plot, "visible", visibility);

        Plotly.relayout(plot, {
            "title.text": config.title,
            "yaxis.range": config.range,
            "shapes": makeShapes(config),
            "annotations": makeAnnotations(config)
        });
    }

    buttons.forEach(function (button) {
        button.addEventListener("click", function () {
            selectIndex(Number(button.dataset.index));
        });
    });
});
</script>
"""

# 標準ボタンは使用しないため、ボタンHTMLをbody冒頭に挿入
html = html.replace(
    "<body>",
    "<body>\n" + button_html,
    1,
)

output_filename.write_text(html, encoding="utf-8")

print(f"HTMLチャートを出力しました: {output_filename}")

