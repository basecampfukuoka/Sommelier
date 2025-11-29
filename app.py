import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ---------------------------
# 初期設定
# ---------------------------
st.set_page_config(page_title="AIビアソムリエ - スタイル比較", layout="centered")

FEEDBACK_FILE = "feedback_style.json"

# ---------------------------
# JSONロード/保存
# ---------------------------
def load_feedback():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_feedback(data):
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------------------
# エクセルロード
# ---------------------------
@st.cache_data
def load_beers():
    df = pd.read_excel("beers.xlsx")
    return df

beers_df = load_beers()

# スタイル一覧をエクセルから抽出
styles_jp = sorted(beers_df["style_main_jp"].dropna().unique().tolist())

# ---------------------------
# UI 表示開始
# ---------------------------
st.title("🍺 AIビアソムリエ - スタイル別比較学習")

st.write("スタイルを選び、ビールを1本選んで説明を書く。")
st.write("5 セット表示、必要なら +5 で追加表示。")

# ---------------------------
# 追加セット数管理
# ---------------------------
if "set_count" not in st.session_state:
    st.session_state.set_count = 5

def add_more():
    st.session_state.set_count += 5

st.button("＋ もっと選ぶ（セット追加）", on_click=add_more)

st.write("---")

# ---------------------------
# 入力フォーム
# ---------------------------

feedback_entries = []

for i in range(st.session_state.set_count):
    st.subheader(f"セット {i + 1}")

    # ① スタイル選択
    style = st.selectbox(
        f"スタイルを選ぶ（セット {i + 1}）",
        [""] + styles_jp,
        key=f"style_{i}"
    )

    # スタイルが選ばれたらビール候補を絞り込む
    beers_filtered = beers_df[beers_df["style_main_jp"] == style] if style else pd.DataFrame()

    # ② ビール選択（そのスタイルのビールのみ）
    beer_names = beers_filtered["name_jp"].tolist() if not beers_filtered.empty else []

    beer = st.selectbox(
        f"ビールを選ぶ（セット {i + 1}）",
        [""] + beer_names,
        key=f"beer_{i}"
    )

    # 説明入力
    explanation = st.text_area(
        f"説明（セット {i + 1}）",
        key=f"exp_{i}",
        placeholder="このビールは◯◯で、理由は◯◯…"
    )

    # 有効な入力のみ保存対象とする
    if style and beer and explanation.strip():
        feedback_entries.append({
            "style_main_jp": style,
            "beer_name_jp": beer,
            "explanation": explanation.strip(),
            "timestamp": datetime.now().isoformat()
        })

st.write("---")

# ---------------------------
# 保存ボタン
# ---------------------------
if st.button("保存する"):
    if feedback_entries:
        old = load_feedback()
        old.extend(feedback_entries)
        save_feedback(old)
        st.success("保存しました！AIソムリエ学習データに追加しました。")
    else:
        st.warning("保存対象のデータがありません。")
