import streamlit as st
import pandas as pd
import json
from pathlib import Path

# -----------------------
# 設定
# -----------------------
EXCEL_FILE = "beer_data.xlsx"
FEEDBACK_FILE = Path("beer_feedback.json")

# JSON読み込み
feedback_data = []
if FEEDBACK_FILE.exists():
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedback_data = json.load(f)

# Excel読み込み（列番号で安全に指定）
df_all = pd.read_excel(EXCEL_FILE, usecols=[2,11,14,17])
df_all.columns = ["name_jp", "style_main_jp", "adv", "price"]

# -----------------------
# お題入力
# -----------------------
st.subheader("🎯 お題入力")
current_topic = st.text_input("お題（フリーテキスト）", "")

# -----------------------
# ビール選択セット数
# -----------------------
if "num_sets" not in st.session_state:
    st.session_state["num_sets"] = 1

# 選択UIを表示
beer_feedback_inputs = []
for i in range(st.session_state["num_sets"]):
    st.markdown(f"### ビール {i+1}")

    # ①スタイル選択
    styles = df_all['style_main_jp'].dropna().unique()
    selected_style = st.selectbox(f"スタイルを選ぶ ({i+1})", options=styles, key=f"style_{i}")

    # ②ビール名選択（styleで絞り込み）
    beers_in_style = df_all[df_all['style_main_jp'] == selected_style]
    beer_options = [f"{row['name_jp']} / {row['adv']}% / ¥{row['price']}" for _, row in beers_in_style.iterrows()]

    selected_beer = st.selectbox(f"ビールを選ぶ ({i+1})", options=beer_options, key=f"beer_{i}")

    # 説明入力
    desc_input = st.text_area(f"説明を入力 ({i+1})", key=f"desc_{i}")

    beer_feedback_inputs.append({
        "style_main_jp": selected_style,
        "beer_info": selected_beer,
        "description": desc_input
    })

# -----------------------
# 画面下に固定する「もっと選ぶ」ボタン用 CSS
# -----------------------
st.markdown("""
<style>
.fixed-bottom {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
}
</style>
""", unsafe_allow_html=True)

# ボタン表示（固定）
if st.button("もっと選ぶ", key="more_sets", help="1セットずつ追加する", args=None):
    st.session_state["num_sets"] += 1

# -----------------------
# 送信ボタン
# -----------------------
if st.button("送信"):
    if current_topic.strip() == "":
        st.warning("お題を入力してください。")
    else:
        for entry in beer_feedback_inputs:
            if entry["description"].strip() == "":
                continue
            name_jp = entry["beer_info"].split(" / ")[0]
            adv = entry["beer_info"].split(" / ")[1].replace("adv:","")
            price = entry["beer_info"].split(" / ")[2].replace("price:","")

            feedback_data.append({
                "topic": current_topic,
                "style_main_jp": entry["style_main_jp"],
                "name_jp": name_jp,
                "adv": adv,
                "price": price,
                "description": entry["description"]
            })
        with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        st.success("説明を保存しました！")
