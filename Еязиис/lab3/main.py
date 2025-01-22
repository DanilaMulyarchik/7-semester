#v14
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import os
from PyPDF2 import PdfReader

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

stop_words = set(stopwords.words('russian') + stopwords.words('italian'))
coll = 5


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text


def compute_tfidf_weights(text):
    vectorizer = TfidfVectorizer(stop_words=list(stop_words))
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    weights = {feature_names[i]: tfidf_matrix[0, i] for i in range(len(feature_names))}
    return weights


def compute_sentence_weights(text, tfidf_weights):
    sentences = sent_tokenize(text)
    sentence_weights = {}
    doc_length = sum(len(sent) for sent in sentences)
    for i, sentence in enumerate(sentences):
        sentence_tokens = word_tokenize(sentence)
        filtered_tokens = [token for token in sentence_tokens if token.lower() not in stop_words]
        tfidf_sum = sum(tfidf_weights.get(word.lower(), 0) for word in filtered_tokens)

        position_factor = (doc_length - sum(len(sentences[j]) for j in range(i))) / doc_length
        weight = tfidf_sum * position_factor
        sentence_weights[sentence] = weight
    return sentence_weights


def generate_classic_abstract(text):
    tfidf_weights = compute_tfidf_weights(text)
    sentence_weights = compute_sentence_weights(text, tfidf_weights)
    selected_sentences = sorted(sentence_weights, key=sentence_weights.get, reverse=True)[:coll]
    sentences = sent_tokenize(text)
    ordered_selected_sentences = [sentence for sentence in sentences if sentence in selected_sentences]
    return " ".join(ordered_selected_sentences)


def extract_keywords_and_phrases(text, max_ngram=3):
    words = word_tokenize(text)
    filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]

    phrases = []
    for n in range(2, max_ngram + 1):
        phrases.extend([" ".join(gram) for gram in ngrams(filtered_words, n)])

    word_freq = defaultdict(int)
    phrase_freq = defaultdict(int)

    for word in filtered_words:
        word_freq[word] += 1
    for phrase in phrases:
        phrase_freq[phrase] += 1

    return word_freq, phrase_freq


def build_hierarchy(word_freq, phrase_freq):
    hierarchy = defaultdict(list)

    for phrase, freq in phrase_freq.items():
        words_in_phrase = phrase.split()
        for word in words_in_phrase:
            if word in word_freq:
                hierarchy[word].append((phrase, freq))
                break

    return hierarchy


def format_hierarchy(hierarchy):
    result = ""
    for root, children in hierarchy.items():
        result += f"{root}\n"
        for phrase, freq in sorted(children, key=lambda x: x[1], reverse=True):
            result += f"  - {phrase} (частота: {freq})\n"
    return result


def generate_keywords_abstract(text):
    word_freq, phrase_freq = extract_keywords_and_phrases(text)
    hierarchy = build_hierarchy(word_freq, phrase_freq)
    return hierarchy


def api_metod(text):
    parser = PlaintextParser.from_string(text, Tokenizer("russian"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, coll)
    result = ''
    for sentence in summary:
        result += str(sentence)
    return result


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process/")
async def process_file(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text_from_pdf(file_path)

    classic_abstract = generate_classic_abstract(text)
    keywords_abstract = generate_keywords_abstract(text)
    api_abstract = api_metod(text)
    results = {
        "original_file": file.filename,
        "classic_abstract": classic_abstract,
        "keywords_abstract": keywords_abstract,
        "api_abstract": api_abstract,
    }

    return templates.TemplateResponse("index.html", {"request": {}, "results": results})
