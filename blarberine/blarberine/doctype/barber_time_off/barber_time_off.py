# Copyright (c) 2026, Yogaselvan S and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class BarberTimeOff(Document):
	def validate(self):
		if not self.to_date:
			self.to_date = self.from_date
		if getdate(self.to_date) < getdate(self.from_date):
			frappe.throw(_("To Date cannot be before From Date"))
		if self.all_day:
			# Frappe fills empty Time fields with the current clock time on
			# insert, so blocking logic must key off all_day — clear them for
			# clarity in the list view.
			self.start_time = None
			self.end_time = None
		elif not (self.start_time and self.end_time):
			frappe.throw(_("Set both Start Time and End Time, or tick All Day"))
