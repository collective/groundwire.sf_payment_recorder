import unittest


class Test_split_name(unittest.TestCase):

	# This returns the "Function Under Test" (FUT).
	# This pattern is used to keep the import at test time,
	# so broken imports break the test rather than preventing it from being discovered.
	@property
	def FUT(self):
		from groundwire.sf_payment_recorder.utils import split_name
		return split_name

	def test_split_name(self):
		self.assertEqual(('David', 'Glick'), self.FUT('David Glick'))

	def test_split_name_three_part(self):
		self.assertEqual(('David Isaac', 'Glick'), self.FUT('David Isaac Glick'))

	def test_split_name_one_part(self):
		self.assertEqual(('', 'Glick'), self.FUT('Glick'))

	def test_split_name_two_part_last_name(self):
		self.assertEqual(('Lisa', 'van Dyk'), self.FUT('Lisa van Dyk'))

	def test_split_name_middle_initial(self):
		self.assertEqual(('David', 'Glick'), self.FUT('David I Glick'))

	def test_split_name_middle_initial_2(self):
		self.assertEqual(('David', 'Glick'), self.FUT('David I. Glick'))
