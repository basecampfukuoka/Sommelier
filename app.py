import streamlit as st
import pandas as pd
import json
from pathlib import Path
import random

# -----------------------

# データ設定

# -----------------------

FEEDBACK_FILE = Path("beer_feedback.json")

# JSON読み込み

if FEEDBACK_FILE.exists():
with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
feedback_data = json.load(f)
else:
feedback_data = []

# サンプルビールデータ

beer_list = [
{"name_jp": "ホワイトエール", "style_main_jp": "ホワイトビール"},
{"name_jp": "IPA", "style_main_jp": "インディアペールエール"},
{"name_jp": "スタウト", "style_main_jp": "スタウト"},
{"name_jp": "ペールエール", "style_main_jp": "ペールエール"},
{"name_jp": "ヴァイツェン", "style_main_jp": "ヴァイツェン"},
{"name_jp": "ベルジャンブロンド", "style_main_jp": "ベルジャンビール"},
{"name_jp": "セゾン", "style_main_jp": "セゾン"},
]

beer_df = pd.DataFrame(beer_list)

# ワードお題サンプル

word_list = ["華やか", "爽やか", "ロースト感", "モルト厚め", "苦味強め", "フルーティ"]

# スマホ向けレイアウト

st.set_page_config(page_title="AIソムリエ", layout="centered")
st.title("🍺 AIソムリエ学習アプリ")
st.markdown("ワード出題・スタイル別比較の両方を行い、説明を入力してください。")

# -----------------------

# モード選択

# -----------------------

mode = st.radio("モード選択", ["ワード出題ループ", "スタイル別ビール比較ループ"])

# -----------------------

# ワード出題ループ

# -----------------------

if mode == "ワード出題ループ":
st.subheader("🎯 ワード出題")
word = st.button("お題ワードを出す")
if word:
current_word = random.choice(word_list)
st.session_state["current_word"] = current_word
current_word = st.session_state.get("current_word", None)

```
if current_word:
    st.markdown(f"### 今日のワード: **{current_word}**")

    # ビール選択
    search = st.text_input("ビール名で検索", "")
    if search:
        results = beer_df[beer_df['name_jp'].str.contains(search)]
    else:
        results = beer_df

    if not results.empty:
        selected_beers = st.multiselect(
            "選択するビールをチェック",
            options=results['name_jp'],
            format_func=lambda x: f"{x} ({results[results['name_jp']==x]['style_main_jp'].values[0]})"
        )

        beer_feedback = {}
        for beer in selected_beers:
            beer_feedback[beer] = st.text_area(f"{beer} の説明", "")

        if st.button("送信 (ワードループ)"):
            for beer, desc in beer_feedback.items():
                if desc.strip() == "":
                    continue
                feedback_data.append({
                    "mode": "word_loop",
                    "word": current_word,
                    "name_jp": beer,
                    "description": desc
                })
            # JSON保存
            with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
                json.dump(feedback_data, f, ensure_ascii=False, indent=2)
            st.success("説明を保存しました！")
    else:
        st.warning("検索結果がありません。")
```

# -----------------------

# スタイル別ビール比較ループ

# -----------------------

elif mode == "スタイル別ビール比較ループ":
st.subheader("🎨 スタイル別ビール比較")
styles = beer_df['style_main_jp'].unique()
selected_style = st.selectbox("スタイルを選択", options=styles)

```
style_beers = beer_df[beer_df['style_main_jp'] == selected_style]

if not style_beers.empty:
    selected_beers = st.multiselect(
        f"{selected_style} のビールを選択",
        options=style_beers['name_jp']
    )

    beer_feedback = {}
    for beer in selected_beers:
        beer_feedback[beer] = st.text_area(f"{beer} の説明", "")

    if st.button("送信 (スタイル比較)"):
        for beer, desc in beer_feedback.items():
            if desc.strip() == "":
                continue
            feedback_data.append({
                "mode": "style_loop",
                "style_main_jp": selected_style,
                "name_jp": beer,
                "description": desc
            })
        # JSON保存
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        st.success("説明を保存しました！")
else:
    st.warning("このスタイルのビールはありません。")
```
