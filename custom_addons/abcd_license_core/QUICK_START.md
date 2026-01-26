# Quick Start - Système de Licence ABCD

## Pour l'Éditeur (ABCD)

### 1. Générer les clés

```bash
cd deployment/server/license_server
python generate_keys.py --output-dir ./keys
```

Cela crée :
- `keys/private_key.pem` (⚠️ NE JAMAIS PARTAGER)
- `keys/public_key.pem`
- `keys/public_key_raw.txt` (clé publique en hex pour Odoo)

### 2. Configurer la clé publique dans le module

1. Ouvrir `custom_addons/abcd_license_core/models/abcd_license.py`
2. Remplacer la ligne 46-48 avec la vraie clé publique (depuis `public_key_raw.txt`)

```python
PUBLIC_KEY_HEX = "a1b2c3d4e5f6..."  # 64 caractères hex
```

### 3. Générer une licence

Créer un fichier `config.json` :

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

Générer la licence :

```bash
python generate_license.py --config config.json --output license_clientx.txt
```

### 4. Livrer au client

- Le blob de licence (contenu de `license_clientx.txt`)
- La clé publique hex (depuis `public_key_raw.txt`)

## Pour le Client

### 1. Installer le module

```bash
# Dans Odoo, Apps > Update Apps List
# Puis installer "ABCD License Core"
```

### 2. Configurer la clé publique

1. Paramètres > Technique > Paramètres > Paramètres système
2. Rechercher `abcd.license.public_key_hex`
3. Coller la clé publique (64 caractères hex)

### 3. Configurer la licence

1. Paramètres > Technique > Paramètres > Paramètres système
2. Rechercher `abcd.license.blob`
3. Coller le blob de licence complet

### 4. Installer les modules ABCD

Les modules ABCD peuvent maintenant être installés normalement.

## Pour les Développeurs de Modules ABCD

### Intégration basique

```python
from odoo import models, api
from odoo.exceptions import UserError

class MonModel(models.Model):
    _name = 'mon.model'
    
    @api.model
    def create(self, vals):
        self.env['abcd.license'].check_license('mon_module_abcd')
        return super().create(vals)
    
    def write(self, vals):
        self.env['abcd.license'].check_license('mon_module_abcd')
        return super().write(vals)
```

### Dans le manifest

```python
{
    'name': "Mon Module ABCD",
    'category': 'ABCD',  # ⚠️ IMPORTANT
    'depends': ['base', 'abcd_license_core'],
    # ...
}
```

## Vérification Rapide

### Test manuel dans Odoo

```python
# Console Python (Paramètres > Technique > Actions serveur)
env['abcd.license'].check_license('abcd_sales_pro')
```

### Vérifier les informations de licence

```python
info = env['abcd.license'].get_license_info()
print(info)
```

## Dépannage Rapide

| Problème | Solution |
|----------|----------|
| "Aucune licence configurée" | Vérifier `abcd.license.blob` dans paramètres système |
| "Signature invalide" | Vérifier que la clé publique correspond à la clé privée |
| "UUID base non valide" | Générer une nouvelle licence avec le bon UUID |
| "Module non autorisé" | Ajouter le module à la liste dans la licence |
| Module ne s'installe pas | Vérifier que la licence est valide et contient le module |

## Documentation Complète

- `ARCHITECTURE_LICENCE_ABCD.md` : Architecture détaillée
- `GUIDE_INSTALLATION.md` : Guide d'installation complet
- `CHECKLIST_SECURITE.md` : Checklist sécurité
- `abcd_license_core/README.md` : Documentation technique
- `abcd_license_core/INTEGRATION_GUIDE.md` : Guide d'intégration
