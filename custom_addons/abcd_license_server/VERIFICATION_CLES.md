# Vérification du Système de Clés

## Comment la Clé Active est Utilisée

### 1. Lors de la Génération de Clés

Quand vous générez une nouvelle paire de clés (`action_generate_keys()`) :

```python
# Ligne 119-123 : Désactive automatiquement les autres clés actives
self.env['license.key'].search([
    ('id', '!=', self.id),
    ('active', '=', True)
]).write({'active': False})

# Ligne 131 : Active automatiquement la nouvelle clé
'active': True
```

**Résultat** : La nouvelle clé est automatiquement activée et devient la clé active.

### 2. Lors de la Génération de Licence

Quand vous générez une licence (`action_generate_license()`) :

```python
# Ligne 214 : Récupère la clé active
key = self._get_active_key()

# Ligne 146-149 : Recherche la clé avec active=True
active_keys = self.env['license.key'].search([
    ('active', '=', True),
    ('key_generated', '=', True)
], order='create_date desc')

# Ligne 164-167 : Charge la clé privée depuis la base
private_key = serialization.load_pem_private_key(
    key.private_key_pem.encode('ascii'),  # ← CLÉ PRIVÉE UTILISÉE ICI
    password=None
)

# Ligne 193 : Signe avec la clé privée
signature = private_key.sign(json_bytes)  # ← SIGNATURE AVEC CLÉ PRIVÉE
```

**Résultat** : La licence est signée avec la clé privée de la clé active.

### 3. Protection contre Plusieurs Clés Actives

Si plusieurs clés sont actives (cas anormal) :

```python
# Ligne 158-165 : Détection et correction automatique
if len(active_keys) > 1:
    # Désactive toutes sauf la plus récente
    active_keys[1:].write({'active': False})
    # Log un avertissement
    _logger.warning("Plusieurs clés actives détectées...")
```

**Résultat** : Le système utilise toujours la clé la plus récente et désactive les autres.

## Vérification Visuelle

### Dans l'Interface Odoo

1. **Voir quelle clé est active** :
   - Aller dans **Licences ABCD > Paires de Clés**
   - La colonne "Active" indique quelle clé est active (✓)

2. **Voir quelle clé a été utilisée pour une licence** :
   - Ouvrir une licence générée
   - Onglet "Informations"
   - Champ "Paire de Clés" : montre quelle clé a signé cette licence
   - Champ "Clé Publique Utilisée" : montre la clé publique hex

### Vérification Technique

Pour vérifier quelle clé est utilisée :

```python
# Dans Odoo, console Python
# 1. Voir toutes les clés actives
env['license.key'].search([('active', '=', True)]).mapped('name')

# 2. Voir quelle clé sera utilisée pour la prochaine licence
key = env['license.license']._get_active_key()
print(f"Clé active: {key.name} (ID: {key.id})")
print(f"Clé publique hex: {key.public_key_hex}")

# 3. Voir quelle clé a été utilisée pour une licence
license = env['license.license'].search([], limit=1)
print(f"Licence: {license.name}")
print(f"Signée avec clé: {license.key_id.name if license.key_id else 'N/A'}")
print(f"Clé publique: {license.public_key_hex}")
```

## Garanties du Système

✅ **Une seule clé active à la fois** :
- Lors de la génération d'une nouvelle clé, les autres sont désactivées
- Lors de l'activation manuelle, les autres sont désactivées
- Si plusieurs clés sont actives (erreur), la plus récente est utilisée

✅ **Traçabilité** :
- Chaque licence enregistre quelle clé l'a signée (`key_id`)
- Chaque licence enregistre la clé publique utilisée (`public_key_hex`)

✅ **Sécurité** :
- La clé privée reste dans la base de données serveur
- Seule la clé active peut signer de nouvelles licences
- Les anciennes licences restent valides même si la clé est désactivée

## Cas d'Usage

### Scénario 1 : Première Clé
1. Générer clé "Production 2025" → Active automatiquement
2. Générer licence → Signée avec "Production 2025"

### Scénario 2 : Nouvelle Clé (Rotation)
1. Générer clé "Production 2026" → Désactive "Production 2025", active "Production 2026"
2. Générer licence → Signée avec "Production 2026"
3. Les anciennes licences (signées avec "Production 2025") restent valides

### Scénario 3 : Activation Manuelle
1. Plusieurs clés existent, "Production 2025" est active
2. Cliquer "Activer cette Clé" sur "Production 2024"
3. "Production 2025" est désactivée, "Production 2024" devient active
4. Prochaines licences seront signées avec "Production 2024"

## Conclusion

Le système garantit que :
- **Toujours** la clé active est utilisée pour signer
- **Une seule** clé est active à la fois
- **Traçabilité** complète de quelle clé a signé quelle licence
- **Sécurité** : clé privée jamais exposée
