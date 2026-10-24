from indexing import build_index, get_available_datasets
from search_engine import search_documents


def show_menu():
    print("\n=== INFORMATION RETRIEVAL SYSTEM ===")
    print("[1] Load & Index Dataset")
    print("[2] Search Query")
    print("[3] Exit")
    print("====================================")


def handle_indexing():
    datasets = get_available_datasets()
    if not datasets:
        print("Peringatan: Tidak ditemukan dataset di folder 'datasets/' atau 'dataset/'.")
        return

    print("\nPILIHAN DATASET UNTUK DIINDEKS:")
    print("[0] Semua dataset sekaligus (etd-usk, etd-ugm, kompas, tempo, mojok)")
    for idx, item in enumerate(datasets, start=1):
        print(f"[{idx}] {item['name']}")

    ds_choice = input(f"\nPilih opsi dataset [0-{len(datasets)}, default 0]: ").strip()
    selected_target = None
    if ds_choice.isdigit() and 1 <= int(ds_choice) <= len(datasets):
        selected_target = datasets[int(ds_choice) - 1]["name"]

    limit_input = input("Batas dokumen per dataset (tekan Enter untuk semua, atau ketik angka misal 500): ").strip()
    max_docs = int(limit_input) if limit_input.isdigit() and int(limit_input) > 0 else None

    build_index(selected_target=selected_target, max_docs_per_source=max_docs)


def main():
    while True:
        show_menu()
        choice = input("Pilih menu [1-3]: ").strip()

        if choice == "1":
            try:
                handle_indexing()
            except Exception as error:
                print(f"Terjadi kesalahan saat indexing: {error}")

        elif choice == "2":
            query = input("\nMasukkan query pencarian: ").strip()

            if not query:
                print("Query tidak boleh kosong.")
                continue

            try:
                # Mengambil 5 dokumen teratas dengan skor tertinggi sesuai instruksi teknis
                results = search_documents(query, top_n=5)

                if not results:
                    print("Dokumen tidak ditemukan.")
                    continue

                print(f"\nHASIL PENCARIAN (Menampilkan {len(results)} dokumen teratas):")
                print("=" * 60)

                for rank, doc in enumerate(results, start=1):
                    print(f"Peringkat : {rank}")
                    print(f"ID        : {doc['id']}")
                    if doc.get("source") and doc["source"] != "-":
                        print(f"Sumber    : {doc['source']}")
                    print(f"Judul     : {doc['title']}")
                    print(f"Skor      : {doc['score']:.4f} (Cosine Similarity)")
                    clean_content = " ".join(doc["content"].split())
                    print(f"Isi       : {clean_content[:250]}...")
                    print("-" * 60)

            except Exception as error:
                print(f"Terjadi kesalahan: {error}")
                print("Pastikan indeks sudah dibangun terlebih dahulu (Menu 1).")

        elif choice == "3":
            print("Keluar dari sistem. Terima kasih!")
            break

        else:
            print("Pilihan tidak valid. Silakan masukkan 1, 2, atau 3.")


if __name__ == "__main__":
    main()
