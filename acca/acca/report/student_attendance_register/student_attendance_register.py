# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, getdate
from frappe import msgprint, _
from calendar import monthrange

status_map = {
	"Present": "P"
	}

day_abbr = [
	"Mon",
	"Tue",
	"Wed",
	"Thu",
	"Fri",
	"Sat",
	"Sun"
]

def execute(filters=None):
	if not filters: filters = {}

	if filters.hide_year_field == 1:
		filters.year = 2020

	conditions, filters = get_conditions(filters)
	columns, days = get_columns(filters)
	att_map = get_attendance_list(conditions, filters)
	if not att_map:
		return columns, [], None, None

	std_map = get_student_details()

	data = []
	record, std_att_map = add_data(std_map, att_map, filters, conditions)
	data += record

	chart_data = get_chart_data(std_att_map, days)

	return columns, data, None, chart_data

def get_chart_data(std_att_map, days):
	labels = []
	datasets = [
		{"name": "Absent", "values": []},
		{"name": "Present", "values": []},
	]
	for idx, day in enumerate(days, start=0):
		p = day.replace("::65", "")
		labels.append(day.replace("::65", ""))
		total_absent_on_day = 0
		total_leave_on_day = 0
		total_present_on_day = 0
		total_holiday = 0
		for std in std_att_map.keys():
			if std_att_map[std][idx]:
				if std_att_map[std][idx] == "A":
					total_absent_on_day += 1
				if std_att_map[std][idx] in ["P", "WFH"]:
					total_present_on_day += 1
				if std_att_map[std][idx] == "HD":
					total_present_on_day += 0.5
					total_leave_on_day += 0.5
				if std_att_map[std][idx] == "L":
					total_leave_on_day += 1


		datasets[0]["values"].append(total_absent_on_day)
		datasets[1]["values"].append(total_present_on_day)


	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	chart["type"] = "line"

	return chart

def add_data(student_map, att_map, filters, conditions):

	record = []
	std_att_map = {}
	for std in student_map:
		std_det = student_map.get(std)
		if not std_det or std not in att_map:
			continue

		row = []
		if filters.group_by:
			row += [" "]
		row += [std, std_det.title]

		total_p = total_a = 0.0
		std_status_map = []
		for day in range(filters["total_days_in_month"]):
			status = None
			status = att_map.get(std).get(day + 1)

			abbr = status_map.get(status, "")
			std_status_map.append(abbr)

			if  filters.summarized_view:
				if status == "Present":
					total_p += 1
				else:
					total_a += 1

		row += std_status_map

		if not filters.get("student"):
			filters.update({"student": std})
			conditions += " and student = %(student)s"
		elif not filters.get("student") == std:
			filters.update({"student": std})
		std_att_map[std] = std_status_map
		record.append(row)

	return record, std_att_map

def get_columns(filters):
	columns = []
	columns += [
		_("Student") + ":Link/Student:120", _("Student Name") + ":Data/:120"
	]
	days = []
	for day in range(filters["total_days_in_month"]):
		date = str(filters.year) + "-" + str(filters.month)+ "-" + str(day+1)
		day_name = day_abbr[getdate(date).weekday()]
		days.append(cstr(day+1)+ " " +day_name +"::65")	
	columns += days
	return columns, days

def get_attendance_list(conditions, filters):
	attendance_list = frappe.db.sql("""select student, day(attendance_date) as day_of_month,
		"Present" as status from `tabStudent Attendance Log` where 1=1 %s order by student, attendance_date""" %
		conditions, filters, as_dict=1)
	if not attendance_list:
		msgprint(_("No attendance record found"), alert=True, indicator="orange")
	att_map = {}
	for d in attendance_list:
		att_map.setdefault(d.student, frappe._dict()).setdefault(d.day_of_month, "")
		att_map[d.student][d.day_of_month] = d.status
	return att_map

def get_conditions(filters):
	if not (filters.get("month") and filters.get("year")):
		msgprint(_("Please select month and year"), raise_exception=1)
	filters["total_days_in_month"] = monthrange(cint(filters.year), cint(filters.month))[1]
	conditions = " and month(attendance_date) = %(month)s and year(attendance_date) = %(year)s"
	if filters.get("student"): conditions += " and student = %(student)s"
	return conditions, filters

def get_student_details():
	std_map = {}
	query = """select name, title from `tabStudent` where enabled = 1"""
	student_details = frappe.db.sql(query , as_dict=1)
	for d in student_details:
		std_map[d.name] = d
	return std_map

@frappe.whitelist()
def get_attendance_years():
	year_list = frappe.db.sql_list("""select distinct YEAR(attendance_date) from `tabStudnet Attendance Log` ORDER BY YEAR(attendance_date) DESC""")
	if not year_list:
		year_list = [getdate().year]

	return "\n".join(str(year) for year in year_list)
