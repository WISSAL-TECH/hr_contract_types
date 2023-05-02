# -*- coding: utf-8 -*-
import base64
from tempfile import TemporaryFile
import random
import string
from itertools import count
import dateutil.rrule as rrule
from odoo import api, fields, models, api
from datetime import date, time, timedelta
from datetime import datetime


class ContractType(models.Model):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _order = 'sequence, id'

    name = fields.Char(string='Contract Type', required=True, help="Name")
    sequence = fields.Integer(help="Gives the sequence when displaying a list of Contract.", default=10)


class ContractInherit(models.Model):
    _inherit = 'hr.contract'

    type_id = fields.Many2one('hr.contract.type', string="Employee Category",
                              required=True, help="Employee category",
                              default=lambda self: self.env['hr.contract.type'].search([], limit=1))

    cjm = fields.Monetary(string="CJM", default=0, currency_field='currency')
    salaire_annuel = fields.Monetary('Salaire annuel (brut)', currency_field='currency')
    salaire_souhait = fields.Monetary("Salaire brut souhaité", default=0, currency_field='currency')
    taux_charge = fields.Float(string="Taux de charge")
    nbr_travaille = fields.Integer(string="Nombre de jour travaillés")
    currency = fields.Many2one('res.currency', string="Devise", default=0)
    inherit_partner_values = fields.Boolean(string="Inherit Partner Values", default=True)
    wage = fields.Monetary(string="salaire de base")

    @api.onchange('cjm', 'nbr_travaille', 'taux_charge', 'inherit_partner_values')
    def _onchange_cout(self):
        for record in self:
            if record.nbr_travaille != 0 and not record.inherit_partner_values:
                record['salaire_annuel']

    @api.onchange('cjm', 'nbr_travaille', 'taux_charge')
    def _onchange_cout(self):
        for record in self:
            if record.nbr_travaille != 0 and record.taux_charge != 0:
                record['salaire_annuel'] = (record.cjm * record.nbr_travaille) / record.taux_charge
            else:
                record['salaire_annuel'] = 0
            if record.taux_charge != 0 and record.nbr_travaille != 0:
                record['cjm'] = (record['salaire_annuel'] * record.taux_charge) / record.nbr_travaille
            else:
                record['cjm'] = 0

    @api.onchange('salaire_souhait')
    def _onchange_test(self):
        if self.salaire_souhait < self.salaire_annuel:
            warning_msg = {
                'title': 'ATTENTION!',
                'message': 'Le salaire souhaité doit être supérieur ou égal au salaire actuel',
            }
            self.salaire_souhait = self.salaire_annuel
            return {'warning': warning_msg}

    @api.onchange('salaire_annuel')
    def _onchange_salaire(self):
        for record in self:
            if record.nbr_travaille != 0:
                record['cjm'] = (record['salaire_annuel'] * record.taux_charge) / record.nbr_travaille
            else:
                record['cjm'] = 0
