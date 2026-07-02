// Loaded automatically on the Appointment calendar (via doctype meta).
// Stacks each event as three lines — customer / time / barber — by using the
// multi-line `calendar_label` field (FullCalendar renders its \n as <br>) and
// hiding the redundant auto time line.
frappe.views.calendar["Appointment"] = {
	field_map: {
		id: "name",
		start: "start_dt",
		end: "end_dt",
		title: "calendar_label",
		allDay: "all_day",
	},
	get_events_method: "frappe.desk.calendar.get_events",
};

(function () {
	if (document.getElementById("bl-appt-cal-css")) return;
	var s = document.createElement("style");
	s.id = "bl-appt-cal-css";
	s.textContent =
		".fc-event .fc-time{display:none !important;}" +
		".fc-event .fc-title{white-space:normal !important;line-height:1.4;display:block;}" +
		".fc-event .fc-title{font-weight:400;}";
	document.head.appendChild(s);
})();
