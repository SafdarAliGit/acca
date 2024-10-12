# -*- coding: utf-8 -*-
# Copyright (c) 2021, Unilink Enterprise and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class AttendanceTool(Document):
	def mark_attendance(self):
		if frappe.db.exists("Gym Member", {'barcode_no':self.barcode_no, "enabled":1}):
			mem = frappe.db.get_value("Gym Member", {'barcode_no':self.barcode_no}, ["name", "member_name"])
			if not frappe.db.exists("Gym Attendance", {"member": mem[0], "attendance_date":frappe.utils.nowdate()}):
				att = frappe.new_doc("Gym Attendance")
				att.member = mem[0]
				att.attendance_date = frappe.utils.nowdate()
				att.check_in = frappe.utils.now().split(' ')[1]
				att.save()
				return mem[1], frappe.utils.now().split(' ')[1]
			else:
				return mem[1], "1"
		elif frappe.db.exists("Verge Student", {'barcode_no':self.barcode_no, "enabled":1}):
			mem = frappe.db.get_value("Verge Student", {'barcode_no':self.barcode_no}, ["name", "student_name"])
			if not frappe.db.exists("Verge Attendance", {"student": mem[0], "attendance_date":frappe.utils.nowdate()}):
				att = frappe.new_doc("Verge Attendance")
				att.student = mem[0]
				att.attendance_date = frappe.utils.nowdate()
				att.check_in = frappe.utils.now().split(' ')[1]
				att.save()
				return mem[1], frappe.utils.now().split(' ')[1]
			else:
				return mem[1], "1"
		elif frappe.db.exists("Student", {'gr_number':self.barcode_no, "enabled":1}):
			mem = frappe.db.get_value("Student", {'gr_number':self.barcode_no}, ["name", "title"])
			dd = frappe.db.get_value("Fees", {"student":mem[0], "docstatus":1, "outstanding_amount":[">", 0]}, "count(name)")
			if dd:
				if dd > 1:
					return mem[1], "2"	
			if not frappe.db.exists("Student Attendance Log", {"student": mem[0], "attendance_date":frappe.utils.nowdate()}):
				att = frappe.new_doc("Student Attendance Log")
				att.student = mem[0]
				att.attendance_date = frappe.utils.nowdate()
				att.check_in = frappe.utils.now().split(' ')[1]
				att.save()
				std = mem[1]+" ("+self.barcode_no+")"
				return std, frappe.utils.now().split(' ')[1]
			else:
				return mem[1], "1"