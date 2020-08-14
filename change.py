#!/usr/bin/python
#
# LDAP modify utility in Python
# to modify or delete people 
# in LDAP
#
# 8/21/2011 DEV
#

import cgi, commands, os

# base strings needed for ldap changes
search="ldapsearch "
modify="ldapmodify"
delete="ldapdelete"
filename="-f single.mod"
host="-h localhost "
auth="-x -w password -D 'cn=Manager,dc=example,dc=com' "
base="-b 'dc=southmac,dc=net' "

# Run a search by name
# to see if the new data item already exists in database
#
# type is integer for what field you are searching for
#   0=cn, 1=mail
# item = string of item searched for (i.e. name or address)
# host = -h hostname
# auth = -x -w password -D cn=xxx,dc=xxx,net=xxx
# base = -b dc=xxx,dc=xxx
# all strings must end in space
# returns a list of all strings found in search
def searchldap( type,item,host,auth,base  ):
   if type == 0:
      prefix="'cn="
   elif type == 1:
      prefix="'mail="
   answer=commands.getoutput("ldapsearch "+host+auth+base+prefix+item+"'")
   nlist=[str(a) for a in answer.split('\n')]
   return nlist


# Test to see if an item exists
# in the address book
# Requires an ldap search list as in input
#
# Returns 1 if item from search is found
# Returns 0 if search returns empty list
def testldap( srchresult ):
   match=1
   for item in srchresult:
      # If line in search result has
      # numResponses: 1 then 
      # there were no items found
      if item[2:] == "numResponses: 1":
         match=0
   return match

# get values from web page inputs
form = cgi.FieldStorage()	# load form data into form variable

# Set up output as a web page
print "Content-Type: text/html\n\n"


# Load python variables from form variables
membername=form.getvalue("list","")

print "<h2>You are about to make changes on member: "+membername+"</h2>"
print "<br><h3>The member's data is as shown below:</h3>"
print "If the data list is blank or appears unreadable then click the BACK button and choose again."
result=searchldap(0,membername,host,auth,base)

print "<form name='mod' action='http://davespc/cgi-bin/domod.py'>"
print "<ul>"
for n,i in enumerate(result):
   if n > 8:
      if n < 17:
         print "<li>"+i+"</li>"
         print "<input type='hidden' name='member' value='"+i+"' />"
print "</ul>" 
print "<h3>Click <input type='submit' name='change' value='modify' /> to edit this member.</h3><br>"
print "<h3>Click <input type='submit' name='change' value='delete' /> to delete this member.</h3><br>"
print "</form>"
  
# Now make a back button to go back to main form
print "<p>Click the back button below to return to previous form.</p>"
print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"


