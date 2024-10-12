// Copyright (c) 2021, Unilink Enterprise and contributors
// For license information, please see license.txt

frappe.ui.form.on('Monthly Fee', {
	program(frm) {
		frappe.call({
			method: "get_students",
			doc:frm.doc,
			callback:function(r){
				frm.refresh_field("students")
			}
		})
	},
	fee_category(frm){
		frm.trigger("program")
	}
});


frappe.realtime.on('data_import_progress', data => {
	let percent = Math.floor((data.current * 100) / data.total);
	let message;
	message = "Updating fee for "+data.student+'. Progress '+percent;
	frm.dashboard.show_progress(__('Import Progress'), percent, message);
	frm.page.set_indicator(__('In Progress'), 'orange');			
	
	if (data.current === data.total) {
		setTimeout(() => {
			frm.dashboard.hide();
			frm.refresh();
		}, 2000);
	}
});