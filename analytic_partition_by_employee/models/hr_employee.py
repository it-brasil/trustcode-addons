# -*- coding: utf-8 -*-
# © 2018 Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_partition_ids = fields.One2many(
        'hr.employee.partition',
        'employee_id',
        'Contas de Rateio')

    def compute_percent_per_employe(self):
        partition_groups = []
        for acc in self.employee_partition_ids.mapped('analytic_account_id'):
            if acc.partition_id:
                partition_groups.append(acc.partition_id)
            else:
                part_group = self.env['account.analytic.account'].search([
                    ('partner_id', '=', acc.partner_id.id),
                    ('partition_id', '!=', False)], limit=1).mapped(
                        'partition_id')
                partition_groups.append(part_group)
        for app in set(partition_groups):
            app.calc_percent_by_employee()

    @api.multi
    def write(self, vals):
        res = super(Employee, self).write(vals)
        if vals.get('employee_partition_ids') or vals.get('active'):
            self.compute_percent_per_employe()
        return res

    @api.model
    def create(self, vals):
        res = super(Employee, self).create(vals)
        res.compute_percent_per_employe()
        return res


class HrEmployeePartition(models.Model):
    _name = 'hr.employee.partition'

    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Conta Analitica')
    weight = fields.Float('Peso', default=1)
    employee_id = fields.Many2one(
        'hr.employee', 'Funcionário')