"""
@author: Munkhbayar Nergui
@email: munkhbayar.nergui@postgrad.manchester.ac.uk
@org: 	University of Manchester
@Year: 	2017
@Place: Manchester, UK
@Desc:	SPARQL to SQL translation program
@Reference: Based on Artem Chebotko's approach
@Database schema: Vertical
"""
# globals
global subject
subject = "subject"
global predicate
predicate = "predicate"
global object
object = "object"

global OP_AND
OP_AND = "AND"
global OP_OPT
OP_OPT = "OPT"
global OP_UNION
OP_UNION = "UNION"
global OP_FILTER
OP_FILTER = "FILTER"

global aliasCount
aliasCount = 0

# MAIN functions
def main():
	init()
	tp1 = TriplePattern("John", "has", "dog")
	tp2 = TriplePattern("Luis", "play", "football")
	gp1 = GraphPattern(tp1, OP_AND, tp2)
	print(trans(gp1))

def init():
	#load from schema.yml
	global relation
	relation = Relation("Triple", "rdf_store", "s", "p", "o")

# mapping functions
def alpha(tp):
	return relation.fullName();

def betta(tp, pos):
	if pos == subject:
		return relation.subject
	if pos == predicate:
		return relation.predicate
	if pos == object:
		return relation.object

# auxiliary translation functions
def name(attrName):
	return "{0}_{1}".format(relation.name, attrName)

def alias(relationName):
	aliasCount += 1
	return "{0}{1}".format(relationName[0], aliasCount)

def term(termName):
	termName = termName.replace("?", "")
	termName = termName.replace("$", "")
	return termName

# helper functions
def findVarInTP(tp, var):
	return False

def findVarInGP(gp, var):
	return False

# SQL translation functions
def genCondSQL(tp):
	condSQL = "True"
	if(findVarInTP(tp, tp.sp) == False):
		condSQL += " and {0} = '{1}'".format(betta(tp, subject), tp.sp)
	if(findVarInTP(tp, tp.pp) == False):
		condSQL += " and {0} = '{1}'".format(betta(tp, predicate), tp.pp)
	if(findVarInTP(tp, tp.op) == False):
		condSQL += " and {0} = '{1}'".format(betta(tp, object), tp.op)

	if(tp.sp == tp.op):
		condSQL += " and {0} = '{1}'".format(betta(tp, subject), betta(tp, object))
	if(tp.sp == tp.pp):
		condSQL += " and {0} = '{1}'".format(betta(tp, subject), betta(tp, predicate))
	if(tp.pp == tp.op):
		condSQL += " and {0} = '{1}'".format(betta(tp, predicate), betta(tp, object))
	return condSQL;

def genPRSQL(tp):
	prSQL = "{0} as {1}".format(betta(tp, subject), name(tp.sp))
	if(tp.sp != tp.pp):
		prSQL += ", {0} as {1}".format(betta(tp, predicate), name(tp.pp))
	if(tp.sp != tp.op):
		prSQL += ", {0} as {1}".format(betta(tp, object), name(tp.op))
	return prSQL

#Main translator function | recursive
def trans(pattern):
	if(type(pattern).__name__ == "TriplePattern"):
		tp = pattern
		return constructSelectQuery(tp)
	if(type(pattern).__name__ == "GraphPattern"):
		gp = pattern
		subqueryAliasCount = 1
		if(gp.operator == OP_AND):
			aliasQ1 = "q{0}".format(subqueryAliasCount)
			q1 = "({0}) {1}".format(trans(gp.gp1), aliasQ1)
			subqueryAliasCount += 1
			aliasQ2 = "q{0}".format(subqueryAliasCount)
			q2 = "({0}) {1}".format(trans(gp.gp2), aliasQ2)
			subqueryAliasCount += 1
			return constructInnerJoinQuery(genCommonPRInnerJoin(gp, aliasQ1, aliasQ2), q1, q2, genCondInnerJoin(gp.gp1, gp.gp2, aliasQ1, aliasQ2))

#SQL constructor from a simple SPARQL query
def constructSelectQuery(tp):
	return "SELECT {0} FROM {1} WHERE {2}".format(genPRSQL(tp), alpha(tp), genCondSQL(tp))

#INNER JOIN translator

def constructInnerJoinQuery(prList, fromClause, whereClause, joinCond):
	return "SELECT {0} FROM {1} INNER JOIN {2} ON {3}".format(prList, fromClause, genCondSQL(tp), joinCond)

def genCondInnerJoin(tp1, tp2, aliasQ1, aliasQ2):
	commonAttributes = findCommonAttributes(tp1, tp2)
	if(len(commonAttributes) == 0):
		return "True"
	condSQL = ""
	for attr in commonAttributes:
		if(condSQL == ""):
			condSQL += "{0}.{1} = {2}.{1}".format(aliasQ1, attr, aliasQ2)
		else:
			condSQL += " and {0}.{1} = {2}.{1}".format(aliasQ1, attr, aliasQ2)
	return condSQL

def genCommonPRInnerJoin(gp, aliasQ1, aliasQ2):
	return "Coalesce(inner join)"
	commonAttributes = findCommonAttributes(gp.gp1, gp.gp2)
	if(len(commonAttributes) == 0):
		return "{0}, {1}".format(genPRSQL(gp.gp1), genPRSQL(gp.gp2))
	prSQL = ""
	uncommonAttributes = findUncommonAttributes(gp.gp1, gp.gp2)
	for attr in uncommonAttributes:
		if(prSQL == ""):
			prSQL = ""
	return "{0}, {1}".format(genPRSQL(gp.gp1), genPRSQL(gp.gp2))

def genUncommonPRInnerJoin(gp, aliasQ1, aliasQ2):
	return "uncommon(inner join)"
	commonAttributes = findCommonAttributes(gp.gp1, gp.gp2)
	if(len(commonAttributes) == 0):
		return "{0}, {1}".format(genPRSQL(gp.gp1), genPRSQL(gp.gp2))
	prSQL = ""
	uncommonAttributes = findUncommonAttributes(gp.gp1, gp.gp2)
	for attr in uncommonAttributes:
		if(prSQL == ""):
			prSQL = ""
	return "{0}, {1}".format(genPRSQL(gp.gp1), genPRSQL(gp.gp2))

# helper functions
def findCommonAttributes(tp1, tp2):
	attributes = []
	if(tp1.sp == tp2.sp):
		attributes.push(tp1.sp)
	if(tp1.pp == tp2.pp):
		attributes.push(tp1.pp)
	if(tp1.op == tp2.op):
		attributes.push(tp1.op)
	return attributes

def findUncommonAttributes(tp1, tp2):
	uncommonAttrs = []
	commonAttrs = []
	uncommonAttrs = pushTripleToArray(tp1, uncommonAttrs)
	uncommonAttrs = pushTripleToArray(tp2, uncommonAttrs)
	if(tp1.sp == tp2.sp):
		commonAttrs = tp2.sp
		uncommonAttrs.remove(tp2.sp)
	if(tp1.sp == tp2.pp):
		commonAttrs = tp2.pp
		uncommonAttrs.remove(tp2.pp)
	if(tp1.sp == tp2.op):
		commonAttrs = tp1.op
		uncommonAttrs.remove(tp2.op)
	if(tp1.pp == tp2.pp):
		commonAttrs = tp2.pp
		uncommonAttrs.remove(tp2.pp)
	if(tp1.pp == tp2.op):
		commonAttrs = tp2.op
		uncommonAttrs.remove(tp2.op)
	if(tp1.op == tp2.op):
		commonAttrs = tp2.op
		uncommonAttrs.remove(tp2.op)
	return attributes

# add triple elements to array
def pushTripleToArray(tp, narray):
	narray.push(tp.sp)
	narray.push(tp.pp)
	narray.push(tp.op)
	return narray

# MAIN
if __name__ == "__main__":
	import sys
	from myclass import *
	main()