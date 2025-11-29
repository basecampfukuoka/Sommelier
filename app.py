import streamlit as st
import pandas as pd
import json
from pathlib import Path

# -----------------------
# データ設定
# -----------------------
FEEDBACK_FILE = Path("beer_feedback.json")
EXCEL_FILE = "beers.xlsx"

# JSON読み込み
if FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedback_data = json.load(f)
else:
    feedback_data = []

# ビールデータ読み込み（Excel A列: style_main_jp, B列: name_jp）
beers_df = pd.read_excel(EXCEL_FILE, usecols=[0, 1])
beers_df.columns = ["style_main_jp", "name_jp"]

# -----------------------
# スマホ向けレイアウト
# -----------------------
st.set_page_config(page_title="AIソムリエ", layout="centered")
st.title("🍺 AIソムリエ学習アプリ")
st.markdown("お題入力 → ビール選択 → 説明入力の順に入力してください。")

# -----------------------
# セット数管理
# -----------------------
if "num_sets" not in st.session_state:
    st.session_state["num_sets"] = 5

# 「もっと選ぶ」ボタンで +5セット
if st.button("もっと選ぶ"):
    st.session_state["num_sets"] += 5

num_sets = st.session_state["num_sets"]

# -----------------------
# 各セットの入力
# -----------------------
inputs = []
for i in range(num_sets):
    st.markdown(f"### セット {i+1}")

    # お題フリーテキスト
    word = st.text_input(f"お題 (セット {i+1})", key=f"word_{i}")

    # スタイル選択
    style_options = sorted(beers_df['style_main_jp'].unique())
    selected_style = st.selectbox(f"スタイル選択 (セット {i+1})", options=style_options, key=f"style_{i}")

    # 選んだスタイルに紐づくビール名選択
    beer_options = beers_df[beers_df['style_main_jp'] == selected_style]['name_jp'].tolist()
    selected_beer = st.selectbox(f"ビール選択 (セット {i+1})", options=beer_options, key=f"beer_{i}")

    # 説明入力
    description = st.text_area(f"{selected_beer} の説明 (セット {i+1})", key=f"desc_{i}")

    inputs.append({
        "word": word,
        "style_main_jp": selected_style,
        "name_jp": selected_beer,
        "description": description
    })

# -----------------------
# 保存ボタン
# -----------------------
if st.button("送信して保存"):
    for entry in inputs:
        if entry['word'].strip() and entry['description'].strip():
            feedback_data.append({
                "mode": "free_text_loop",
                "word": entry['word'],
                "style_main_jp": entry['style_main_jp'],
                "name_jp": entry['name_jp'],
                "description": entry['description']
            })

    # JSON保存
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)

    st.success("説明を保存しました！")
