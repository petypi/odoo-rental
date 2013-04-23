from openerp.osv import fields, osv

class deduction_master_data(osv.osv):
    
    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            return user.company_id.id

    
    _name = 'bpl.deduction.master.data'
    _description = 'BPL Deduction Master Data'
    _columns = {
                'based_on': fields.selection([('company', 'Company')], 'Based On'),
                'bpl_company_id':fields.many2one('res.company', 'Company', help='Company'),
                'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
                'bpl_division_id':fields.many2one('bpl.division.n.registration', 'Division', help='Division', domain="[('estate_id','=',bpl_estate_id)]"),
                'fixed_deduction_ids': fields.one2many('bpl.fixed.deductions', 'deduction_id', 'Fixed Deductions', ondelete="cascade"),
                'variable_deduction_ids': fields.one2many('bpl.variable.deductions', 'deduction_id', 'Variable Deductions', ondelete="cascade"),
                'bank_deduction_ids': fields.one2many('bpl.master.bank.deductions', 'deduction_id', 'Bank Deductions', ondelete="cascade"),
                'loan_deduction_ids': fields.one2many('bpl.master.loan.deductions', 'deduction_id', 'Loan Deductions', ondelete="cascade"),
                'insurance_deduction_ids': fields.one2many('bpl.master.insurance.deductions', 'deduction_id', 'Insurance Deductions', ondelete="cascade"),
                }
    _defaults = {
                 'based_on': 'company',
                 'bpl_company_id':_default_company,
                 }
deduction_master_data()

class fixed_deduction_ids(osv.osv):
    _name = 'bpl.fixed.deductions'
    _description = 'Fixed Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Fixed Deductions', ondelete='cascade'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','fixed')]"),
        }

fixed_deduction_ids()

class variable_deduction_ids(osv.osv):
    _name = 'bpl.variable.deductions'
    _description = 'Variable Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Variable Deductions', ondelete='cascade'),
                'deduction_name':fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','variable')]"),
        }

variable_deduction_ids()

#=================================================================================================================================

class deduction_registration(osv.osv):
    
    def _check_unique_insesitive(self, cr, uid, ids, context=None):
        sr_ids = self.search(cr, 1 , [], context=context)
        lst = [x.name.lower() for x in self.browse(cr, uid, sr_ids, context=context) if x.name and x.id not in ids]
        for self_obj in self.browse(cr, uid, ids, context=context):
            if self_obj.name and self_obj.name.lower() in  lst:
                return False
            return True
    
    _name = "bpl.deduction.registration"
    _description = "Deduction Registration"
    _columns = {
        'bpl_company_id':fields.many2one('res.company', 'Company'),
        'bpl_estate_id':fields.many2one('bpl.estate.n.registration', 'Estate', help='Estate', domain="[('company_id','=',bpl_company_id)]"),
        'deduction_id':fields.many2one('bpl.deduction.master.data', 'deduction_id', readonly=True),
        'name': fields.char('Name', size=256, required=True),
        'type': fields.selection([('fixed', 'Fixed'), ('variable', 'Variable'), ('special', 'Special'), ('bank', 'Bank'), ('loan', 'Loan'), ('insurance', 'Insurance')], 'Type'),
    }
    _sql_constraints = [('deduction_registration_name_unique', 'unique(name)', 'Deduction name already exists')]
    _constraints = [(_check_unique_insesitive, 'Deduction name already exists', ['name'])]
    
deduction_registration()

class master_bank_deductions(osv.osv):
    _name = 'bpl.master.bank.deductions'
    _description = 'master Bank Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Bank Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','bank')]"),
        }

master_bank_deductions()
class master_loan_deductions(osv.osv):
    _name = 'bpl.master.loan.deductions'
    _description = 'master Loan Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Loan Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','loan')]"),
        }

master_loan_deductions()
class master_insurance_deductions(osv.osv):
    _name = 'bpl.master.insurance.deductions'
    _description = 'master Insurance Deductions'
    _columns = {
                'deduction_id':fields.many2one('bpl.deduction.master.data', 'Insurance Deductions', ondelete='cascade'),
                'name': fields.many2one('bpl.deduction.registration', 'Deduction', domain="[('type','=','insurance')]"),
        }

master_insurance_deductions()
