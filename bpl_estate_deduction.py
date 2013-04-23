from openerp.osv import fields, osv

class deduction_estate_data(osv.osv):
    
    def on_change_company(self, cr, uid, ids, company_id):
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
        
        
        if company_id:            
            
            master_deduction_id = self.pool.get('bpl.deduction.master.data').search(cr, uid, [('bpl_company_id', '=', company_id)])
            master_deduction_obj = self.pool.get('bpl.deduction.master.data').browse(cr, uid, master_deduction_id)
            for deduction_record in master_deduction_obj[0].fixed_deduction_ids:
                fixed_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'deduction_name': deduction_record.deduction_name.id})
            fixed_v['fixed_deduction_ids'] = fixed_list_data
            
            for deduction_record in master_deduction_obj[0].variable_deduction_ids:
                variable_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'deduction_name': deduction_record.deduction_name.id})
            variable_v['variable_deduction_ids'] = variable_list_data
            
            for deduction_record in master_deduction_obj[0].bank_deduction_ids:
                if deduction_record.deduction_id.bpl_company_id.id == company_id:
                    bank_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'name': deduction_record.name.id})
            bank_v['bank_deduction_ids'] = bank_list_data
            
            for deduction_record in master_deduction_obj[0].loan_deduction_ids:
                if deduction_record.deduction_id.bpl_company_id.id == company_id:
                    loan_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'name': deduction_record.name.id})
            loan_v['loan_deduction_ids'] = loan_list_data
            
            for deduction_record in master_deduction_obj[0].insurance_deduction_ids:
                if deduction_record.deduction_id.bpl_company_id.id == company_id:
                    insurance_list_data.append({'deduction_id':deduction_record.deduction_id.id, 'name': deduction_record.name.id})
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
    
    _name = 'bpl.deduction.estate.data'
    _description = 'BPL Deduction Estate Data'
    _columns = {
                'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
                'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
                'fixed_deduction_ids': fields.one2many('bpl.estate.fixed.deductions', 'deduction_id', 'Fixed Deductions', ondelete="cascade"),
                'variable_deduction_ids': fields.one2many('bpl.variable.estate.deductions', 'deduction_id', 'Variable Deductions', ondelete="cascade"),
                'bank_deduction_ids': fields.one2many('bpl.estate.bank.deductions', 'deduction_id', 'Bank Deductions', ondelete="cascade"),
                'loan_deduction_ids': fields.one2many('bpl.estate.loan.deductions', 'deduction_id', 'Loan Deductions', ondelete="cascade"),
                'insurance_deduction_ids': fields.one2many('bpl.estate.insurance.deductions', 'deduction_id', 'Insurance Deductions', ondelete="cascade"),
                }
    _defaults = {
                 'bpl_company_id':_default_company,
                 }
deduction_estate_data()

class fixed_estate_deduction_ids(osv.osv):
    _name = 'bpl.estate.fixed.deductions'
    _description = 'Estate Fixed Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Fixed Estate Deductions'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
        }

fixed_estate_deduction_ids()

class variable_estate_deduction_ids(osv.osv):
    _name = 'bpl.variable.estate.deductions'
    _description = 'Estate Variable Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Variable Deductions'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction'),
        }

variable_estate_deduction_ids()

class estate_bank_deductions(osv.osv):
    _name = 'bpl.estate.bank.deductions'
    _description = 'Estate Bank Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Bank Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','bank')]"),
                'bank_id': fields.many2one('bpl.bank.registration', 'Bank Name'),
                'branch_id': fields.many2one('bpl.branch.registration', 'Branch',domain="[('bank_id','=',bank_id)]"),
        }

estate_bank_deductions()

class estate_loan_deductions(osv.osv):
    _name = 'bpl.estate.loan.deductions'
    _description = 'Estate Loan Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Loan Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','loan')]"),
        }

estate_loan_deductions()

class estate_insurance_deductions(osv.osv):
    _name = 'bpl.estate.insurance.deductions'
    _description = 'Estate Insurance Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.estate.data', 'Insurance Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','insurance')]"),
                'insurance_id': fields.many2one('bpl.insurance.provider', 'Company'),
                'branch_id': fields.many2one('bpl.insurance.branch', 'Branch',domain="[('insurance_id','=',insurance_id)]"),
        }

estate_insurance_deductions()
