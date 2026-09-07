// Copyright (c) 2026, Blarberine and contributors

frappe.query_reports["Daily Schedule"] = {
	filters: [
		{
			fieldname: "date",
			label: __("Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
	],
};
