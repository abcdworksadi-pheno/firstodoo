# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import json
import re
from datetime import datetime


class LettreMotivationInstance(models.Model):
    """Instance de lettre de motivation générée"""
    _name = 'lettre.motivation.instance'
    _description = 'Instance de Lettre de Motivation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_generation desc'

    name = fields.Char(
        string='Nom',
        required=True,
        default=lambda self: _('Nouvelle Lettre'),
        help='Nom de l\'instance de lettre'
    )

    template_id = fields.Many2one(
        'lettre.motivation.template',
        string='Modèle',
        required=True,
        ondelete='restrict',
        tracking=True,
        help='Modèle utilisé pour générer cette lettre'
    )

    # Relations avec les modèles Odoo
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Commande',
        ondelete='cascade',
        help='Commande depuis laquelle cette lettre a été générée'
    )

    account_move_id = fields.Many2one(
        'account.move',
        string='Facture',
        ondelete='cascade',
        help='Facture depuis laquelle cette lettre a été générée'
    )

    res_model = fields.Char(
        string='Modèle Source',
        help='Modèle Odoo source (ex: sale.order)'
    )

    res_id = fields.Integer(
        string='ID Source',
        help='ID de l\'enregistrement source'
    )

    niveau = fields.Selection(
        related='template_id.niveau',
        string='Niveau',
        readonly=True,
        store=True
    )

    format_sortie = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('html', 'HTML'),
            ('docx', 'DOCX'),
        ],
        string='Format de Sortie',
        default='docx',
        help='Format du fichier généré'
    )

    valeurs_variables = fields.Text(
        string='Valeurs des Variables',
        help='Valeurs JSON des variables injectées'
    )

    variables_valeurs_ids = fields.One2many(
        'lettre.motivation.instance.variable',
        'instance_id',
        string='Variables et Valeurs',
        help='Variables avec leurs valeurs'
    )

    valeurs_variables_dict = fields.Char(
        string='Valeurs (Dict)',
        compute='_compute_valeurs_dict',
        store=False,
        help='Valeurs des variables sous forme de dictionnaire'
    )

    contenu_final = fields.Html(
        string='Contenu Final',
        help='Contenu HTML final généré'
    )

    fichier_genere = fields.Binary(
        string='Fichier Généré',
        help='Fichier PDF/DOCX/HTML généré'
    )

    nom_fichier = fields.Char(
        string='Nom du Fichier',
        help='Nom du fichier généré'
    )

    date_generation = fields.Datetime(
        string='Date de Génération',
        default=fields.Datetime.now,
        required=True,
        readonly=True,
        tracking=True,
        help='Date et heure de génération de la lettre'
    )

    state = fields.Selection(
        [
            ('draft', 'Brouillon'),
            ('generated', 'Générée'),
            ('sent', 'Envoyée'),
        ],
        string='État',
        default='draft',
        tracking=True,
        help='État de la lettre'
    )

    @api.depends('valeurs_variables')
    def _compute_valeurs_dict(self):
        """Convertit les valeurs JSON en dictionnaire"""
        for record in self:
            if record.valeurs_variables:
                try:
                    record.valeurs_variables_dict = json.dumps(
                        json.loads(record.valeurs_variables),
                        ensure_ascii=False,
                        indent=2
                    )
                except:
                    record.valeurs_variables_dict = record.valeurs_variables
            else:
                record.valeurs_variables_dict = '{}'

    def get_valeurs_dict(self):
        """Retourne les valeurs sous forme de dictionnaire Python"""
        valeurs = {}
        
        # Priorité aux valeurs dans variables_valeurs_ids
        if self.variables_valeurs_ids:
            for var_val in self.variables_valeurs_ids:
                # Essayer de récupérer le nom de la variable de plusieurs façons
                var_name = None
                
                # Méthode 1: Depuis variable_id
                if var_val.variable_id and var_val.variable_id.name:
                    var_name = var_val.variable_id.name
                # Méthode 2: Depuis le champ name (related)
                elif hasattr(var_val, 'name') and var_val.name:
                    var_name = var_val.name
                
                if var_name:
                    # Utiliser la valeur si remplie, sinon valeur par défaut
                    if var_val.valeur:
                        valeurs[var_name] = var_val.valeur
                    elif var_val.variable_id and var_val.variable_id.valeur_par_defaut:
                        valeurs[var_name] = var_val.variable_id.valeur_par_defaut
                    elif hasattr(var_val, 'valeur_par_defaut') and var_val.valeur_par_defaut:
                        valeurs[var_name] = var_val.valeur_par_defaut
        
        # Compléter avec les valeurs par défaut du template pour les variables manquantes
        if self.template_id:
            for var_obj in self.template_id.variables_ids:
                if var_obj.name not in valeurs:
                    # Si la variable n'est pas dans valeurs, utiliser sa valeur par défaut
                    if var_obj.valeur_par_defaut:
                        valeurs[var_obj.name] = var_obj.valeur_par_defaut
        
        # Si pas de valeurs dans variables_valeurs_ids, utiliser le JSON
        if not valeurs and self.valeurs_variables:
            try:
                valeurs = json.loads(self.valeurs_variables)
            except:
                pass
        
        return valeurs
    
    @api.model_create_multi
    def create(self, vals_list):
        """S'assure que toutes les variables sont créées lors de la création"""
        instances = super().create(vals_list)
        # S'assurer que toutes les variables sont présentes après création
        for instance in instances:
            if instance.template_id:
                instance._ensure_all_variables_present()
        return instances
    
    def write(self, vals):
        """S'assure que toutes les variables sont présentes après modification du template"""
        result = super().write(vals)
        # Si le template a changé, s'assurer que toutes les variables sont présentes
        if 'template_id' in vals:
            for instance in self:
                if instance.template_id:
                    instance._ensure_all_variables_present()
        return result
    
    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Crée les lignes de variables lorsque le modèle change"""
        if self.template_id:
            variables = []
            # S'assurer que le template est chargé avec ses variables
            template = self.template_id.with_context(prefetch_fields=True)
            # Charger explicitement les variables
            template.invalidate_recordset(['variables_ids'])
            for var in template.variables_ids:
                if var.id:  # S'assurer que la variable a un ID
                    variables.append((0, 0, {
                        'variable_id': var.id,
                        'valeur': var.valeur_par_defaut or '',
                        'sequence': 10,
                    }))
            # S'assurer qu'on remplace toutes les lignes existantes
            self.variables_valeurs_ids = [(5, 0, 0)]  # Supprimer toutes les lignes existantes
            if variables:
                self.variables_valeurs_ids = variables
        elif not self.template_id:
            # Si le modèle est supprimé, supprimer aussi les variables
            self.variables_valeurs_ids = [(5, 0, 0)]
    
    def _ensure_all_variables_present(self):
        """S'assure que toutes les variables du template sont présentes dans variables_valeurs_ids"""
        if not self.template_id:
            return
        
        # S'assurer que le template est chargé avec ses variables
        self.template_id.invalidate_recordset(['variables_ids'])
        
        # Récupérer les IDs des variables déjà présentes
        existing_var_ids = set(self.variables_valeurs_ids.mapped('variable_id.id'))
        
        # Pour chaque variable du template, vérifier si elle est présente
        missing_vars = []
        for var_obj in self.template_id.variables_ids:
            if var_obj.id and var_obj.id not in existing_var_ids:
                missing_vars.append({
                    'instance_id': self.id,
                    'variable_id': var_obj.id,
                    'valeur': var_obj.valeur_par_defaut or '',
                    'sequence': 10,
                })
        
        # Créer toutes les lignes manquantes en une seule fois
        if missing_vars:
            self.env['lettre.motivation.instance.variable'].create(missing_vars)
    
    @api.constrains('variables_valeurs_ids', 'template_id')
    def _check_variables_valeurs_ids(self):
        """Vérifie que toutes les lignes ont un variable_id et essaie de le remplir automatiquement"""
        for record in self:
            if record.template_id:
                # S'assurer que toutes les variables du template sont présentes
                record._ensure_all_variables_present()
                
                for var_val in record.variables_valeurs_ids:
                    if not var_val.variable_id:
                        # Essayer de trouver la variable par son nom si disponible
                        if hasattr(var_val, 'name') and var_val.name and record.template_id:
                            variable = record.template_id.variables_ids.filtered(
                                lambda v: v.name == var_val.name
                            )
                            if variable:
                                var_val.variable_id = variable[0].id
                            else:
                                raise ValidationError(_(
                                    'La variable "%s" n\'existe pas dans le modèle. '
                                    'Veuillez supprimer cette ligne et recréer les variables en sélectionnant le modèle.'
                                ) % var_val.name)
                        else:
                            raise ValidationError(_(
                                'Toutes les variables doivent avoir un champ Variable défini. '
                                'Veuillez supprimer et recréer les lignes en sélectionnant d\'abord le modèle.'
                            ))

    def action_generer_contenu(self):
        """Génère le contenu final à partir du template et des valeurs"""
        self.ensure_one()
        
        # Si on utilise un template Word, pas besoin de générer le contenu HTML
        # Le rendu se fait directement dans _generer_docx() avec docxtpl
        if self.template_id.use_word_template and self.template_id.word_template:
            # Pour les templates Word, on marque juste comme généré
            # Le contenu réel sera généré lors de l'appel à _generer_docx()
            self.state = 'generated'
            # Créer un contenu minimal pour la prévisualisation (optionnel)
            self.contenu_final = '<p>Template Word - Le contenu sera généré lors de l\'export DOCX</p>'
            return
        
        if not self.template_id.contenu:
            raise UserError(_('Le modèle n\'a pas de contenu valide!'))
        
        # S'assurer que toutes les variables sont présentes avant la génération
        self._ensure_all_variables_present()
        
        valeurs = self.get_valeurs_dict()
        
        # Remplacer les variables dans le contenu
        try:
            contenu = self.template_id.contenu
            
            # Traiter les tableaux (niveau 2 et 3)
            for tableau in self.template_id.tableaux_ids:
                var_name = tableau.variable_name
                # Générer le HTML du tableau
                tableau_html = self._generer_tableau_html(tableau)
                # Remplacer toutes les occurrences de la variable du tableau
                pattern = r'\{\{' + re.escape(var_name) + r'\}\}'
                contenu = re.sub(pattern, tableau_html, contenu, flags=re.IGNORECASE)
            
            # Remplacer les variables simples
            # Pour chaque variable définie dans le modèle
            for var_obj in self.template_id.variables_ids:
                # Ignorer les variables de tableau (déjà traitées)
                if any(t.variable_name == var_obj.name for t in self.template_id.tableaux_ids):
                    continue
                
                # Récupérer la valeur (utiliser le nom technique comme clé)
                var_value = ''
                if var_obj.name in valeurs:
                    var_value = str(valeurs[var_obj.name])
                elif var_obj.valeur_par_defaut:
                    var_value = str(var_obj.valeur_par_defaut)
                
                # Créer une liste de tous les patterns possibles à remplacer
                patterns_to_replace = []
                
                # Ajouter le nom technique (exact et insensible à la casse)
                patterns_to_replace.append((r'\{\{' + re.escape(var_obj.name) + r'\}\}', var_value))
                
                # Ajouter le libellé original si différent
                if var_obj.label and var_obj.label != var_obj.name:
                    patterns_to_replace.append((r'\{\{' + re.escape(var_obj.label) + r'\}\}', var_value))
                
                # Effectuer tous les remplacements
                for pattern, replacement in patterns_to_replace:
                    contenu = re.sub(pattern, replacement, contenu, flags=re.IGNORECASE)
            
            # Remplacer aussi toutes les variables restantes qui pourraient être dans le template
            # mais qui n'ont pas de valeur (les remplacer par chaîne vide)
            all_vars_in_template = re.findall(r'\{\{([^}]+?)\}\}', contenu)
            for var_found in all_vars_in_template:
                var_found = var_found.strip()
                # Si cette variable n'a pas été remplacée, la remplacer par chaîne vide
                if '{{' + var_found + '}}' in contenu:
                    pattern = r'\{\{' + re.escape(var_found) + r'\}\}'
                    contenu = re.sub(pattern, '', contenu)
            
            self.contenu_final = contenu
            self.state = 'generated'
        except Exception as e:
            raise UserError(_('Erreur lors de la génération: %s') % str(e))
    
    def _generer_tableau_html(self, tableau):
        """Génère le HTML d'un tableau dynamique"""
        html = '<table class="table table-bordered" style="width: 100%; border-collapse: collapse; margin: 20px 0;">\n'
        
        # En-tête
        html += '  <thead>\n    <tr>\n'
        for colonne in tableau.colonnes_ids.sorted('sequence'):
            style = f'width: {colonne.width};' if colonne.width else ''
            html += f'      <th style="{style} border: 1px solid #ddd; padding: 8px; background-color: #f2f2f2;">{colonne.label}</th>\n'
        html += '    </tr>\n  </thead>\n'
        
        # Corps
        html += '  <tbody>\n'
        for ligne in tableau.lignes_ids.sorted('sequence'):
            html += '    <tr>\n'
            try:
                valeurs = json.loads(ligne.valeurs)
                for colonne in tableau.colonnes_ids.sorted('sequence'):
                    valeur = valeurs.get(colonne.name, '')
                    html += f'      <td style="border: 1px solid #ddd; padding: 8px;">{valeur}</td>\n'
            except:
                pass
            html += '    </tr>\n'
        html += '  </tbody>\n'
        
        html += '</table>'
        return html

    def _auto_map_from_record(self, record, binding):
        """Mapper automatiquement les champs depuis un enregistrement Odoo"""
        self.ensure_one()
        
        if not binding or not binding.auto_map_fields:
            return
        
        # Parcourir tous les mappings configurés
        for mapping in binding.field_mapping_ids:
            if not mapping.variable_id:
                continue
            
            # Récupérer la valeur depuis l'enregistrement
            try:
                value = mapping.get_value_from_record(record)
                
                # Trouver ou créer la ligne de variable
                var_val = self.variables_valeurs_ids.filtered(
                    lambda v: v.variable_id.id == mapping.variable_id.id
                )
                
                if var_val:
                    # Mettre à jour la valeur
                    var_val[0].valeur = value
                else:
                    # Créer une nouvelle ligne
                    self.env['lettre.motivation.instance.variable'].create({
                        'instance_id': self.id,
                        'variable_id': mapping.variable_id.id,
                        'valeur': value,
                    })
            except Exception as e:
                # Logger l'erreur mais continuer avec les autres mappings
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(
                    f"Erreur lors du mapping du champ {mapping.model_field} "
                    f"vers la variable {mapping.variable_id.name}: {str(e)}"
                )

    def _auto_map_from_sale_order(self, sale_order):
        """Mapper automatiquement les champs depuis une commande de vente"""
        self.ensure_one()
        
        if not sale_order:
            return
        
        # Mapping basique des champs communs
        common_mappings = {
            'nom_client': sale_order.partner_id.name if sale_order.partner_id else '',
            'nom_commercial': sale_order.user_id.name if sale_order.user_id else '',
            'date_commande': sale_order.date_order.strftime('%d/%m/%Y') if sale_order.date_order else '',
            'montant_total': f"{sale_order.amount_total:.2f} {sale_order.currency_id.symbol}" if sale_order.currency_id else f"{sale_order.amount_total:.2f}",
            'num_commande': sale_order.name or '',
            'adresse_client': self._format_partner_address(sale_order.partner_id) if sale_order.partner_id else '',
            'email_client': sale_order.partner_id.email if sale_order.partner_id else '',
            'telephone_client': sale_order.partner_id.phone if sale_order.partner_id else '',
        }
        
        # Remplir les variables qui correspondent
        for var_val in self.variables_valeurs_ids:
            if var_val.variable_id and var_val.variable_id.name:
                var_name = var_val.variable_id.name.lower()
                # Chercher une correspondance
                for mapping_key, mapping_value in common_mappings.items():
                    if var_name == mapping_key or var_name.replace('_', '') == mapping_key.replace('_', ''):
                        var_val.valeur = str(mapping_value) if mapping_value else ''
                        break

    def _format_partner_address(self, partner):
        """Formate l'adresse d'un partenaire"""
        if not partner:
            return ''
        
        parts = []
        if partner.street:
            parts.append(partner.street)
        if partner.street2:
            parts.append(partner.street2)
        if partner.city:
            parts.append(partner.city)
        if partner.zip:
            parts.append(partner.zip)
        if partner.country_id:
            parts.append(partner.country_id.name)
        
        return ', '.join(parts)

    def action_generer_fichier(self):
        """Génère le fichier dans le format choisi"""
        self.ensure_one()
        
        format_sortie = self.format_sortie or self.template_id.format_sortie or 'docx'
        
        # Pour les templates Word, on peut générer directement sans contenu_final
        # car le rendu se fait avec docxtpl
        if self.template_id.use_word_template and self.template_id.word_template:
            if format_sortie == 'docx':
                return self._generer_docx()
            else:
                # Pour HTML/PDF avec template Word, il faut d'abord extraire le contenu
                if not self.contenu_final:
                    raise UserError(_('Pour les formats HTML/PDF avec template Word, veuillez d\'abord générer le contenu!'))
        
        # Pour les templates HTML normaux, vérifier que le contenu est généré
        if not self.contenu_final:
            raise UserError(_('Veuillez d\'abord générer le contenu de la lettre!'))
        
        if format_sortie == 'html':
            return self._generer_html()
        elif format_sortie == 'docx':
            return self._generer_docx()
        else:  # pdf
            return self._generer_pdf()

    def _generer_html(self):
        """Génère un fichier HTML"""
        self.ensure_one()
        
        html_content = self.contenu_final or ''
        
        # Créer un fichier HTML complet
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        self.fichier_genere = full_html.encode('utf-8')
        self.nom_fichier = f"{self.name.replace(' ', '_')}.html"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Fichier généré'),
                'message': _('Le fichier HTML a été généré avec succès.'),
                'type': 'success',
                'sticky': False,
            }
        }

    def _generer_docx(self):
        """Génère un fichier DOCX"""
        self.ensure_one()
        
        try:
            import base64
            from io import BytesIO
            from docxtpl import DocxTemplate
            from docx import Document
            
            # Vérifier si le template a un fichier Word
            if self.template_id.use_word_template and self.template_id.word_template:
                # Utiliser le template Word
                docx_bytes = base64.b64decode(self.template_id.word_template)
                docx_io = BytesIO(docx_bytes)
                doc = DocxTemplate(docx_io)
                
                # Préparer le contexte - comme alnas-docx, passer 'docs' pour compatibilité
                context = {}
                
                # Ajouter 'docs' si sale_order_id existe (comme dans alnas-docx)
                if self.sale_order_id:
                    context['docs'] = self.sale_order_id
                
                # Ajouter les fonctions utilitaires locales
                from ..tools import misc as misc_tools
                from functools import partial
                context.update({
                    "company": self.env.company,
                    "lang": self._context.get("lang", "fr_FR"),
                    "sysdate": fields.Datetime.now(),
                    "spelled_out": misc_tools.spelled_out,
                    "parsehtml": misc_tools.parse_html,
                    "formatdate": misc_tools.formatdate,
                    "convert_currency": misc_tools.convert_currency,
                    "formatabs": misc_tools.format_abs,
                    "rich_text": misc_tools.rich_text,
                    "render_image": partial(misc_tools.render_image, doc),
                    "html2docx": partial(misc_tools.render_html_as_subdoc, doc),
                    "add_subdoc": partial(misc_tools.add_new_subdoc, doc),
                    "replace_image": partial(misc_tools.replace_image, doc),
                    "replace_media": partial(misc_tools.replace_media, doc),
                    "replace_embedded": partial(misc_tools.replace_embedded, doc),
                    "replace_zipname": partial(misc_tools.replace_zipname, doc),
                })
                
                # Ajouter les autres variables personnalisées
                valeurs = self.get_valeurs_dict()
                context.update(valeurs)
                
                # Rendre le template avec gestion d'erreur améliorée
                try:
                    doc.render(context)
                except Exception as render_error:
                    # Vérifier si c'est une erreur de variable non définie
                    error_msg = str(render_error)
                    var_names = list(valeurs.keys())
                    
                    # Vérifier les erreurs communes de variables non définies
                    if "'docs'" in error_msg or '"docs"' in error_msg or "'docs' is undefined" in error_msg:
                        raise UserError(_(
                            'Erreur dans le template Word : la variable "docs" est utilisée mais n\'est pas définie.\n\n'
                            'Variables disponibles : %s\n\n'
                            'Vérifiez votre template Word et remplacez "docs" par une des variables disponibles, '
                            'ou ajoutez la variable "docs" dans les variables du modèle.'
                        ) % (', '.join(var_names) if var_names else 'Aucune'))
                    elif 'undefined' in error_msg.lower() or 'is not defined' in error_msg.lower():
                        # Extraire le nom de la variable depuis le message d'erreur si possible
                        raise UserError(_(
                            'Erreur dans le template Word : variable non définie.\n\n'
                            'Erreur : %s\n\n'
                            'Variables disponibles : %s\n\n'
                            'Vérifiez que toutes les variables utilisées dans le template Word sont définies dans les variables du modèle.'
                        ) % (error_msg, ', '.join(var_names) if var_names else 'Aucune'))
                    else:
                        # Si ce n'est pas une erreur de variable, relancer l'exception originale
                        raise
                
                # Sauvegarder dans un BytesIO
                output = BytesIO()
                doc.save(output)
                output.seek(0)
                
                self.fichier_genere = base64.b64encode(output.read())
                self.nom_fichier = f"{self.name.replace(' ', '_')}.docx"
            else:
                # Créer un nouveau document DOCX depuis le HTML
                from htmldocx import HtmlToDocx
                
                doc = Document()
                parser = HtmlToDocx()
                parser.add_html_to_document(self.contenu_final or '', doc)
                
                output = BytesIO()
                doc.save(output)
                output.seek(0)
                
                self.fichier_genere = base64.b64encode(output.read())
                self.nom_fichier = f"{self.name.replace(' ', '_')}.docx"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Fichier généré'),
                    'message': _('Le fichier DOCX a été généré avec succès.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except ImportError:
            raise UserError(_('Les bibliothèques docxtpl ou htmldocx ne sont pas installées. Installez-les avec: pip install docxtpl htmldocx'))
        except Exception as e:
            raise UserError(_('Erreur lors de la génération du fichier DOCX: %s') % str(e))

    def _generer_pdf(self):
        """Génère un fichier PDF"""
        self.ensure_one()
        
        try:
            from weasyprint import HTML
            from io import BytesIO
            import base64
            
            # Créer un HTML complet pour WeasyPrint
            html_content = self.contenu_final or ''
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}
        table td, table th {{
            border: 1px solid #ddd;
            padding: 8px;
        }}
        table th {{
            background-color: #f2f2f2;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            # Générer le PDF
            pdf_bytes = BytesIO()
            HTML(string=full_html).write_pdf(pdf_bytes)
            pdf_bytes.seek(0)
            
            self.fichier_genere = base64.b64encode(pdf_bytes.read())
            self.nom_fichier = f"{self.name.replace(' ', '_')}.pdf"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Fichier généré'),
                    'message': _('Le fichier PDF a été généré avec succès.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        except ImportError:
            raise UserError(_(
                'La bibliothèque WeasyPrint n\'est pas installée.\n\n'
                'Pour générer des PDF, vous devez installer WeasyPrint dans votre environnement Docker.\n\n'
                'Alternative : Utilisez le format DOCX ou HTML qui ne nécessitent pas de dépendances supplémentaires.\n\n'
                'Pour installer WeasyPrint dans Docker (si vous avez les droits) :\n'
                'docker exec -it odoo18 pip install --break-system-packages weasyprint'
            ))
        except Exception as e:
            error_msg = str(e)
            # Détecter les erreurs de dépendances système manquantes
            if 'libpango' in error_msg.lower() or 'cannot load library' in error_msg.lower():
                raise UserError(_(
                    'Erreur lors de la génération du fichier PDF : dépendances système manquantes.\n\n'
                    'WeasyPrint nécessite des bibliothèques système qui ne sont pas installées dans votre conteneur Docker.\n\n'
                    'Pour résoudre ce problème, vous devez installer les dépendances système dans votre Dockerfile :\n'
                    'RUN apt-get update && apt-get install -y \\\n'
                    '    libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libcairo2 \\\n'
                    '    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info\n\n'
                    'OU utilisez le format DOCX qui ne nécessite pas de dépendances système.'
                ))
            else:
                raise UserError(_('Erreur lors de la génération du fichier PDF: %s') % error_msg)

    def action_telecharger(self):
        """Télécharge le fichier généré"""
        self.ensure_one()
        if not self.fichier_genere:
            raise UserError(_('Aucun fichier généré!'))
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/lettre.motivation.instance/%s/fichier_genere/%s' % (
                self.id,
                self.nom_fichier or 'lettre.pdf'
            ),
            'target': 'self',
        }

