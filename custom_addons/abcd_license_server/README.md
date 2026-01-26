# ABCD License Server - Module Odoo

Module Odoo complet pour la gestion et génération de licences ABCD avec interface graphique.

## 🎯 Fonctionnalités

### Gestion des Clients
- Création et gestion des clients
- Code client unique
- Informations de contact
- Historique des licences par client

### Génération de Clés
- Génération de paires de clés Ed25519 via interface
- Activation/désactivation de clés
- Téléchargement des clés (privée et publique)
- Affichage de la clé publique en hex pour Odoo

### Génération de Licences
- Interface graphique complète
- Génération automatique d'alias (ex: `ABCD-LIC-CLIENTX-2025-001`)
- Wizard rapide pour génération
- Export de licences
- Copie du blob dans le presse-papiers
- Historique complet des licences générées

## 📦 Installation

### 1. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

### 2. Installer le module dans Odoo

1. Copier le module dans `custom_addons/`
2. Mettre à jour la liste des apps
3. Installer "ABCD License Server"

## 🚀 Utilisation

### Étape 1 : Générer une paire de clés

1. Aller dans **Licences ABCD > Paires de Clés**
2. Créer un nouvel enregistrement
3. Cliquer sur **"Générer les Clés"**
4. Activer la clé (désactive automatiquement les autres)

### Étape 2 : Créer un client

1. Aller dans **Licences ABCD > Clients**
2. Créer un nouveau client avec un code unique
3. Remplir les informations de contact

### Étape 3 : Générer une licence

**Méthode 1 : Wizard rapide**
1. Aller dans **Licences ABCD > Générer une Licence**
2. Remplir le formulaire
3. Cliquer sur **"Générer"**

**Méthode 2 : Formulaire complet**
1. Aller dans **Licences ABCD > Licences**
2. Créer une nouvelle licence
3. Remplir tous les champs
4. Cliquer sur **"Générer Alias"** (optionnel)
5. Cliquer sur **"Générer la Licence"**

### Étape 4 : Distribuer la licence

1. Copier le **Blob de Licence** depuis la vue détaillée
2. Copier la **Clé Publique (Hex)** depuis la paire de clés
3. Envoyer au client pour configuration dans son Odoo

## 🔐 Sécurité

- **Clé privée** : Ne jamais partager, reste uniquement sur le serveur
- **Clé publique** : Peut être partagée avec les clients
- **Blob de licence** : Contient toutes les informations signées

## 📋 Champs de Licence

- **Alias** : Identifiant lisible (ex: `ABCD-LIC-CLIENTX-2025-001`)
- **Client** : Client pour lequel la licence est générée
- **UUID Base** : UUID de la base de données Odoo cible
- **Modules** : Liste des modules autorisés (séparés par virgules)
- **Édition** : Standard / Pro / Enterprise
- **Date d'expiration** : Date et heure d'expiration (UTC)
- **Max Utilisateurs** : Nombre maximum d'utilisateurs (0 = illimité)

## 🎨 Interface

Le module fournit une interface complète avec :
- Vues liste pour tous les modèles
- Formulaires détaillés avec onglets
- Wizards pour génération rapide
- Boutons d'action contextuels
- Notifications de succès/erreur

## 🔄 Workflow Typique

1. **Générer les clés** → Activer une clé
2. **Créer les clients** → Enregistrer les clients
3. **Générer les licences** → Via wizard ou formulaire
4. **Distribuer** → Envoyer blob + clé publique au client
5. **Suivre** → Historique dans les vues liste

## 📝 Notes

- Une seule clé peut être active à la fois
- Les alias sont générés automatiquement avec séquence
- Les licences sont signées avec la clé active
- L'historique complet est conservé

## 🆘 Support

Pour toute question, consulter la documentation ou contacter le support ABCD.
