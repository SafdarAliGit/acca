# -*- coding: utf-8 -*-
# Copyright (c) 2021, Unilink Enterprise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MonthlyFee(Document):
	def before_submit(self):
		self.create_fees()

	def get_students(self):
		self.students= []
		students = frappe.get_all("Program Enrollment", filters={"program":self.program}, fields=["student", "student_name"])
		for std in students:
			student = self.append("students")
			student.student = std["student"]
			student.student_name = std["student_name"]
			if frappe.db.exists("Fees", {"student":std["student"]}):
				fee = frappe.get_doc("Fees", {"student":std["student"]})
				student.last_fee_period_date = fee.posting_date
				for row in fee.components:
					if row.fees_category == self.fee_category:
						student.fee_amount = row.amount

	def create_fees(self):
		for cr, std in enumerate(self.students):
			fee = frappe.new_doc("Fees")
			fee.posting_date = self.fee_period
			fee.student = std.student
			fee.program = self.program
			fee.due_date = frappe.utils.add_days(self.fee_period, 10)
			item = fee.append("components")
			item.fees_category = self.fee_category
			item.amount = std.fee_amount
			schedule = fee.append("schedules")
			schedule.due_date = fee.due_date
			schedule.receiveable_amount = std.fee_amount
			fee.monthly_fee = self.name
			fee.save()
			std.fee_reference = fee.name
			frappe.publish_realtime(
				"data_import_progress",
				{
					"current": cr + 1,
					"total": len(self.students),
					"student": std.student_name
				},
			)
