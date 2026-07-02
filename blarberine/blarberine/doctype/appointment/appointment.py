# Copyright (c) 2026, Yogaselvan S and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime


class Appointment(Document):
	def validate(self):
		self.set_calendar_fields()

	def set_calendar_fields(self):
		"""Keep the desk Calendar view in sync: combine the Date + Time fields
		into full datetimes and build a readable event title like
		'10:00 Marius K. — Skin Fade (Mantas)'."""
		if not (self.appointment_date and self.start_time):
			return
		start = get_datetime("%s %s" % (self.appointment_date, self.start_time))
		end = get_datetime("%s %s" % (self.appointment_date, self.end_time or self.start_time))
		self.start_dt = start
		self.end_dt = end
		customer = frappe.db.get_value("Customer", self.customer, "customer_name") or self.customer
		barber = frappe.db.get_value("Barber", self.barber, "barber_name") or self.barber
		hhmm = start.strftime("%H:%M")
		# Single-line title for the form header / list view.
		self.title = "%s %s — %s · %s" % (hhmm, customer, barber, self.service)
		# Stacked label for the calendar: customer / time / barber on 3 lines
		# (FullCalendar turns the newlines into <br>).
		self.calendar_label = "%s\n%s\n%s" % (customer, hhmm, barber)
