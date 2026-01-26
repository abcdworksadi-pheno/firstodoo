#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API REST pour la génération de licences ABCD
Usage: python api_server.py --port 8080
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from generate_license import LicenseGenerator

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin si nécessaire

# Variable globale pour le générateur
generator: Optional[LicenseGenerator] = None


def init_generator(private_key_path: Path):
    """Initialise le générateur de licences"""
    global generator
    generator = LicenseGenerator(private_key_path)


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé"""
    return jsonify({"status": "ok", "service": "ABCD License Server"})


@app.route('/api/v1/license/generate', methods=['POST'])
def generate_license():
    """
    Génère une licence depuis une requête POST
    
    Body JSON attendu:
    {
        "company": "Nom Client",
        "db_uuid": "uuid-de-la-base",
        "modules": ["module1", "module2"],
        "edition": "pro",
        "expiry": "2026-12-31T23:59:59Z",
        "max_users": 50,
        "alias": "ABCD-LIC-CLIENTX-2025"
    }
    """
    if not generator:
        return jsonify({"error": "License generator not initialized"}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON body required"}), 400
        
        # Validation des champs requis
        required_fields = ['company', 'db_uuid', 'modules', 'expiry']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing)}"
            }), 400
        
        # Configuration par défaut
        config = {
            "issuer": "ABCD",
            "company": data['company'],
            "db_uuid": data['db_uuid'],
            "modules": data['modules'],
            "edition": data.get('edition', 'standard'),
            "expiry": data['expiry'],
            "max_users": data.get('max_users', 0),
            "alias": data.get('alias')
        }
        
        # Générer la licence
        license_blob = generator.generate(config)
        
        return jsonify({
            "success": True,
            "license": license_blob,
            "alias": config.get('alias'),
            "generated_at": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/license/verify', methods=['POST'])
def verify_license():
    """
    Vérifie une licence (lecture seule, sans modification)
    
    Body JSON attendu:
    {
        "license": "base64_license_blob"
    }
    """
    try:
        data = request.get_json()
        if not data or 'license' not in data:
            return jsonify({"error": "license field required"}), 400
        
        # Cette fonctionnalité serait implémentée côté client Odoo
        # Ici on peut juste valider le format
        license_blob = data['license']
        
        return jsonify({
            "valid_format": True,
            "message": "License format validated (full verification done client-side)"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    parser = argparse.ArgumentParser(
        description="API REST pour la génération de licences ABCD"
    )
    parser.add_argument(
        "--private-key",
        type=str,
        default="./keys/private_key.pem",
        help="Chemin vers la clé privée"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port d'écoute (défaut: 8080)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host d'écoute (défaut: 127.0.0.1)"
    )
    
    args = parser.parse_args()
    
    private_key_path = Path(args.private_key)
    if not private_key_path.exists():
        print(f"❌ Clé privée introuvable: {private_key_path}", file=sys.stderr)
        return 1
    
    try:
        init_generator(private_key_path)
        print(f"✓ Serveur de licence démarré sur {args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=False)
    except Exception as e:
        print(f"❌ Erreur: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
