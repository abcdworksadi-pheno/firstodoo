# Modèle de Test - Lettre de Motivation

Voici un exemple de contenu HTML que vous pouvez utiliser pour créer un modèle de lettre de test.

## Contenu du Modèle (HTML)

Copiez ce contenu dans le champ "Contenu du Modèle" lors de la création d'un nouveau modèle :

```html
<div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <div style="text-align: right; margin-bottom: 30px;">
        <p>{{nom_client}}</p>
        <p>{{adresse_client}}</p>
        <p>{{email_client}}</p>
        <p>{{telephone_client}}</p>
    </div>

    <div style="margin-bottom: 20px;">
        <p>Le {{date_commande}}</p>
    </div>

    <div style="margin-bottom: 20px;">
        <p><strong>Objet : Lettre de Motivation - Commande {{num_commande}}</strong></p>
    </div>

    <div style="margin-bottom: 20px; line-height: 1.6;">
        <p>Madame, Monsieur,</p>
        <p>Je me permets de vous adresser la présente lettre suite à votre commande n° <strong>{{num_commande}}</strong> du {{date_commande}}.</p>
    </div>

    <div style="margin-bottom: 20px; line-height: 1.6;">
        <p>Nous avons le plaisir de confirmer la réception de votre commande d'un montant total de <strong>{{montant_total}}</strong>.</p>
    </div>

    <div style="margin-bottom: 20px; line-height: 1.6;">
        <p>Votre commercial référent pour cette commande est : <strong>{{nom_commercial}}</strong>.</p>
    </div>

    <div style="margin-bottom: 20px; line-height: 1.6;">
        <p>Nous nous engageons à traiter votre commande dans les meilleurs délais et à vous tenir informé(e) de son avancement.</p>
        <p>N'hésitez pas à nous contacter si vous avez la moindre question.</p>
    </div>

    <div style="margin-top: 40px; line-height: 1.6;">
        <p>Nous vous remercions de votre confiance et restons à votre disposition.</p>
        <p>Cordialement,</p>
        <p style="margin-top: 30px;"><strong>L'équipe commerciale</strong></p>
    </div>
</div>
```

## Variables Utilisées

Les variables suivantes seront automatiquement remplacées par les données de la commande :

- `{{nom_client}}` : Nom du client (partner_id.name)
- `{{adresse_client}}` : Adresse complète du client
- `{{email_client}}` : Email du client
- `{{telephone_client}}` : Téléphone du client
- `{{date_commande}}` : Date de la commande (format: JJ/MM/AAAA)
- `{{num_commande}}` : Numéro de la commande
- `{{montant_total}}` : Montant total avec devise (ex: "1500.00 €")
- `{{nom_commercial}}` : Nom du commercial responsable

## Instructions d'Utilisation

1. **Créer un nouveau modèle** :
   - Aller dans **Lettres de Motivation > Modèles**
   - Cliquer sur **Créer**
   - Remplir :
     - **Nom** : "Lettre de Mission - Test"
     - **Niveau** : "Niveau 1 - Variables Texte"
     - **Contenu** : Coller le HTML ci-dessus
     - **Format de Sortie** : PDF

2. **Tester depuis une commande** :
   - Ouvrir une commande de vente
   - Cliquer sur **"Générer Lettre de Motivation"**
   - Sélectionner le modèle "Lettre de Mission - Test"
   - Cliquer sur **Générer**

3. **Résultat** :
   - La lettre sera générée automatiquement avec les données de la commande
   - Les variables seront remplacées par les valeurs réelles
   - Vous pourrez ensuite télécharger ou modifier la lettre générée

## Exemple de Résultat

Après génération, le contenu ressemblera à :

```html
<div style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
    <div style="text-align: right; margin-bottom: 30px;">
        <p>ABC Company</p>
        <p>123 Rue de la République, Paris, 75001, France</p>
        <p>contact@abc-company.fr</p>
        <p>01 23 45 67 89</p>
    </div>

    <div style="margin-bottom: 20px;">
        <p>Le 15/01/2024</p>
    </div>

    <div style="margin-bottom: 20px;">
        <p><strong>Objet : Lettre de Motivation - Commande SO001</strong></p>
    </div>
    ...
</div>
```

## Variables Personnalisées

Si vous voulez ajouter d'autres variables personnalisées qui ne sont pas mappées automatiquement :

1. Créer le modèle avec le contenu HTML
2. Les variables seront détectées automatiquement
3. Aller dans l'onglet **Variables** du modèle
4. Pour chaque variable personnalisée, remplir la **Valeur par Défaut** ou la remplir manuellement lors de la génération

Par exemple, si vous ajoutez `{{motif_commande}}` dans le contenu, vous devrez remplir cette valeur lors de la génération ou définir une valeur par défaut dans le modèle.

