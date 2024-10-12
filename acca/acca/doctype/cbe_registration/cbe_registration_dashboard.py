from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'cbe_registration',
		'transactions': [
			{
				'label': _('Payment'),
				'items': ['Sales Invoice']
			}
		]
	}