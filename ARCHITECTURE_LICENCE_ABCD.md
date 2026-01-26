# Architecture du Système de Licence ABCD

## Vue d'ensemble

Système de licence professionnel pour modules Odoo personnalisés, fonctionnant en mode **offline-first** avec vérification online optionnelle.

## Diagramme de flux

```
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: GÉNÉRATION                          │
└─────────────────────────────────────────────────────────────────┘

Serveur Licence ABCD
    │
    ├─> Génération clés Ed25519
    │   ├─> private_key.pem (NE JAMAIS PARTAGER)
    │   └─> public_key.pem → public_key_raw.txt (hex)
    │
    ├─> Création licence
    │   ├─> Payload JSON (issuer, company, db_uuid, modules, etc.)
    │   ├─> Signature Ed25519 du JSON canonique
    │   └─> Blob BASE64(JSON.SIGNATURE)
    │
    └─> Livraison au client
        ├─> Blob de licence
        └─> Clé publique (hex)

┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 2: INSTALLATION                         │
└─────────────────────────────────────────────────────────────────┘

Client Odoo
    │
    ├─> Installation module abcd_license_core
    │   ├─> Dépendance: cryptography
    │   └─> Configuration initiale
    │
    ├─> Configuration clé publique
    │   └─> ir.config_parameter: abcd.license.public_key_hex
    │
    └─> Configuration licence
        └─> ir.config_parameter: abcd.license.blob

┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 3: VÉRIFICATION                         │
└─────────────────────────────────────────────────────────────────┘

Module ABCD (ex: abcd_sales_pro)
    │
    └─> Appel: env['abcd.license'].check_license('abcd_sales_pro')
        │
        ├─> Cache mémoire (10 min) ?
        │   └─> OUI → Retour immédiat
        │
        ├─> Cache base (24h) ?
        │   └─> OUI → Validation depuis cache
        │
        └─> Vérification complète
            │
            ├─> Décodage blob BASE64
            │   ├─> JSON payload
            │   └─> Signature
            │
            ├─> Vérification signature Ed25519
            │   └─> Échec → Exception UserError
            │
            ├─> Vérification UUID base
            │   └─> Échec → Exception UserError
            │
            ├─> Vérification expiration
            │   ├─> Expirée → Période de grâce ?
            │   │   ├─> OUI → Warning log, autoriser
            │   │   └─> NON → Exception UserError
            │   └─> Valide → Continuer
            │
            ├─> Vérification module autorisé
            │   └─> Échec → Exception UserError
            │
            ├─> Vérification quota utilisateurs
            │   └─> Échec → Exception UserError
            │
            └─> Mise en cache + Retour True

┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 4: VÉRIFICATION ONLINE (OPTIONNELLE)    │
└─────────────────────────────────────────────────────────────────┘

Cron (toutes les 24h)
    │
    └─> Requête POST /api/v1/license/verify
        │
        ├─> Timeout 3s ?
        │   └─> OUI → Fallback offline, log warning
        │
        ├─> Erreur réseau ?
        │   └─> OUI → Fallback offline, log warning
        │
        └─> Succès
            └─> Mise à jour timestamp dernière vérification
```

## Architecture technique

### Composants serveur

```
deployment/server/license_server/
├── generate_keys.py          # Génération clés Ed25519
├── generate_license.py       # Génération licences
├── api_server.py             # API REST (optionnelle)
├── example_config.json       # Exemple configuration
└── requirements.txt          # Dépendances Python
```

### Composants Odoo

```
custom_addons/
├── abcd_license_core/        # Module central
│   ├── models/
│   │   ├── abcd_license.py   # Service de vérification
│   │   ├── cron.py           # Vérification online
│   │   └── module.py         # Blocage installation
│   ├── controllers/
│   │   └── license_controller.py  # API REST interne
│   ├── data/
│   │   ├── ir_config_parameter.xml
│   │   └── ir_cron.xml
│   └── views/
│       └── license_config_views.xml
│
└── abcd_sales_pro/          # Module exemple
    └── models/
        └── sale_order.py    # Intégration licence
```

## Flux de données

### Génération de licence

```
1. Serveur génère clés Ed25519
   └─> private_key.pem (secret)
   └─> public_key.pem → public_key_raw.txt

2. Serveur crée payload JSON
   {
     "issuer": "ABCD",
     "company": "Client",
     "db_uuid": "uuid-base",
     "modules": ["module1", "module2"],
     "edition": "pro",
     "expiry": "2026-12-31T23:59:59Z",
     "max_users": 50
   }

3. Serveur signe le JSON canonique
   signature = Ed25519.sign(json_canonique)

4. Serveur assemble le blob
   blob = BASE64(json_bytes + '.' + signature)

5. Livraison au client
   └─> blob (à stocker dans Odoo)
   └─> public_key_hex (à stocker dans Odoo)
```

### Vérification de licence

```
1. Module ABCD appelle check_license('module_name')

2. Service récupère blob depuis ir.config_parameter

3. Décodage
   license_data = BASE64.decode(blob)
   json_bytes, signature = license_data.split('.')

4. Vérification signature
   public_key.verify(signature, json_bytes)

5. Validation métier
   - UUID base correspond ?
   - Expiration OK ?
   - Module dans la liste ?
   - Quota utilisateurs OK ?

6. Retour True ou Exception UserError
```

## Sécurité

### Protection cryptographique

- **Ed25519** : Signature asymétrique moderne et rapide
- **JSON canonique** : Format déterministe (sans espaces, clés triées)
- **Base64** : Encodage sûr pour transmission

### Protection applicative

- **UUID base** : Lien fort entre licence et base de données
- **Expiration** : Contrôle temporel avec période de grâce
- **Modules** : Liste blanche stricte
- **Quota** : Limitation nombre d'utilisateurs

### Bonnes pratiques

- Clé privée jamais stockée côté client
- Cache avec expiration pour performance
- Fail-open en cas d'erreur inattendue (ne pas bloquer Odoo)
- Logs non-bloquants pour audit

## Performance

### Optimisations

- **Cache mémoire LRU** : 10 minutes, max 128 entrées
- **Cache base** : 24 heures dans ir.config_parameter
- **Vérification online** : Timeout 3s, non-bloquant
- **Lazy loading** : Clé publique chargée à la demande

### Métriques attendues

- Vérification depuis cache : < 1ms
- Vérification complète : ~10-50ms
- Vérification online : 0-3s (timeout)

## Compatibilité

### Odoo

- **Version** : 18+ (compatible 19+)
- **Environnements** : On-premise, Odoo.sh
- **Modules** : Compatible avec tous les modules Odoo standards

### Python

- **Version** : 3.8+
- **Dépendances** :
  - cryptography>=41.0.0
  - requests>=2.31.0 (optionnel, pour vérification online)

## Évolutivité

### Extensions possibles

- Support multi-licences
- Révocation online
- Statistiques d'utilisation
- Renouvellement automatique
- Support d'autres algorithmes cryptographiques

### Limitations actuelles

- Une seule licence active par base
- Pas de révocation offline
- Pas de statistiques d'utilisation

## Maintenance

### Mise à jour

1. Mettre à jour le module `abcd_license_core`
2. Vérifier la compatibilité des dépendances
3. Tester la vérification de licence
4. Mettre à jour les modules ABCD si nécessaire

### Monitoring

- Logs Odoo : Vérifier les erreurs de licence
- Cache : Surveiller les performances
- Vérification online : Vérifier les timeouts
