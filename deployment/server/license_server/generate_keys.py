#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de génération de clés Ed25519 pour le système de licence ABCD
Usage: python generate_keys.py [--output-dir OUTPUT_DIR]
"""

import argparse
import os
import sys
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization


def generate_keypair(output_dir: Path = None) -> tuple:
    """
    Génère une paire de clés Ed25519
    
    Returns:
        tuple: (private_key, public_key) en bytes
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    return private_key, public_key


def save_keys(private_key, public_key, output_dir: Path):
    """
    Sauvegarde les clés dans des fichiers séparés
    
    Args:
        private_key: Clé privée Ed25519
        public_key: Clé publique Ed25519
        output_dir: Répertoire de sortie
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Sauvegarder la clé privée (PEM)
    private_path = output_dir / "private_key.pem"
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_path.write_bytes(private_pem)
    os.chmod(private_path, 0o600)  # Lecture/écriture uniquement pour le propriétaire
    
    # Sauvegarder la clé publique (PEM)
    public_path = output_dir / "public_key.pem"
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_path.write_bytes(public_pem)
    os.chmod(public_path, 0o644)
    
    # Sauvegarder la clé publique en format raw (pour Odoo)
    public_raw_path = output_dir / "public_key_raw.txt"
    public_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    public_raw_path.write_text(public_raw.hex())
    
    print(f"[OK] Cles generees avec succes dans {output_dir}")
    print(f"  - Cle privee: {private_path} (mode 600)")
    print(f"  - Cle publique (PEM): {public_path}")
    print(f"  - Cle publique (raw hex): {public_raw_path}")
    print("\n[ATTENTION] IMPORTANT: La cle privee ne doit JAMAIS etre partagee ou stockee cote client!")


def main():
    parser = argparse.ArgumentParser(
        description="Génère une paire de clés Ed25519 pour le système de licence ABCD"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./keys",
        help="Répertoire de sortie pour les clés (défaut: ./keys)"
    )
    
    args = parser.parse_args()
    output_dir = Path(args.output_dir).resolve()
    
    try:
        private_key, public_key = generate_keypair()
        save_keys(private_key, public_key, output_dir)
        return 0
    except Exception as e:
        print(f"[ERREUR] Erreur lors de la generation des cles: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
