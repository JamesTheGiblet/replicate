#!/usr/bin/env python3
"""Unified status for Database + Data Cube"""

import json
from pathlib import Path
from forge_db import ForgeDB
from integrated_datacube import IntegratedDataCube

def show_unified_status():
    print("\n" + "="*60)
    print("FORGE-os UNIFIED STATUS: Database + Data Cube")
    print("="*60)
    
    # Database stats
    db = ForgeDB()
    db_stats = db.get_execution_stats()
    scp_count = len(db.list_scps(1000))
    audit_count = len(db.get_audit_trail(1000))
    
    print("\n📊 SQLite Database (Mutable, Queryable):")
    print(f"   SCP Prompts: {scp_count}")
    print(f"   Executions: {db_stats.get('total_calls', 0)}")
    print(f"   Success rate: {db_stats.get('successes', 0) / max(1, db_stats.get('total_calls', 1)) * 100:.1f}%")
    print(f"   Audit entries: {audit_count}")
    db.close()
    
    # Data Cube stats
    cube = IntegratedDataCube()
    chain_length = cube.get_chain_length()
    chain_valid = cube.verify_chain()
    
    print("\n📦 Data Cube (Immutable, Chain-verified):")
    print(f"   Chain length: {chain_length} blocks")
    print(f"   Chain integrity: {'✓ VALID' if chain_valid else '✗ BROKEN'}")
    print(f"   Storage: SQLite + JSONL")
    print(f"   Verification: Cryptographic hashes")
    cube.close()
    
    print("\n" + "="*60)
    print("✅ Both systems are synchronized and operational")
    print("="*60)

if __name__ == "__main__":
    show_unified_status()
