# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2014-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import logging
import time
from datetime import datetime,date,timedelta

from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_is_zero
from openerp.tools.translate import _
from openerp import tools, api, models
from openerp.addons.base.res.res_partner import format_address

import openerp.addons.decimal_precision as dp
import openerp.addons.product.product

AVAILABLE_PRIORITIES = [
    ('0', 'Very Low'),
    ('1', 'Low'),
    ('2', 'Normal'),
    ('3', 'High'),
    ('4', 'Very High'),
]

class crm_lead(format_address, osv.osv):
    """ CRM Lead Case """
    _inherit = "crm.lead"
    _rec_name = 'lead_full_name'
    
    _defaults = {
        'sequence': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'crm.demo') + ' / ' + datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%B, %Y") ,
    }
    
    def create(self, cr, uid, vals, context=None):
        print '\n create of crm lead',vals,context
        return super(crm_lead, self).create(cr, uid, vals, context=context)
        
    def onchange_cust_state_2(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id=self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value': {'cust_country_id_2': country_id}}
        return {}
        
    def convert_lead_to_dealer(self, cr, uid, ids, context):
        result = {}
        print '\n convert_lead_to_dealer',ids,context
        if ids:
            lead_obj = self.browse(cr, uid, ids, context=context)
            print '\n cont to dealer',lead_obj
            values = {
                'name' : lead_obj.name,
                'last_name' : lead_obj.last_name,
                'comp_title' : lead_obj.partner_title.id,
                'marital_status' : lead_obj.marital_status,
                'personal_no' : lead_obj.personal_no,
                'street' : lead_obj.street,
                'street2' : lead_obj.street2,
                'city' : lead_obj.city,
                'state_id' : lead_obj.state_id.id,
                'zip' : lead_obj.zip,
                'country_id' : lead_obj.country_id.id,
                'home_phone' : lead_obj.phone,
                'home_phone2' : lead_obj.home_phone,
                'work_phone' : lead_obj.work_phone,
                'fname' : lead_obj.partner_first_name,
                'lname' : lead_obj.partner_last_name,
                'address_same_yes' : lead_obj.address_same_yes,
                'street_2' : lead_obj.street_2,
                'street2_2' : lead_obj.street2_2,
                'city_2' : lead_obj.city_2,
                'state_id_2' : lead_obj.state_id_2.id,
                'zip_2' : lead_obj.zip_2,
                'country_id_2' : lead_obj.country_id_2.id,
                
                'partner_work_phone' : lead_obj.partner_work_phone,
                'partner_home_phone' : lead_obj.partner_home_phone,
                'partner_cell_phone' : lead_obj.partner_cell_phone,
                'partner_email' : lead_obj.partner_email,
                'allergies_yes' : lead_obj.allergies_yes,
                'pets_yes' : lead_obj.pets_yes,
                'children' : lead_obj.children,
                'child_1' : lead_obj.child_1,
                'child_2' : lead_obj.child_2,
                'child_3' : lead_obj.child_3,
                'child_4' : lead_obj.child_4,
                
            }
            dealer_id = self.pool.get('res.dealer').create(cr, uid, values)
            print '\n lead to dealer',dealer_id
        return result
        
    def onchange_state_id_2(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id=self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value': {'country_id_2': country_id}}
        return {}

    def onchange_stage_id(self, cr, uid, ids, stage_id, context=None):
        if not stage_id:
            return {'value': {}}
        stage = self.pool.get('crm.case.stage').browse(cr, uid, stage_id, context=context)
        if not stage.on_change:
            return {'value': {}}
        vals = {'probability': stage.probability}
        if stage.name == 'Appointment Set':
            vals['apt_attrs'] = True
        else:
            vals['apt_attrs'] = False
        
        if stage.probability >= 100 or (stage.probability == 0 and stage.sequence > 1):
                vals['date_closed'] = fields.datetime.now()
        return {'value': vals}
    
    def _get_stage_id(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if ids:
            for lead in self.browse(cr, uid, ids):
                res[lead.id] = lead.stage_id.name
        print '\n get stage id',res
        return res
        
            
    def _select_objects(self, cr, uid, context=None):
        model_pool = self.pool.get('ir.model')
        ids = model_pool.search(cr, uid, [], limit=None)
        res = model_pool.read(cr, uid, ids, ['model', 'name'])
        return [(r['model'], r['name']) for r in res] + [('', '')]
        
    def _combine(self, cr, uid, ids, field_name, args, context=None):
        values = {}
        print '\n full name of lead function',ids,field_name,context,args
        if (context and context.get('default_type') == 'lead') or (context and context.get('stage_type') == 'lead'):
            for id in ids:
                rec = self.browse(cr, uid, [id], context=context)[0]
                values[id] = {}
                values[id] = '%s %s' % (rec.name, rec.last_name)
            return values
        elif (context and context.get('default_type') == 'opportunity') or (context and context.get('stage_type') == 'opportunity'):
            for id in ids:
                rec = self.browse(cr, uid, [id], context=context)[0]
                values[id] = {}
                values[id] = '%s %s' % (rec.name, rec.last_name)
            return values
        
    def _appointment_records_of_lead(self, cr, uid, ids, field_name, arg, context=None):
        """Return the list of appointment for this lead and his child leads."""
        res = {}
        Calendar_event_pool = self.pool.get('calendar.event')
        lead_ids = []
        for lead in self.browse(cr, uid, ids, context=context):
            lead_ref = 'crm.lead'+','+str(lead.id)
            lead_ids = self.search(cr, uid, [('referred_by', '=', lead_ref)])
            lead_ids.append(lead.id)
            appointment_ids = Calendar_event_pool.search(cr, uid, [('lead_id', 'in', lead_ids)])
            res[lead.id] = appointment_ids
        return res
        
    def _lead_records_of_lead(self, cr, uid, ids, field_name, arg, context=None):
        """Return the list of leads referred by this lead."""
        res = {}
        lead_ids = []
        for lead in self.browse(cr, uid, ids, context=context):
            if lead.referred_by and str(lead.referred_by).split('(')[0] == 'crm.lead':
                lead_ids.append(lead.referred_by.id)
                res[lead.id] = lead_ids
        return res
            
    def _check_country_code(self, cr, uid, ids, context=None):
        print '\n _check_country_code',ids,context
        return True
    _constraints = [
        (_check_country_code , 'Error! Wrong format for country code.', ['home_phone_code', 'phone_code'])
    ]
    _columns = {
            'priority': fields.selection(AVAILABLE_PRIORITIES, 'Priority', select=True),
            'name': fields.char('Name', select=1, readonly=False),
            'sequence' : fields.char('Name', select=1, readonly=True),
            'last_name': fields.char('Name', select=1, readonly=False, required=True),
            'lead_full_name' : fields.function(_combine, string="Name", type='char', method=True, arg=('name', 'last_name'), store={
                'crm.lead': (lambda self, cr, uid, ids, c={}: ids, ['name', 'last_name'], 10),
            },),
            'partner_title': fields.many2one('res.partner.title', 'Title'),
            'company_owner': fields.boolean('Company Owner?'),
            'company_name': fields.many2one('res.company', 'Company'),
            'customer_code' : fields.char('Existing Customer Code'),
            'home_phone_code' : fields.char('Code'),
            'phone_code' : fields.char('Code'),
            'mobile_code' : fields.char('Code'),
            'home_phone' : fields.char('Home Phone (2)'),
            'mobile_phone_code' : fields.char('Code'),
            'mobile_phone' : fields.char('Mobile Phone (2)'),
            'work_phone_code' : fields.char('Code'),
            'work_phone' : fields.char('Work Phone'),
            'email_2' : fields.char('Email (2)'),
            'place_emp': fields.char('Place of Employment'),
            'job_title': fields.char('Job Title'),
            'marital_status': fields.selection(
                [('single', 'Single'), ('engaged', 'Engaged'), ('married', 'Married'), ('partners', 'Partners'), ('couple', 'Couple'), ('widower', 'Widower'), ('divorced', 'Divorced')],
                string='Marital Status', copy=False),
			'personal_no_code' : fields.char('Code'),
            'personal_no' : fields.char('Personal No'),
            'cust_street_2': fields.char('Street'),
            'cust_street2_2': fields.char('Street2'),
            'cust_city_2': fields.char('City'),
            'cust_country_id_2': fields.many2one('res.country', 'Country', ondelete='restrict'),
            'cust_state_id_2': fields.many2one("res.country.state", 'State', ondelete='restrict'),
            'cust_zip_2': fields.char('Zip', size=24, change_default=True),
            'image': fields.binary("Image",
                help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
            'source_id' : fields.many2one('crm.tracking.source', string="Lead Source"),
            'dealer_id' : fields.many2one('res.dealer', string="Dealer"),
            'lead_type': fields.many2one('crm.lead.type', 'Lead type'),
            'own_rent': fields.selection(
                    [('own', 'Own'), ('rent', 'Rent')],
                    string='Own or Rent?', copy=False),
            'more_comp' : fields.boolean('More Companies?'),
                    
            'partner_first_name': fields.char('First Name'),
            'partner_last_name': fields.char('Last Name'),
            'partner_email': fields.char('Email'),
            'partner_function': fields.char('Job Title'),
            'partner_place_emp': fields.char('Place of Employment'),
            'partner_cell_phone_code' : fields.char('Code'),
            'partner_cell_phone': fields.char('Cell Phone'),
            'partner_home_phone_code' : fields.char('Code'),
            'partner_home_phone': fields.char('Home Phone'),
            'partner_work_phone_code' : fields.char('Code'),
            'partner_work_phone': fields.char('Work Phone'),
            'allergies_yes': fields.selection([('yes', 'Yes'), ('no', 'No')], string="Allergies"),
            'pets_yes': fields.selection([('yes', 'Yes'), ('no', 'No')], string="Pets"),

            'children' : fields.boolean('Children'),
            'child_1': fields.char('Child 1'),
            'child_2': fields.char('Child 2'),
            'child_3': fields.char('Child 3'),
            'child_4': fields.char('Child 4'),
            'appointment_type': fields.selection(
                    [('owner', 'Owner')],
                    'Appointment Type', copy=False),
            'referred_by': fields.reference('Referred By', [('res.partner', 'Partner'),('res.dealer', 'Dealer'), ('crm.lead', 'Lead')]),
            'lead_type': fields.many2one('crm.lead.type', 'Lead type'),
            'dealer': fields.many2one('res.dealer', 'Dealer'),
            'sponsor': fields.many2one('res.partner', 'Sponsor'),
            'event_source': fields.many2one('crm.tracking.source', string='Event'),
            'section_id': fields.many2one('crm.case.section', string='Sales Team'),
            'comment_other': fields.text('Notes'),
            'comment': fields.text('Notes'),                    
            
            'company_id_1': fields.many2one('res.company', 'Company'),
            'comp1_title': fields.many2one('res.partner.title', 'Title'),
            'company_act_1': fields.text('Company Activity Domain'),
            'comp1_fiscal_id': fields.char('Fiscal ID'),
            'comp1_registry': fields.char('Registration Number'),
            'comp1_street': fields.char('Street'),
            'comp1_street2': fields.char('Street2'),
            'comp1_country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
            'comp1_state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
            'comp1_zip': fields.char('ZIP', size=24, change_default=True),
            'comp1_city': fields.char('CITY'),
            
            'company_id_2': fields.many2one('res.company', 'Company'),
            'comp2_title': fields.many2one('res.partner.title', 'Title'),
            'company_act_2': fields.text('Company Activity Domain'),
            'comp2_fiscal_id': fields.char('Fiscal ID'),
            'comp2_registry': fields.char('Registration Number'),
            'comp2_street': fields.char('Street'),
            'comp2_street2': fields.char('Street2'),
            'comp2_country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
            'comp2_state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
            'comp2_zip': fields.char('ZIP', size=24, change_default=True),
            'comp2_city': fields.char('CITY'),

            'company_id_3': fields.many2one('res.company', 'Company'),
            'comp3_title': fields.many2one('res.partner.title', 'Title'),
            'company_act_3': fields.text('Company Activity Domain'),
            'comp3_fiscal_id': fields.char('Fiscal ID'),
            'comp3_registry': fields.char('Registration Number'),
            'comp3_street': fields.char('Street'),
            'comp3_street2': fields.char('Street2'),
            'comp3_country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
            'comp3_state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
            'comp3_zip': fields.char('ZIP', size=24, change_default=True),
            'comp3_city': fields.char('CITY'),
            
            'company_id_4': fields.many2one('res.company', 'Company'),
            'comp4_title': fields.many2one('res.partner.title', 'Title'),
            'company_act_4': fields.text('Company Activity Domain'),
            'comp4_fiscal_id': fields.char('Fiscal ID'),
            'comp4_registry': fields.char('Registration Number'),
            'comp4_street': fields.char('Street'),
            'comp4_street2': fields.char('Street2'),
            'comp4_country_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
            'comp4_state_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
            'comp4_zip': fields.char('ZIP', size=24, change_default=True),
            'comp4_city': fields.char('CITY'),
            
            'address_same_yes': fields.selection([('yes', 'Yes'), ('no', 'No')]),
            'street_2': fields.char('Street'),
            'street2_2': fields.char('Street2'),
            'city_2': fields.char('City'),
            'country_id_2': fields.many2one('res.country', 'Country', ondelete='restrict'),
            'state_id_2': fields.many2one("res.country.state", 'State', ondelete='restrict'),
            'zip_2': fields.char('Zip', size=24, change_default=True),
            'result_id' : fields.many2one('appointment.result', 'Result'),
            
            'lead_id' : fields.many2one('crm.lead', 'Leads'),
            
            'appt_type' : fields.many2one('appt.type', 'Appt Type'),
            'date_set' : fields.date('Date Set'),
            'date_sold' : fields.date('Date Sold'),
            'serial_no' : fields.many2one('stock.production.lot', 'Serial #'),
            'dealer_id': fields.many2one('res.dealer', 'Dealer'),
            'dealer_position' : fields.many2one('dealer.position', 'Position'),
            'advance_date' : fields.date('Advance Date'),
            'sale_amt' : fields.char('Sale'),
            'tax_rate' : fields.char('Tax Rate'),
            'total_tax' : fields.char('Total Tax'),
            'total_sale' : fields.char('Total Sale'),
            'sponsor_id_2': fields.many2one('res.partner', 'Sponsor'),
            'lead_dealer_id': fields.many2one('res.dealer', 'Lead Dealer'),
            'assistant_id' : fields.many2one('res.users', 'Assistant'),
            'ride_along_id' : fields.many2one('res.users', 'Ride-Along'),
            'set_by' : fields.many2one('res.users', 'Set By'),
            'prob_with_sale' : fields.many2one('sale.problem', 'Problem With Sale'),
            'sale_comment' : fields.text('Sale Comments'),
            
            'pay_type': fields.many2one('account.payment.term', 'Payment Type'),
            'option' : fields.char('Options'),
            'down_payment' : fields.char('Down Payment'),
            'down_type': fields.many2one('payment.type', 'Down Type'),
            'amount_financed' : fields.char('Amount Financed'),
            'filling_fee' : fields.char('Filling Fee'),
            'reserve_amt' : fields.char('Reserve Amount'),
            'discount_amt' : fields.char('Discount Amount'),
            'sac_disc' : fields.char('S.A.C Discount'),
            'balance_due' : fields.char('Balance Due'),
            'net_sale' : fields.char('Net Sale'),
            'comment_warranty' : fields.text('Notes'),
            'comment_service' : fields.text('Notes'),
            
            
            'leads_ids': fields.function(_lead_records_of_lead, type="one2many", obj='crm.lead', string="Leads"),
            'appointment_ids': fields.function(_appointment_records_of_lead, type="one2many", obj='calendar.event', string="Appointments"),
#            'appointment_ids' : fields.one2many('calendar.event', 'lead_id', string="Appointments", readonly=True),
            'active_campaign_ids' : fields.one2many('crm.campaign', 'lead_id', string="Campaigns", domain=[('days_left', '!=', 0)]),
            'past_campaign_ids' : fields.one2many('crm.campaign', 'lead_id', string="Campaigns", domain=[('days_left', '=', 0)]),
            'call_history_ids' : fields.one2many('crm.phonecall', 'opportunity_id', string="Logged Calls", readonly=True),
            'gift_ids': fields.one2many('gift.line', 'lead_id', 'Gifts', copy=False),
            'customer_acc_inv' : fields.one2many('account.invoice', 'lead_id', string="Customer Invoice Info", readonly=True, domain=[('type', '=', 'out_invoice')]),
            'customer_payment' : fields.one2many('account.voucher', 'lead_id', string="Customer Payment Info", readonly=True, domain=[('type', '=', 'receipt')]),
            'prod_warr_ids': fields.one2many('product.warranty', 'lead_warr_id', 'Warranty Revision', copy=False),
            'prod_service_ids' : fields.one2many('product.warranty', 'lead_service_id', 'Service Revision', copy=False),
            'lead_type_button' : fields.char('Lead Type'),
            'next_action' : fields.date('Next Action', readonly=True),
            'button_stage': fields.function(_get_stage_id,
            type="char", readonly=True, string='Stage'),
            'km': fields.char('KM'),
            'apt_attrs' : fields.boolean('Apt Attrs'),
            'lead_source': fields.selection(
                    [('owner', 'Owner'), ('non owner', 'Non Owner'), ('mail exibits', 'Mail Exibits'), ('personal', 'Personal')],
                    string='Lead Source'),
            'default_add_1' : fields.boolean('Default'),
            'default_add_2' : fields.boolean('Default'),
            'default_add_3' : fields.boolean('Default'),
            
            'supervisor_id' : fields.many2one('res.dealer', 'Supervisor'),
            'assistant_id' : fields.many2one('res.dealer', 'Assistant'),
            'ride_along_id' : fields.many2one('crm.lead', 'Ride-Along'),
            'start_datetime' : fields.datetime('Starting at', required=True),
            'stop_datetime' : fields.datetime('Ending at', required=True),
            'alarm_ids': fields.many2many('calendar.alarm', 'calendar_alarm_crm_lead_rel', string='Reminders', ondelete="restrict", copy=False),
            'attendee_ids': fields.one2many('calendar.attendee', 'event_id', 'Attendees', ondelete='cascade'),
            'order_line' : fields.one2many('product.order.line', 'lead_id', 'Products'),

    }
    
#    _defaults = {
#        'name': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'crm.demo'),
#    }
    
    
#    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
#        values = {}
#        if partner_id:
#            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
#            values = {
#                'street': partner.street,
#                'street2': partner.street2,
#                'city': partner.city,
#                'state_id': partner.state_id and partner.state_id.id or False,
#                'country_id': partner.country_id and partner.country_id.id or False,
#                'zip': partner.zip,
#            }
#        return {'value': values}
        
    def show_google_map(self, cr, uid, ids, context):
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'crm_lead_extended', 'view_crm_lead_map')
        view_id = view_ref and view_ref[1] or False,
        return {
        'type': 'ir.actions.act_window',
        'name': 'Lead Location on Map',
        'res_model': 'crm.lead',
        'res_id': ids[0],
        'view_id': view_id,
        'view_type': 'form',
        'view_mode': 'form',
        'target': 'new',
        'nodestroy': True,
        }

    def onchange_lead_type(self, cr, uid, ids, lead_type, context=None):
        values = {}
        print '\n lead type ',ids,lead_type,context
        if lead_type:
            lead_type = self.pool.get('crm.lead.type').browse(cr, uid, lead_type).name
            values = {
                'lead_type_button': lead_type,
            }
        return {'value': values}
        
    def onchange_referred_by(self, cr, uid, ids, referred_by, context=None):
        result = {}
        if referred_by:
            model = referred_by.split(",")[0]
            id = referred_by.split(",")[1]
            if model == 'res.partner':
                result['value'] = {'lead_source' : 'owner'}
            else:
                result['value'] = {'lead_source' : 'non owner'}
        print '\n onchange_referred_by',ids,referred_by,context,result
        return result
    
    def onchange_add(self, cr, uid, ids, address_same_yes, context=None):
        result = {}
        partner_obj = self.browse(cr, uid, ids)
        if address_same_yes == 'yes':
            result['value'] = {'street_2': partner_obj.street, 'street2_2': partner_obj.street2, 'city_2' : partner_obj.city, 'country_id_2' : partner_obj.country_id, 'state_id_2' : partner_obj.state_id, 'zip_2' : partner_obj.zip}
        return result

    def onchange_comp1(self, cr, uid, ids, company, context=None):
        result = {}
        company_obj = self.pool.get('res.company').browse(cr, uid, company)
        result['value'] = {'comp1_street': company_obj.street, 'comp1_street2': company_obj.street2,  'comp1_country_id': company_obj.country_id, 'comp1_state_id': company_obj.state_id, 'comp1_zip': company_obj.zip, 'comp1_city' : company_obj.city, 'comp1_registry' : company_obj.company_registry, 'company_id_1' : company, 'lead_type1' : company_obj.city}
        return result

    def onchange_comp2(self, cr, uid, ids, company, context=None):
        result = {}
        company_obj = self.pool.get('res.company').browse(cr, uid, company)
        result['value'] = {'comp2_street': company_obj.street, 'comp2_street2': company_obj.street2,  'comp2_country_id': company_obj.country_id, 'comp2_state_id': company_obj.state_id, 'comp2_zip': company_obj.zip, 'comp2_city' : company_obj.city, 'comp2_registry' : company_obj.company_registry}
        return result
    
    def onchange_comp3(self, cr, uid, ids, company, context=None):
        result = {}
        company_obj = self.pool.get('res.company').browse(cr, uid, company)
        result['value'] = {'comp3_street': company_obj.street, 'comp3_street2': company_obj.street2,  'comp3_country_id': company_obj.country_id, 'comp3_state_id': company_obj.state_id, 'comp3_zip': company_obj.zip, 'comp3_city' : company_obj.city, 'comp3_vat' : company_obj.vat, 'comp3_registry' : company_obj.company_registry}
        return result

    def onchange_comp4(self, cr, uid, ids, company, context=None):
        result = {}
        company_obj = self.pool.get('res.company').browse(cr, uid, company)
        result['value'] = {'comp4_street': company_obj.street, 'comp4_street2': company_obj.street2,  'comp4_country_id': company_obj.country_id, 'comp4_state_id': company_obj.state_id, 'comp4_zip': company_obj.zip, 'comp4_city' : company_obj.city, 'comp4_vat' : company_obj.vat, 'comp4_registry' : company_obj.company_registry}
        return result
    
    
    def action_schedule_meeting(self, cr, uid, ids, context=None):
        return super(crm_lead, self).action_schedule_meeting(cr, uid, ids, context=context)
    
    def onchange_dealer(self, cr, uid, ids, dealer, context=None):
        print '\n onchange of partner',ids,context,self,dealer
        result = {}
        Dealer_pool = self.pool.get('res.dealer')
        if dealer:
            dealer_obj = Dealer_pool.browse(cr, uid, dealer)
            result['value'] = {'sponsor' : dealer_obj.sponsor.id, 'section_id' : dealer_obj.team_name.id}
        print '\n onchange dealer',result
        return result

    def do_sendmail(self, cr, uid, ids, context=None):
        for demo in self.browse(cr, uid, ids, context):
            current_user = self.pool['res.users'].browse(cr, uid, uid, context=context)

            if current_user.email:
                if self.pool['calendar.attendee']._send_mail_to_attendees(cr, uid, [att.id for att in demo.attendee_ids], email_from=current_user.email, context=context):
                    self.message_post(cr, uid, demo.id, body=_("An invitation email has been sent to attendee(s)"), subtype="calendar.subtype_invitation", context=context)
        return
        

class product_order_line(osv.osv):
    _name = 'product.order.line'
    
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            print '\n _amount_line####',line
            price = line.price_unit
            qty = line.product_uom_qty
            res[line.id] = price * qty
        return res
    
    _columns = {
            'lead_id' : fields.many2one('crm.lead', 'Lead'),
            'name': fields.text('Description', required=False, readonly=True),
            'order_id': fields.many2one('sale.order', 'Order Reference', ondelete='cascade', select=True, readonly=True),
            'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, ondelete='restrict'),
            'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
            'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute= dp.get_precision('Account')),
            'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
            'product_uom': fields.many2one('product.uom', 'Unit of Measure ', required=True),
            'serial_no' : fields.many2one('stock.production.lot', 'Serial Number'),
    }
    
    def onchange_product_id(self, cr, uid, ids, product, context=None):
        print '\n \n product_id_change of crm lead.order',product,ids,context
        context = context or {}
        result = {}
        product_obj = self.pool.get('product.product')
        if product:
            product_obj = product_obj.browse(cr, uid, product, context=context)
            result = {'price_unit' : product_obj.lst_price, 'name' : product_obj.name, 'product_uom' : product_obj.uom_id}
        return {'value': result}

class demo2sale_order(osv.osv):
    _name = 'demo2sale.order'
    _columns = {
        'partner_id' : fields.many2one('crm.lead', 'Partner'),
        'company_id' : fields.many2one('res.company', 'Company'),
    }
    
    
    def create_order(self, cr, uid, ids, context=None):
        print '\n create order%%%%%%%',ids,context
        return True

class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'connected_with' : fields.reference('Connected With', [('res.partner', 'Partner'), ('res.dealer', 'Dealer'), ('crm.lead', 'Lead')], readonly=True),
    }

    def create(self, cr, uid, vals, context=None):
        print '\n create of company',vals,context
        if context.get('connect_with') == 'lead' and context.get('active_id'):
            connect_with = 'crm.lead'+','+str(context.get('active_id'))
            vals['connected_with'] = connect_with
        elif context.get('connect_with') == 'dealer' and context.get('active_id'):
            connect_with = 'res.dealer'+','+str(context.get('active_id'))
            vals['connected_with'] = connect_with
        elif context.get('connect_with') == 'partner' and context.get('active_id'):
            connect_with = 'res.partner'+','+str(context.get('active_id'))
            vals['connected_with'] = connect_with
        return super(res_company, self).create(cr, uid, vals, context=context)
