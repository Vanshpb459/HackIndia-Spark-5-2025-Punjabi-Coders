import os
import time
import joblib
import nltk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sklearn.feature_extraction.text import TfidfVectorizer


# Simple Hate Speech Detector
class HateSpeechDetector:
    def __init__(self):
        self.model = joblib.load('hate_speech_model.pkl')
        self.vectorizer = joblib.load('tfidf_vectorizer.pkl')
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)

    def clean_text(self, text):
        text = text.lower()
        tokens = nltk.word_tokenize(text)
        tokens = [word for word in tokens if word not in nltk.corpus.stopwords.words('english')]
        return ' '.join(tokens)

    def is_hate(self, comment):
        cleaned = self.clean_text(comment)
        vec = self.vectorizer.transform([cleaned])
        prob = self.model.predict_proba(vec)[0, 1]
        return prob > 0.35  # Returns True if hate, False if not


# Real-Time File Watcher
class CommentWatcher(FileSystemEventHandler):
    def __init__(self):
        self.detector = HateSpeechDetector()
        self.last_size = 0

    def on_modified(self, event):
        if event.src_path.endswith("comments.txt"):
            self.check_comments()

    def check_comments(self):
        try:
            current_size = os.path.getsize("comments.txt")
            if current_size == self.last_size:
                return
            self.last_size = current_size

            with open("comments.txt") as f:
                comments = [line.strip() for line in f if line.strip()]

            print("\n--- Current Predictions ---")
            for comment in comments:
                if self.detector.is_hate(comment):
                    print(f"HATE: {comment[:70]}{'...' if len(comment) > 70 else ''}")
                else:
                    print(f"CLEAN: {comment[:70]}{'...' if len(comment) > 70 else ''}")
            print("\nEditing comments.txt... (Ctrl+C to quit)")

        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("Hate Speech Detector - Watching comments.txt")
    print("Edit and save the file to see predictions\n")

    watcher = CommentWatcher()
    watcher.check_comments()  # Initial check

    observer = Observer()
    observer.schedule(watcher, path=".")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
