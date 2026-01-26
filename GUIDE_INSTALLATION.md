# Guide d'Installation - Système de Licence ABCD

## Prérequis

- Odoo 18+ installé et fonctionnel
- Python 3.8+
- Accès administrateur Odoo
- Clés de licence générées par ABCD

## Étape 1 : Installation du Module Core

### 1.1 Copier le module

```bash
# Copier le module dans le répertoire custom_addons
cp -r abcd_license_core /path/to/odoo/custom_addons/
```

### 1.2 Installer les dépendances Python

```bash
pip install -r custom_addons/abcd_license_core/requirements.txt
```

Dépendances requises :
- `cryptography>=41.0.0`
- `requests>=2.31.0` (optionnel, pour vérification online)

### 1.3 Mettre à jour la liste des modules

1. Se connecter à Odoo en tant qu'administrateur
2. Aller dans **Apps**
3. Cliquer sur **Update Apps List**

### 1.4 Installer le module

1. Dans **Apps**, rechercher "ABCD License Core"
2. Cliquer sur **Install**

## Étape 2 : Configuration de la Clé Publique

### 2.1 Récupérer la clé publique

La clé publique vous a été fournie par ABCD au format hex (64 caractères).

Exemple : `a1b2c3d4e5f6...` (64 caractères hex)

### 2.2 Configurer dans Odoo

1. Aller dans **Paramètres > Technique > Paramètres > Paramètres système**
2. Rechercher `abcd.license.public_key_hex`
3. Cliquer sur **Modifier**
4. Coller la clé publique hex complète (64 caractères)
5. Cliquer sur **Enregistrer**

⚠️ **Important** : La clé doit être exactement 64 caractères hex (0-9, a-f).

## Étape 3 : Configuration de la Licence

### 3.1 Récupérer le blob de licence

Le blob de licence vous a été fourni par ABCD. C'est une chaîne base64 longue.

Exemple : `eyJpc3N1ZXIiOi...` (plusieurs centaines de caractères)

### 3.2 Configurer dans Odoo

1. Dans **Paramètres > Technique > Paramètres > Paramètres système**
2. Rechercher `abcd.license.blob`
3. Cliquer sur **Modifier**
4. Coller le blob de licence complet
5. Cliquer sur **Enregistrer**

⚠️ **Important** : Copier le blob en entier, sans espaces ni retours à la ligne.

## Étape 4 : Vérification de la Configuration

### 4.1 Test manuel

Dans Odoo, ouvrir une console Python (via **Paramètres > Technique > Actions serveur > Code Python**) :

```python
# Tester la vérification de licence
license_service = env['abcd.license']
try:
    license_service.check_license('abcd_sales_pro')  # Remplacer par votre module
    print("✓ Licence valide")
except Exception as e:
    print(f"✗ Erreur: {e}")
```

### 4.2 Vérifier les informations de licence

```python
# Récupérer les informations de licence
license_info = env['abcd.license'].get_license_info()
print(license_info)
```

Vous devriez voir :
- `issuer`: "ABCD"
- `company`: Nom de votre entreprise
- `modules`: Liste des modules autorisés
- `edition`: Edition (standard/pro/enterprise)
- `expiry`: Date d'expiration

## Étape 5 : Configuration Optionnelle

### 5.1 Période de grâce

Par défaut, une période de grâce de 7 jours est appliquée après expiration.

Pour modifier :
1. Paramètres système > `abcd.license.grace_period_days`
2. Modifier la valeur (nombre de jours)

### 5.2 Vérification online (optionnelle)

Si vous souhaitez activer la vérification online :

1. **Configurer l'URL du serveur** :
   - Paramètres système > `abcd.license.server_url`
   - Entrer l'URL : `https://license.abcd.com`

2. **Activer le cron** :
   - Apps > Scheduled Actions
   - Rechercher "ABCD License: Vérification Online"
   - Cliquer sur **Activer**

Le cron vérifiera la licence toutes les 24h (timeout 3s, non-bloquant).

## Étape 6 : Installation des Modules ABCD

### 6.1 Installer un module ABCD

1. Aller dans **Apps**
2. Rechercher le module ABCD (ex: "ABCD Sales Pro")
3. Cliquer sur **Install**

⚠️ **Note** : L'installation sera bloquée si :
- La licence n'est pas configurée
- Le module n'est pas dans la liste des modules autorisés
- La licence est expirée (au-delà de la période de grâce)

### 6.2 Vérifier l'installation

Après installation, le module devrait fonctionner normalement. Les vérifications de licence se font automatiquement lors de l'utilisation.

## Dépannage

### Erreur "Aucune licence configurée"

- Vérifier que `abcd.license.blob` est configuré
- Vérifier que le blob n'est pas vide

### Erreur "Signature invalide"

- Vérifier que la clé publique correspond à la clé privée utilisée pour générer la licence
- Vérifier que le blob n'a pas été modifié
- Vérifier que la clé publique est au bon format (64 caractères hex)

### Erreur "UUID base non valide"

- La licence est liée à une base de données spécifique
- Vérifier l'UUID de votre base : Paramètres système > `database.uuid`
- Contacter ABCD pour générer une nouvelle licence avec le bon UUID

### Erreur "Module non autorisé"

- Vérifier que le module est dans la liste des modules autorisés de la licence
- Contacter ABCD pour ajouter le module à votre licence

### Erreur "Licence expirée"

- Vérifier la date d'expiration dans les informations de licence
- Contacter ABCD pour renouveler la licence

### Module ne s'installe pas

- Vérifier que `abcd_license_core` est installé
- Vérifier que la licence est valide
- Vérifier que le module est dans la liste des modules autorisés
- Consulter les logs Odoo pour plus de détails

## Support

Pour toute question ou problème :

- **Email** : support@abcd.com
- **Documentation** : Voir `README.md` dans `abcd_license_core`
- **Logs** : Vérifier les logs Odoo pour les erreurs détaillées
