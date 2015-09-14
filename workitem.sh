#!/usr/bin/bash -xf

COOKIES=./cookies.txt

USER=dXXXXX
PASSWORD=YYYYYYY
HOST="https://ideazz-rtc.in.XXXXXX.com.au:ZZZZ/ccm"
WORKITEM_CATALOG="rpt/repository/workitem"
QUERY_PROJECT="workitem/workItem\[projectArea/name='PA_BPMI_INTEGRATION'\]/(stringExtensions/*|category/name|stringComplexity|owner/name|id|summary|type/name|integerComplexity|parent/(id|summary|type/name)|itemHistory/(stateTransitions/(transitionDate|action|sourceStateId|targetStateId|changedBy/(modified|name))|modified|state/*))"
#QUERY_PROJECT="workitem/workItem\[projectArea/name='PA_BPMI_INTEGRATION'\]/(id|summary|type/name|parent/(id|summary|type/name)|itemHistory/(modified|state/*))"
#QUERY_PROJECT="workitem/workItem\[projectArea/name='PA_BPMI_INTEGRATION'\]/*/*"
QUERY_STATES='workitem/workItem\[type/id="com.ibm.team.apt.workItemType.story"\]/(id|summary|type/(id|name))'

curl -k -c $COOKIES "$HOST/authenticated/identity"

curl -k -L -b $COOKIES -c $COOKIES -d j_username=$USER -d j_password=$PASSWORD "$HOST/authenticated/j_security_check"

# Get workitems
curl -k -L -b $COOKIES $HOST"/"$WORKITEM_CATALOG"?fields="$QUERY_PROJECT"&size=10000" > workitems.xml
#curl -k -L -b $COOKIES $HOST"/"$WORKITEM_CATALOG"?fields="$QUERY_PROJECT"&size=100"

