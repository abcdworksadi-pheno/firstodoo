# Résumé du Système de Licence ABCD

## 📦 Livrables Produits

### 1. Serveur de Génération de Licences

**Emplacement** : `deployment/server/license_server/`

- ✅ `generate_keys.py` : Script de génération de clés Ed25519
- ✅ `generate_license.py` : Script de génération de licences
- ✅ `api_server.py` : API REST optionnelle
- ✅ `example_config.json` : Exemple de configuration
- ✅ `requirements.txt` : Dépendances Python
- ✅ `README.md` : Documentation serveur

### 2. Module Odoo Core

**Emplacement** : `custom_addons/abcd_license_core/`

- ✅ Module complet de vérification de licence
- ✅ Vérification offline par défaut
- ✅ Vérification online optionnelle (cron)
- ✅ Cache mémoire et base de données
- ✅ Blocage installation modules ABCD
- ✅ API interne `check_license(module_name)`
- ✅ Gestion période de grâce
- ✅ Messages d'erreur utilisateur-friendly

### 3. Module Exemple

**Emplacement** : `custom_addons/abcd_sales_pro/`

- ✅ Module exemple démontrant l'intégration
- ✅ Vérification dans `create()` et `write()`
- ✅ Vérification dans actions métier
- ✅ Documentation d'intégration

### 4. Documentation

- ✅ `ARCHITECTURE_LICENCE_ABCD.md` : Architecture complète avec diagrammes
- ✅ `CHECKLIST_SECURITE.md` : Checklist sécurité détaillée
- ✅ `GUIDE_INSTALLATION.md` : Guide d'installation pas à pas
- ✅ `abcd_license_core/README.md` : Documentation technique du module
- ✅ `abcd_sales_pro/README.md` : Guide d'intégration

## 🏗️ Architecture

### Format de Licence

```
BASE64(
  JSON_PAYLOAD_CANONIQUE
  .
  SIGNATURE_ED25519
)
```

### Flux de Vérification

1. **Cache mémoire** (10 min) → Retour immédiat si disponible
2. **Cache base** (24h) → Validation depuis cache si disponible
3. **Vérification complète** :
   - Décodage blob
   - Vérification signature Ed25519
   - Vérification UUID base
   - Vérification expiration (avec période de grâce)
   - Vérification modules autorisés
   - Vérification quota utilisateurs
4. **Mise en cache** + Retour

### Sécurité

- ✅ Aucune clé privée côté client
- ✅ Signature asymétrique Ed25519
- ✅ Validation stricte (UUID, expiration, modules, quota)
- ✅ Protection contre modification payload
- ✅ Fail-open (ne bloque jamais Odoo globalement)

## 🚀 Utilisation

### Pour l'éditeur (ABCD)

1. Générer les clés : `python generate_keys.py`
2. Générer une licence : `python generate_license.py --config config.json`
3. Livrer au client : blob de licence + clé publique

### Pour le client

1. Installer `abcd_license_core`
2. Configurer la clé publique dans Odoo
3. Configurer le blob de licence dans Odoo
4. Installer les modules ABCD

### Pour les développeurs de modules ABCD

```python
# Dans create() / write()
self.env['abcd.license'].check_license('mon_module_abcd')

# Dans actions métier
try:
    self.env['abcd.license'].check_license('mon_module_abcd')
except UserError as e:
    raise UserError(str(e))
```

## ✅ Contraintes Respectées

- ✅ Odoo 18+ (compatible 19+)
- ✅ On-premise + Odoo.sh
- ✅ Offline-first (fonctionne sans connexion)
- ✅ Vérification online optionnelle
- ✅ Aucune clé privée côté client
- ✅ Respect LGPL/OPL
- ✅ Ne bloque jamais Odoo globalement
- ✅ Ne supprime jamais de données
- ✅ Ne désinstalle jamais automatiquement
- ✅ Pas d'obfuscation

## 📋 Checklist Rapide

- [ ] Clés générées et sécurisées
- [ ] Module `abcd_license_core` installé
- [ ] Clé publique configurée
- [ ] Licence configurée
- [ ] Modules ABCD installés
- [ ] Vérification fonctionnelle
- [ ] Documentation consultée

## 🔗 Fichiers Clés

- **Serveur** : `deployment/server/license_server/`
- **Module Core** : `custom_addons/abcd_license_core/`
- **Exemple** : `custom_addons/abcd_sales_pro/`
- **Documentation** : Fichiers `.md` à la racine

## 📞 Support

Pour toute question, consulter la documentation ou contacter le support ABCD.
