# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import re


class LettreMotivationTemplate(models.Model):
    """Modèle de lettre de motivation"""
    _name = 'lettre.motivation.template'
    _description = 'Modèle de Lettre de Motivation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Nom du Modèle',
        required=True,
        tracking=True,
        help='Nom du modèle de lettre de motivation'
    )

    niveau = fields.Selection(
        [
            ('niveau1', 'Niveau 1 - Variables Texte'),
            ('niveau2', 'Niveau 2 - Tableaux Dynamiques'),
            ('niveau3', 'Niveau 3 - Intégration Excel'),
        ],
        string='Niveau de Complexité',
        required=True,
        default='niveau1',
        tracking=True,
        help='Niveau de complexité du modèle'
    )

    description = fields.Text(
        string='Description',
        help='Description du modèle'
    )

    use_word_template = fields.Boolean(
        string='Utiliser un Fichier Word',
        default=False,
        help='Si activé, utilise le fichier Word uploadé comme template'
    )

    word_template = fields.Binary(
        string='Template Word (.docx)',
        help='Fichier Word (.docx) à utiliser comme template. Utilisez {{variable}} pour les variables.'
    )

    word_template_filename = fields.Char(
        string='Nom du Fichier Word',
        help='Nom du fichier Word uploadé'
    )

    contenu = fields.Html(
        string='Contenu du Modèle',
        help='Contenu HTML du modèle avec variables {{variable}} (non requis si fichier Word utilisé). Le contenu sera extrait automatiquement depuis le fichier Word si activé.'
    )

    contenu_qweb = fields.Text(
        string='Template QWeb',
        help='Template QWeb pour le rendu final (généré automatiquement)'
    )

    format_sortie = fields.Selection(
        [
            ('pdf', 'PDF'),
            ('html', 'HTML'),
            ('docx', 'DOCX'),
        ],
        string='Format de Sortie',
        default='docx',
        required=True,
        help='Format du fichier généré'
    )

    variables_ids = fields.One2many(
        'lettre.motivation.variable',
        'template_id',
        string='Variables',
        help='Variables disponibles pour ce modèle'
    )

    tableaux_ids = fields.One2many(
        'lettre.motivation.tableau',
        'template_id',
        string='Tableaux',
        help='Tableaux dynamiques (niveau 2 et 3)'
    )

    instances_ids = fields.One2many(
        'lettre.motivation.instance',
        'template_id',
        string='Lettres Générées',
        help='Historique des lettres générées'
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Désactiver pour masquer le modèle sans le supprimer'
    )

    @api.model
    def _extract_variables_from_content(self, content):
        """Extrait les variables du contenu (format {{variable}})"""
        if not content:
            return []
        # Pattern amélioré pour accepter espaces, apostrophes, caractères accentués, etc.
        # Capture tout ce qui est entre {{ et }} sauf les accolades fermantes
        pattern = r'\{\{([^}]+?)\}\}'
        variables_raw = re.findall(pattern, content)
        
        # Normaliser les variables : créer un nom technique valide
        variables = []
        for var_raw in variables_raw:
            var_raw = var_raw.strip()  # Enlever les espaces en début/fin
            if var_raw:
                # Créer un nom technique à partir du libellé
                # Remplacer espaces, apostrophes, caractères spéciaux par underscore
                var_name = re.sub(r'[^\w]', '_', var_raw)
                # Enlever les underscores multiples
                var_name = re.sub(r'_+', '_', var_name)
                # Enlever les underscores en début/fin
                var_name = var_name.strip('_')
                # Convertir en minuscules pour la cohérence
                var_name = var_name.lower()
                
                if var_name:  # S'assurer qu'on a un nom valide
                    variables.append((var_name, var_raw))  # (nom_technique, libellé_original)
        
        # Retourner les noms techniques uniques
        return list(set([v[0] for v in variables]))

    @api.onchange('contenu')
    def _onchange_contenu(self):
        """Affiche un message informatif sur la détection des variables"""
        # Note: La détection réelle se fait dans create/write pour éviter les problèmes
        # avec les enregistrements non sauvegardés
        pass

    def _convert_to_qweb(self, html_content):
        """Convertit le contenu HTML avec {{variables}} en template QWeb"""
        if not html_content:
            return ""
        
        # Remplacer {{variable}} par <t t-esc="variable"/>
        pattern = r'\{\{(\w+)\}\}'
        qweb_content = re.sub(
            pattern,
            r'<t t-esc="\1"/>',
            html_content
        )
        
        return qweb_content

    @api.constrains('use_word_template', 'word_template', 'contenu')
    def _check_template_source(self):
        """Vérifier qu'au moins une source de template est fournie"""
        for record in self:
            if record.use_word_template and not record.word_template:
                raise ValidationError(_('Veuillez uploader un fichier Word si vous activez "Utiliser un Fichier Word".'))
            if not record.use_word_template and not record.contenu:
                raise ValidationError(_('Veuillez fournir soit un contenu HTML, soit un fichier Word.'))

    @api.onchange('word_template')
    def _onchange_word_template(self):
        """Extraire le contenu HTML depuis le fichier Word et détecter les variables"""
        if self.word_template and self.use_word_template:
            try:
                html_content = self._extract_html_from_docx()
                if html_content:
                    self.contenu = html_content
                    # Détecter les variables depuis le contenu extrait
                    self._detect_and_create_variables()
            except Exception as e:
                # Si l'extraction échoue, laisser l'utilisateur gérer manuellement
                pass

    def _extract_html_from_docx(self):
        """Extrait le contenu HTML depuis un fichier Word"""
        if not self.word_template:
            return False
        
        try:
            import base64
            from io import BytesIO
            import mammoth
            
            # Décoder le fichier Word
            docx_bytes = base64.b64decode(self.word_template)
            docx_io = BytesIO(docx_bytes)
            
            # Convertir DOCX en HTML avec mammoth
            result = mammoth.convert_to_html(docx_io)
            html_content = result.value
            
            return html_content
        except ImportError:
            # Si mammoth n'est pas installé, essayer avec python-docx
            try:
                import base64
                from io import BytesIO
                from docx import Document
                from docx.oxml.text.paragraph import CT_P
                from docx.oxml.table import CT_Tbl
                from docx.table import Table
                from docx.text.paragraph import Paragraph
                
                docx_bytes = base64.b64decode(self.word_template)
                docx_io = BytesIO(docx_bytes)
                doc = Document(docx_io)
                
                html_parts = []
                for element in doc.element.body:
                    if isinstance(element, CT_P):
                        para = Paragraph(element, doc)
                        html_parts.append(f'<p>{para.text}</p>')
                    elif isinstance(element, CT_Tbl):
                        tbl = Table(element, doc)
                        html_parts.append('<table>')
                        for row in tbl.rows:
                            html_parts.append('<tr>')
                            for cell in row.cells:
                                html_parts.append(f'<td>{cell.text}</td>')
                            html_parts.append('</tr>')
                        html_parts.append('</table>')
                
                return ''.join(html_parts)
            except Exception as e:
                raise UserError(_('Impossible d\'extraire le contenu du fichier Word. Assurez-vous que le module mammoth ou python-docx est installé. Erreur: %s') % str(e))
        except Exception as e:
            raise UserError(_('Erreur lors de l\'extraction du contenu Word: %s') % str(e))

    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement le template QWeb et détecte les variables"""
        records = super().create(vals_list)
        for record in records:
            if record.contenu:
                record.contenu_qweb = record._convert_to_qweb(record.contenu)
                # Détecter et créer les variables après la création
                record._detect_and_create_variables()
            elif record.word_template and record.use_word_template:
                # Extraire le HTML depuis Word si nécessaire
                html_content = record._extract_html_from_docx()
                if html_content:
                    record.contenu = html_content
                    record.contenu_qweb = record._convert_to_qweb(html_content)
                    record._detect_and_create_variables()
        return records

    def write(self, vals):
        """Met à jour le template QWeb si le contenu change et détecte les variables"""
        result = super().write(vals)
        if 'contenu' in vals:
            for record in self:
                record.contenu_qweb = record._convert_to_qweb(record.contenu)
                # Détecter et créer les nouvelles variables
                record._detect_and_create_variables()
        elif 'word_template' in vals and vals.get('use_word_template'):
            # Extraire le HTML depuis Word si un nouveau fichier est uploadé
            for record in self:
                html_content = record._extract_html_from_docx()
                if html_content:
                    record.contenu = html_content
                    record.contenu_qweb = record._convert_to_qweb(html_content)
                    record._detect_and_create_variables()
        return result
    
    def _detect_and_create_variables(self):
        """Détecte et crée automatiquement les variables dans le contenu"""
        if not self.contenu or not self.id:
            return
        
        # Extraire les variables avec leurs libellés originaux
        pattern = r'\{\{([^}]+?)\}\}'
        variables_raw = re.findall(pattern, self.contenu)
        
        # Créer un mapping nom_technique -> libellé_original
        var_mapping = {}
        for var_raw in variables_raw:
            var_raw = var_raw.strip()
            if var_raw:
                # Créer un nom technique valide
                var_name = re.sub(r'[^\w]', '_', var_raw)
                var_name = re.sub(r'_+', '_', var_name)
                var_name = var_name.strip('_').lower()
                
                if var_name:
                    # Garder le libellé original (avec espaces, majuscules, etc.)
                    if var_name not in var_mapping:
                        var_mapping[var_name] = var_raw
        
        existing_vars = {var.name: var for var in self.variables_ids}
        
        # Créer les variables manquantes avec leurs libellés originaux
        for var_name, var_label in var_mapping.items():
            if var_name not in existing_vars:
                self.env['lettre.motivation.variable'].create({
                    'name': var_name,
                    'label': var_label,  # Utiliser le libellé original
                    'type': 'texte',
                    'template_id': self.id,
                })


