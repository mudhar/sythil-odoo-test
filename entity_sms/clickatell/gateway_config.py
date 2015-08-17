from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime

class sms_response():
     response_string = ""
     response_code = ""

class clickatell_core(models.Model):

    _name = "esms.clickatell"
    
    api_url = fields.Char(string='API URL')
    
    def send_sms(self, sms_gateway_id, to_number, sms_content, my_model_name, my_record_id, my_field_name):
        sms_account = self.env['esms.accounts'].search([('id','=',sms_gateway_id)])
       
        gateway_name = "CLICKATELL"
        format_number = to_number
        if " " in format_number: format_number.replace(" ", "")
        if "+" in format_number: format_number = format_number.replace("+", "")
        clickatell_url = "http://api.clickatell.com/http/sendmsg?user=" + sms_account.clickatell_username + "&password=" + sms_account.clickatell_password + "&api_id=" + sms_account.clickatell_api_id + "&from=" + self.env.user.partner_id.mobile + "&to=" + format_number + "&text=" + sms_content
        response_string = requests.get(clickatell_url)
        
        response_code = ""
        if "ERR: 002" in response_string.text:
	    response_code = "BAD CREDENTIALS"
	elif "ERR: 301" in response_string.text:
	    response_code = "INSUFFICIENT CREDIT"
	elif "ERR:" in response_string.text:
	    response_code = "FAILED DELIVERY"
	else:
	    response_code = "SUCCESSFUL"
       
        
        my_model = self.env['ir.model'].search([('model','=',my_model_name)])
        my_field = self.env['ir.model.fields'].search([('name','=',my_field_name)])
        
        if response_code == "SUCCESSFUL":
            esms_history = self.env['esms.history'].create({'field_id':my_field[0].id, 'record_id': my_record_id,'model_id':my_model[0].id,'from_mobile':self.env.user.partner_id.mobile, 'to_mobile':to_number,'sms_content':sms_content,'status_string':response_string.text, 'gateway_name': gateway_name, 'direction':'O','my_date':datetime.utcnow(), 'status_code':response_code})
        
        my_sms_response = sms_response()
        my_sms_response.response_string = response_string.text
        my_sms_response.response_code = response_code
        
        return my_sms_response

class clickatell_conf(models.Model):

    _inherit = "esms.accounts"
    
    clickatell_username = fields.Char(string='API Usernname')
    clickatell_password = fields.Char(string='API Password')
    clickatell_api_id = fields.Char(string='API ID')