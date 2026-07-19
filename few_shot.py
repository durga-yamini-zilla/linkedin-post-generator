import os
import json
import pandas as pd
from pathlib import Path


class FewShotPosts:
    def __init__(self):
        file_path = "data/processed_posts.json"

        # Debug info
        print("CURRENT DIR:", os.getcwd())
        print("FILES HERE:", os.listdir())
        print("DATA FOLDER:", os.listdir("data") if os.path.exists("data") else "NO DATA FOLDER")
        print("TRYING PATH:", file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Missing file: {file_path}")

        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)

    def load_posts(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            posts = json.load(f)

        clean_posts = []
        for post in posts:
            clean_post = {}
            for k, v in post.items():
                clean_post[k] = str(v).encode("ascii", "ignore").decode()
            clean_posts.append(clean_post)

        # build dataframe once
        self.df = pd.DataFrame(clean_posts).astype(str)

        # Add length category if available
        if "line_count" in self.df.columns:
            self.df["length"] = self.df["line_count"].apply(self.categorize_length)
        else:
            self.df["length"] = "Unknown"

        # Normalize tags into lists so UI receives full titles not characters
        if "tags" in self.df.columns:
            def parse_tags(cell):
                # Try JSON parsing for proper lists
                try:
                    if isinstance(cell, str) and cell.strip().startswith("[") and cell.strip().endswith("]"):
                        parsed = json.loads(cell)
                        if isinstance(parsed, list):
                            cleaned = []
                            for t in parsed:
                                if t is None:
                                    continue
                                s = str(t).strip()
                                s = s.strip("'\"[] ")
                                if s:
                                    cleaned.append(s)
                            return cleaned
                except Exception:
                    pass

                # Fallback: split on commas and clean stray brackets/quotes
                if isinstance(cell, str) and "," in cell:
                    parts = [p.strip().strip("'\"[] ") for p in cell.split(",")]
                    return [p for p in parts if p]

                # Single value or empty
                if cell and cell != "nan":
                    return [str(cell).strip().strip("'\"[] ")]
                return []

            self.df["tags_list"] = self.df["tags"].apply(parse_tags)
            # flatten and unique
            all_tags = self.df["tags_list"].explode().dropna().unique().tolist()
            self.unique_tags = sorted(all_tags)
        else:
            self.df["tags_list"] = [[] for _ in range(len(self.df))]
            self.unique_tags = []

 
    def categorize_length(self, line_count):
        line_count = int(line_count)

        if line_count < 5:
            return "Short"
        elif line_count < 10:
            return "Medium"
        else:
            return "Long"

    def get_tags(self):
        return self.unique_tags

    def get_filtered_posts(self, length=None, language=None, tag=None):
        df = self.df.copy()
        if length:
            df = df[df.get("length") == length]
        if language and "language" in df.columns:
            df = df[df["language"] == language]
        if tag:
            df = df[df["tags_list"].apply(lambda tags: tag in tags if isinstance(tags, list) else False)]
        return df



if __name__ == "__main__":
    fs = FewShotPosts()
    posts = fs.get_filtered_posts("Short", "English", "Job Search")
    print(posts)
    print(posts)