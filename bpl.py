from openerp.osv import fields, osv
import random

class bpl_officer_registration(osv.osv):
    _name = "bpl.officer"
    _description = "Officer registration details"
    _columns = {
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'name': fields.char('Name', size=128, required=True, select=True),
        'nic_no': fields.char('NIC No', size=128,),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'city': fields.char('City', size=128),
        'country_id': fields.many2one('res.country', 'Country'),
        'website': fields.char('Website', size=64, help="Website"),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile', size=64),
        'fax': fields.char('Fax', size=64),
        'email': fields.char('Email', size=240),
        'job_position': fields.char('Job Position', size=240),
        }
    _defaults = {
#     'bpl_company_id': get_default_company
     }

bpl_officer_registration()

class bpl_worker_registration(osv.osv):
        
    def on_change_indic_cost(self, cr, uid, ids, cost_ids, context=None):
        totalsum = 0.0
        for element in cost_ids:
            totalsum += element[1]
        return {
            'value': {
                'sum_cost': totalsum,
            }
        }        
        
    def on_change_company(self, cr, uid, ids, company_id, context=None):
        if not company_id:
            return {'value': {
                'bpl_estate_id': False
            }}
        company = self.pool.get('bpl.company.n.registration').browse(cr, uid, company_id, context=context)
        estatelist = company.estates
        if estatelist:
            return { 
                    'value': {
                              'bpl_estate_id': estatelist[0].id
                              }
                    }
            
        else:
            return {
                    'value': {
                              'bpl_estate_id': False
                              }
                    }
    
    def on_change_estate(self, cr, uid, ids, estate_id, context=None):
        if not estate_id:
            return {'value': {
                'bpl_estate_id': False
            }}
        estate = self.pool.get('bpl.estate.n.registration').browse(cr, uid, estate_id, context=context)
        divisionslist = estate.divisions
        if divisionslist:
            return { 
                    'value': {
                              'bpl_division_id': divisionslist[0].id
                              }
                    }
        else:
            return {
                    'value': {
                              'bpl_division_id': False
                              }
                    }
        
    def create(self, cr, uid, values, context=None):
        values['register_no'] = self.pool.get('ir.sequence').get(cr, uid, 'bpl.worker')
        values['employer_no'] = self.pool.get('ir.sequence').get(cr, uid, 'bpl.employer')
        return super(bpl_worker_registration, self).create(cr, uid, values, context=context)

    def _get_result(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = 'BPL001/' + record.register_no
        return res
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
        return self.pool.get('bpl.company.n.registration').search(cr, uid, [])[0]
    
    _name = "bpl.worker"
    _description = "Worker registration details"
    _columns = {
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'register_no': fields.char('Register No', size=32, help='Register No', readonly=True),  # employer wise ,estate wise
        'employer_no': fields.char('Employer No', type='char', readonly=True),
        'epf_no': fields.char('EPF No', size=32, help='EPF No'),
#        'epf_no': fields.function(_get_result, string='EPF No', type='char'),
        'epf': fields.boolean('EPF', help="EPF eligible or not"),
        'emp_no': fields.char('Emp No', type='char', readonly=True),
        'nic_no': fields.char('NIC No', size=32, help='NIC No'),
        'name': fields.char('Name with Initials', size=256, help='Name it to easily find a record'),
        'name_in_full': fields.char('Name in Full', size=256, help='Name it to easily find a record'),
        'date_of_birth': fields.date('Date of Birth'),
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender'),
        'civil_status': fields.selection([('single', 'Single'), ('married', 'Married')], 'Civil Status'),
        'is_married': fields.boolean('Married', help="Is Married or not"),
        'father_name': fields.char('Father Name', size=256, help='Father Name'),
        'mother_name': fields.char('Mother Name', size=256, help='Mother Name'),
        'spouse_name': fields.char('Spouse Name', size=256, help='Spouse Name'),
        'date_appointed': fields.date('Date Appointed'),
        'religion_id': fields.many2one('bpl.religion', 'Religions', help='Religion'),
        'festival_id': fields.many2one('bpl.festival', 'Festival', help='Festival'),
        'status': fields.selection([('permanent', 'Permanent'), ('casual', 'Casual')], 'Category'),
        'date_of_approval': fields.date('Date of Approval'),
        'default_work': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Default Work'),
        'union_id': fields.many2one('bpl.union', 'Union', help='Union'),
        'estate_resident': fields.boolean('Estate Resident', help="Estate resident or not"),
        
        'address_line_1': fields.char('Address Line 1', size=256, help='Address Line 1'),
        'address_line_2': fields.char('Address Line 2', size=256, help='Address Line 2'),
        'address_line_3': fields.char('Address Line 3', size=256, help='Address Line 3'),
        
        'occupation_code': fields.char('Occupation Code', size=32, help='Occupation Code'),
        'is_active': fields.boolean('Inactive', help="Is active or not"),
        'current_status': fields.selection([('active', 'Active'), ('inactive', 'Inactive'), ('suspend', 'Suspend'), ('terminate', 'Terminate'), ('dismiss', 'Dismiss')], 'Current Status'),
        }
    _defaults = {
     'register_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'bpl.worker'),
     'employer_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'bpl.employer'),
#     'employer_no': _get_result,
     }


bpl_worker_registration()

class relegion_registration(osv.osv):
    _name = "bpl.religion"
    _description = "Religions"
    _columns = {
        'name': fields.char('Religion Name', size=256, required=True, help='Religion Name'),
    }

relegion_registration()

class festival_registration(osv.osv):
    _name = "bpl.festival"
    _description = "Festivals"
    _columns = {
        'name': fields.char('Festival Name', size=256, required=True, help='Festival Name'),
    }

festival_registration()

class union_registration(osv.osv):
    _name = "bpl.union"
    _description = "Unions"
    _columns = {
        'name': fields.char('Union Name', size=256, required=True, help='Union Name'),
    }

union_registration()

class company_define(osv.osv):
    
    def onchange_is_company(self, cr, uid, ids, is_company, context=None):
        print('this works my on change')
        return {'value': {'min': is_company}}
    
    _name = "bpl.company.define"
    _description = "Company Definition"
    _columns = {
        'department_id':fields.many2one('bpl.division.n.registration', 'Division', required=True, help='Division'),
        'is_company': fields.boolean('Numbering Unit', help="Is numbering unit or not"),
        'min_no': fields.integer('Min'),
        'max_no': fields.integer('Max'),
        'current_no': fields.integer('Current No'),
    }

company_define()


class employer_epf(osv.osv):
    _name = "bpl.employer.epf"
    _description = "Employer's EPF no"
    _columns = {
                'department_id': fields.many2one('bpl.estate.n.registration', 'Estate Name', required=True),
                'epf_no': fields.char('EPF No', size=32, required=True, help='EPF No'),
    }

employer_epf()

class bpl_work_offer(osv.osv):
    
    def onchange_division(self, cr, uid, ids, division_id, context=None):
        if division_id:
            division_self = self.pool.get('bpl.division.n.registration')
            division_browse = division_self.browse(cr, uid, division_id, context=context)
            result_id = division_browse.id
            worker_object = self.pool.get('bpl.worker')            
            search_condition = [
                              ('bpl_division_id', '=', result_id)
                              ]
            worker_list = worker_object.search(cr, uid, search_condition, context=context)
            return worker_list

    def on_change_country(self, cr, uid, ids, country_id, context=None):
        currency_id = self._get_euro(cr, uid, context=context)
        if country_id:
            currency_id = self.pool.get('res.country').browse(cr, uid, country_id, context=context).currency_id.id
        return {'value': {'currency_id': currency_id}}
    
    def _get_selection(self, cursor, user_id, context=None):
        return (
                ('head_office', 'Head Office'),
                ('estate', 'Estate'))
    
    def _sel_func(self, cr, uid, context=None):
        obj = self.pool.get('bpl.officer')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name', 'id'], context)
        res = [(r['id'], r['name']) for r in res]
        return res
    
    _name = "bpl.work.offer"
    _description = "BPL Work Offer"
    _columns = {
#        'user_id': fields.many2one('bpl.officer', 'User Name'),
        'user_id': fields.many2one('bpl.officer', 'User Name'),
        'date_of_offer': fields.date('Offer date'),
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate'),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
#        'report_for': fields.selection([('head_office', 'Head Office'), ('estate', 'Estate')], 'Report for'),
        'report_for' : fields.selection(_get_selection, 'Report for'),
        'payment_type': fields.selection([('normal_work', 'Normal Work'), ('cash_work', 'Cash Work')], 'Payment Type'),
        'select_by': fields.selection([('by_name', 'By Names'), ('by_count', 'By Count')], 'Select  By'),
        'no_of_workers': fields.integer('No of Workers'),
        'work_type': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Work Type'),
        'total_workers': fields.integer('Total Workers'),
        'selected_tea_workers_line_ids': fields.one2many('bpl.selected.tea.workers.line', 'tea_line_worker_id', 'Tea Workers', ondelete="cascade"),
        'selected_rubber_workers_line_ids': fields.one2many('bpl.selected.rubber.workers.line', 'rubber_line_worker_id', 'Rubber Workers', ondelete="cascade"),
        'selected_sundry_workers_line_ids': fields.one2many('bpl.selected.sundry.workers.line', 'sundry_line_worker_id', 'Sundry Workers', ondelete="cascade"),
        'is_confirmed': fields.boolean('Is Confirmed', help="confirmed"),
    }
    
    _defaults = {
                 'is_confirmed': False,
                 # 'user_id':_sel_func,
                 # 'user_id': lambda self, cr, uid, ctx: self.pool['bpl.officer']._sel_func(cr, uid, object='bpl.officer', context=ctx)
                 }

bpl_work_offer()

class selected_tea_workers_line_ids(osv.osv):
    _name = 'bpl.selected.tea.workers.line'
    _description = 'BPL Selected Tea Workers line'
    _columns = {
        'tea_line_worker_id':fields.many2one('bpl.work.offer', 'Tea Worker Line', ondelete='cascade', help='Worker Line'),
        'worker_id':fields.many2one('bpl.worker', 'Tea Worker', ondelete='cascade', help='Tea Worker'),
        'is_selected': fields.boolean('Select', help="Selected or not"),
        }
        
selected_tea_workers_line_ids()

class selected_rubber_workers_line_ids(osv.osv):
    _name = 'bpl.selected.rubber.workers.line'
    _description = 'BPL Selected Rubber Workers line'
    _columns = {
        'rubber_line_worker_id':fields.many2one('bpl.work.offer', 'Rubber Worker', ondelete='cascade', help='Worker'),
        'worker_id':fields.many2one('bpl.worker', 'Rubber Worker', ondelete='cascade', help='Rubber Worker'),
        'is_selected': fields.boolean('Select', help="Selected or not"),
        }
        
selected_rubber_workers_line_ids()

class selected_sundry_workers_line_ids(osv.osv):
    _name = 'bpl.selected.sundry.workers.line'
    _description = 'BPL Selected Sundry Workers line'
    _columns = {
        'sundry_line_worker_id':fields.many2one('bpl.work.offer', 'Sundry Worker', ondelete='cascade', help='Sundry Worker'),
        'worker_id':fields.many2one('bpl.worker', 'Sundry Worker', ondelete='cascade', help='Sundry Worker'),
        'is_selected': fields.boolean('Select', help="Selected or not"),
        }
        
selected_sundry_workers_line_ids()

class company_estate_division(osv.osv):
    
    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        return self.pool.get('bpl.company.n.registration').search(cr, uid, [])[0]

    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        return True    
    
    _name = 'bpl.company.estate.division'
    _description = 'bpl company estate division mapping'
    _columns = {
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate'),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division'),

        'company_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', relation='bpl.company.n.registration', string="Country New",
        multi='address'),
        
        'state_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', domain="[('company_id', '=', bpl_company_id)]",
        relation='bpl.estate.n.registration', string="Estate New"),
                }
    
company_estate_division()
#######################################################################################################
class company_new_registration(osv.osv):
    _name = "bpl.company.n.registration"
    _description = "Company"
    _columns = {
                'name': fields.char('Company Name', size=128, required=True),
                'estates': fields.one2many('bpl.estate.n.registration', 'company_id', 'Estate')                                        
    }
# Bill of Material
company_new_registration()

class estate_new_registration(osv.osv):
    _name = "bpl.estate.n.registration"
    _description = "Estates"
    _columns = {
        'name': fields.char('Estate Name', size=128, required=True),
        'company_id': fields.many2one('bpl.company.n.registration', 'Company Name', select=True),
        'divisions': fields.one2many('bpl.division.n.registration', 'estate_id', 'Division')
    }

estate_new_registration()

class division_new_registration(osv.osv):
    _name = "bpl.division.n.registration"
    _description = "Divisions"
    _columns = {
        'name': fields.char('Division Name', size=128, required=True),
        'estate_id': fields.many2one('bpl.estate.n.registration', 'Estate Name', select=True),
    }

division_new_registration()


# //////////////////////////////////////////////Work  update//////////////////////////////////////////////////////////////////////

class sundry_work_registration(osv.osv):
    _name = "bpl.sundry.work.registration"
    _description = "Sundry Works"
    _columns = {
        'name': fields.char('Work Name', size=256, required=True, help='Work Name'),
    }

sundry_work_registration()

class bpl_work_update(osv.osv):
    _name = "bpl.work.update"
    _description = "BPL Work Update"
    _columns = {
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'ref_no': fields.char('Reference No', size=10,),
        'offered_date': fields.date('Offered Date'),
        'gang_no': fields.char('Gang No', size=10, required=True),
        'selected_tea_workers_update_line_ids': fields.one2many('bpl.selected.tea.workers.update.line', 'work_id', 'Tea Work Offers', ondelete="cascade"),
        'selected_rubber_workers_update_line_ids': fields.one2many('bpl.selected.rubber.workers.update.line', 'work_id', 'Rubber Offers', ondelete="cascade"),
        'selected_sundry_workers_update_line_ids': fields.one2many('bpl.selected.sundry.workers.update.line', 'work_id', 'Sundry Offers', ondelete="cascade"),
        'casual_eligible': fields.boolean('Casual Eligible', help="Casual Eligible"),
    }

bpl_work_update()
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

class selected_tea_workers_update_line_ids(osv.osv):
    _name = 'bpl.selected.tea.workers.update.line'
    _description = 'BPL Selected Tea update Workers line'
    _columns = {
        'work_id':fields.many2one('bpl.work.update', 'Tea Work Offers', ondelete='cascade', help='Work Offers'),
        'epf_no': fields.char('EPF No', size=32, help='EPF No'),
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'tea_norm':fields.integer('Norm - Tea'),
        'tea_hrs_worked':fields.integer('Hours worked'),
        'tea_total_kgs':fields.integer('Total Kgs'),
        'tea_over_kgs':fields.integer('Over Kgs'),
        }
        
selected_tea_workers_update_line_ids()

class selected_rubber_workers_update_line_ids(osv.osv):
    _name = 'bpl.selected.rubber.workers.update.line'
    _description = 'BPL Selected Rubber Workers line'
    _columns = {
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'work_id':fields.many2one('bpl.work.update', 'Rubber Work Offers', ondelete='cascade', help='Work Offers'),
        'epf_no': fields.char('EPF No', size=32, help='EPF No'),
        'rubber_norm':fields.integer('Norm - Rubber'),
        'rubber_hrs_worked':fields.integer('Hours worked'),
        'rubber_total_kgs':fields.integer('Total Kgs'),
        'rubber_over_kgs':fields.integer('Over Kgs'),
        'rubber_scrap_kgs':fields.integer('Scrap Kgs'),
        }
        
selected_rubber_workers_update_line_ids()

class selected_sundry_workers_update_line_ids(osv.osv):
    _name = 'bpl.selected.sundry.workers.update.line'
    _description = 'BPL Selected Sundry Workers line'
    _columns = {
        'work_id':fields.many2one('bpl.work.update', 'Sundry Work Offers', ondelete='cascade', help='Work Offers'),
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'epf_no': fields.char('EPF No', size=32, help='EPF No'),
        'sundry_hrs_worked':fields.integer('Hours worked'),
        'sundry_work_id':fields.many2one('bpl.sundry.work.registration', 'Sundry Work', help='Sundry Work'),
        }
        
selected_sundry_workers_update_line_ids()
