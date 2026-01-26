#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour vérifier la génération et la validation de licences
Usage: python test_license.py
"""

import sys
import json
import base64
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from generate_keys import generate_keypair, save_keys
from generate_license import LicenseGenerator


def test_key_generation():
    """Test de génération de clés"""
    print("=" * 60)
    print("TEST 1: Génération de clés Ed25519")
    print("=" * 60)
    
    try:
        private_key, public_key = generate_keypair()
        print("✓ Clés générées avec succès")
        
        # Vérifier que les clés sont valides
        test_message = b"test message"
        signature = private_key.sign(test_message)
        public_key.verify(signature, test_message)
        print("✓ Signature/ vérification fonctionnelle")
        
        return private_key, public_key
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return None, None


def test_license_generation(private_key_path):
    """Test de génération de licence"""
    print("\n" + "=" * 60)
    print("TEST 2: Génération de licence")
    print("=" * 60)
    
    try:
        generator = LicenseGenerator(private_key_path)
        
        # Créer un payload de test
        expiry = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        config = {
            "issuer": "ABCD",
            "company": "Client Test",
            "db_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "modules": ["abcd_sales_pro", "abcd_inventory_plus"],
            "edition": "pro",
            "expiry": expiry,
            "max_users": 50,
            "alias": "ABCD-LIC-TEST-2025"
        }
        
        license_blob = generator.generate(config)
        print(f"✓ Licence générée: {len(license_blob)} caractères")
        print(f"  Alias: {config['alias']}")
        print(f"  Modules: {', '.join(config['modules'])}")
        print(f"  Expiration: {config['expiry']}")
        
        return license_blob, config
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_license_validation(license_blob, public_key):
    """Test de validation de licence"""
    print("\n" + "=" * 60)
    print("TEST 3: Validation de licence")
    print("=" * 60)
    
    try:
        # Décoder le blob
        license_data = base64.b64decode(license_blob.encode('ascii'))
        json_bytes, signature = license_data.split(b'.', 1)
        
        # Parser le JSON
        payload = json.loads(json_bytes.decode('utf-8'))
        print(f"✓ Blob décodé")
        print(f"  Issuer: {payload.get('issuer')}")
        print(f"  Company: {payload.get('company')}")
        print(f"  Modules: {payload.get('modules')}")
        
        # Recréer le JSON canonique
        json_canonical = json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        json_bytes_canonical = json_canonical.encode('utf-8')
        
        # Vérifier la signature
        public_key.verify(signature, json_bytes_canonical)
        print("✓ Signature valide")
        
        # Vérifier l'expiration
        expiry = payload.get('expiry')
        if expiry:
            expiry_dt = datetime.fromisoformat(expiry.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            if expiry_dt > now:
                print(f"✓ Licence valide jusqu'au {expiry_dt.strftime('%Y-%m-%d')}")
            else:
                print(f"✗ Licence expirée depuis le {expiry_dt.strftime('%Y-%m-%d')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Fonction principale de test"""
    print("\n" + "=" * 60)
    print("TESTS DU SYSTÈME DE LICENCE ABCD")
    print("=" * 60 + "\n")
    
    # Test 1: Génération de clés
    private_key, public_key = test_key_generation()
    if not private_key:
        print("\n✗ Les tests ont échoué")
        return 1
    
    # Sauvegarder temporairement les clés pour les tests
    test_keys_dir = Path(__file__).parent / "test_keys"
    test_keys_dir.mkdir(exist_ok=True)
    save_keys(private_key, public_key, test_keys_dir)
    private_key_path = test_keys_dir / "private_key.pem"
    
    # Test 2: Génération de licence
    license_blob, config = test_license_generation(private_key_path)
    if not license_blob:
        print("\n✗ Les tests ont échoué")
        return 1
    
    # Test 3: Validation de licence
    success = test_license_validation(license_blob, public_key)
    
    # Nettoyer
    import shutil
    if test_keys_dir.exists():
        shutil.rmtree(test_keys_dir)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ TOUS LES TESTS RÉUSSIS")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ CERTAINS TESTS ONT ÉCHOUÉ")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
