import json
import os
from collections import defaultdict
import pandas as pd

DATA_FILE = "user_feedback.json"
BEER_DB_FILE = "beer_data.xlsx"

class BeerTrainer:
    def __init__(self, data_file=DATA_FILE, beer_db_file=BEER_DB_FILE):
        self.data_file = data_file
        self.feedback = []
        self.profile = defaultdict(float)
        self.style_words = defaultdict(list)
        self.beer_db = self.load_beer_db(beer_db_file)
        self.load_feedback()

    def load_beer_db(self, file_path):
        if os.path.exists(file_path):
            df = pd.read_excel(file_path)
            df = df.fillna("")
            return df.set_index("beer_id").to_dict(orient="index")
        else:
            print(f"Error: {file_path} が見つかりません")
            return {}

    def load_feedback(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.feedback = json.load(f)
        else:
            self.feedback = []

    def add_feedback(self, beer_id, rating_str, notes, style=None):
        rating_map = {"良い": 2, "普通": 1, "悪い": 0}
        rating = rating_map.get(rating_str, 1)
        if beer_id not in self.beer_db:
            print(f"Warning: {beer_id} はビールDBに存在しません")
        else:
            if style is None:
                style = self.beer_db[beer_id].get("style_main_jp")
        entry = {"beer_id": beer_id, "rating": rating, "notes": notes, "style": style}
        self.feedback.append(entry)
        self.save_feedback()
        self.update_profile(entry)

    def save_feedback(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.feedback, f, ensure_ascii=False, indent=2)

    def update_profile(self, entry):
        beer_id = entry["beer_id"]
        rating = entry["rating"]
        notes = entry["notes"]
        style = entry.get("style")
        self.profile[beer_id] += rating
        if style:
            self.style_words[style].append(notes)

    def get_top_beers(self, top_n=5):
        sorted_beers = sorted(self.profile.items(), key=lambda x: x[1], reverse=True)
        top_ids = [beer_id for beer_id, _ in sorted_beers[:top_n]]
        results = []
        for beer_id in top_ids:
            beer = self.beer_db.get(beer_id, {})
            results.append({
                "beer_id": beer_id,
                "name": beer.get("name_jp",""),
                "style_main": beer.get("style_main_jp",""),
                "style_sub": beer.get("style_sub_jp",""),
                "abv": beer.get("abv",""),
                "volume": beer.get("volume",""),
                "price": beer.get("price","")
            })
        return results

    def get_style_examples(self, style):
        return self.style_words.get(style, [])

if __name__ == "__main__":
    trainer = BeerTrainer()
    trainer.add_feedback("beer_001", "良い", "香りが華やかでジューシー", style="Hazy IPA")
    trainer.add_feedback("beer_002", "普通", "少し苦味が強い", style="Stout")

    print("Top beers:", trainer.get_top_beers())
    print("Hazy IPA examples:", trainer.get_style_examples("Hazy IPA"))
