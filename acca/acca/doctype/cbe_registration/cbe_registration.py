# -*- coding: utf-8 -*-
# Copyright (c) 2021, Unilink Enterprise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from datetime import datetime, date as dd
from frappe.model.mapper import get_mapped_doc

class CBERegistration(Document):
	def before_save(self):
		self.validate()

	def on_cancel(self):
		if self.transfer_from:
			frappe.db.set_value("CBE Registration", self.transfer_from, "status", "Paid")
			frappe.db.set_value("CBE Registration", self.transfer_from, "transferred_to", "")
		frappe.db.set(self, 'status', 'Cancelled')
	def before_submit(self):
		
		if frappe.db.exists('Customer', {'acca_registration_no': self.acca_registration_no}):
			self.customer = frappe.db.get_value('Customer', {'acca_registration_no': self.acca_registration_no}, "name")
		else:
			cs = frappe.new_doc("Customer")
			cs.customer_name = self.applicant_name
			cs.acca_registration_no = self.acca_registration_no
			cs.save()
			self.customer = cs.name
		if self.amount > 0:
			self.create_payment()
		self.set_transferred_status()
		self.status = "Paid"
	def set_transferred_status(self):
		if self.transfer_from:
			frappe.db.set_value("CBE Registration", self.transfer_from, "status", "Transferred")
			frappe.db.set_value("CBE Registration", self.transfer_from, "transferred_to", self.name)

	@frappe.whitelist()
	def get_dates(self):
		cbedates = []
		dates = frappe.get_all('CBE Datesheet Paper', filters={'paper':self.cbe_paper}, fields=["parent"])
		for d in dates:
			date1 = frappe.db.get_value('CBE Paper Datesheet', d["parent"], 'exam_date')
			if frappe.utils.nowdate() <= datetime.strptime(str(date1), '%Y-%m-%d').strftime("%Y-%m-%d"):
				date = date1.strftime("%d-%m-%Y")
				cbedates.append(date)
		return cbedates

	@frappe.whitelist()
	def get_amount(self):
		return frappe.db.get_value("CBE Datesheet Paper", {
			'paper': self.cbe_paper, 
			'parent': frappe.db.get_value("CBE Paper Datesheet", {'exam_date': str(datetime.strptime(self.cbe_exam_date, '%d-%m-%Y').strftime("%Y-%m-%d"))}, "name")
			}, 'amount')

	@frappe.whitelist()
	def get_tr_amount(self, date):
		return frappe.db.get_value("CBE Datesheet Paper", {
			'paper': self.cbe_paper, 
			'parent': frappe.db.get_value("CBE Paper Datesheet", {'exam_date': str(datetime.strptime(date, '%d-%m-%Y').strftime("%Y-%m-%d"))}, "name")
			}, 'amount')

	@frappe.whitelist()
	def validate(self):
		count = frappe.db.get_value("CBE Registration", {'shift':self.shift, 'cbe_exam_date': self.cbe_exam_date, "docstatus":1, "status":"Paid"}, "count(name)") or 0
		if count >= 45:
			frappe.throw('The qouta for this exam date and shift has been completed. Please select another shift or date.')
		return count

	@frappe.whitelist()
	def reg(self):
		if frappe.db.exists('CBE Registration', {'acca_registration_no':self.acca_registration_no}):
			return frappe.get_doc('CBE Registration', {'acca_registration_no':self.acca_registration_no})


	@frappe.whitelist()
	def create_payment(self):
		si = frappe.new_doc("Sales Invoice")
		si.customer = self.customer
		si.company = "K.R Education Services (Pvt) Ltd."
		si.is_pos = True
		si.set_posting_time = True
		si.cbe_registration = self.name
		si.posting_date = self.application_date
		si.pos_profile = 'CBE Registration'
		item = si.append("items")
		if self.transfer_from:
			item.item_code = "Transfer Charges"
		else:	
			item.item_code = frappe.db.get_value("CBE Paper", self.cbe_paper, "item")
		item.qty = 1
		item.cost_center = "Main - KRESPL"
		item.rate = self.amount
		payment = si.append("payments")
		payment.mode_of_payment = self.payment_mode
		payment.amount = self.amount
		si.debit_to = "CBE Debtors - KRESPL"
		si.save()
		si.submit()
		#self.payment_reference = si.name
		self.payment_received_by = si.owner

@frappe.whitelist()
def transfer(source_name, target_doc=None):
	doclist = get_mapped_doc("CBE Registration", source_name, {
		"CBE Registration": {
			"doctype": "CBE Registration",
			"field_map": {
                "name": "transfer_from",
                "" : "application_date",
                "amount": "previous_paid_amount",
                0:"amount"
            }				
		}

	}, target_doc, ignore_permissions=True)
	return doclist