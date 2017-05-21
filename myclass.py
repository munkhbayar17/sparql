class Relation:
	def __init__(self, nm, sc, sub, pre, obj):
		self.name = nm
		self.schema = sc
		self.subject = sub
		self.predicate =pre
		self.object =obj
	def toString(self):
		return "Relation name:{0}\nsubject:{1}\npredicate:{2}\nobject:{3}".format(self.name, self.subject, self.predicate, self.object)
	def fullName(self):
		return "{0}.{1}".format(self.schema, self.name)
# (IB)x(I)x(IBL)
class Triple:
	def __init__(self, sub, pre, obj):
		self.subject = sub
		self.predicate =pre
		self.object =obj
	
	def toString(self):
		return "{s:{0}, p:{1}, o:{2}}".format(self.subject, self.predicate, self.object)

# (IVL)x(IV)x(IVL)
class TriplePattern:
	def __init__(self, sub, pre, obj):
		self.sp = sub
		self.pp =pre
		self.op =obj
	
	def toString(self):
		return "s:{0}, p:{1}, o:{2}".format(self.sp, self.pp, self.op)

#
class GraphPattern:
	def __init__(self, g1, op, g2):
		self.gp1 = g1
		self.operator =op
		self.gp2 =g2

	def allVariables():
		return []
	
	def toString(self):
		return "gp1: {0}\nop: {1}\ngp2: {2}".format(self.gp1.toString(), self.operator, self.gp2.toString())