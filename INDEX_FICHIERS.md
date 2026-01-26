# Index des Fichiers - Système de Licence ABCD

## 📁 Structure Complète

### Serveur de Génération de Licences

```
deployment/server/license_server/
├── __init__.py                    # Module Python
├── generate_keys.py              # Script génération clés Ed25519
├── generate_license.py            # Script génération licences
├── api_server.py                 # API REST optionnelle
├── test_license.py               # Script de test
├── example_config.json           # Exemple configuration
├── requirements.txt              # Dépendances Python
└── README.md                     # Documentation serveur
```

### Module Odoo Core

```
custom_addons/abcd_license_core/
├── __init__.py
├── __manifest__.py               # Manifest du module
├── requirements.txt               # Dépendances Python
│
├── models/
│   ├── __init__.py
│   ├── abcd_license.py           # Service de vérification principal
│   ├── cron.py                   # Vérification online (cron)
│   └── module.py                 # Blocage installation
│
├── controllers/
│   ├── __init__.py
│   └── license_controller.py     # API REST interne
│
├── data/
│   ├── ir_config_parameter.xml   # Configuration par défaut
│   └── ir_cron.xml               # Cron vérification online
│
├── security/
│   └── ir.model.access.csv       # Droits d'accès
│
├── views/
│   └── license_config_views.xml  # Vues configuration
│
├── README.md                     # Documentation technique
├── INTEGRATION_GUIDE.md          # Guide intégration développeurs
└── QUICK_START.md                # Guide rapide
```

### Module Exemple

```
custom_addons/abcd_sales_pro/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── sale_order.py             # Exemple intégration licence
├── security/
│   └── ir.model.access.csv
├── views/
│   └── sale_order_views.xml
└── README.md                     # Guide exemple
```

### Documentation

```
Racine du projet/
├── ARCHITECTURE_LICENCE_ABCD.md  # Architecture complète
├── CHECKLIST_SECURITE.md         # Checklist sécurité
├── GUIDE_INSTALLATION.md         # Guide installation
├── RESUME_SYSTEME_LICENCE.md     # Résumé système
├── CHANGELOG.md                  # Historique versions
└── INDEX_FICHIERS.md             # Ce fichier
```

## 📋 Fichiers par Fonctionnalité

### Génération de Licences

- `deployment/server/license_server/generate_keys.py` : Génération clés
- `deployment/server/license_server/generate_license.py` : Génération licences
- `deployment/server/license_server/api_server.py` : API REST
- `deployment/server/license_server/test_license.py` : Tests

### Vérification de Licence

- `custom_addons/abcd_license_core/models/abcd_license.py` : Core vérification
- `custom_addons/abcd_license_core/models/cron.py` : Vérification online
- `custom_addons/abcd_license_core/models/module.py` : Blocage installation

### Configuration

- `custom_addons/abcd_license_core/data/ir_config_parameter.xml` : Paramètres
- `custom_addons/abcd_license_core/views/license_config_views.xml` : Vues

### Exemples

- `custom_addons/abcd_sales_pro/models/sale_order.py` : Exemple intégration
- `custom_addons/abcd_sales_pro/README.md` : Guide exemple

## 🔑 Fichiers Clés à Modifier

### Pour l'Éditeur

1. **Clé publique** : `custom_addons/abcd_license_core/models/abcd_license.py` (ligne 46)
   - Remplacer les zéros par la vraie clé publique hex

2. **Génération licences** : `deployment/server/license_server/generate_license.py`
   - Utiliser avec `generate_keys.py` pour créer les licences

### Pour le Client

1. **Configuration clé publique** : Paramètres Odoo > `abcd.license.public_key_hex`
2. **Configuration licence** : Paramètres Odoo > `abcd.license.blob`

## 📚 Documentation par Public

### Pour l'Éditeur (ABCD)

- `deployment/server/license_server/README.md` : Utilisation serveur
- `QUICK_START.md` : Démarrage rapide
- `ARCHITECTURE_LICENCE_ABCD.md` : Architecture détaillée

### Pour le Client

- `GUIDE_INSTALLATION.md` : Installation pas à pas
- `QUICK_START.md` : Démarrage rapide
- `custom_addons/abcd_license_core/README.md` : Documentation technique

### Pour les Développeurs

- `custom_addons/abcd_license_core/INTEGRATION_GUIDE.md` : Guide intégration
- `custom_addons/abcd_sales_pro/README.md` : Exemple code
- `ARCHITECTURE_LICENCE_ABCD.md` : Architecture technique

### Pour la Sécurité

- `CHECKLIST_SECURITE.md` : Checklist complète
- `ARCHITECTURE_LICENCE_ABCD.md` : Section sécurité

## 🧪 Tests

- `deployment/server/license_server/test_license.py` : Tests serveur
- Tests manuels : Voir `GUIDE_INSTALLATION.md`

## 📝 Notes Importantes

### Fichiers à NE JAMAIS Partager

- `deployment/server/license_server/keys/private_key.pem` : Clé privée
- Toute clé privée ou secret

### Fichiers à Partager avec les Clients

- Blob de licence (généré)
- Clé publique hex (depuis `public_key_raw.txt`)

### Fichiers de Configuration

- `custom_addons/abcd_license_core/data/ir_config_parameter.xml` : Valeurs par défaut
- Modifiable via interface Odoo après installation

## 🔄 Workflow Typique

### Génération d'une Licence

1. `generate_keys.py` → Génère clés
2. Configurer clé publique dans `abcd_license.py`
3. `generate_license.py` → Génère licence
4. Livrer blob + clé publique au client

### Installation Client

1. Installer `abcd_license_core`
2. Configurer clé publique (paramètres Odoo)
3. Configurer licence (paramètres Odoo)
4. Installer modules ABCD

### Développement Module ABCD

1. Dépendre de `abcd_license_core`
2. Catégorie `ABCD`
3. Appeler `check_license()` dans create/write/actions
4. Voir `INTEGRATION_GUIDE.md`

## 📞 Support

Pour toute question, consulter la documentation appropriée ou contacter le support ABCD.
