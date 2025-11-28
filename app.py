import streamlit as st
from trainer import BeerTrainer

st.set_page_config(page_title="AIソムリエ", layout="centered")
st.title("🍺 AIソムリエ")

# --------------------------
# セッションに Trainer を保持
# --------------------------
if "trainer" not in st.session_state:
    st.session_state.trainer = BeerTrainer()

trainer = st.session_state.trainer

# --- ビール選択 ---
beer_ids = list(trainer.beer_db.keys())
selected_beer_id = st.selectbox("ビールを選択してください", beer_ids)
selected_beer = trainer.beer_db.get(selected_beer_id, {})

st.write("### 選択中のビール情報")
st.write(f"**名前:** {selected_beer.get('name_jp','')}")
st.write(f"**スタイル:** {selected_beer.get('style_main_jp','')} / {selected_beer.get('style_sub_jp','')}")
st.write(f"**ABV:** {selected_beer.get('abv','')} %")
st.write(f"**容量:** {selected_beer.get('volume','')} ml")
st.write(f"**価格:** {selected_beer.get('price','')} 円")

# --- 評価入力 ---
st.write("### フィードバック入力")
rating = st.radio("評価", ["良い", "普通", "悪い"])
notes = st.text_area("感想を入力してください")

# フィードバック追加ボタン
if st.button("フィードバックを追加"):
    trainer.add_feedback(selected_beer_id, rating, notes)
    st.success("✅ フィードバックを追加しました！")

# --- 上位ビール表示 ---
st.write("## 上位ビール")
top_beers = trainer.get_top_beers()
for beer in top_beers:
    st.write(f"**{beer['name']}** ({beer['style_main']}) - ABV: {beer['abv']} %, 価格: {beer['price']}円")

# --- スタイル別説明例 ---
st.write("## スタイル別説明例")
all_styles = list(trainer.style_words.keys())
for style in all_styles:
    st.write(f"### {style}")
    for note in trainer.get_style_examples(style):
        st.write("-", note)
