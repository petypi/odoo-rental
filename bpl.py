from openerp.osv import fields, osv
import random

class bpl_res_users(osv.osv):
    
    def demo_create_function(self, cr, uid, values, context=None):
        res_users_obj = self.pool.get('res.users')
        res_users_obj.create(cr, uid, {
            'login': values['login'],
            'password': values['password'],
            'company_id': values['bpl_company_id'],
            'partner_id': values['officer_id'],
            'name': values['login'],
        }, context=context)
        return super(res_users, self).create(cr, uid, values, context=context)

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id

    # _inherit = "res.users"
    _name = "bpl.res.users"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'officer_id':fields.many2one('bpl.officer', 'Officer', domain="[('bpl_estate_id','=',bpl_estate_id)]"),
        'user_id':fields.many2one('res.users', 'User'),
    }
    _defaults = {
                 'bpl_company_id':_default_company,
     }

    
    
bpl_res_users()

    
class bpl_officer_registration(osv.osv):
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id

    _name = "bpl.officer"
    _description = "Officer registration details"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id', '=', bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'name': fields.char('Name', size=128, required=True),
        'nic_no': fields.char('NIC No', size=128, required=True),
        'emp_no': fields.char('EMP No', size=128,),
        'epf_no': fields.char('EPF No', size=128,),
        'street': fields.char('Street', size=128),
        'street2': fields.char('Street2', size=128),
        'city': fields.char('City', size=128),
        'country_id': fields.many2one('res.country', 'Country'),
        'website': fields.char('Website', size=64, help="Website"),
        'phone': fields.char('Phone', size=64, required=True),
        'mobile': fields.char('Mobile', size=64),
        'fax': fields.char('Fax', size=64),
        'email': fields.char('Email', size=240),
        'job_position': fields.many2one('bpl.designation', 'Designation', required=True),
        'work_for': fields.selection([('estate', 'Estate'), ('head_office', 'Head Office')], 'Work For', required=True),
        'date_of_birth': fields.date('Date of Birth', required=True),
        'date_of_appointed': fields.date('Date of Appointed', required=True),
        'is_active': fields.boolean('Inactive', help="Is active or not"),
        'current_status': fields.selection([('suspend', 'Suspend'), ('terminate', 'Terminate'), ('dismiss', 'Dismiss')], 'Inactive Status'),

        }
    _defaults = {
                 'bpl_company_id':_default_company,
                 'work_for':'head_office',
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
            emp_no = employer_no[0].epf_no or False
            return {'value': {'employer_no':  emp_no}}            

    def _max_reg_no(self, cr, uid, context=None):
        res = {}
        cr.execute("""
        select COALESCE(register_no, 'W00001') as reg_no        
        from bpl_worker 
        where id in 
        (select coalesce(max(id),0) from bpl_worker)        
        """)
        rows = cr.fetchall()
        if len(rows) == 0:
            return 'W00001'
        else:
            res = rows[0][0]
            emp_no = str(res)
            emp_int = emp_no[1:6]
            emp_no_int = int(emp_int)
            result = 'W' + (str(emp_no_int + 1).zfill(5))
            return result        

        
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
            
            current_no = no_define_object_no and no_define_object_no[0].current_no or False
            return {'value': {'emp_no': current_no }}


    def create(self, cr, uid, values, context=None):
        values['register_no'] = self.pool.get('ir.sequence').get(cr, uid, 'bpl.worker')
        emp_no_i = values['emp_no']
        emp_no = int(emp_no_i)
        emp_no += 1
        division_id = values['bpl_division_id']
        no_define_object = self.pool.get('bpl.company.define')
        no_define_object_browse = no_define_object.browse(cr, uid, division_id, context=context)
        if no_define_object_browse:
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


    def on_change_company(self, cr, uid, ids, bpl_company_id, context=None):
        v = {}
        search_condition = [
                              ('user_id', '=', uid)
                              ]
        bpl_res_users_ids = self.pool.get('bpl.res.users').search(cr, uid, search_condition, context=context)
        officer = self.pool.get('bpl.officer').browse(cr, uid, bpl_res_users_ids, context=context)[0]
        if officer.work_for == 'estate':
            if officer.bpl_estate_id:
                estate_id = officer.bpl_estate_id.id
                return {'value': {'bpl_estate_id': estate_id }}
        else:
            return {'value': v}

    _name = "bpl.worker"
    _description = "Worker registration details"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'register_no': fields.char('Register No', size=32, help='Register No'),
        'employer_no': fields.char('Employer No', type='char'),
        'epf_no': fields.char('EPF No', size=32, help='EPF No'),
        'epf': fields.boolean('EPF', help="EPF eligible or not"),
        'emp_no': fields.char('Emp No', type='char'),
        'nic_no': fields.char('NIC No', size=32, help='NIC No'),
        'initials': fields.char('Initials', size=256),
        'name': fields.char('Surname', size=256, help='Name it to easily find a record'),
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
                 'bpl_company_id':_default_company,
                 # 'bpl_estate_id':_default_estate,
                 'register_no': _max_reg_no,
                 'civil_status':'single',
                 'date_appointed':fields.date.context_today
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
        'work_type': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Default Work Type'),
        'is_company': fields.boolean('Numbering Unit', help="Is numbering unit or not"),
        'name': fields.char('Name'),
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
        work_v = {}
        
        division_ids = self.pool.get('bpl.company.define').search(cr, uid, [('department_id', '=', division_id)])
        division_obj = self.pool.get('bpl.company.define').browse(cr, uid, division_ids)[0]
        work_type = division_obj.work_type
        work_v = {'work_type': work_type}
        
        tea_v = {}
        tea_list_data = []
        
        rubber_v = {}
        rubber_list_data = []
        
        sundry_v = {}
        sundry_list_data = []
        
        if division_id:
            
            tea_worker_ids = self.pool.get('bpl.worker').search(cr, uid, [('bpl_division_id', '=', division_id), ('default_work', '=', 'tea')])
            for record in self.pool.get('bpl.worker').browse(cr, uid, tea_worker_ids):
                tea_list_data.append({'worker_id': record.id, 'worker_emp_no': record.emp_no})
            tea_v['selected_tea_workers_line_ids'] = tea_list_data
            
        if division_id:    
            rubber_worker_ids = self.pool.get('bpl.worker').search(cr, uid, [('bpl_division_id', '=', division_id), ('default_work', '=', 'rubber')])
            for record in self.pool.get('bpl.worker').browse(cr, uid, rubber_worker_ids):
                rubber_list_data.append({'worker_id': record.id, 'worker_emp_no': record.emp_no})
            rubber_v['selected_rubber_workers_line_ids'] = rubber_list_data
            
        if division_id:
            sundry_worker_ids = self.pool.get('bpl.worker').search(cr, uid, [('bpl_division_id', '=', division_id), ('default_work', '=', 'sundry')])
            for record in self.pool.get('bpl.worker').browse(cr, uid, sundry_worker_ids):
                sundry_list_data.append({'worker_id': record.id, 'worker_emp_no': record.emp_no})
            sundry_v['selected_sundry_workers_line_ids'] = sundry_list_data
            
            tea_v.update(rubber_v)
            tea_v.update(sundry_v)
            tea_v.update(work_v)
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

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id

    def _default_estate_demo(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            company_id = user.company_id.id
        estate_ids = self.pool.get('bpl.estate.n.registration').search(cr, uid, [('company_id', '=', company_id)])
        for estate_id in self.pool.get('bpl.estate.n.registration').browse(cr, uid, estate_ids, context=context):
            return estate_id  # TODO

    def default_work_type(self, cr, uid, context=None):
        division = self.pool.get('bpl.company.define').browse(cr, uid, uid, context=context)
        
    
    def button_total(self, cr, uid, ids, context=None):
        tea_worker_line_ids = self.browse(cr, uid, ids[0], context=context).selected_tea_workers_line_ids or []
        rubber_worker_line_ids = self.browse(cr, uid, ids[0], context=context).selected_rubber_workers_line_ids or []
        sundry_worker_line_ids = self.browse(cr, uid, ids[0], context=context).selected_sundry_workers_line_ids or []
        other_worker_line_ids = self.browse(cr, uid, ids[0], context=context).selected_other_workers_line_ids or []
        total_workers = len(tea_worker_line_ids) + len(rubber_worker_line_ids) + len(sundry_worker_line_ids) + len(other_worker_line_ids)
        self.write(cr, uid, ids, {'total_workers': total_workers}, context=context)
        return True

    _name = "bpl.work.offer"
    _description = "BPL Work Offer"
    _columns = {
        'user_id': fields.many2one('bpl.officer', 'User Name'),
        'date_of_offer': fields.date('Offer Date'),
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate'),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'report_for' : fields.selection(_get_selection, 'Report for'),
        'payment_type': fields.selection([('normal_work', 'Normal'), ('cash_work', 'Cash')], 'Payment Type'),
        'select_by': fields.selection([('by_name', 'Names'), ('by_count', 'Count')], 'Offer  By'),
        
        'norm':fields.float('Norm'),
        'checkroll_no': fields.integer('Checkroll No'),
        'gang_no': fields.integer('Gang'),
        'field_no': fields.integer('Field No'),
        'sequence_no': fields.char('Sequence No', size=10, help='Sequence No'),
        
        'no_of_workers': fields.integer('No of Workers'),
        'work_type': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Work Type'),
        'total_workers': fields.integer('Total Workers'),
        'selected_tea_workers_line_ids': fields.one2many('bpl.selected.tea.workers.line', 'tea_line_worker_id', 'Tea Workers', ondelete="cascade"),
        'selected_rubber_workers_line_ids': fields.one2many('bpl.selected.rubber.workers.line', 'rubber_line_worker_id', 'Rubber Workers', ondelete="cascade"),
        'selected_sundry_workers_line_ids': fields.one2many('bpl.selected.sundry.workers.line', 'sundry_line_worker_id', 'Sundry Workers', ondelete="cascade"),
        
        'selected_other_workers_line_ids': fields.one2many('bpl.selected.other.workers.line', 'other_line_worker_id', 'From Other Divisions', ondelete="cascade"),
        
        'is_confirmed': fields.boolean('Is Confirmed', help="confirmed"),
        'work_update_id':fields.many2one('bpl.work.update', 'Work Update'),
    }

    _defaults = {
                 'is_confirmed': False,
                 'date_of_offer': fields.date.context_today,
                 'bpl_company_id':_default_company,
                 'select_by':'by_name',
                 'payment_type':'normal_work',
                 'sequence_no': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'bpl.work.offer'),
                 }

bpl_work_offer()

class selected_tea_workers_line_ids(osv.osv):
    
    def on_change_worker_emp_no(self, cr, uid, ids, worker_emp_no):
        worker_id = self.pool.get('bpl.worker').search(cr, uid, [('emp_no', '=', worker_emp_no)])
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_id': worker_obj[0].id}}
    
    def on_change_worker_id(self, cr, uid, ids, worker_id):
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_emp_no': worker_obj.emp_no}}
    
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
    
    def on_change_worker_emp_no(self, cr, uid, ids, worker_emp_no):
        worker_id = self.pool.get('bpl.worker').search(cr, uid, [('emp_no', '=', worker_emp_no)])
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_id': worker_obj[0].id}}

    def on_change_worker_id(self, cr, uid, ids, worker_id):
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_emp_no': worker_obj.emp_no}}        
    
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
    
    def on_change_worker_emp_no(self, cr, uid, ids, worker_emp_no):
        worker_id = self.pool.get('bpl.worker').search(cr, uid, [('emp_no', '=', worker_emp_no)])
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_id': worker_obj[0].id}}
    
    def on_change_worker_id(self, cr, uid, ids, worker_id):
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_emp_no': worker_obj.emp_no}}        
    
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

class selected_other_workers_line_ids(osv.osv):

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id    
    
    def on_change_worker_emp_no(self, cr, uid, ids, worker_emp_no):
        worker_id = self.pool.get('bpl.worker').search(cr, uid, [('emp_no', '=', worker_emp_no)])
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_id': worker_obj[0].id}}
    
    def on_change_worker_id(self, cr, uid, ids, worker_id):
        worker_obj = self.pool.get('bpl.worker').browse(cr, uid, worker_id)
        return {'value': {'worker_emp_no': worker_obj.emp_no}}        
    
    _name = 'bpl.selected.other.workers.line'
    _description = 'BPL Selected Other Workers line'
    _columns = {
                'other_line_worker_id':fields.many2one('bpl.work.offer', 'From Other Divisions', ondelete='cascade', help='other Worker'),
                'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
                'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
                'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
                'worker_emp_no': fields.char('EMP No', size=32, help='EPF No'),
                'worker_id':fields.many2one('bpl.worker', 'Worker', ondelete='cascade', help='other Worker', domain="[('bpl_division_id','=',bpl_division_id)]"),
                'is_selected': fields.boolean('Select', select=True, help="Selected or not"),
                }
    _defaults = {
                 'is_selected': True,
                 'bpl_company_id':_default_company,
                 }

selected_other_workers_line_ids()

class company_estate_division(osv.osv):

    def _get_address_data(self, cr, uid, ids, field_names, arg, context=None):
        return self.pool.get('res.company').search(cr, uid, [])[0]

    def _set_address_data(self, cr, uid, company_id, name, value, arg, context=None):
        return True

    _name = 'bpl.company.estate.division'
    _description = 'bpl company estate division mapping'
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate'),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division'),
        'company_id': fields.function(_get_address_data, fnct_inv=_set_address_data, type='many2one', relation='res.company', string="Country New",
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
        'company_id': fields.many2one('res.company', 'Company Name', select=True),
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
    
    def on_change_estate(self, cr, uid, ids, estate_id, context=None):
        work_offer_v = {}
        work_offer_list_data = []
        if estate_id:
            estate_object = self.pool.get('bpl.estate.n.registration')
            estate_browse = estate_object.browse(cr, uid, estate_id, context=context)
            result_estate_id = estate_browse.id
            
            work_offer_ids = self.pool.get('bpl.work.offer').search(cr, uid, [('bpl_estate_id', '=', result_estate_id)])
            for record in self.pool.get('bpl.work.offer').browse(cr, uid, work_offer_ids):
                work_offer_list_data.append({'id': record.id,
                                             'bpl_division_id': record.bpl_division_id.id,
                                             'date_of_offer': record.date_of_offer,
                                             'payment_type': record.payment_type,
                                             'select_by': record.select_by})
            work_offer_v['work_offer_id'] = work_offer_list_data
            return {'value':work_offer_v}
        
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id

    
    _name = "bpl.work.update"
    _description = "BPL Work Update"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'ref_no': fields.char('Reference No', size=10,),
        'offered_date': fields.date('Offered Date'),
        'work_offer_id':fields.one2many('bpl.work.offer', 'work_update_id', 'Work Offer'),
        'gang_no': fields.char('Gang No', size=10, required=True),
        'selected_tea_workers_update_line_ids': fields.one2many('bpl.selected.tea.workers.update.line', 'work_id', 'Tea Work Offers', ondelete="cascade"),
        'selected_rubber_workers_update_line_ids': fields.one2many('bpl.selected.rubber.workers.update.line', 'work_id', 'Rubber Offers', ondelete="cascade"),
        'selected_sundry_workers_update_line_ids': fields.one2many('bpl.selected.sundry.workers.update.line', 'work_id', 'Sundry Offers', ondelete="cascade"),
        'casual_eligible': fields.boolean('Casual Eligible', help="Casual Eligible"),
     
     }
    _defaults = {
                 'bpl_company_id':_default_company,
                 'offered_date':fields.date.context_today
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

#=================================================================================================================================

class bank_registration(osv.osv):
    
    def on_change_name(self, cr, uid, ids, name):
        branch_v = {}
        branch_list_data = []
        if name:
            bank_id = self.pool.get('bpl.bank.registration').search(cr, uid, [('name', '=', name)])
            branch_ids = self.pool.get('bpl.branch.registration').search(cr, uid, [('bank_id', '=', bank_id)])
            for record in self.pool.get('bpl.branch.registration').browse(cr, uid, branch_ids):
                branch_list_data.append({'branch_id': record.id, 'name': record.name})
            branch_v['branch_id'] = branch_list_data
            return {'value':branch_v}
    
    _name = "bpl.bank.registration"
    _description = "Bank"
    _columns = {
                'name': fields.char('Bank Name', size=128, required=True),
                'branch_id': fields.one2many('bpl.branch.registration', 'bank_id', 'Branch')
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

#########################################################################################################################################

class cash_advance_register(osv.osv):
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
    
    _name = "bpl.cash.advance.register"
    _description = "Cash Advance Register"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'date': fields.date('Date'),
        'amount': fields.float('Amount'),
    }
    
    _defaults = {
                 'bpl_company_id':_default_company,
                 }


cash_advance_register()

class loan_register(osv.osv):
    _name = "bpl.loan.register"
    _description = "Loan Register"
    _columns = {
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'loan_amount': fields.float('Amount'),
        'installment': fields.float('Installment'),
        'paid_amount': fields.float('Paid Amount'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
    }

loan_register()

class relegious_places(osv.osv):
    _name = "bpl.relegious.places"
    _description = "Religious Places"
    _columns = {
        'religion_id': fields.many2one('bpl.religion', 'Religion'),
        'festival_id': fields.many2one('bpl.festival', 'Festival'),
        'relegious_place': fields.char('Place', size=128, required=True),
        'relegious_location': fields.char('Location', size=128, required=True),
    }

relegious_places()

class festival_advance_register(osv.osv):
    _name = "bpl.festival.advance.register"
    _description = "Festival Advance Register"
    _columns = {
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'festival_id': fields.many2one('bpl.festival', 'Festival'),
        'festival_advance': fields.float('Amount'),
        'installment': fields.float('Installment'),
        'paid_amount': fields.float('Paid Amount'),
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
    }

festival_advance_register()

#==========================TABLE CREATE==================================================================================================
class daily_transaction_master(osv.osv):
    _name = "bpl.daily.transaction.master"
    _description = "Daily Transaction Master"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
        'worker_id': fields.many2one('bpl.worker', 'Worker'),
        'date': fields.date('Date'),
        'names': fields.float('Names'),
        'type': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Type'),
        'output': fields.float('Output'),
        'over_kgs': fields.float('Over Kgs'),
        'scrap': fields.float('Scrap'),
        'pss': fields.float('PSS'),
        'holiday_type_id': fields.many2one('bpl.holiday.type', 'Holiday Type'),

    }

daily_transaction_master()

class holiday_type(osv.osv):
    _name = "bpl.holiday.type"
    _description = "Holiday Type"
    _columns = {
                'date': fields.date('Date'),
                'name': fields.char('Holiday Type', size=50),
                }
holiday_type()

class offer_summary(osv.osv):
    _name = "bpl.work.offer.summary"
    _description = "Work Offer Summary"
    _columns = {
                'date': fields.date('Date'),
                'type': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Type'),
                'norm': fields.float('Norm'),
                'payment_type': fields.selection([('normal_work', 'Normal Work'), ('cash_work', 'Cash Work')], 'Payment Type'),
                }
offer_summary()


class rate_mapping(osv.osv):
    _name = "bpl.rate.mapping"
    _description = "Rate Mapping"
    _columns = {
                'date': fields.date('Date'),
                'name': fields.float('Rate'),
                }
rate_mapping()

class wages_mapping(osv.osv):
    _name = "bpl.wages.mapping"
    _description = "Wages Mapping"
    _columns = {
                'name': fields.selection([('tea', 'Tea'), ('rubber', 'Rubber'), ('sundry', 'Sundry')], 'Type'),
                'wage': fields.float('Wage'),
                }
wages_mapping()

class Temporary_posting_additions(osv.osv):
    _name = "bpl.temporary.posting.additions"
    _description = "Temporary Posting Additions"
    _columns = {
                'worker_id':fields.many2one('bpl.worker', 'Worker'),
                'basic': fields.float('Basic'),
                'pss': fields.float('PSS'),
                'overtime': fields.float('Overtime'),
                }
Temporary_posting_additions()

class Temporary_posting_deductions(osv.osv):
    _name = "bpl.temporary.posting.deductions"
    _description = "Temporary Posting Deductions"
    _columns = {
                'worker_id':fields.many2one('bpl.worker', 'Worker'),
                'deduction': fields.float('Deduction'),
                }
Temporary_posting_deductions()


class current_allowances(osv.osv):
    _name = "bpl.current.allowances"
    _description = "Current Allowances"
    _columns = {
                'worker_id':fields.many2one('bpl.worker', 'Worker'),
                'name': fields.char('Allowance', size=50),
                'amount': fields.float('Amount'),
                'month':fields.selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'),
            ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month'),
                }
current_allowances()

class insurance_provider(osv.osv):
    _name = "bpl.insurance.provider"
    _description = "Insurance Provider"
    _columns = {
                'name': fields.char('Insurance Company', size=50),
                }
insurance_provider()

class insurance_registration(osv.osv):
    _name = "bpl.insurance.branch"
    _description = "Branch"
    _columns = {
        'name': fields.char('Branch Name', size=128, required=True),
        'insurance_id': fields.many2one('bpl.insurance.provider', 'Insurance Name'),
    }

insurance_registration()

class loan_registration(osv.osv):
    _name = "bpl.loan.registration"
    _description = "Loan Registration"
    _columns = {
                'name': fields.char('Loan Registration', size=50),
                }
loan_registration()
