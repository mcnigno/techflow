frappe.provide("frappe.treeview_settings");

frappe.treeview_settings['Discipline'] = {
	get_tree_nodes: "techflow.techflow.techflow.doctype.discipline.discipline.get_children",
	add_tree_node: "techflow.techflow.techflow.doctype.discipline.discipline.add_node",
	filters: [
		{
			fieldname: "project",
			fieldtype:"Link",
			options: "Project",
			label: __("Project"),
		},
		{
			fieldname: "discipline",
			fieldtype:"Link",
			options: "Discipline",
			label: __("Discipline"),
			get_query: function() {
				var me = frappe.treeview_settings['Discipline'];
				var project = me.page.fields_dict.project.get_value();
				var args = [["Discipline", 'is_group', '=', 1]];
				if(project){
					args.push(["Discipline", 'project', "=", project]);
				}
				return {
					filters: args
				};
			}
		}
	],
	breadcrumb: "Projects",
	get_tree_root: false,
	root_label: "All Disciplines",
	ignore_fields: ["parent_discipline"],
	onload: function(me) {
		frappe.treeview_settings['Discipline'].page = {};
		$.extend(frappe.treeview_settings['Discipline'].page, me.page);
		me.make_tree();
	},
	toolbar: [
		{
			label:__("Add Multiple"),
			condition: function(node) {
				return node.expandable;
			},
			click: function(node) {
				this.data = [];
				const dialog = new frappe.ui.Dialog({
					title: __("Add Multiple Disciplines"),
					fields: [
						{
							fieldname: "multiple_disciplines", fieldtype: "Table",
							in_place_edit: true, data: this.data,
							get_data: () => {
								return this.data;
							},
							fields: [{
								fieldtype:'Data',
								fieldname:"subject",
								in_list_view: 1,
								reqd: 1,
								label: __("Subject")
							}]
						},
					],
					primary_action: function() {
						dialog.hide();
						return frappe.call({
							method: "techflow.techflow.techflow.doctype.discipline.discipline.add_multiple_disciplines",
							args: {
								data: dialog.get_values()["multiple_disciplines"],
								parent: node.data.value
							},
							callback: function() { }
						});
					},
					primary_action_label: __('Create')
				});
				dialog.show();
			}
		}
	],
	extend_toolbar: true
};