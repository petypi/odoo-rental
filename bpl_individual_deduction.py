from openerp.osv import fields, osv

class deduction_individual_data(osv.osv):
    
    def on_change_estate(self, cr, uid, ids, estate_id):
        fixed_v = {}
        fixed_list_data = []
        variable_v = {}
        variable_list_data = []      
        bank_v = {}
        bank_list_data = []
        loan_v = {}
        loan_list_data = []
        insurance_v = {}
        insurance_list_data = []
        
        
        if estate_id:            
            
            master_deduction_id = self.pool.get('bpl.deduction.estate.data').search(cr, uid, [('bpl_estate_id', '=', estate_id)])
            master_deduction_obj = self.pool.get('bpl.deduction.estate.data').browse(cr, uid, master_deduction_id)
            for deduction_record in master_deduction_obj[0].fixed_deduction_ids:
                fixed_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'deduction_name': deduction_record.deduction_name.id})
            fixed_v['fixed_deduction_ids'] = fixed_list_data
            
            for deduction_record in master_deduction_obj[0].variable_deduction_ids:
                variable_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'deduction_name': deduction_record.deduction_name.id})
            variable_v['variable_deduction_ids'] = variable_list_data
            
            for deduction_record in master_deduction_obj[0].bank_deduction_ids:
                bank_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'name': deduction_record.name.id,
                                       'bank_id':deduction_record.bank_id.id, 'branch_id':deduction_record.branch_id.id})
            bank_v['bank_deduction_ids'] = bank_list_data
            
            for deduction_record in master_deduction_obj[0].loan_deduction_ids:
                loan_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'name': deduction_record.name.id})
            loan_v['loan_deduction_ids'] = loan_list_data
            
            for deduction_record in master_deduction_obj[0].insurance_deduction_ids:
                insurance_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'name': deduction_record.name.id,
                                            'insurance_id':deduction_record.insurance_id.id, 'branch_id': deduction_record.branch_id.id})
            insurance_v['insurance_deduction_ids'] = insurance_list_data
            
            
            fixed_v.update(variable_v)
            fixed_v.update(bank_v)
            fixed_v.update(loan_v)
            fixed_v.update(insurance_v)
            return {'value':fixed_v}
    
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id
    
    _name = 'bpl.deduction.individual.data'
    _description = 'BPL Deduction individual Data'
    _columns = {
                'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
                'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
                'worker_id':fields.many2one('bpl.worker', 'Worker', ondelete='cascade', domain="[('bpl_estate_id','=',bpl_estate_id)]"),
                'fixed_deduction_ids': fields.one2many('bpl.individual.fixed.deductions', 'deduction_id', 'Fixed Deductions', ondelete="cascade"),
                'variable_deduction_ids': fields.one2many('bpl.variable.individual.deductions', 'deduction_id', 'Variable Deductions', ondelete="cascade"),
                'bank_deduction_ids': fields.one2many('bpl.individual.bank.deductions', 'deduction_id', 'Bank Deductions', ondelete="cascade"),
                'loan_deduction_ids': fields.one2many('bpl.individual.loan.deductions', 'deduction_id', 'Loan Deductions', ondelete="cascade"),
                'insurance_deduction_ids': fields.one2many('bpl.individual.insurance.deductions', 'deduction_id', 'Insurance Deductions', ondelete="cascade"),
                }
    _defaults = {
                 'bpl_company_id':_default_company,
                 }
deduction_individual_data()

class fixed_individual_deduction_ids(osv.osv):
    _name = 'bpl.individual.fixed.deductions'
    _description = 'individual Fixed Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.individual.data', 'Fixed individual Deductions'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
                'amount': fields.float('Amount', required=True),
                'active': fields.boolean('Active'),
        }

fixed_individual_deduction_ids()

class variable_individual_deduction_ids(osv.osv):
    _name = 'bpl.variable.individual.deductions'
    _description = 'individual Variable Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.individual.data', 'Variable Deductions'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
                'amount': fields.float('Amount', required=True),
                'active': fields.boolean('Active'),
        }

variable_individual_deduction_ids()

class individual_bank_deductions(osv.osv):
    _name = 'bpl.individual.bank.deductions'
    _description = 'individual Bank Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.individual.data', 'Bank Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','bank')]"),
                'bank_id': fields.many2one('bpl.bank.registration', 'Bank Name'),
                'branch_id': fields.many2one('bpl.branch.registration', 'Branch', domain="[('bank_id','=',bank_id)]"),
                'amount': fields.float('Amount', required=True),
                'start_date':fields.date('Start Date', select=True,),
                'end_date':fields.date('End Date', select=True),
                'active': fields.boolean('Active'),
        }

individual_bank_deductions()

class individual_loan_deductions(osv.osv):
    _name = 'bpl.individual.loan.deductions'
    _description = 'individual Loan Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.individual.data', 'Loan Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','loan')]"),
                'total': fields.float('Total', required=True),
                'installment': fields.float('Installment', required=True),
                'start_date':fields.date('Start Date', select=True,),
                'end_date':fields.date('End Date', select=True),
                'active': fields.boolean('Active'),
                
        }

individual_loan_deductions()

class individual_insurance_deductions(osv.osv):
    _name = 'bpl.individual.insurance.deductions'
    _description = 'individual Insurance Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.individual.data', 'Insurance Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','insurance')]"),
                'insurance_id': fields.many2one('bpl.insurance.provider', 'Company'),
                'branch_id': fields.many2one('bpl.insurance.branch', 'Branch', domain="[('insurance_id','=',insurance_id)]"),
                'installment': fields.float('Installment', required=True),
                'active': fields.boolean('Active'),
                
        }

individual_insurance_deductions()
