#!/usr/bin/python

from lxml import etree
import csv
import pycurl
import urllib

def get_workitems():
	WORKITEMS_FILE = "./workitems.xml"
	COOKIES = "./cookies.txt"
	SIZE = 20000
	USER = "dXXXXXX"
	PASSWORD = "YYYY"
	HOST = "https://this is url/ccm"
	WORKITEM_CATALOG = "rpt/repository/workitem"
	QUERY_PROJECT = '''	workitem/workItem[projectArea/name='PA_BPMI_INTEGRATION']/(stringExtensions/*|category/name|stringComplexity|owner/name|id|summary|type/name|integerComplexity|parent/(id|summary|type/name)|itemHistory/(stateTransitions/(transitionDate|action|sourceStateId|targetStateId|changedBy/(modified|name))|modified|state/*))
	'''
	c = pycurl.Curl()
	c.setopt(c.COOKIEJAR, COOKIES)
	c.setopt(c.COOKIEFILE, COOKIES)
	c.setopt(pycurl.SSL_VERIFYPEER, False)
	c.setopt(pycurl.SSL_VERIFYHOST, False)
	c.setopt(pycurl.FOLLOWLOCATION, True)

	#curl -k -c $COOKIES "$HOST/authenticated/identity"

	c.setopt(c.POST, False)
	c.setopt(c.URL, "%s/authenticated/identity" % HOST)
	c.perform()

	#curl -k -L -b $COOKIES -c $COOKIES -d j_username=$USER -d j_password=$PASSWORD "$HOST/authenticated/j_security_check"

	c.setopt(c.URL, "%s/authenticated/j_security_check" % HOST)
	data = {
		"j_username": USER,
		"j_password": PASSWORD
	}
	c.setopt(c.POST, True)
	c.setopt(c.POSTFIELDS, urllib.urlencode(data))
	c.perform()

	#curl -k -L -b $COOKIES $HOST"/"$WORKITEM_CATALOG"?fields="$QUERY_PROJECT"&size=10000" > workitems.xml

	with open(WORKITEMS_FILE, 'wb') as f:
		params = {
			"fields": QUERY_PROJECT,
			"size": SIZE
		}
		c.setopt(c.URL, "%s/%s?%s" % (HOST, WORKITEM_CATALOG, urllib.urlencode(params)))
		c.setopt(c.WRITEDATA, f)
		c.setopt(c.POST, False)
		c.setopt(c.NOPROGRESS, False)
		c.perform()
		c.close()
	
	return WORKITEMS_FILE
	
def parse_workitems(input):
	root = etree.parse(input)

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
		
	# Epics 
	epic_fields = {
		"epic_id": "id/text()",
		"epic_name": "summary/text()",
	}
	epics = write_features("Epic", epic_fields)

	feature_fields = {
		"feature_id": "id/text()",
		"feature_name": "summary/text()",
		"feature_parent": "parent/summary/text()",
		"feature_parent_id": "parent/id/text()",
		"feature_parent_type": "parent/type/name/text()",
		"feature_owner": "category/name/text()",
		"feature_sizing": "stringExtensions[key='com.acn.ideazz.workitem.attribute.featureestimate']/value[1]/text()",
	}
	features = write_features("Feature", feature_fields)
	
	subfeature_fields = {
		"subfeature_id": "id/text()",
		"subfeature_name": "summary/text()",
		"subfeature_parent": "parent/summary/text()",
		"subfeature_parent_id": "parent/id/text()",
		"subfeature_parent_type": "parent/type/name/text()",
	}
	subfeatures = write_features("Sub Feature", subfeature_fields)

	#		"story_type": "type/name/text()",

	story_fields = {
		"story_id": "id/text()",
		"story_name": "summary/text()",
		"story_parent": "parent/summary/text()",
		"story_parent_id": "parent/id/text()",
		"story_parent_type": "parent/type/name/text()",
		"story_complexity": "integerComplexity/text()",
	}
	stories = write_features("Story", story_fields)

	task_fields = {
		"task_id": "id/text()",
		"task_name": "summary/text()",
		"task_parent": "parent/summary/text()",
		"task_parent_id": "parent/id/text()",
		"task_parent_type": "parent/type/name/text()",
		"task_assigned": "owner/name/text()",
	}
	tasks = write_features("Task", task_fields)

	def left_inner_join(l1, l1_key, l2, l2_key):
		merged = []
		for l1_item in l1:
			
			not_found = True
			
			left = dict(l1_item)
			
			for l2_item in l2:
				if left[l1_key] == l2_item[l2_key]:
					right = dict(l2_item)
					#del left[l1_key]
					not_found = False
					break
			
			if not_found:
				right = dict((el,"") for el in l2[0].keys())
				#del left[l1_key]

			left.update(right)
			merged.append(left)

		return merged
	
	def merge_keys(list, key1, key2, keyout):
		for item in list:
			if item[key1] == "": 
				item[keyout] = item[key2]
			else:
				item[keyout] = item[key1]
		
		return list
	
	join1 = left_inner_join(tasks, "task_parent_id", stories, "story_id")
	join2 = left_inner_join(join1, "story_parent_id", subfeatures, "subfeature_id")
	join2a = merge_keys(join2, "subfeature_parent_id", "story_parent_id", "combined_story_parent_id")	
	
	join3 = left_inner_join(join2a, "combined_story_parent_id", features, "feature_id")
	join4 = left_inner_join(join3, "feature_parent_id", epics, "epic_id")
	
	save("joined_tasks", join4)
	
	items = []
	for task in root.xpath("/workitem/workItem[type/name='Task']"):
		item = {}
		for hist in task.xpath("./itemHistory"):
			item["task_id"] = task.xpath("./id/text()")[0]
			item["task_modified"] = hist.xpath("./modified/text()")[0]
			item["task_state"] = hist.xpath("./state/name/text()")[0]
			items.append(item.copy())
			
	save("task_item", items)

	
# Main
parse_workitems(get_workitems())
