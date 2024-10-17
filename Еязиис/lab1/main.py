from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.requests import Request
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser, AndGroup, OrGroup
from sklearn.metrics import precision_score, recall_score, f1_score
import os
from update import update


update()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/downloaded_files", StaticFiles(directory="downloaded_files"), name="downloaded_files")
templates = Jinja2Templates(directory="templates")


def create_search_index(documents):
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True))
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = create_in("indexdir", schema)
    with ix.writer() as writer:
        for path, content in documents.items():
            writer.add_document(title=path.split('.')[0], path=path, content=content)
    return ix


def search_in_index(query_str, ix, logic_operator="AND"):
    results_list = []
    group = AndGroup if logic_operator == "AND" else OrGroup
    with ix.searcher() as searcher:
        parser = MultifieldParser(["title", "content"], schema=ix.schema, group=group)
        query = parser.parse(query_str)
        results = searcher.search(query)
        for result in results:
            highlighted_content = result.highlights('content')
            results_list.append({
                'title': result['title'],
                'path': result['path'],
                'highlighted': highlighted_content
            })
    return results_list


def evaluate_search_results(true_labels, predicted_labels):
    precision = precision_score(true_labels, predicted_labels, average='binary', zero_division=1)
    recall = recall_score(true_labels, predicted_labels, average='binary')
    f1 = f1_score(true_labels, predicted_labels, average='binary')

    a = sum(1 for t, p in zip(true_labels, predicted_labels) if t == p == 1)
    b = sum(1 for t, p in zip(true_labels, predicted_labels) if p == 1 and t == 0)
    c = sum(1 for t, p in zip(true_labels, predicted_labels) if t == 1 and p == 0)
    d = sum(1 for t, p in zip(true_labels, predicted_labels) if t == p == 0)

    accuracy = (a + d) / (a + b + c + d)
    error = (b + c) / (a + b + c + d)

    return precision, recall, f1, accuracy, error


@app.get("/", response_class=HTMLResponse)
async def get_search_page(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.post("/search", response_class=HTMLResponse)
async def search_documents(request: Request, query: str = Form(...), logic_op: str = Form(...)):

    with open('paths.txt', 'r') as f:
        files = [i.strip() for i in f.readlines()]

    documents = {}
    for i in files:
        with open(i, 'r') as f:
            data = f.readlines()
        documents[i] = data[0]

    ix = create_search_index(documents)

    search_results = search_in_index(query, ix, logic_operator=logic_op)

    true_results = files
    predicted_labels = [1 if f"{doc.split('.')[0]}" in [res['title'] for res in search_results] else 0 for doc in
                        true_results]
    true_labels = [1 for _ in true_results]

    precision, recall, f1, accuracy, error = evaluate_search_results(true_labels, predicted_labels)

    return templates.TemplateResponse("search.html", {
        "request": request,
        "results": search_results,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
        "error": error,
    })
