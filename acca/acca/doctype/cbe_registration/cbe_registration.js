// Copyright (c) 2021, Unilink Enterprise and contributors
// For license information, please see license.txt

frappe.ui.form.on('CBE Registration', {
	refresh: function(frm) {
		if(frm.doc.docstatus == 0){
			frm.trigger("cbe_paper")
		}
		if(frm.doc.docstatus == 1 && frm.doc.status != "Transferred"){

			frm.add_custom_button(("Transfer"),function(){
				frappe.model.open_mapped_doc({
							method: "acca.acca.doctype.cbe_registration.cbe_registration.transfer",
							frm: frm
						})
			})
		}
		if(frm.doc.status == "Unpaid"){
			frm.add_custom_button(("Create Payment Entry"), function(){
				/*frappe.route_options = {
					"payment_type": "Receive",
					"mode_of_payment":"Cash",
					"paid_to": "Cash - AHC",
					"paid_from": "Debtors - AHC",
					"party_type": "Customer",
					"party": frm.doc.customer
				},
				frappe.set_route("Form", "Payment Entry" , "New Payment Entry");*/
				frappe.call({method:'create_payment', doc:frm.doc, callback:function(r){frm.reload_doc()}})
			})
		}
		
	},
	submit_info(frm){
		frm.save()	
	},
	after_save(frm){
		if(frappe.session.user == "cbecandidate@alhamd.edu.pk"){
			frappe.set_route("Form", "CBE Registration", "new");
		}
	},
	cbe_paper(frm){
		
		if(frm.doc.cbe_paper){
			frappe.call({
				method:'get_dates', 
				doc:frm.doc,
				callback: function(r){
					if(r.message){
						console.log(r.message)
						frm.set_df_property('cbe_exam_date', "options", r.message)
						frm.refresh_field('cbe_exam_date');
						//frm.set_value('cbe_exam_date', r.message[0])
					}
				}
			})	
		}
			
	},
	transfer_charges(frm){
		set_amount(frm)
	},
	
	cbe_exam_date(frm){
		
		if(frm.doc.cbe_paper && frm.doc.cbe_exam_date){
			frappe.call({
				method:'get_amount', 
				doc:frm.doc,
				callback: function(r){
					console.log(r.message)
					if(r.message){
						frm.set_value('exam_charges', r.message)	
						set_amount(frm)
					}
					else{
						frm.set_value('exam_charges', 0)
					}
					
					
				}
			})	
		}
			
	},
	acca_registration_no(frm){
		frappe.call({
			method:'reg', 
			doc:frm.doc, 
			callback:function(r){
				if(r.message){
					var p = r.message;
					frm.set_value("applicant_name", p.applicant_name)
					frm.set_value("whatsapp", p.whatsapp)
					frm.set_value("date_of_birth", p.date_of_birth)
					frm.set_value("gender", p.gender)
					frm.set_value("student_email_id", p.student_email_id)
					frm.set_value("student_mobile_number", p.student_mobile_number)
					frm.set_value("nationality", p.nationality)
					frm.set_value("area", p.area)
					frm.set_value("city", p.city)
					frm.set_value("guardian", p.guardian)
					frm.set_value("occupation", p.occupation)
					frm.set_value("designation", p.designation)
					frm.set_value("organization", p.organization)
					frm.set_value("tution_provider", p.tution_provider)
					frm.set_value("subject_teacher_name", p.subject_teacher_name)
					frm.set_value("address_line_2", p.address_line_2)	
				}
			}
		});
	},
	transfer_from(frm){
		set_amount(frm)
	},
	onload(frm){
		if(cur_frm.doc.__islocal){
			set_amount(frm)
		}
	},
	exam_charges(frm){
		

	}
});


function get_dates(frm){
	var dates = ["2020"]
	
		frappe.call({
			method:'get_dates', 
			doc:frm.doc,
			callback: function(r){
				if(r.message){
					console.log(r.message)
					return r.message
				}
			}
		})	
}


function set_amount(frm){
	if(frm.doc.transfer_from){
		frappe.call({
	        method: 'frappe.client.get_value',
	        args: {
	            'doctype': 'CBE Registration',
	            'filters': { 'name': frm.doc.transfer_from },
	            'fieldname': [
	                "previous_paid_amount",
	                "amount"
	            ]
	        },
	        callback: function(r) {
				console.log(r.message)
				var am = r.message["amount"]
				var pre = r.message["previous_paid_amount"]
				var total = am + pre
				frm.set_value("previous_paid_amount", total)
				frm.set_value('amount', frm.doc.exam_charges+frm.doc.transfer_charges-frm.doc.previous_paid_amount)
			}
	    });	
		
	}
	frm.set_value('amount', frm.doc.exam_charges+frm.doc.transfer_charges-frm.doc.previous_paid_amount)	
}