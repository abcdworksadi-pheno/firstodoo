# ABCD License Core - Documentation Technique

## Vue d'ensemble

`abcd_license_core` est le module central de vérification de licences pour tous les modules personnalisés ABCD. Il fournit une API sécurisée et non-bloquante pour vérifier la validité des licences.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVEUR LICENCE ABCD                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Génération de clés Ed25519                           │  │
│  │  - private_key.pem (NE JAMAIS PARTAGER)              │  │
│  │  - public_key.pem                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Génération de licence                                │  │
│  │  Format: BASE64(JSON_PAYLOAD.SIGNATURE)              │  │
│  │  - Payload: issuer, company, db_uuid, modules, etc.   │  │
│  │  - Signature: Ed25519 du JSON canonique               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API REST (optionnelle)                               │  │
│  │  POST /api/v1/license/generate                        │  │
│  │  POST /api/v1/license/verify                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ (licence blob)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    INSTALLATION ODOO                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Module: abcd_license_core                            │  │
│  │  - Stockage: ir.config_parameter                      │  │
│  │    * abcd.license.blob                                │  │
│  │    * abcd.license.public_key_hex                      │  │
│  │    * abcd.license.grace_period_days                   │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Vérification de licence                              │  │
│  │  - Cache mémoire: 10 minutes (LRU)                   │  │
│  │  - Cache base: 24 heures                              │  │
│  │  - Vérifications:                                     │  │
│  │    * Signature Ed25519                                │  │
│  │    * UUID base de données                             │  │
│  │    * Expiration                                       │  │
│  │    * Modules autorisés                                │  │
│  │    * Quota utilisateurs                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Vérification Online (optionnelle)                  │  │
│  │  - Cron toutes les 24h                               │  │
│  │  - Timeout 3s                                        │  │
│  │  - Fallback offline si erreur                        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API: check_license(module_name)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MODULES ABCD (ex: abcd_sales_pro)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Intégration dans:                                    │  │
│  │  - create() / write()                                 │  │
│  │  - Actions métier                                     │  │
│  │  - Installation (bloquée si licence invalide)         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### 1. Installation du module

```bash
# Copier le module dans custom_addons
cp -r abcd_license_core /path/to/odoo/custom_addons/

# Installer les dépendances Python
pip install -r abcd_license_core/requirements.txt

# Mettre à jour la liste des modules dans Odoo
# Interface: Apps > Update Apps List

# Installer le module
# Interface: Apps > Rechercher "ABCD License Core" > Install
```

### 2. Configuration de la clé publique

1. Générer les clés sur le serveur de licence (voir `deployment/server/license_server/`)
2. Récupérer la clé publique en hex (fichier `public_key_raw.txt`)
3. Dans Odoo : Paramètres > Technique > Paramètres > Paramètres système
   - Chercher `abcd.license.public_key_hex`
   - Coller la clé publique (64 caractères hex)

### 3. Configuration de la licence

1. Générer une licence sur le serveur de licence
2. Dans Odoo : Paramètres > Technique > Paramètres > Paramètres système
   - Chercher `abcd.license.blob`
   - Coller le blob de licence complet

### 4. Configuration optionnelle

- **Période de grâce** : `abcd.license.grace_period_days` (défaut: 7)
- **Serveur de licence** : `abcd.license.server_url` (pour vérification online)
- **Activer le cron online** : Apps > Scheduled Actions > "ABCD License: Vérification Online" > Activer

## Utilisation dans les modules ABCD

### Exemple basique

```python
from odoo import models, api
from odoo.exceptions import UserError

class MyModel(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        # Vérifier la licence
        self.env['abcd.license'].check_license('mon_module_abcd')
        
        return super().create(vals)
```

### Gestion des erreurs

```python
def action_metier(self):
    try:
        self.env['abcd.license'].check_license('mon_module_abcd')
    except UserError as e:
        # Message utilisateur-friendly déjà formaté
        raise UserError(str(e))
    
    # Logique métier...
```

### Blocage installation

Le module `abcd_license_core` bloque automatiquement l'installation de modules ABCD si la licence est invalide. Aucune action supplémentaire requise.

## Format de la licence

### Structure du payload JSON

```json
{
  "issuer": "ABCD",
  "company": "Client Example SARL",
  "db_uuid": "550e8400-e29b-41d4-a716-446655440000",
  "modules": ["abcd_sales_pro", "abcd_inventory_plus"],
  "edition": "pro",
  "expiry": "2026-12-31T23:59:59Z",
  "max_users": 50,
  "issued_at": "2025-01-15T10:30:00Z",
  "alias": "ABCD-LIC-CLIENTX-2025"
}
```

### Format du blob

```
BASE64(
  JSON_PAYLOAD_CANONIQUE
  .
  SIGNATURE_ED25519
)
```

- **JSON_PAYLOAD_CANONIQUE** : JSON sans espaces, clés triées
- **SIGNATURE_ED25519** : 64 bytes de signature
- **BASE64** : Encodage base64 de l'ensemble

## Sécurité

### Principes

1. **Aucune clé privée côté client** : Seule la clé publique est stockée dans Odoo
2. **Signature asymétrique** : Ed25519 pour vérification cryptographique
3. **Validation stricte** : UUID base, expiration, modules, quota
4. **Protection contre modification** : Signature invalide si payload modifié

### Bonnes pratiques

- Stocker la clé privée avec permissions restrictives (600)
- Utiliser HTTPS pour l'API REST en production
- Authentifier les requêtes API si exposée publiquement
- Logger les tentatives de licence invalide
- Ne jamais exposer la clé privée

## Performance

- **Cache mémoire** : 10 minutes (LRU, max 128 entrées)
- **Cache base** : 24 heures
- **Vérification online** : Timeout 3s, non-bloquant
- **Fail-open** : En cas d'erreur inattendue, ne pas bloquer Odoo

## Compatibilité

- **Odoo** : 18+ (compatible 19+)
- **Environnements** : On-premise, Odoo.sh
- **Python** : 3.8+
- **Dépendances** : cryptography>=41.0.0, requests>=2.31.0

## Troubleshooting

### Erreur "Aucune licence configurée"

- Vérifier que `abcd.license.blob` est configuré dans les paramètres système

### Erreur "Signature invalide"

- Vérifier que la clé publique correspond à la clé privée utilisée pour générer la licence
- Vérifier que le blob n'a pas été modifié

### Erreur "UUID base non valide"

- La licence est liée à une base de données spécifique
- Générer une nouvelle licence avec le bon UUID

### Module ne s'installe pas

- Vérifier que le module est dans la liste des modules autorisés de la licence
- Vérifier que la licence n'est pas expirée

## Support

Pour toute question ou problème, contacter le support ABCD.
