#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de génération de licences ABCD
Usage: python generate_license.py --config config.json --output license.txt
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64


class LicenseGenerator:
    """Générateur de licences ABCD"""
    
    def __init__(self, private_key_path: Path):
        """
        Initialise le générateur avec la clé privée
        
        Args:
            private_key_path: Chemin vers la clé privée PEM
        """
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )
    
    def create_payload(
        self,
        issuer: str,
        company: str,
        db_uuid: str,
        modules: List[str],
        edition: str,
        expiry: str,
        max_users: int,
        alias: str = None
    ) -> Dict[str, Any]:
        """
        Crée le payload JSON canonique de la licence
        
        Args:
            issuer: Identifiant de l'éditeur (ex: "ABCD")
            company: Nom du client
            db_uuid: UUID de la base de données Odoo
            modules: Liste des modules autorisés
            edition: Edition (standard/pro/enterprise)
            expiry: Date d'expiration (ISO 8601)
            max_users: Nombre maximum d'utilisateurs
            alias: Alias lisible de la licence (optionnel)
        
        Returns:
            dict: Payload de la licence
        """
        # Normaliser les modules (tri alphabétique pour canonique)
        modules_sorted = sorted(modules)
        
        payload = {
            "issuer": issuer,
            "company": company,
            "db_uuid": db_uuid,
            "modules": modules_sorted,
            "edition": edition,
            "expiry": expiry,
            "max_users": max_users,
            "issued_at": datetime.now(timezone.utc).isoformat()
        }
        
        if alias:
            payload["alias"] = alias
        
        return payload
    
    def sign_payload(self, payload: Dict[str, Any]) -> bytes:
        """
        Signe le payload avec la clé privée
        
        Args:
            payload: Payload JSON à signer
        
        Returns:
            bytes: Signature Ed25519
        """
        # JSON canonique (sans espaces, trié)
        json_str = json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        
        # Signature
        signature = self.private_key.sign(json_bytes)
        return signature
    
    def generate_license_blob(self, payload: Dict[str, Any]) -> str:
        """
        Génère le blob de licence au format BASE64(JSON.SIGNATURE)
        
        Args:
            payload: Payload de la licence
        
        Returns:
            str: Blob de licence encodé en base64
        """
        # Créer le JSON canonique
        json_str = json.dumps(payload, separators=(',', ':'), sort_keys=True, ensure_ascii=False)
        json_bytes = json_str.encode('utf-8')
        
        # Signer
        signature = self.sign_payload(payload)
        
        # Assembler: JSON + '.' + SIGNATURE
        license_data = json_bytes + b'.' + signature
        
        # Encoder en base64
        license_blob = base64.b64encode(license_data).decode('ascii')
        
        return license_blob
    
    def generate(self, config: Dict[str, Any]) -> str:
        """
        Génère une licence complète depuis une configuration
        
        Args:
            config: Dictionnaire de configuration
        
        Returns:
            str: Blob de licence
        """
        payload = self.create_payload(
            issuer=config.get('issuer', 'ABCD'),
            company=config['company'],
            db_uuid=config['db_uuid'],
            modules=config['modules'],
            edition=config.get('edition', 'standard'),
            expiry=config['expiry'],
            max_users=config.get('max_users', 0),
            alias=config.get('alias')
        )
        
        return self.generate_license_blob(payload)


def load_config(config_path: Path) -> Dict[str, Any]:
    """Charge la configuration depuis un fichier JSON"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Génère une licence ABCD depuis un fichier de configuration"
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        help="Fichier JSON de configuration"
    )
    parser.add_argument(
        "--private-key",
        type=str,
        default="./keys/private_key.pem",
        help="Chemin vers la clé privée (défaut: ./keys/private_key.pem)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Fichier de sortie pour la licence (optionnel, affiche sur stdout si absent)"
    )
    
    args = parser.parse_args()
    
    try:
        config_path = Path(args.config)
        private_key_path = Path(args.private_key)
        
        if not config_path.exists():
            print(f"❌ Fichier de configuration introuvable: {config_path}", file=sys.stderr)
            return 1
        
        if not private_key_path.exists():
            print(f"❌ Clé privée introuvable: {private_key_path}", file=sys.stderr)
            return 1
        
        # Charger la configuration
        config = load_config(config_path)
        
        # Générer la licence
        generator = LicenseGenerator(private_key_path)
        license_blob = generator.generate(config)
        
        # Sauvegarder ou afficher
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(license_blob, encoding='utf-8')
            print(f"✓ Licence générée: {output_path}")
        else:
            print(license_blob)
        
        return 0
        
    except KeyError as e:
        print(f"❌ Champ manquant dans la configuration: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
