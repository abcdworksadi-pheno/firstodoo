# Checklist Sécurité - Système de Licence ABCD

## ✅ Génération et Stockage des Clés

- [ ] Clés Ed25519 générées avec `generate_keys.py`
- [ ] Clé privée stockée avec permissions 600 (rw-------)
- [ ] Clé privée **JAMAIS** partagée ou envoyée au client
- [ ] Clé privée sauvegardée de manière sécurisée (chiffrement, accès restreint)
- [ ] Clé publique distribuée aux clients via canal sécurisé
- [ ] Clé publique vérifiée (intégrité) avant utilisation

## ✅ Génération de Licences

- [ ] Payload JSON validé avant signature
- [ ] JSON canonique (sans espaces, clés triées) pour signature
- [ ] UUID base de données vérifié avant génération
- [ ] Date d'expiration validée (format ISO 8601)
- [ ] Liste de modules validée (non vide, format correct)
- [ ] Quota utilisateurs validé (entier positif ou 0)
- [ ] Signature Ed25519 correctement appliquée
- [ ] Blob base64 correctement encodé
- [ ] Licence testée avant livraison

## ✅ Configuration Odoo

- [ ] Module `abcd_license_core` installé
- [ ] Dépendance `cryptography` installée et à jour
- [ ] Clé publique configurée dans `ir.config_parameter`
- [ ] Clé publique au format hex (64 caractères)
- [ ] Blob de licence configuré dans `ir.config_parameter`
- [ ] Période de grâce configurée (défaut: 7 jours)
- [ ] Serveur de licence configuré si vérification online activée

## ✅ Vérification de Licence

- [ ] Signature Ed25519 vérifiée à chaque appel
- [ ] UUID base de données vérifié
- [ ] Expiration vérifiée (avec période de grâce)
- [ ] Modules autorisés vérifiés
- [ ] Quota utilisateurs vérifié
- [ ] Cache mémoire avec expiration (10 min)
- [ ] Cache base avec expiration (24h)
- [ ] Erreurs loggées sans bloquer Odoo

## ✅ Intégration Modules ABCD

- [ ] Module dépend de `abcd_license_core`
- [ ] Module taggé `category = 'ABCD'`
- [ ] Vérification dans `create()` et `write()`
- [ ] Vérification dans actions métier critiques
- [ ] Messages d'erreur utilisateur-friendly
- [ ] Exceptions `UserError` correctement gérées
- [ ] Pas de hook sur `__init__` ou registry
- [ ] Pas de blocage du démarrage Odoo

## ✅ Installation de Modules

- [ ] Blocage installation si licence invalide
- [ ] Message d'erreur clair pour l'utilisateur
- [ ] Autorisation mise à jour même si licence invalide
- [ ] Pas de désinstallation automatique
- [ ] Pas de suppression de données

## ✅ Vérification Online (Optionnelle)

- [ ] Cron configuré (toutes les 24h)
- [ ] Timeout 3s configuré
- [ ] Fallback offline en cas d'erreur
- [ ] HTTPS utilisé pour l'API
- [ ] Authentification API si exposée publiquement
- [ ] Logs non-bloquants
- [ ] Pas de blocage si serveur offline

## ✅ Sécurité Générale

- [ ] Aucune clé privée dans le code source
- [ ] Aucune clé privée dans les fichiers de configuration
- [ ] Aucune clé privée dans les logs
- [ ] Validation JSON stricte
- [ ] Protection contre injection (pas de code exécuté)
- [ ] Protection contre modification payload
- [ ] Logs d'audit pour tentatives invalides
- [ ] Respect LGPL/OPL (pas d'obfuscation)

## ✅ Performance et Robustesse

- [ ] Cache mémoire optimisé (LRU)
- [ ] Cache base avec expiration
- [ ] Fail-open en cas d'erreur inattendue
- [ ] Pas de blocage du démarrage Odoo
- [ ] Pas de blocage du login utilisateur
- [ ] Timeout appropriés pour requêtes réseau
- [ ] Gestion d'erreurs complète

## ✅ Documentation et Formation

- [ ] Documentation technique complète
- [ ] Guide d'installation
- [ ] Guide d'intégration pour développeurs
- [ ] Exemples de code
- [ ] Procédures de dépannage
- [ ] Contact support documenté

## ✅ Tests

- [ ] Tests de génération de licence
- [ ] Tests de vérification de signature
- [ ] Tests de validation UUID
- [ ] Tests de vérification expiration
- [ ] Tests de vérification modules
- [ ] Tests de vérification quota
- [ ] Tests de cache
- [ ] Tests de vérification online
- [ ] Tests de blocage installation
- [ ] Tests de fail-open

## ✅ Déploiement

- [ ] Serveur de licence sécurisé (firewall, accès restreint)
- [ ] Clés privées sauvegardées
- [ ] Procédure de récupération en cas de perte
- [ ] Monitoring des erreurs de licence
- [ ] Alertes en cas de licence expirée
- [ ] Procédure de renouvellement

## ✅ Conformité

- [ ] Respect LGPL/OPL
- [ ] Pas d'obfuscation de code
- [ ] Transparence du fonctionnement
- [ ] Respect de la vie privée (pas de données sensibles envoyées)
- [ ] Conformité RGPD si applicable

## 🔍 Audit de Sécurité

### Points critiques à vérifier régulièrement

1. **Clé privée** : Vérifier qu'elle n'a jamais été exposée
2. **Signatures** : Vérifier qu'elles sont toujours valides
3. **UUID** : Vérifier qu'il n'y a pas de contournement
4. **Cache** : Vérifier qu'il n'y a pas de bypass
5. **Logs** : Vérifier les tentatives d'accès non autorisées

### Tests de pénétration recommandés

- [ ] Tentative de modification du blob
- [ ] Tentative de bypass de vérification
- [ ] Tentative d'utilisation licence sur autre base
- [ ] Tentative d'utilisation module non autorisé
- [ ] Tentative de contournement quota utilisateurs

## 📝 Notes

- Cette checklist doit être complétée avant chaque déploiement
- Les points critiques doivent être vérifiés régulièrement
- En cas de doute, contacter l'équipe sécurité
