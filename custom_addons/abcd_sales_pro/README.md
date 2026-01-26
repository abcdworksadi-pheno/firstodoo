# ABCD Sales Pro - Module Exemple

Ce module est un exemple d'intégration du système de licence ABCD.

## Fonctionnalités

- Extension du modèle `sale.order` avec un champ personnalisé
- Vérification de licence lors de la création/modification
- Action métier nécessitant une licence valide

## Intégration de la licence

### Dans les méthodes create() et write()

```python
@api.model
def create(self, vals):
    license_service = self.env['abcd.license']
    license_service.check_license('abcd_sales_pro')
    return super().create(vals)
```

### Dans les actions métier

```python
def action_abcd_pro_report(self):
    license_service = self.env['abcd.license']
    license_service.check_license('abcd_sales_pro')
    # ... logique métier ...
```

## Bonnes pratiques

1. **Toujours vérifier la licence** dans les méthodes critiques (create, write, actions)
2. **Gérer les exceptions UserError** pour afficher des messages clairs
3. **Ne jamais bloquer** le démarrage d'Odoo ou le login
4. **Logger les erreurs** pour le debugging
