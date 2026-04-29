import os
import json
import pandas as pd
from pathlib import Path


class FewShotPosts:
    def __init__(self):
        # Get project root
        base_dir = Path(__file__).resolve().parent

        # Correct file path
        file_path = base_dir / "data" / "processed_posts.json"

        print("BASE DIR:", base_dir)
        print("FILE PATH:", file_path)
        print("EXISTS:", file_path.exists())

        if not file_path.exists():
            raise FileNotFoundError(f"Missing file: {file_path}")

        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)

    def load_posts(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            posts = json.load(f)
            self.df = pd.json_normalize(posts)

            # Add length category
            self.df['length'] = self.df['line_count'].apply(self.categorize_length)

            # Extract tags
            all_tags = self.df['tags'].sum()
            self.unique_tags = list(set(all_tags))

 
    def get_filtered_posts(self, length, language, tag):
        df_filtered = self.df[
            (self.df['tags'].apply(lambda tags: tag in tags)) &
            (self.df['language'] == language) &
            (self.df['length'] == length)
        ]
        return df_filtered.to_dict(orient='records')

    def categorize_length(self, line_count):
        if line_count < 5:
            return "Short"
        elif line_count <= 10:
            return "Medium"
        else:
            return "Long"

    def get_tags(self):
        return self.unique_tags



if __name__ == "__main__":
    fs = FewShotPosts()
    posts = fs.get_filtered_posts("Short", "English", "Job Search")
    print(posts)
    print(posts)