"""
Batch document ingestion script.
Indexes all supported files in a directory.

Usage:
    python scripts/batch_ingest.py --dir ./data/sample_docs --department hr --access_level hr
    python scripts/batch_ingest.py --dir ./data/raw/engineering --department engineering --access_level engineering
"""
import sys
import os
import argparse
import time

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from app.db.session import create_tables, SessionLocal
from app.db.models import Document
from app.rag.pipelines.ingest_pipeline import run_ingest_pipeline, LOADER_MAP
from datetime import datetime, timezone

SUPPORTED_EXTENSIONS = set(LOADER_MAP.keys())


def batch_ingest(directory: str, department: str, access_level: str, document_type: str = "document"):
    print(f"\n[START] Batch ingestion starting")
    print(f"   Directory:    {directory}")
    print(f"   Department:   {department}")
    print(f"   Access level: {access_level}")
    print("-" * 60)

    create_tables()
    db = SessionLocal()
    dir_path = Path(directory)

    if not dir_path.exists():
        print(f"[ERROR] Directory not found: {directory}")
        sys.exit(1)

    files = [f for f in dir_path.rglob("*") if f.suffix.lower() in SUPPORTED_EXTENSIONS and f.is_file()]

    if not files:
        print(f"[WARN] No supported files found in {directory}")
        print(f"   Supported: {', '.join(SUPPORTED_EXTENSIONS)}")
        sys.exit(0)

    print(f"[INFO] Found {len(files)} file(s) to index\n")
    success_count = 0
    fail_count = 0

    for file_path in files:
        print(f"Processing: {file_path.name}")
        start = time.time()

        # Check if already indexed
        existing = db.query(Document).filter(Document.file_name == file_path.name).first()
        if existing and existing.status == "indexed":
            print(f"  [SKIP] Already indexed ({existing.chunk_count} chunks). Skipping.")
            continue

        # Create DB record
        if not existing:
            doc = Document(
                file_name=file_path.name,
                file_type=file_path.suffix.lstrip(".").lower(),
                file_path=str(file_path),
                department=department,
                access_level=access_level,
                status="uploaded",
                file_size_kb=int(file_path.stat().st_size / 1024),
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)
        else:
            doc = existing

        # Ingest
        result = run_ingest_pipeline(
            file_path=str(file_path),
            document_id=doc.id,
            file_name=file_path.name,
            department=department,
            access_level=access_level,
            document_type=document_type,
        )

        elapsed = round(time.time() - start, 1)

        if result["success"]:
            doc.status = "indexed"
            doc.chunk_count = result["chunk_count"]
            doc.indexed_at = datetime.now(timezone.utc)
            db.commit()
            print(f"  [OK]  {result['chunk_count']} chunks | {elapsed}s")
            success_count += 1
        else:
            doc.status = "failed"
            db.commit()
            print(f"  [FAIL] {result['error']}")
            fail_count += 1

    db.close()
    print("\n" + "-" * 60)
    print(f"[DONE] Success: {success_count} | Failed: {fail_count}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch index documents into the RAG system")
    parser.add_argument("--dir", required=True, help="Directory containing documents")
    parser.add_argument("--department", default="public", help="Department (hr/engineering/sales/public)")
    parser.add_argument("--access_level", default="public", help="Access level (public/hr/engineering/sales)")
    parser.add_argument("--type", default="document", help="Document type label")
    args = parser.parse_args()

    batch_ingest(args.dir, args.department, args.access_level, args.type)
