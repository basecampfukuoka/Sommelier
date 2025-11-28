import streamlit as st
from trainer import BeerTrainer

trainer = BeerTrainer()

st.set_page_config(page_title="AIソムリエ", layout="centered")
st.title("🍺 AIソムリエ - カード表示")

# --- ビール選択 ---

beer_ids = list(trainer.beer_db.keys())
selected_beer_id = st.selectbox("ビールを選択してください", beer_ids)
selected_beer = trainer.beer_db.get(selected_beer_id, {})

st.markdown("### 選択中のビール情報")
st.markdown(f"""

<div style="border:1px solid #ccc; padding:10px; border-radius:8px; margin-bottom:10px; background-color:#fafafa">
<b>名前:</b> {selected_beer.get('name_jp','')}<br>
<b>スタイル:</b> {selected_beer.get('style_main_jp','')} / {selected_beer.get('style_sub_jp','')}<br>
<b>ABV:</b> {selected_beer.get('abv','')} %<br>
<b>容量:</b> {selected_beer.get('volume','')} ml<br>
<b>価格:</b> {selected_beer.get('price','')} 円
</div>
""", unsafe_allow_html=True)

# --- 評価入力 ---

st.markdown("### フィードバック入力")
rating = st.radio("評価", ["良い", "普通", "悪い"], horizontal=True)
notes = st.text_area("感想を入力してください")

if st.button("フィードバックを追加"):
trainer.add_feedback(selected_beer_id, rating, notes)
st.success("✅ フィードバックを追加しました！")

# --- 上位ビール表示 ---

st.markdown("## 上位ビール")
top_beers = trainer.get_top_beers()
for beer in top_beers:
st.markdown(f"""

<div style="border:1px solid #ccc; padding:10px; border-radius:8px; margin-bottom:10px; background-color:#e8f5e9">
<b>{beer['name']}</b> ({beer['style_main']})<br>
ABV: {beer['abv']} %<br>
価格: {beer['price']}円
</div>
""", unsafe_allow_html=True)

# --- スタイル別説明例 ---

st.markdown("## スタイル別説明例")
all_styles = list(trainer.style_words.keys())
for style in all_styles:
st.markdown(f"### {style}")
notes_list = trainer.get_style_examples(style)
for note in notes_list:
st.markdown(f"""

<div style="border:1px solid #ddd; padding:6px; border-radius:6px; margin-bottom:6px; background-color:#fffde7">
- {note}
</div>
""", unsafe_allow_html=True)
