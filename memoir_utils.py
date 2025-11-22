#!/usr/bin/env python3
"""
memoir_utils.py - Utility script for Memoir+ backup, restore, and export operations

Memoir+ a persona extension for Text Gen Web UI.
MIT License
Copyright (c) 2024 brucepro

Usage:
    python memoir_utils.py backup <character_name>
    python memoir_utils.py restore <character_name> <snapshot_file>
    python memoir_utils.py export <character_name> <output_file.txt>
    python memoir_utils.py list
    python memoir_utils.py stats <character_name>
"""

import sys
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import argparse

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("WARNING: qdrant-client not installed. Install requirements.txt first.")


class MemoirUtils:
    def __init__(self, qdrant_address="http://localhost:6333"):
        """Initialize Memoir utilities"""
        self.qdrant_address = qdrant_address
        self.script_dir = Path(__file__).parent
        self.storage_dir = self.script_dir / "storage" / "sqlite"
        self.backup_dir = self.script_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        if QDRANT_AVAILABLE:
            try:
                self.qdrant = QdrantClient(url=qdrant_address)
            except Exception as e:
                print(f"[!] Could not connect to Qdrant at {qdrant_address}: {e}")
                self.qdrant = None
        else:
            self.qdrant = None

    def list_collections(self):
        """List all Qdrant collections and SQLite databases"""
        print("=" * 80)
        print("MEMOIR+ COLLECTIONS")
        print("=" * 80)

        if self.qdrant:
            try:
                collections = self.qdrant.get_collections()
                print(f"\n[Qdrant Collections] ({len(collections.collections)}):")
                for col in collections.collections:
                    try:
                        info = self.qdrant.get_collection(col.name)
                        points = info.points_count
                        vectors = info.vectors_count if hasattr(info, 'vectors_count') else 'N/A'
                        print(f"  - {col.name}: {points} memories, {vectors} vectors")
                    except:
                        print(f"  - {col.name}")
            except Exception as e:
                print(f"[!] Could not list collections: {e}")
        else:
            print("[!] Qdrant not available")

        # List SQLite databases
        if self.storage_dir.exists():
            db_files = list(self.storage_dir.glob("*_sqlite.db"))
            print(f"\n[SQLite Databases] ({len(db_files)}):")
            for db_file in db_files:
                char_name = db_file.stem.replace("_sqlite", "")
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM short_term_memory")
                    count = cursor.fetchone()[0]
                    conn.close()
                    print(f"  - {char_name}: {count} short-term memories")
                except Exception as e:
                    print(f"  - {char_name}: (error reading)")

    def get_stats(self, character_name):
        """Show detailed stats for a character"""
        print("=" * 80)
        print(f"STATS: {character_name}")
        print("=" * 80)

        # Qdrant stats
        if self.qdrant:
            try:
                # Try main collection
                collection_name = character_name
                try:
                    info = self.qdrant.get_collection(collection_name)
                    print(f"\n[LTM] Long-Term Memories ({collection_name}):")
                    print(f"  Total memories: {info.points_count}")
                    print(f"  Vector size: {info.config.params.vectors.size} dimensions")
                    print(f"  Distance metric: {info.config.params.vectors.distance}")
                    print(f"  Status: {info.status}")
                except:
                    print(f"  No LTM collection found for {character_name}")

                # Try RAG collection
                rag_collection = f"{character_name}_rag_data"
                try:
                    rag_info = self.qdrant.get_collection(rag_collection)
                    print(f"\n[RAG] RAG Data ({rag_collection}):")
                    print(f"  Total documents: {rag_info.points_count}")
                except:
                    print(f"  No RAG collection found")

            except Exception as e:
                print(f"[!] Error accessing Qdrant: {e}")

        # SQLite stats
        db_file = self.storage_dir / f"{character_name.lower()}_sqlite.db"
        if db_file.exists():
            try:
                conn = sqlite3.connect(str(db_file))
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM short_term_memory")
                total = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM short_term_memory WHERE saved_to_longterm=1")
                indexed = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM short_term_memory WHERE saved_to_longterm=0")
                pending = cursor.fetchone()[0]

                print(f"\n[STM] Short-Term Memories:")
                print(f"  Total: {total}")
                print(f"  Indexed to LTM: {indexed}")
                print(f"  Pending indexing: {pending}")

                conn.close()
            except Exception as e:
                print(f"[!] Error reading SQLite: {e}")
        else:
            print(f"\n[!] No SQLite database found at {db_file}")

    def backup_collection(self, character_name):
        """Create backup of character's Qdrant collection and SQLite database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{character_name}_{timestamp}"

        print(f"[BACKUP] Creating backup: {backup_name}")
        print("=" * 80)

        # Backup Qdrant collection
        if self.qdrant:
            try:
                collection_name = character_name
                snapshot = self.qdrant.create_snapshot(collection_name=collection_name)
                print(f"[OK] Qdrant LTM snapshot created: {snapshot}")

                # Try RAG collection too
                try:
                    rag_collection = f"{character_name}_rag_data"
                    rag_snapshot = self.qdrant.create_snapshot(collection_name=rag_collection)
                    print(f"[OK] Qdrant RAG snapshot created: {rag_snapshot}")
                except:
                    print(f"  (No RAG collection to backup)")

                print(f"\n[INFO] Snapshots saved to Qdrant storage directory")
                print(f"   Access via dashboard: {self.qdrant_address}/dashboard")

            except Exception as e:
                print(f"[!] Qdrant backup failed: {e}")

        # Backup SQLite database
        db_file = self.storage_dir / f"{character_name.lower()}_sqlite.db"
        if db_file.exists():
            backup_db = self.backup_dir / f"{backup_name}_sqlite.db"
            try:
                import shutil
                shutil.copy2(db_file, backup_db)
                print(f"[OK] SQLite backup saved: {backup_db}")
            except Exception as e:
                print(f"[!] SQLite backup failed: {e}")

        print("\n[OK] Backup complete!")

    def export_to_text(self, character_name, output_file):
        """Export all memories to a human-readable text file"""
        print(f"[EXPORT] Exporting {character_name} memories to {output_file}")
        print("=" * 80)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"MEMOIR+ EXPORT: {character_name}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            # Export short-term memories
            db_file = self.storage_dir / f"{character_name.lower()}_sqlite.db"
            if db_file.exists():
                try:
                    conn = sqlite3.connect(str(db_file))
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT memory_text, DateTime, people, memory_type, initiated_by, roleplay, saved_to_longterm
                        FROM short_term_memory
                        ORDER BY DateTime DESC
                    """)

                    f.write("SHORT-TERM MEMORIES\n")
                    f.write("-" * 80 + "\n\n")

                    count = 0
                    for row in cursor.fetchall():
                        memory_text, dt, people, mem_type, initiated_by, roleplay, indexed = row
                        status = "indexed" if indexed else "pending"
                        rp = "roleplay" if roleplay else "conversation"

                        f.write(f"[{dt}] {initiated_by} ({rp}, {status})\n")
                        f.write(f"{memory_text}\n")
                        f.write(f"People: {people}\n\n")
                        count += 1

                    conn.close()
                    print(f"[OK] Exported {count} short-term memories")
                    f.write("\n" + "=" * 80 + "\n\n")

                except Exception as e:
                    print(f"[!] Error reading STM: {e}")

            # Export long-term memories (Qdrant)
            if self.qdrant:
                try:
                    collection_name = character_name
                    # Get all points from collection
                    result = self.qdrant.scroll(
                        collection_name=collection_name,
                        limit=10000,  # Max memories to export
                        with_payload=True,
                        with_vectors=False
                    )

                    points = result[0]

                    f.write("LONG-TERM MEMORIES\n")
                    f.write("-" * 80 + "\n\n")

                    for point in points:
                        payload = point.payload
                        comment = payload.get('comment', 'N/A')
                        dt = payload.get('datetime', 'N/A')
                        people = payload.get('people', 'N/A')
                        username = payload.get('username', 'N/A')

                        f.write(f"[{dt}] (ID: {point.id})\n")
                        f.write(f"{comment}\n")
                        f.write(f"People: {people}\n")
                        f.write(f"User: {username}\n\n")

                    print(f"[OK] Exported {len(points)} long-term memories")

                except Exception as e:
                    print(f"[!] Error reading LTM: {e}")

        print(f"\n[OK] Export complete: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Memoir+ Utility - Backup, restore, and export memories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python memoir_utils.py list
  python memoir_utils.py stats AI
  python memoir_utils.py backup AI
  python memoir_utils.py export AI memories_export.txt
        """
    )

    parser.add_argument('command', choices=['list', 'stats', 'backup', 'export'],
                        help='Command to execute')
    parser.add_argument('character_name', nargs='?',
                        help='Character name (required for stats, backup, export)')
    parser.add_argument('output_file', nargs='?',
                        help='Output file for export command')
    parser.add_argument('--qdrant', default='http://localhost:6333',
                        help='Qdrant server address (default: http://localhost:6333)')

    args = parser.parse_args()

    utils = MemoirUtils(qdrant_address=args.qdrant)

    if args.command == 'list':
        utils.list_collections()

    elif args.command == 'stats':
        if not args.character_name:
            print("Error: character_name required for stats command")
            sys.exit(1)
        utils.get_stats(args.character_name)

    elif args.command == 'backup':
        if not args.character_name:
            print("Error: character_name required for backup command")
            sys.exit(1)
        utils.backup_collection(args.character_name)

    elif args.command == 'export':
        if not args.character_name or not args.output_file:
            print("Error: character_name and output_file required for export command")
            sys.exit(1)
        utils.export_to_text(args.character_name, args.output_file)


if __name__ == "__main__":
    main()
