# Serveur de Génération de Licences ABCD

Ce serveur permet de générer des licences sécurisées pour les modules Odoo personnalisés ABCD.

## Installation

```bash
pip install -r requirements.txt
```

## Génération des clés

```bash
python generate_keys.py --output-dir ./keys
```

Cela génère :
- `private_key.pem` : Clé privée (NE JAMAIS PARTAGER)
- `public_key.pem` : Clé publique (PEM format)
- `public_key_raw.txt` : Clé publique (hex, pour Odoo)

## Génération d'une licence

### Via fichier de configuration

1. Créer un fichier `config.json` :

```json
{
  "issuer": "ABCD",
  "company": "Client Example SARL",
  "db_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "modules": ["abcd_sales_pro", "abcd_inventory_plus"],
  "edition": "pro",
  "expiry": "2026-12-31T23:59:59Z",
  "max_users": 50,
  "alias": "ABCD-LIC-CLIENTX-2025"
}
```

2. Générer la licence :

```bash
python generate_license.py --config config.json --output license.txt
```

### Via API REST

```bash
# Démarrer le serveur
python api_server.py --port 8080

# Générer une licence
curl -X POST http://localhost:8080/api/v1/license/generate \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Client Example",
    "db_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "modules": ["abcd_sales_pro"],
    "edition": "pro",
    "expiry": "2026-12-31T23:59:59Z",
    "max_users": 50,
    "alias": "ABCD-LIC-CLIENTX-2025"
  }'
```

## Format de la licence

La licence est au format : `BASE64(JSON_PAYLOAD.SIGNATURE)`

- **JSON_PAYLOAD** : JSON canonique (sans espaces, clés triées)
- **SIGNATURE** : Signature Ed25519 du payload
- **BASE64** : Encodage base64 de l'ensemble

## Sécurité

- La clé privée ne doit JAMAIS quitter le serveur
- Stocker la clé privée avec des permissions restrictives (600)
- Utiliser HTTPS en production
- Authentifier les requêtes API si exposée publiquement
