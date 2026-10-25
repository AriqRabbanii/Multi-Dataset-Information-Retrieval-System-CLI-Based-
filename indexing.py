import csv
import glob
import json
import os
import sys

from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.analysis import StandardAnalyzer

from preprocessing import preprocess

PRIMARY_DATASET_DIR = "datasets"
FALLBACK_DATASET_DIR = "dataset"
INDEX_DIR = "indexdir"

# Meningkatkan batas ukuran field CSV agar aman untuk artikel dan dokumen panjang
max_int = sys.maxsize
while True:
    try:
        csv.field_size_limit(max_int)
        break
    except OverflowError:
        max_int = int(max_int / 10)

schema = Schema(
    doc_id=ID(stored=True, unique=True),
    source=STORED,
    title=STORED,
    content=STORED,
    processed=TEXT(
        stored=True,
        analyzer=StandardAnalyzer(stoplist=None)
    )
)


def get_available_datasets():
    """Mendeteksi struktur dataset di folder datasets/ (subfolder per sumber) maupun dataset/."""
    dataset_base = PRIMARY_DATASET_DIR if os.path.exists(PRIMARY_DATASET_DIR) else FALLBACK_DATASET_DIR
    if not os.path.exists(dataset_base):
        return []

    items = []

    # 1. Cek subfolder di dalam folder datasets/ (misal: etd-usk/, etd-ugm/, kompas/, tempo/, mojok/)
    for entry in sorted(os.listdir(dataset_base)):
        entry_path = os.path.join(dataset_base, entry)
        if os.path.isdir(entry_path):
            files = [
                os.path.join(entry_path, f) for f in os.listdir(entry_path)
                if f.endswith(".csv") or f.endswith(".json")
            ]
            if files:
                items.append({
                    "name": entry,
                    "type": "folder",
                    "files": files
                })

    # 2. Cek file langsung di dalam dataset_base jika tidak ada subfolder
    if not items:
        direct_files = sorted(
            glob.glob(os.path.join(dataset_base, "*.csv")) +
            glob.glob(os.path.join(dataset_base, "*.json"))
        )
        for f in direct_files:
            items.append({
                "name": os.path.basename(f),
                "type": "file",
                "files": [f]
            })

    return items


def load_documents_from_file(file_path, source_override=None, max_docs=None):
    """Membaca dokumen dari file CSV atau JSON dengan mengekstrak judul dan konten."""
    filename = os.path.basename(file_path)
    source_name = source_override or os.path.splitext(filename)[0]
    docs = []

    if filename.endswith(".csv"):
        with open(file_path, mode="r", encoding="utf-8-sig", errors="replace", newline="") as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames or []

            # Identifikasi kolom judul dan konten secara otomatis
            title_col = next((c for c in fieldnames if c.strip().lower() in ["judul", "title"]), None)
            content_col = next((c for c in fieldnames if c.strip().lower() in ["konten", "content", "isi", "abstract", "abstrak"]), None)

            # Fallback jika kolom tidak standar
            if not title_col or not content_col:
                if len(fieldnames) >= 2:
                    title_col, content_col = fieldnames[0], fieldnames[1]
                else:
                    return docs

            for idx, row in enumerate(reader, start=1):
                title = (row.get(title_col) or "").strip()
                content = (row.get(content_col) or "").strip()

                if not title and not content:
                    continue

                doc_id = f"{source_name}_{idx}"
                docs.append({
                    "id": doc_id,
                    "source": source_name,
                    "title": title,
                    "content": content
                })

                if max_docs and len(docs) >= max_docs:
                    break

    elif filename.endswith(".json"):
        with open(file_path, mode="r", encoding="utf-8", errors="replace") as file:
            data = json.load(file)
            for idx, item in enumerate(data, start=1):
                docs.append({
                    "id": str(item.get("id", f"{source_name}_{idx}")),
                    "source": source_name,
                    "title": item.get("title", ""),
                    "content": item.get("content", "")
                })
                if max_docs and len(docs) >= max_docs:
                    break

    return docs


def build_index(selected_target=None, max_docs_per_source=None):
    """Membangun indeks Whoosh dari dataset."""
    os.makedirs(INDEX_DIR, exist_ok=True)

    available = get_available_datasets()
    if not available:
        raise FileNotFoundError(
            f"Tidak ditemukan file dataset di folder '{PRIMARY_DATASET_DIR}' atau '{FALLBACK_DATASET_DIR}'."
        )

    targets_to_process = []
    if selected_target and selected_target != "all":
        matched = next((item for item in available if item["name"] == selected_target), None)
        if not matched:
            raise ValueError(f"Dataset '{selected_target}' tidak ditemukan.")
        targets_to_process.append(matched)
    else:
        targets_to_process = available

    print(f"\nMemulai indexing dari {len(targets_to_process)} sumber dataset...")
    ix = create_in(INDEX_DIR, schema)
    writer = ix.writer()

    total_indexed = 0

    for item in targets_to_process:
        source_name = item["name"]
        print(f"\n[+] Memuat dataset: {source_name}")

        source_docs = []
        for fpath in item["files"]:
            loaded = load_documents_from_file(
                fpath,
                source_override=source_name,
                max_docs=max_docs_per_source
            )
            source_docs.extend(loaded)
            if max_docs_per_source and len(source_docs) >= max_docs_per_source:
                source_docs = source_docs[:max_docs_per_source]
                break

        doc_count = len(source_docs)
        print(f"    Ditemukan {doc_count} dokumen. Mulai pemrosesan & indexing Whoosh...")

        for i, doc in enumerate(source_docs, start=1):
            text = (doc["title"] + " " + doc["content"]).strip()
            processed_text = preprocess(text)

            writer.update_document(
                doc_id=str(doc["id"]),
                source=doc["source"],
                title=doc["title"],
                content=doc["content"],
                processed=processed_text
            )
            total_indexed += 1

            if i % 100 == 0 or i == doc_count:
                print(f"    Progress: {i}/{doc_count} dokumen diproses...", end="\r", flush=True)

        print()

    print("\nMenyimpan (commit) indeks ke direktori indexdir...")
    writer.commit()
    print(f"Sukses! Total {total_indexed} dokumen berhasil diindeks.")


def get_index():
    """Membuka indeks Whoosh yang sudah ada."""
    if not os.path.exists(INDEX_DIR) or not exists_in(INDEX_DIR):
        raise RuntimeError(
            "Indeks belum tersedia. Jalankan build_index() dahulu."
        )

    return open_dir(INDEX_DIR)
