# Information Retrieval System

Sistem pencarian dan pemeringkatan dokumen berbasis Command-Line Interface (CLI) menggunakan Python untuk UTS Praktikum Information Retrieval.

## Fitur Utama Sesuai Spesifikasi Teknis
1. **Bahasa Pemrograman**: Dibangun murni menggunakan Python.
2. **Antarmuka CLI Interaktif**:
   ```text
   === INFORMATION RETRIEVAL SYSTEM ===
   [1] Load & Index Dataset
   [2] Search Query
   [3] Exit
   ====================================
   ```
3. **Indexing & Searching Whoosh**: Menggunakan pustaka Whoosh Reloaded untuk membangun inverted index dan temu kembali dokumen kandidat.
4. **Vektorisasi & Perangkingan**: Menggunakan **CountVectorizer** dan **Cosine Similarity** (Scikit-learn) untuk menghitung bobot kemiripan dokumen terhadap query.
5. **Text Preprocessing**:
   - Case folding
   - Tokenization
   - Stopword removal
   - Stemming Bahasa Indonesia (Sastrawi) dengan optimasi *memoization cache*
6. **Top-5 Hasil Pencarian**: Menampilkan tepat 5 dokumen teratas dengan skor kemiripan tertinggi.

## Struktur Dataset
Seluruh kelima dataset digabungkan dalam satu folder `datasets/` dengan subfolder masing-masing:
```text
UTS Praktikum PI/
├── datasets/
│   ├── etd-usk/
│   │   └── etd_usk.csv
│   ├── etd-ugm/
│   │   └── etd_ugm.csv
│   ├── kompas/
│   │   └── kompas.csv
│   ├── tempo/
│   │   └── tempo.csv
│   └── mojok/
│       └── mojok.csv
├── indexdir/
├── main.py
├── preprocessing.py
├── indexing.py
├── search_engine.py
├── requirements.txt
└── README.md
```

Setiap file dataset bertipe CSV dengan kolom:
- `judul`: Judul artikel berita atau tugas akhir mahasiswa
- `konten`: Isi lengkap artikel atau abstrak tugas akhir

## Instalasi dan Penggunaan

1. Buat virtual environment (opsional):
   ```bash
   python -m venv venv
   ```

2. Aktifkan virtual environment di Windows:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Instal dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan program:
   ```bash
   python main.py
   ```

5. **Menu CLI:**
   - **[1] Load & Index Dataset**: Membangun indeks dari folder `datasets/` (bisa memilih semua dataset atau salah satu subfolder).
   - **[2] Search Query**: Memasukkan query pencarian dan menampilkan 5 hasil teratas berperingkat Cosine Similarity tertinggi.
   - **[3] Exit**: Keluar dari aplikasi.

## Tim Pengembang
- Anggota 1: [Ariq Rabbani - 2408107010111]
- Anggota 2: [Muhammad Faruq Rais - 2408107010108]
- Anggota 3: [T Muhammad Alfi - 2408107010112]

**Proyek UTS Praktikum Information Retrieval**