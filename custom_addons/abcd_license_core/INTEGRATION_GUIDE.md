# Guide d'Intégration - Modules ABCD

Ce guide explique comment intégrer la vérification de licence dans vos modules ABCD.

## Prérequis

- Module `abcd_license_core` installé
- Votre module dépend de `abcd_license_core`
- Votre module est taggé `category = 'ABCD'`

## Étape 1 : Configuration du Manifest

Dans `__manifest__.py` :

```python
{
    'name': "Mon Module ABCD",
    'category': 'ABCD',  # ⚠️ IMPORTANT : Catégorie ABCD
    'depends': ['base', 'abcd_license_core'],  # Dépendance obligatoire
    # ...
}
```

## Étape 2 : Vérification dans create() et write()

```python
from odoo import models, api
from odoo.exceptions import UserError

class MonModel(models.Model):
    _name = 'mon.model'
    
    @api.model
    def create(self, vals):
        # Vérifier la licence AVANT création
        self.env['abcd.license'].check_license('mon_module_abcd')
        
        return super().create(vals)
    
    def write(self, vals):
        # Vérifier la licence AVANT modification
        self.env['abcd.license'].check_license('mon_module_abcd')
        
        return super().write(vals)
```

## Étape 3 : Vérification dans Actions Métier

```python
def action_ma_fonction_metier(self):
    """
    Action métier nécessitant une licence
    """
    self.ensure_one()
    
    # Vérifier la licence
    try:
        self.env['abcd.license'].check_license('mon_module_abcd')
    except UserError as e:
        # Le message est déjà formaté pour l'utilisateur
        raise UserError(str(e))
    
    # Votre logique métier ici
    # ...
    
    return {
        'type': 'ir.actions.act_window',
        # ...
    }
```

## Étape 4 : Vérification dans les Boutons

Les boutons appellent généralement des actions métier, donc la vérification se fait automatiquement.

Si vous avez des boutons directs :

```python
def button_action(self):
    self.env['abcd.license'].check_license('mon_module_abcd')
    # Votre logique...
```

## Bonnes Pratiques

### ✅ À FAIRE

- ✅ Vérifier la licence dans `create()` et `write()`
- ✅ Vérifier la licence dans toutes les actions métier critiques
- ✅ Utiliser `UserError` pour les messages d'erreur (déjà géré par `check_license`)
- ✅ Logger les erreurs pour le debugging
- ✅ Tester avec une licence valide et invalide

### ❌ À NE PAS FAIRE

- ❌ Ne pas hooker `__init__` ou le registry
- ❌ Ne pas bloquer le démarrage d'Odoo
- ❌ Ne pas bloquer le login utilisateur
- ❌ Ne pas supprimer de données
- ❌ Ne pas désinstaller automatiquement des modules
- ❌ Ne pas utiliser d'obfuscation

## Exemple Complet

```python
# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import UserError

class MonModel(models.Model):
    _name = 'mon.model'
    _description = 'Mon Modèle ABCD'
    
    name = fields.Char(required=True)
    valeur_pro = fields.Float(string="Valeur Pro", help="Réservé à l'édition Pro")
    
    @api.model
    def create(self, vals):
        # Vérification licence
        self.env['abcd.license'].check_license('mon_module_abcd')
        
        return super().create(vals)
    
    def write(self, vals):
        # Vérification licence
        self.env['abcd.license'].check_license('mon_module_abcd')
        
        return super().write(vals)
    
    def action_generer_rapport_pro(self):
        """
        Génère un rapport Pro nécessitant une licence
        """
        self.ensure_one()
        
        # Vérification licence
        try:
            self.env['abcd.license'].check_license('mon_module_abcd')
        except UserError as e:
            raise UserError(str(e))
        
        # Logique métier
        # ...
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Rapport Pro',
            'res_model': 'mon.model',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
```

## Gestion des Erreurs

### Messages d'Erreur Automatiques

Le système génère automatiquement des messages utilisateur-friendly :

- "Aucune licence ABCD configurée. Contactez votre éditeur."
- "La licence a expiré le 31/01/2026. Contactez votre éditeur ABCD."
- "Le module 'mon_module_abcd' n'est pas autorisé par cette licence."
- "Quota d'utilisateurs dépassé (60/50). Contactez votre éditeur ABCD."

### Personnalisation (Optionnelle)

Si vous voulez personnaliser le message :

```python
try:
    self.env['abcd.license'].check_license('mon_module_abcd')
except UserError as e:
    # Personnaliser le message
    raise UserError(
        f"Impossible d'exécuter cette action : {str(e)}\n\n"
        "Pour plus d'informations, contactez le support."
    )
```

## Tests

### Test avec Licence Valide

1. Configurer une licence valide dans Odoo
2. Tester la création/modification d'enregistrements
3. Tester les actions métier
4. Vérifier que tout fonctionne normalement

### Test avec Licence Invalide

1. Configurer une licence invalide ou expirée
2. Tenter de créer/modifier un enregistrement
3. Vérifier que l'erreur est affichée correctement
4. Vérifier que les données ne sont pas corrompues

### Test Installation

1. Tenter d'installer le module sans licence
2. Vérifier que l'installation est bloquée
3. Configurer une licence valide
4. Vérifier que l'installation fonctionne

## Support

Pour toute question sur l'intégration, consulter :
- `README.md` dans `abcd_license_core`
- `ARCHITECTURE_LICENCE_ABCD.md`
- Contacter le support ABCD
