# Changelog - Système de Licence ABCD

## Version 1.0.0 (2025-01-XX)

### Ajouts

- ✅ Serveur de génération de licences avec Ed25519
- ✅ Module Odoo `abcd_license_core` complet
- ✅ Vérification offline par défaut
- ✅ Vérification online optionnelle (cron)
- ✅ Cache mémoire et base de données
- ✅ Blocage installation modules ABCD sans licence
- ✅ Période de grâce configurable
- ✅ Messages d'erreur utilisateur-friendly
- ✅ Module exemple `abcd_sales_pro`
- ✅ Documentation complète
- ✅ Scripts de test

### Caractéristiques

- **Sécurité** : Signature Ed25519, aucune clé privée côté client
- **Performance** : Cache multi-niveaux optimisé
- **Robustesse** : Fail-open, ne bloque jamais Odoo
- **Compatibilité** : Odoo 18+ (compatible 19+)
- **Offline-first** : Fonctionne sans connexion
- **Professionnel** : Messages clairs, documentation complète

### Fichiers Principaux

#### Serveur
- `deployment/server/license_server/generate_keys.py`
- `deployment/server/license_server/generate_license.py`
- `deployment/server/license_server/api_server.py`
- `deployment/server/license_server/test_license.py`

#### Module Odoo
- `custom_addons/abcd_license_core/`
- `custom_addons/abcd_sales_pro/` (exemple)

#### Documentation
- `ARCHITECTURE_LICENCE_ABCD.md`
- `CHECKLIST_SECURITE.md`
- `GUIDE_INSTALLATION.md`
- `RESUME_SYSTEME_LICENCE.md`
- `QUICK_START.md`

### Notes

- Le système respecte toutes les contraintes demandées
- Aucune clé privée ne quitte le serveur de licence
- Le système ne bloque jamais Odoo globalement
- Compatible avec on-premise et Odoo.sh
