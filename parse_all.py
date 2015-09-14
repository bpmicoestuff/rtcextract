#!/usr/bin/python

from lxml import etree
import csv

root = etree.parse("workitems.xml")

def process(elem, xpath_expr):
	val = elem.xpath(xpath_expr)
	if len(val)>0:
		return val[0].encode('utf-8')
	else:
		""

def parse_items_1st_level(type, fields):
	items = []
	for workitem in root.xpath("/workitem/workItem[type/name='%s']" % type):
		item = {}
		for key in fields.keys():		
			item[key] = process(workitem, fields[key])
		
		items.append(item.copy())

	return items


def save(type, items):
	with open("%ss.csv" % type.lower().replace(" ", "_").replace("y", "ie"), "wb") as csvfile:
		keys = items[0].keys()
		writer = csv.DictWriter(csvfile, fieldnames=keys)
		writer.writeheader()
		writer.writerows(items)

		
def write_features(type, fields):
	items = parse_items_1st_level(type, fields)
	save(type, items)		
	return items

	
# main

# Epics 
epic_fields = {
	"id": "id/text()",
	"summary": "summary/text()",
	"type": "type/name/text()",
}
write_features("Epic", epic_fields)

feature_fields = {
	"id": "id/text()",
	"summary": "summary/text()",
	"type": "type/name/text()",
	"parent": "parent/summary/text()",
	"parent_id": "parent/id/text()",
	"parent_type": "parent/type/name/text()",
	"owner": "category/name/text()",
	"sizing": "stringExtensions[key='com.acn.ideazz.workitem.attribute.featureestimate']/value[1]/text()",
}
write_features("Feature", feature_fields)

subfeature_fields = {
	"id": "id/text()",
	"summary": "summary/text()",
	"type": "type/name/text()",
	"parent": "parent/summary/text()",
	"parent_id": "parent/id/text()",
	"parent_type": "parent/type/name/text()",
}
write_features("Sub Feature", subfeature_fields)

story_fields = {
	"id": "id/text()",
	"summary": "summary/text()",
	"type": "type/name/text()",
	"parent": "parent/summary/text()",
	"parent_id": "parent/id/text()",
	"parent_type": "parent/type/name/text()",
	"complexity": "integerComplexity/text()",
}
write_features("Story", story_fields)

task_fields = {
	"id": "id/text()",
	"summary": "summary/text()",
	"type": "type/name/text()",
	"parent": "parent/summary/text()",
	"parent_id": "parent/id/text()",
	"parent_type": "parent/type/name/text()",
	"assigned": "owner/name/text()",
}
write_features("Task", task_fields)

items = []
for task in root.xpath("/workitem/workItem[type/name='Task']"):
	item = {}
	for hist in task.xpath("./itemHistory"):
		item["id"] = task.xpath("./id/text()")[0]
		item["modified"] = hist.xpath("./modified/text()")[0]
		item["state"] = hist.xpath("./state/name/text()")[0]
		items.append(item.copy())
		
save("task_item", items)