from openerp.osv import fields, osv
import random

class bpl_officer_registration(osv.osv):
    _name = "bpl.officer"
    _description = "Officer registration details"
    _columns = {
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'name': fields.char('Name', size=128, required=True),
        'nic_no': fields.char('NIC No', size=128,),
        'emp_no': fields.char('EMP No', size=128,),
        'epf_no': fields.char('EPF No', size=128,),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'city': fields.char('City', size=128),
        'country_id': fields.many2one('res.country', 'Country'),
        'website': fields.char('Website', size=64, help="Website"),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile', size=64),
        'fax': fields.char('Fax', size=64),
        'email': fields.char('Email', size=240),
        'job_position': fields.many2one('bpl.designation', 'Designation'),
        'work_for': fields.selection([('estate', 'Estate'), ('head_office', 'Head Office')], 'Work For'),
        'date_of_birth': fields.date('Date of Birth'),
        'date_of_appointed': fields.date('Date of Appointed'),
        'is_active': fields.boolean('Inactive', help="Is active or not"),
        'current_status': fields.selection([('suspend', 'Suspend'), ('terminate', 'Terminate'), ('dismiss', 'Dismiss')], 'Current Status'),

        }
    _defaults = {
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


    def on_change_estate(self, cr, uid, ids, estate_id, context=None):
        if estate_id:
            estate_object = self.pool.get('bpl.estate.n.registration')
            estate_browse = estate_object.browse(cr, uid, estate_id, context=context)
            result_estate_id = estate_browse.id
            search_condition = [
                              ('department_id', '=', result_estate_id)
                              ]
            employer_no_object = self.pool.get('bpl.employer.epf')
            employers_id = employer_no_object.search(cr, uid, search_condition, context=context)
            employer_no = employer_no_object.browse(cr, uid, employers_id, context=context)
            return {'value': {'employer_no': employer_no[0].epf_no }}


    def _max_reg_no(self, cr, uid, context=None):
        cr.execute("""
        select register_no as reg_no
        from bpl_worker
        where id in (select max(id) from bpl_worker)
        """)
        if cr:
            res = cr.fetchone()[0]
            emp_no = str(res)
            emp_int = emp_no[1:6]
            emp_no_int = int(emp_int)
            result = 'W' + (str(emp_no_int + 1).zfill(4))
            return result
        else:
            return 'W0001'
        
    def on_change_division(self, cr, uid, ids, division_id, context=None):
        if division_id:
            division_object = self.pool.get('bpl.division.n.registration')
            division_browse = division_object.browse(cr, uid, division_id, context=context)
            result_division_id = division_browse.id
            search_condition = [
                              ('department_id', '=', result_division_id)
                              ]
            no_define_object = self.pool.get('bpl.company.define')
            no_define_id = no_define_object.search(cr, uid, search_condition, context=context)
            no_define_object_no = no_define_object.browse(cr, uid, no_define_id, context=context)
            return {'value': {'emp_no': no_define_object_no[0].current_no }}


    def create(self, cr, uid, values, context=None):
        values['register_no'] = self.pool.get('ir.sequence').get(cr, uid, 'bpl.worker')
        emp_no = values['emp_no']
        division_id = values['bpl_division_id']
        no_define_object = self.pool.get('bpl.company.define')
        no_define_object_browse = no_define_object.browse(cr, uid, division_id, context=context)
        no_define_object_browse.write({'current_no': emp_no})
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
        return self.pool.get('bpl.company.n.registration').search(cr, uid, search_condition)[0]

    _name = "bpl.worker"
    _description = "Worker registration details"
    _columns = {
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'register_no': fields.char('Register No', size=32, help='Register No'),
        'employer_no': fields.char('Employer No', type='char'),
        'epf_no': fields.char('EPF No', size=32, help='EPF No'),
        'epf': fields.boolean('EPF', help="EPF eligible or not"),
        'emp_no': fields.char('Emp No', type='char'),
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
        'current_status': fields.selection([('suspend', 'Suspend'), ('terminate', 'Terminate'), ('dismiss', 'Dismiss')], 'Current Status'),
        }
    _defaults = {
     'register_no': _max_reg_no,
     'civil_status':'single',
     }


bpl_worker_registration()

class relegion_registration(osv.osv):
    _name = "bpl.religion"
    _description = "Religions"
    _columns = {
        'name': fields.char('Religion Name', size=256, required=True, help='Religion Name'),
    }

relegion_registration()


class bpl_designation(osv.osv):
    _name = "bpl.designation"
    _description = "Designations"
    _columns = {
        'name': fields.char('Designation', size=256, required=True, help='Designation Name'),
    }

bpl_designation()

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

    def on_change_division(self, cr, uid, ids, division_id):
        tea_v = {}
        tea_list_data = []
        
        rubber_v = {}
        rubber_list_data = []
        
        sundry_v = {}
        sundry_list_data = []
        
        if division_id:
            
            tea_worker_ids = self.pool.get('bpl.worker').search(cr, uid, [('bpl_division_id', '=', division_id)])
            for record in self.pool.get('bpl.worker').browse(cr, uid, tea_worker_ids):
                tea_list_data.append({'worker_id': record.id, 'worker_emp_no': record.emp_no})
            tea_v['selected_tea_workers_line_ids'] = tea_list_data
            
        if division_id:    
            rubber_worker_ids = self.pool.get('bpl.worker').search(cr, uid, [('bpl_division_id', '=', division_id)])
            for record in self.pool.get('bpl.worker').browse(cr, uid, rubber_worker_ids):
                rubber_list_data.append({'worker_id': record.id, 'worker_emp_no': record.emp_no})
            rubber_v['selected_rubber_workers_line_ids'] = rubber_list_data
            
        if division_id:
            sundry_worker_ids = self.pool.get('bpl.worker').search(cr, uid, [('bpl_division_id', '=', division_id)])
            for record in self.pool.get('bpl.worker').browse(cr, uid, sundry_worker_ids):
                sundry_list_data.append({'worker_id': record.id, 'worker_emp_no': record.emp_no})
            sundry_v['selected_sundry_workers_line_ids'] = sundry_list_data
            
            tea_v.update(rubber_v)
            tea_v.update(sundry_v)
            return {'value':tea_v}
            

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
        'user_id': fields.many2one('bpl.officer', 'User Name'),
        'date_of_offer': fields.date('Offer Date'),
        'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate'),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'report_for' : fields.selection(_get_selection, 'Report for'),
        'payment_type': fields.selection([('normal_work', 'Normal Work'), ('cash_work', 'Cash Work')], 'Payment Type'),
        'select_by': fields.selection([('by_name', 'Names'), ('by_count', 'Count')], 'Offer  By'),
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
                 }

bpl_work_offer()

class selected_tea_workers_line_ids(osv.osv):
    _name = 'bpl.selected.tea.workers.line'
    _description = 'BPL Selected Tea Workers line'
    _columns = {
        'tea_line_worker_id':fields.many2one('bpl.work.offer', 'Tea Worker Line', ondelete='cascade', help='Worker Line'),
        'worker_emp_no': fields.char('EMP No', size=32, help='EPF No'),
        'worker_id':fields.many2one('bpl.worker', 'Tea Worker', ondelete='cascade', help='Tea Worker'),
        'is_selected': fields.boolean('Select', select=True, help="Selected or not"),
        }
    _defaults = {
                 'is_selected': True,
                 }

selected_tea_workers_line_ids()

class selected_rubber_workers_line_ids(osv.osv):
    _name = 'bpl.selected.rubber.workers.line'
    _description = 'BPL Selected Rubber Workers line'
    _columns = {
        'rubber_line_worker_id':fields.many2one('bpl.work.offer', 'Rubber Worker', ondelete='cascade', help='Worker'),
        'worker_emp_no': fields.char('EMP No', size=32, help='EPF No'),
        'worker_id':fields.many2one('bpl.worker', 'Rubber Worker', ondelete='cascade', help='Rubber Worker'),
        'is_selected': fields.boolean('Select', select=True, help="Selected or not"),
        }
    _defaults = {
                 'is_selected': True,
                 }

selected_rubber_workers_line_ids()

class selected_sundry_workers_line_ids(osv.osv):
    _name = 'bpl.selected.sundry.workers.line'
    _description = 'BPL Selected Sundry Workers line'
    _columns = {
        'sundry_line_worker_id':fields.many2one('bpl.work.offer', 'Sundry Worker', ondelete='cascade', help='Sundry Worker'),
        'worker_emp_no': fields.char('EMP No', size=32, help='EPF No'),
        'worker_id':fields.many2one('bpl.worker', 'Sundry Worker', ondelete='cascade', help='Sundry Worker'),
        'is_selected': fields.boolean('Select', select=True, help="Selected or not"),
        }
    _defaults = {
                 'is_selected': True,
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

class company_new_registration(osv.osv):
    _name = "bpl.company.n.registration"
    _description = "Company"
    _columns = {
                'name': fields.char('Company Name', size=128, required=True),
                'estates': fields.one2many('bpl.estate.n.registration', 'company_id', 'Estate')
    }
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


class deduction_master_data(osv.osv):
    _name = 'bpl.deduction.master.data'
    _description = 'BPL Deduction Master Data'
    _columns = {
                'based_on': fields.selection([('company', 'Company'), ('estate', 'Estate'), ('division', 'Division')], 'Based On'),
                'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
                'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
                'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
                'fixed_deduction_ids': fields.one2many('bpl.fixed.deductions', 'deduction_id', 'Fixed Deductions', ondelete="cascade"),
                'variable_deduction_ids': fields.one2many('bpl.variable.deductions', 'deduction_id', 'Variable Deductions', ondelete="cascade"),
                'special_deduction_ids': fields.one2many('bpl.special.deductions', 'deduction_id', 'Special Deductions', ondelete="cascade"),
                }
    _defaults = {
                 'based_on': 'company',
                 }
deduction_master_data()

class fixed_deduction_ids(osv.osv):
    _name = 'bpl.fixed.deductions'
    _description = 'Fixed Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Fixed Deductions', ondelete='cascade'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
                'deduction_type': fields.selection([('rate', 'Rate'), ('amount', 'Amount')], 'Deduction Type'),
                'rate':fields.float('Rate'),
                'amount':fields.float('Amount'),
                'active': fields.boolean('Active', help="Active"),
        }

fixed_deduction_ids()

class variable_deduction_ids(osv.osv):
    _name = 'bpl.variable.deductions'
    _description = 'Variable Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Variable Deductions', ondelete='cascade'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
                'active': fields.boolean('Active', help="Active"),
        }

variable_deduction_ids()

class special_deduction_ids(osv.osv):
    _name = 'bpl.special.deductions'
    _description = 'Special Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Special Deductions', ondelete='cascade'),
                'special_deduction_type': fields.selection([('bank', 'Bank'), ('union', 'Union'), ('insurance', 'Insurance'), ('loan', 'Loan')], 'Deduct for'),
                'bank_id': fields.many2one('bpl.bank.deductions', 'Bank Deductions'),
                'union_id': fields.many2one('bpl.union.deductions', 'Union Deductions'),
                'insurance_id': fields.many2one('bpl.insurance.deductions', 'Insurance Deductions'),
                'loan_id': fields.many2one('bpl.loan.deductions', 'Loan Deductions'),
        }

special_deduction_ids()

class deduction_estate_data(osv.osv):
    _name = 'bpl.deduction.estate.data'
    _description = 'BPL Deduction Estate Data'
    _columns = {
                'bpl_company_id':fields.many2one('bpl.company.n.registration', 'Company', help='Company'),
                'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
                'fixed_deduction_ids': fields.one2many('bpl.fixed.deductions', 'deduction_id', 'Fixed Deductions', ondelete="cascade"),
                'variable_deduction_ids': fields.one2many('bpl.variable.deductions', 'deduction_id', 'Variable Deductions', ondelete="cascade"),
                'special_deduction_ids': fields.one2many('bpl.special.deductions', 'deduction_id', 'Special Deductions', ondelete="cascade"),
                }
    _defaults = {}
deduction_estate_data()

class fixed_estate_deduction_ids(osv.osv):
    _name = 'bpl.estate.fixed.deductions'
    _description = 'Estate Fixed Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Fixed Estate Deductions'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
                'deduction_type': fields.selection([('rate', 'Rate'), ('amount', 'Amount')], 'Deduction Type'),
                'rate':fields.float('Rate'),
                'amount':fields.float('Amount'),
                'active': fields.boolean('Active', help="Active"),
        }

fixed_estate_deduction_ids()

class variable_estate_deduction_ids(osv.osv):
    _name = 'bpl.variable.estate.deductions'
    _description = 'Estate Variable Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Variable Deductions'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
                'active': fields.boolean('Active', help="Active"),
        }

variable_estate_deduction_ids()

class special_estate_deduction_ids(osv.osv):
    _name = 'bpl.special.estate.deductions'
    _description = 'Estate Special Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Special Deductions', ondelete='cascade'),
                'special_deduction_type': fields.selection([('bank', 'Bank'), ('union', 'Union'), ('insurance', 'Insurance'), ('loan', 'Loan')], 'Deduct for'),
                'bank_id': fields.many2one('bpl.bank.deductions', 'Bank Deductions'),
                'union_id': fields.many2one('bpl.union.deductions', 'Union Deductions'),
                'insurance_id': fields.many2one('bpl.insurance.deductions', 'Insurance Deductions'),
                'loan_id': fields.many2one('bpl.loan.deductions', 'Loan Deductions'),
        }

special_estate_deduction_ids()

class bank_deductions(osv.osv):
    _name = "bpl.bank.deductions"
    _description = "Bank Deductions"
    _columns = {
                'bank_id':fields.many2one('bpl.bank.registration', 'Bank'),
                'branch_id': fields.many2one('bpl.branch.registration', 'Branch', ondelete='cascade', domain="[('bank_id','=',bank_id)]"),
                'name': fields.char('Deduction', size=256),
                'amount':fields.float('Amount'),
                'active': fields.boolean('Active'),
                }

bank_deductions()

class union_deductions(osv.osv):
    _name = "bpl.union.deductions"
    _description = "Union Deductions"
    _columns = {
                'union_id': fields.many2one('bpl.union', 'Union', help='Union'),
                'name': fields.char('Deduction', size=256),
                'amount':fields.float('Amount'),
                'active': fields.boolean('Active'),
                }

union_deductions()

class insurance_deductions(osv.osv):
    _name = "bpl.insurance.deductions"
    _description = "Insurance Deductions"
    _columns = {
                'name': fields.char('Insurance Name', size=256),
                'policy_no': fields.char('Policy No', size=256),
                'amount':fields.float('Amount'),
                'active': fields.boolean('Active'),
                }

insurance_deductions()

class loan_deductions(osv.osv):
    _name = "bpl.loan.deductions"
    _description = "Loan Deductions"
    _columns = {
                'name': fields.char('Loan Name', size=256, required=True),
                'loan_amount':fields.float('Loan Amount'),
                'installment_amount':fields.float('Installment Amount'),
                'remain_amount':fields.float('Remain Amount'),
                'active': fields.boolean('Active'),
                }

loan_deductions()

class deduction_registration(osv.osv):
    _name = "bpl.deduction.registration"
    _description = "Deduction Registration"
    _columns = {
        'name': fields.char('Deduction Name', size=256, required=True),
    }

deduction_registration()


class bank_registration(osv.osv):
    _name = "bpl.bank.registration"
    _description = "Bank"
    _columns = {
                'name': fields.char('Bank Name', size=128, required=True),
                'branches': fields.one2many('bpl.branch.registration', 'bank_id', 'Branch')
    }

bank_registration()

class branch_registration(osv.osv):
    _name = "bpl.branch.registration"
    _description = "Branch"
    _columns = {
        'name': fields.char('Branch Name', size=128, required=True),
        'bank_id': fields.many2one('bpl.bank.registration', 'Bank Name'),
    }

branch_registration()
