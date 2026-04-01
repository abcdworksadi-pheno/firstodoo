# ABCD License Guard

## 🔒 Protection d'installation pour modules ABCD

Module minimal qui intercepte l'installation de modules ABCD **AVANT** qu'Odoo n'installe automatiquement `abcd_license_core`.

## ⚠️ CRITIQUE - INSTALLATION OBLIGATOIRE

**Ce module DOIT être installé en PREMIER** avant tout autre module ABCD.

Tous les modules ABCD personnalisés doivent déclarer `abcd_license_guard` dans leurs dépendances.

## Installation

### Ordre OBLIGATOIRE :

1. **Installer `abcd_license_guard` EN PREMIER** ⚠️
2. Installer `abcd_license_core`
3. Configurer la licence (clé publique + blob)
4. Installer les autres modules ABCD

## Fonctionnement

Ce module intercepte `_button_immediate_function` qui est appelé **AVANT** qu'Odoo n'installe les dépendances. Il vérifie que :

1. `abcd_license_core` est installé
2. La clé publique est configurée
3. Le license_blob est configuré

Si l'une de ces conditions n'est pas remplie, l'installation est **bloquée** avec un message clair.

## Intégration dans les modules ABCD

Tous les modules ABCD personnalisés doivent inclure `abcd_license_guard` dans leurs dépendances :

```python
'depends': ['base', 'sale', 'abcd_license_guard', 'abcd_license_core'],
```

Cela garantit que `abcd_license_guard` sera installé automatiquement avant le module personnalisé.

## Avantages

- ✅ Fonctionne même si `abcd_license_core` n'est pas installé
- ✅ Intercepte AVANT l'installation des dépendances
- ✅ Messages d'erreur clairs
- ✅ Logs détaillés pour le diagnostic
- ✅ Protection double (guard + core)
