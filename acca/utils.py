import frappe

@frappe.whitelist()
def create_payment(name, ref, mode_of_payment, ref_no=None, ref_date=None):
	fee = frappe.get_doc("Fees", name)
	for row in fee.schedules:
		if row.name == ref:
			pe = frappe.new_doc("Payment Entry")
			pe.company = "K.R Education Services (Pvt) Ltd."
			pe.posting_date = frappe.utils.nowdate()
			pe.payment_type = "Receive"
			pe.mode_of_payment = mode_of_payment
			pe.party_type = "Student"
			pe.party = fee.student
			pe.paid_to = frappe.db.get_value("Mode of Payment Account", {"company":"K.R Education Services (Pvt) Ltd.", "parent":mode_of_payment}, "default_account")
			pe.paid_from = "Debtors - KRESPL"
			pe.paid_amount = row.receiveable_amount
			pe.received_amount = row.receiveable_amount
			pe.target_exchange_rate = 1
			pe.source_exchange_rate = 1
			ch = pe.append("references")
			ch.reference_doctype = "Fees"
			ch.reference_name = fee.name
			ch.allocated_amount = row.receiveable_amount
			pe.reference_no = ref_no
			pe.reference_date = ref_date
			pe.save()
			pe.submit()
	frappe.db.set_value("Fee Payment Schedule", ref, {
		"payment_receipt_date": pe.posting_date,
		"received_amount": pe.received_amount,
		"payment_reference":pe.name,
		"ref_no":ref_no,
		"ref_date":ref_date,
		"mode_of_payment":mode_of_payment
		})


@frappe.whitelist()
def remove_payent_reference(ref):
	frappe.db.set_value("Fee Payment Schedule", {"payment_reference": ref}, {
    "payment_reference":"",
    "received_amount":0,
    "payment_receipt_date":None
	})