#!/usr/bin/python
#
# LDAP search utility in Python
# to lookup up specific people 
# in LDAP
#
# 8/17/2011 DEV
#

import cgi, commands, os

# base strings needed for ldap changes
search="ldapsearch "
modify="ldapmodify"
delete="ldapdelete"
filename="-f single.mod"
host="-h localhost "
auth="-x -w password -D 'cn=Manager,dc=example,dc=com' "
base="-b 'dc=example,dc=com' "

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
name = form.getvalue("name","")
choice = form.getvalue("choice","")


# Run a search by name or by address
# and format the output
# search to see if the NEW items already exist in address book
# search by cn uses 0
# search by mail uses 1
if choice == "N":
   newlist=searchldap( 0,name,host,auth,base )
elif choice == "A":
   newlist=searchldap( 1,name,host,auth,base )

# Don't know why, but we get an undefined value error if 
# this isn't done this way
membername = ""
memberaddress = ""

# Print out all possible answers
# by making a table
print "<h2>We found the following answers to your query.</h2>"
print "<br>"
print "<p>If the table is empty, then the query returned no matches.</p>"
print "<form name='output' action='http://davespc/cgi-bin/change.py' method='POST'>"
print "<table border=1>"
print "<tr><th>Member Name<th>E-mail address"

for z in newlist:
   if z[0:3] == "cn:":		# Find member name
      membername = z[4:]	# lop off cn:
   if z[:5] == "mail:":		# Find email address
      memberaddress = z[5:]	# lop off mail:
      print "<tr><td><input type='radio' name='list' value="+"\""+membername+"\""+" />"
      print membername+"</td><td>"+memberaddress+"</td></tr>"
print "</table>"
print "<h3>Choose the name or address that you wish to modify or delete.</h3>"
print "<h3>Then click the submit button below.</h3>"
print "<input type='submit' value='Submit' />"
print "</form>"

# Now make a back button to go back to main form
print "<p>Click the back button below to return to previous form.</p>"
print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"


