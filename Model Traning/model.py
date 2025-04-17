import joblib
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import emoji
import contractions

class HateSpeechModel:
    def __init__(self, model_path='hate_speech_model.pkl', vectorizer_path='tfidf_vectorizer.pkl'):
        """Load trained model and vectorizer"""
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self._init_nltk()

    def _init_nltk(self):
        """Initialize NLP resources"""
        nltk.data.path.append('/Users/vansh./nltk_data')
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')

    def preprocess(self, text):
        """Clean and tokenize text"""
        if not isinstance(text, str):
            return ""
        text = emoji.demojize(text, delimiters=(' ', ' '))
        text = contractions.fix(text)
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
        return ' '.join(tokens)

    def predict(self, comments, threshold=0.35):
        """Predict hate speech with confidence scores"""
        clean_comments = [self.preprocess(c) for c in comments]
        vectors = self.vectorizer.transform(clean_comments)
        probas = self.model.predict_proba(vectors)[:, 1]
        preds = (probas >= threshold).astype(int)
        return list(zip(comments, preds, probas))
