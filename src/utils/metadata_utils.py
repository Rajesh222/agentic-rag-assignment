import json

def load_metadata(file_path="data/corpus/metadata.json"):
    with open(file_path, "r") as f:
        return json.load(f)

def filter_superseded(documents, metadata):
    # Filter out superseded documents
    current_docs = []
    for doc in documents:
        doc_id = doc.metadata['doc_id']
        if not metadata[doc_id].get('superseded_by'):
            current_docs.append(doc)
    return current_docs