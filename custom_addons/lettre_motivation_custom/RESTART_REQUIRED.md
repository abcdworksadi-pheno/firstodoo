# Instructions de Redémarrage

## Problème
Lors de la mise à jour du module, Odoo peut ne pas reconnaître immédiatement les nouvelles méthodes ajoutées au modèle `sale.order`.

## Solution

### Étape 1 : Redémarrer le serveur Odoo

**Important** : Vous devez redémarrer complètement le serveur Odoo pour que le nouveau modèle soit enregistré.

#### Si vous utilisez Docker :
```bash
docker-compose restart
```

#### Si vous utilisez un serveur local :
- Arrêtez le serveur Odoo (Ctrl+C)
- Redémarrez-le avec : `odoo-bin -c odoo.conf`

### Étape 2 : Mettre à jour le module

Une fois le serveur redémarré :
1. Allez dans **Applications**
2. Cherchez "Lettre de Motivation Personnalisée"
3. Cliquez sur **Mettre à jour**

### Étape 3 : Vérification

Après la mise à jour, ouvrez une commande de vente et vérifiez que le bouton **"Générer Lettre de Motivation"** apparaît dans l'en-tête.

## Pourquoi ce redémarrage est nécessaire ?

Lorsque vous ajoutez un nouveau modèle Python avec `_inherit`, Odoo doit :
1. Charger le fichier Python
2. Enregistrer le modèle dans le registre
3. Valider les vues XML qui référencent ce modèle

Si la vue XML est chargée avant que le modèle ne soit complètement enregistré, Odoo génère une erreur. Un redémarrage complet garantit que tous les modèles sont chargés avant la validation des vues.

