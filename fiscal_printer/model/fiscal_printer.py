#!/usr/bin/python
# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP Venezuela (<http://openerp.com.ve>).
#    All Rights Reserved Credits
#
#    Coded by: Eduardo Ochoa    <eduardo.ochoa@clusterbrands.com.ve>
#                               <elos3000@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from openerp.osv.orm import except_orm, BaseModel
from openerp.osv import osv, fields
from openerp.tools.translate import _

class proxy (osv.Model):

    _name = 'fiscal_printer.proxy'
    _columns = {
        'connection_name': fields.char('Connection Name', size=255,
                                       required=True),
        'url': fields.char('Local Proxy Url', size=255,
                           required=True)
    }


class brand(osv.Model):

    _name = 'fiscal_printer.brand'
    _rec_name = 'name'
    _columns = {
        'name': fields.char(size=50)
    }


class model(osv.Model):

    _name = 'fiscal_printer.model'
    _rec_name = 'name'
    _columns = {
        'name': fields.char(size=50),
        'brand_id': fields.many2one('fiscal_printer.brand')
    }


class printer(osv.Model):
    
    _inherit = "generic.device"
    _name = 'fiscal_printer.printer'
    
    def get_printer(self, cr, uid, json=False, context=None):
        context = context or {}
        printer = {}
        wrk = self.read_workstation(cr, uid, [], context=context)
        p_id = self.search(cr, uid, [('workstation', '=', wrk),
                                 ('enabled', '=', True)])
        if not p_id:
            self._print_error("Error",
                              _("This POS does not have configured a fiscal printer"))
        else:
            if json:
                printer = self._get_device(cr,uid,p_id,context=context)
            else:
                printer = self.browse(cr,uid,p_id,context=context)[0]
        return printer

    def read_workstation(self, cr, uid, ids, context=None):
        context = context or {}
        response = self.send_command(cr, uid, ids, 'read_workstation',
                                     context=context)
        return response.get('workstation') or ""

    def has_pending_reduce(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'has_pending_reduce', 
                                     params, context=context)
        return response.get('reduce')

    def print_report_x(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'print_report_x_http', 
                                     params, context=context)
        return response

    def print_report_z(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'print_report_z', 
                                     params, context=context)
        return response

    def read_payment_methods(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'read_payment_methods', 
                                     params, context=context)
        return True

    def write_payment_methods(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        payment_methods = []
        printer = self.browse(cr, uid, ids)[0]
        for pm in printer.payment_method_ids:
            payment_methods.append({'code': str(pm.code),
                                    'description': str(pm.description)})
        params.update({'payment_methods': payment_methods})
        response = self.send_command(cr, uid, ids, 
                                     'write_payment_methods', params,
                                     context=context)
        return True

    def read_tax_rates(self, cr, uid, ids, context=None):
        context = context or {}
        tax_rates = {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'read_tax_rates', params, 
                                     context=context)
        tax_rates = response.get('tax_rates')
        obj = self.pool.get('fiscal_printer.tax_rate')
        for tr in tax_rates:
            tax_id = obj.search(cr, uid, [('code', '=', tr.get('code'))],
                                context=context)
            if not tax_id:
                vals = {'printer_id': ids[0],
                        'current_value': tr.get('value'),
                        'value': tr.get('value'),
                        'description': tr.get('description'),
                        'code': tr.get('code')
                        }
                obj.create(cr, uid, vals, context=context)
            else:
                obj.write(cr, uid, tax_id, {'current_value': tr.get('value')},
                          context=context)
        return True

    def write_tax_rates(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        tax_rates = []
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        printer = self.browse(cr, uid, ids)[0]
        for tax in printer.tax_rate_ids:
            tax_rates.append({'code': tax.code, 'value': tax.value})
        params.update({'tax_rates': tax_rates})
        response = self.send_command(cr, uid, ids, 'write_tax_rates', 
                                     params,context=context)
        return True

    def read_headers(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'read_headers', params,
                                     context=context)
        headers = response.get('headers')
        obj = self.pool.get('fiscal_printer.header')
        for header in headers:
            if header.strip() != "":
                header_id = obj.search(
                    cr, uid, [('current_value', '=', header.rstrip())],
                    context=context)
                if not header_id:
                    vals = {'printer_id': ids[0],
                            'current_value': header.rstrip(),
                            'value': header.rstrip(),
                            }
                    obj.create(cr, uid, vals, context=context)
        return True

    def write_headers(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        headers = []
        header_ids = []
        printer = self.browse(cr, uid, ids)[0]
        for header in printer.header_ids:
            if (header.value != header.current_value):
                headers.append(header.value)
                header_ids.append(header.id)
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        params.update({'headers': headers})
        response = self.send_command(cr, uid, ids, 'write_headers', params,
                                context=context)
        if (response.get('exec')):
            for id in header_ids:
                obj = self.pool.get('fiscal_printer.header')
                brw = obj.browse(cr, uid, id)
                obj.write(cr, uid, id, {'current_value': brw.value},
                          context=context)

        return True

    def read_footers(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'read_footers', params, 
                                     context=context)
        footers = response.get('footers')
        obj = self.pool.get('fiscal_printer.footer')
        for footer in footers:
            if footer.strip() != "":
                footer_id = obj.search(
                    cr, uid, [('current_value', '=', footer.rstrip())],
                    context=context)
                if not footer_id:
                    vals = {'printer_id': ids[0],
                            'current_value': footer.rstrip(),
                            'value': footer.rstrip(),
                            }
                    obj.create(cr, uid, vals, context=context)
        return True

    def write_footers(self, cr, uid, ids, context=None):
        context = context or {}
        footers = []
        footer_ids = []
        params = {}
        printer = self.browse(cr, uid, ids)[0]
        for footer in printer.footer_ids:
            if (footer.value != footer.current_value):
                footers.append(footer.value)
                footer_ids.append(footer.id)
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        params.update({'footers': footers})
        response = self.send_command(cr, uid, ids, 'write_footers',
                                     params, context=context)
        if (response.get('exec')):
            for id in footer_ids:
                obj = self.pool.get('fiscal_printer.footer')
                brw = obj.browse(cr, uid, id,context=context)
                obj.write(cr, uid, id, {'current_value': brw.value}, 
                          context=context)
        return True

    def read_serial(self, cr, uid, ids, context=None):
        context = context or {}
        params = {}
        params["printer"] = self._get_device(cr, uid, ids, context=context)
        response = self.send_command(cr, uid, ids, 'read_printer_serial',
                                     params, context=context)
        serial = response.get('serial')
        self.write(cr, uid, ids, {'serial': serial}, context=context)
        return True

    def _check_active_printer_uniqueness(self, cr, uid, ids, context=None):
        brw = self.browse(cr, uid, ids)[0]
        wrk = brw.workstation
        ids = self.search(
            cr, uid, [('workstation', '=', wrk), ('enabled', '=', True)])
        return len(ids) <= 1

    def default_get(self, cr, uid, fields, context=None):
        context = context or {}
        printers = self.send_command(cr, uid, [],'get_supported_printers',context=context)
       
        pb_obj = self.pool.get('fiscal_printer.brand')
        pm_obj = self.pool.get('fiscal_printer.model')
        for brand in printers:
            brand_id = pb_obj.search(cr, uid, [('name', '=', brand)],
                                     context=context)
            if not brand_id:
                brand_id = [pb_obj.create(cr, uid, {'name': brand},
                            context=context)]
            for model in printers[brand]:
                m = pm_obj.search(cr, uid, [('name', '=', model)],
                                  context=context, count=True)
                if (m == 0):
                    pm_obj.create(cr, uid, {'brand_id': brand_id[0],
                                            'name': model}, context)
        res = {}
        wrk = self.read_workstation(cr, uid, [], context=context)
        res.update({"workstation": wrk})
        return res

    _columns = {
        'name': fields.char(string='Name', size=50, required=True),
        'brand': fields.many2one('fiscal_printer.brand',
                                 string='Brand', required=True),
        'model': fields.many2one('fiscal_printer.model',
                                 string='Model', required=True),
        'port': fields.char(string='Port', size=100, required=True),
        'workstation': fields.char(string='Workstation', size=255, required=True, readonly=True),
        'type': fields.boolean('Ticket Printer'),
        'serial': fields.char(string='Serial', size=50),
        'enabled': fields.boolean(string="Active"),
        'payment_method_ids': fields.one2many('fiscal_printer.payment_method',
                                              'printer_id', string="Payment Methods"),
        'payment_instrument_ids': fields.one2many('fiscal_printer.payment_instrument',
                                                  'printer_id', string="Payment Instrument"),
        'tax_rate_ids': fields.one2many('fiscal_printer.tax_rate',
                                        'printer_id', string="Tax Rates"),
        'measure_unit_ids': fields.one2many('fiscal_printer.measure_unit',
                                            'printer_id', string="Unit of Measure"),
        'header_ids': fields.one2many('fiscal_printer.header',
                                      'printer_id', string="Header"),
        'footer_ids': fields.one2many('fiscal_printer.footer',
                                      'printer_id', string="Footers"),
    }

    _constraints = [
        (_check_active_printer_uniqueness,
         _("Only one active printer allowed per workstation"), [])

    ]


class payment_method(osv.Model):

    _name = 'fiscal_printer.payment_method'
    _rec_name = 'code' 
    _columns = {
        'printer_id': fields.many2one('fiscal_printer.printer', ondelete='cascade'),
        # 'account_journal_id': fields.many2one('account.journal',
        #                                       string='Payment Method', domain=[('journal_user', '=', 'True')]),
        'code': fields.char(string='Code', size=2),
        'description': fields.char(string='Description', size=50),
        'current_description': fields.char(string='Current Description', size=50),
    }

    _defaults = {
        'current_description': lambda *a: "Not available"
    }

class payment_instrument(osv.Model):
    _name = 'fiscal_printer.payment_instrument'

    def onchange_journal(self, cr, uid, ids, journal_id, context=None):
        context = context or {}
        vals = {}
        if journal_id:
            obj = self.pool.get('account.journal')
            journal = obj.browse(cr, uid, journal_id, context=context)
            vals.update({'type': journal.type, 'instrument_id': False})
        return {'value': vals}

    _columns = {
        'printer_id': fields.many2one('fiscal_printer.printer', ondelete='cascade'),
        'journal_id':  fields.many2one('account.journal',
                                        string='Journal', 
                                        domain=[('journal_user', '=', 'True')]),
        'type': fields.char('Type', size=64),
        'instrument_id': fields.many2one('payment_instrument.instrument', 'Instrument'), 
        'payment_method_id': fields.many2one('fiscal_printer.payment_method', 'Code'),      
    }


class tax_rate(osv.Model):

    _name = 'fiscal_printer.tax_rate'
    _columns = {
        'printer_id': fields.many2one('fiscal_printer.printer', ondelete='cascade'),
        'account_tax_id': fields.many2one('account.tax',
                                          string='Tax', domain=[('type_tax_use', '=', 'sale')]),
        'code': fields.char(string='Tax Code', size=4),
        'description': fields.char(string='Description', size=255),
        'value': fields.float(digits=(12, 2), string='Value'),
        'current_value': fields.float(digits=(12, 2), string='Current Value'),
    }
    _defaults = {
        'current_value': lambda *a: 0.0
    }


class measure_unit (osv.Model):

    _name = 'fiscal_printer.measure_unit'
    _columns = {
        'printer_id': fields.many2one('fiscal_printer.printer', ondelete='cascade'),
        'product_uom_id': fields.many2one('product.uom',
                                          string='Tax', domain=[('active', '=', 'True')]),
        'Name': fields.char(size=255, string='Name'),
        'current_code': fields.char(size=255, string='Current Code'),
        'code': fields.char(size=2, string='Code')
    }


class header(osv.Model):

    _name = 'fiscal_printer.header'
    _columns = {
        'printer_id': fields.many2one('fiscal_printer.printer', ondelete='cascade'),
        'current_value': fields.char(size=255, string='Current Value'),
        'value': fields.char(size=255, string='Value')
    }

    _defaults = {
        'current_value': lambda *a: "Not available"
    }


class footer(osv.Model):

    _name = 'fiscal_printer.footer'
    _columns = {
        'printer_id': fields.many2one('fiscal_printer.printer', ondelete='cascade'),
        'current_value': fields.char(size=255, string='Current Value'),
        'value': fields.char(size=255, string='Value')
    }

    _defaults = {
        'current_value': lambda *a: "Not available"
    }