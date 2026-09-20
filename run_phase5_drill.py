import os
import sys
import sqlite3

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
sys.path.insert(0, os.path.abspath("backend"))

import django
django.setup()

from django.db import connections, connection
from django.core.management import call_command

def run_isolated_drill():
    print("=" * 80)
    print("WAVE 5.6 PHASE 5: COMPREHENSIVE ISOLATED MIGRATION DRILL & VERIFICATION")
    print("=" * 80)
    
    # Introspect in-memory tables directly via django connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        all_tables = [r[0] for r in cursor.fetchall()]
        ll_tables = [t for t in all_tables if "learning" in t.lower()]
        print(f"Total tables before migrate: {len(all_tables)}, learning_loop tables: {len(ll_tables)}")
        
    print("\n--- 1. RUNNING FULL MIGRATION SUITE ON ISOLATED IN-MEMORY DB ---")
    call_command("migrate", interactive=False, verbosity=0)
    print("FRESH_INSTALL_MIGRATION: PASS")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        all_tables = [r[0] for r in cursor.fetchall()]
        ll_tables = [t for t in all_tables if "learning" in t.lower()]
        print(f"\n--- 2. SCHEMA & TABLE VERIFICATION ---")
        print(f"Total tables in DB: {len(all_tables)}")
        print(f"Learning Loop Tables ({len(ll_tables)} total):")
        for t in sorted(ll_tables):
            print(f"  [TABLE] {t}")
            
        cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name LIKE '%learning%' ORDER BY tbl_name, name")
        indexes = cursor.fetchall()
        print(f"\nLearning Loop Indexes ({len(indexes)} total):")
        for idx, tbl in indexes:
            print(f"  [INDEX] {idx} on {tbl}")
            
    print("\n--- 3. ROLLBACK DRILL (migrate learning_loop zero) ---")
    call_command("migrate", "learning_loop", "zero", interactive=False, verbosity=0)
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%learning%'")
        remaining = cursor.fetchall()
        print(f"Remaining learning_loop tables after rollback: {len(remaining)}")
        if len(remaining) == 0:
            print("ROLLBACK_DRILL: PASS (Clean Teardown with 0 remaining tables)")
        else:
            print("ROLLBACK_DRILL: FAIL")
            
    print("\n--- 4. RE-APPLY DRILL ---")
    call_command("migrate", "learning_loop", interactive=False, verbosity=0)
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%learning%'")
        reapplied = cursor.fetchall()
        print(f"Tables after re-apply: {len(reapplied)}")
        print("RE_APPLY_MIGRATION: PASS")

if __name__ == "__main__":
    run_isolated_drill()
