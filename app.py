# app.py
import streamlit as st
import pandas as pd
import json
from pathlib import Path
import random

# -----------------------
# 設定
# -----------------------
BEERS_XLSX = Path("beers.xlsx")           # 既存の Excel ファイルを想定
FEEDBACK_FILE = Path("beer_feedback.json")
INITIAL_BOXES = 5                         # 最初に表示する検索ボックス数
BOX_INCREMENT = 5                         # 「さらに表示」で増える数
SUGGEST_LIMIT = 10                        # サジェスト表示の上限件数

# -----------------------
# データ読み込み
# -----------------------
# beers.xlsx があれば読み込む。なければサンプルデータを使う。
if BEERS_XLSX.exists():
    beers_df = pd.read_excel(BEERS_XLSX, engine="openpyxl")
    # 必要なカラムが存在するか確認し、なければ空カラムを作る
    for col in ("name_jp", "style_main_jp"):
        if col not in beers_df.columns:
            beers_df[col] = ""
    beers_df = beers_df[["name_jp", "style_main_jp"]].fillna("").astype(str)
else:
    # フォールバックのサンプル
    beers_df = pd.DataFrame([
        {"name_jp": "ホワイトエール", "style_main_jp": "ホワイトビール"},
        {"name_jp": "IPA", "style_main_jp": "インディアペールエール"},
        {"name_jp": "スタウト", "style_main_jp": "スタウト"},
        {"name_jp": "ペールエール", "style_main_jp": "ペールエール"},
        {"name_jp": "ヴァイツェン", "style_main_jp": "ヴァイツェン"},
        {"name_jp": "ベルジャンブロンド", "style_main_jp": "ベルジャンビール"},
        {"name_jp": "セゾン", "style_main_jp": "セゾン"},
    ])

# フィードバック格納先読み込み（なければ初期化）
if FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedback_data = json.load(f)
else:
    feedback_data = []

# ワードお題（必要なら増やして）
word_list = ["華やか", "爽やか", "ロースト感", "モルト厚め", "苦味強め", "フルーティ"]

# -----------------------
# ヘルパー関数
# -----------------------
def suggest_candidates(query: str, df: pd.DataFrame, style_filter: str = None, limit: int = SUGGEST_LIMIT):
    """
    部分一致で候補を抽出（name_jp または style_main_jp にマッチ）。
    style_filter が与えられたらそのスタイルに絞る。
    小文字大文字は区別しない。
    """
    q = str(query).strip()
    if q == "":
        # 空クエリは全件（style_filter があればそれに従う）
        if style_filter:
            candidates = df[df["style_main_jp"] == style_filter]
        else:
            candidates = df
    else:
        # 部分一致（name_jp または style_main_jp）
        mask = df["name_jp"].str.contains(q, case=False, na=False) | df["style_main_jp"].str.contains(q, case=False, na=False)
        candidates = df[mask]
        if style_filter:
            candidates = candidates[candidates["style_main_jp"] == style_filter]

    # 重複を除き name_jp を優先で返す
    names = candidates["name_jp"].drop_duplicates().tolist()
    return names[:limit]

def save_feedback(entries):
    """
    フィードバックエントリ（リスト）を feedback_data に追加して JSON に保存する。
    """
    global feedback_data
    feedback_data.extend(entries)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedback_data, f, ensure_ascii=False, indent=2)

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="AIソムリエ", layout="centered")
st.title("🍺 AIソムリエ学習アプリ（サジェスト検索・5ボックス方式）")
st.markdown("検索ボックスに文字を入れると候補が表示されます。name_jp と style_main_jp 両方で検索します。")

# モード選択
mode = st.radio("モード選択", ["ワード出題ループ", "スタイル別ビール比較ループ"], index=0)

# 何個ボックスを表示しているかをセッションで管理
if "n_boxes" not in st.session_state:
    st.session_state["n_boxes"] = INITIAL_BOXES

# 「さらに表示」ボタン
col_more = st.columns([1, 3, 1])
with col_more[1]:
    if st.button("さらに表示"):
        st.session_state["n_boxes"] += BOX_INCREMENT

# -----------------------
# ワード出題ループ
# -----------------------
if mode == "ワード出題ループ":
    st.subheader("🎯 ワード出題モード")
    if "current_word" not in st.session_state:
        st.session_state["current_word"] = random.choice(word_list)

    if st.button("お題ワードを出す（再抽選）"):
        st.session_state["current_word"] = random.choice(word_list)

    st.markdown(f"### 今日のワード: **{st.session_state['current_word']}**")

    # 検索ボックス群（下に n_boxes 個表示）
    st.markdown("**ビールを検索して選択してください（複数可）**")
    entries_to_save = []
    for i in range(st.session_state["n_boxes"]):
        st.markdown(f"**検索欄 #{i+1}**")
        query = st.text_input(f"検索テキスト #{i+1}", key=f"word_query_{i}")
        # サジェスト（selectbox）を表示
        suggestions = suggest_candidates(query, beers_df)
        if suggestions:
            choice = st.selectbox(f"候補を選ぶ #{i+1}", options=["（未選択）"] + suggestions, key=f"word_choice_{i}")
        else:
            choice = "（未選択）"
        # 説明欄
        desc = st.text_area(f"{choice if choice != '（未選択）' else 'ビール'} の説明（#{i+1}）", key=f"word_desc_{i}")

        # Prepare entry but only append when user presses 送信
        if choice != "（未選択）" and desc.strip() != "":
            entries_to_save.append({
                "mode": "word_loop",
                "word": st.session_state["current_word"],
                "name_jp": choice,
                "description": desc.strip()
            })

    if st.button("送信 (ワードループ)"):
        if entries_to_save:
            save_feedback(entries_to_save)
            st.success(f"{len(entries_to_save)} 件を保存しました。")
        else:
            st.info("保存する説明が見つかりませんでした。選択と説明を確認してください。")

# -----------------------
# スタイル別ビール比較ループ
# -----------------------
else:
    st.subheader("🎨 スタイル別比較モード")
    # スタイル選択（Excel にある style_main_jp 列のユニーク値）
    styles = beers_df["style_main_jp"].replace("", pd.NA).dropna().unique().tolist()
    styles = sorted(styles)
    if not styles:
        st.warning("beers.xlsx に style_main_jp のデータがありません。")
    selected_style = st.selectbox("スタイルを選択 (style_main_jp)", options=["（指定なし）"] + styles, index=0)

    st.markdown("**スタイル条件を使って検索して選択してください（複数可）**")
    entries_to_save = []
    # 表示するボックス数は同じく n_boxes
    for i in range(st.session_state["n_boxes"]):
        st.markdown(f"**検索欄 #{i+1}**")
        query = st.text_input(f"検索テキスト #{i+1}", key=f"style_query_{i}")
        # サジェストは style が指定されていればそれで絞る
        style_filter = None if selected_style == "（指定なし）" else selected_style
        suggestions = suggest_candidates(query, beers_df, style_filter=style_filter)
        if suggestions:
            choice = st.selectbox(f"候補を選ぶ #{i+1}", options=["（未選択）"] + suggestions, key=f"style_choice_{i}")
        else:
            choice = "（未選択）"
        desc = st.text_area(f"{choice if choice != '（未選択）' else 'ビール'} の説明（#{i+1}）", key=f"style_desc_{i}")

        if choice != "（未選択）" and desc.strip() != "":
            entry = {
                "mode": "style_loop",
                "style_main_jp": style_filter if style_filter else "",
                "name_jp": choice,
                "description": desc.strip()
            }
            entries_to_save.append(entry)

    if st.button("送信 (スタイル比較)"):
        if entries_to_save:
            save_feedback(entries_to_save)
            st.success(f"{len(entries_to_save)} 件を保存しました。")
        else:
            st.info("保存する説明が見つかりませんでした。選択と説明を確認してください。")

# -----------------------
# フッター（デバッグ用に現在のフィードバック数表示）
# -----------------------
st.markdown("---")
st.caption(f"保存済みフィードバック件数: {len(feedback_data)}")

