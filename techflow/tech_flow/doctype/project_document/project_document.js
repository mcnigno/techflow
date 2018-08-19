// Copyright (c) 2018, QuasarPM.com and contributors
// For license information, please see license.txt
frappe.provide("erpnext.utils");

frappe.ui.form.on('Project Document', {
	refresh: function(frm) {
		console.log("this is the frm now", frm);
				if (!cur_frm.doc.__islocal) {
					$(frm.fields_dict['document_pages'].wrapper)
						.html(frappe.render_template("pdf_pages_list", cur_frm.doc.__onload));
				}
				

		frm.page.add_menu_item(__("Custom BTN"), function() {
					console.log("Custom BTN Yeah!!!")
					var ts =  $("#pdf_thumb").scrollTop();
					console.log(ts);
			}
		);
		


		frm.add_custom_button(__("Do Something"), function() {
			console.log('this argument:', frm.doc.name);
			frappe.call({
				method:"techflow.tech_flow.doctype.project_document.project_document.split_pages",
				args: {
					args: frm.doc.name,
					
				}, 
				callback: function(r) { 
					frm.reload_doc();
					console.log(r);
					
		
				}
			});
			
			}
		);
		

	}
});
