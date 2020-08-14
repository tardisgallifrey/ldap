#!/usr/bin/python
#
# LDAP search utility in Python
# to lookup up specific people 
# in LDAP
#
# 8/17/2011 DEV
#

import cgi, commands, os
import cgitb
cgitb.enable()

# base strings needed for ldap changes
modify="ldapmodify "
add="ldapadd "
delete="ldapdelete "
tmpfile="/tmp/single.tmp"
addto=">>"
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

# Check to see that first and last name fields and email field have been completed
if not (form.has_key("fname") and form.has_key("lname") and form.has_key("email")):
   # print out error message and quit
   print "<hr>"
   print "<h2>Problem Found</h2>"
   print "<p>In order to add an e-mail address to the update"
   print " you must have a first and last name, and a valid"
   print "e-mail address.  One or more of these values were"
   print "submitted as empty.</p>"
   print "<p>Please click the back button below to return"
   print "to the previous form and correct the values.</p>"
   print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"

else:
   # Assign values passed form form to Python variables
   fname=form.getvalue("fname")
   lname=form.getvalue("lname")
   address=form.getvalue("email")


# Assign checkbox values to python variables, if they were checked.
if form.has_key("update"):
   update="echo \'ou: update\'"
else:
   update=""

if form.has_key("member"):
   member="echo \'ou: member\'"
else:
   member=""

if form.has_key("staff"):
   staff="echo \'ou: staff\'"
else:
   staff=""

if form.has_key("elder"):
   elder="echo \'ou: elder\'"
else:
   elder=""

if len(update) == 0 and len(member) == 0 and len(staff) == 0 and len(elder) ==0:
   # Print out error and quit
   print "<hr>"
   print "<h2>Problem encountered with checkbox values.</h2>"
   print "<p>At least one choice for update, staff, elder, or member"
   print " must be"
   print " selected in order to add a name and e-mail address.</p>"
   print "<p>Click the back button below to return to the form"
   print " and correct the value(s).</p>"
   print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"

# search to see if the NEW items already exist in address book
# search by cn uses 0
# search by mail uses 1
newlist=searchldap( 0,fname+" "+lname,host,auth,base )
newlist2=searchldap( 1,address,host,auth,base )

namematch=testldap( searchldap( 0,fname+" "+lname,host,auth,base ))
addrmatch=testldap( searchldap( 1,address,host,auth,base ))

# Don't know why, but we get an undefined value error if 
# this isn't done this way
membername = ""
memberaddress = ""

# If there is a match
# Print it out and ask person
# to go back and enter correctly
if namematch or addrmatch:
   if namematch:
      print "<hr><h3>There is a match to the name you entered.</h3>"
      print "<p>We found the following entries"
      print "already in the address book:</p>"
      print "<table border=1>"
      print "<tr><th>Member Name<th>E-mail address"
      for z in newlist:
         if z[:3] == "cn:":
            membername=z[4:]
         if z[:5] == "mail:":
            memberaddress=z[6:]   
            print "<tr><td>"+membername+"<td>"+memberaddress
      print "</table>"
      print "<p>Click the back button below to return to previous form.</p>"
      print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"

   if addrmatch:
      print "<hr><h3>There is a match to the address you entered.</h3>"
      print "<p>We found the following entries"
      print "already in the address book:</p>"
      print "<table border=1>"
      print "<tr><th>Member Name<th>E-mail address"
      for z in newlist2:
         if z[:3] == "cn:":
            membername=z[4:]
         if z[:5] == "mail:":
            memberaddress=z[6:]
            print "<tr><td>"+membername+"<td>"+memberaddress
      print "</table>"
      print "<p>Click the back button below to return to previous form.</p>"
      print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"

# If there is no match
# add the name to the addressbook
else:
   print "<p>No matches found.  Continue regular processing.</p>"
   print "<hr><h3>You have just added: "
   print fname+" "+lname+"<br><br>"
   os.system("echo \'dn: cn="+fname+" "+lname+",dc=southmac,dc=net\'"+addto+tmpfile)
   os.system("echo \'cn: "+fname+" "+lname+"\'"+addto+tmpfile)
   os.system("echo \'sn: "+lname+"\'"+addto+tmpfile)
   os.system("echo \'gn: "+fname+"\'"+addto+tmpfile)
   print "With the email address of: "+address+"<br><br>"
   print "And, the status of: <br>"
   os.system("echo \'mail: "+address+"\'"+addto+tmpfile)
   if len(update) > 2:
      print update[9:-1]+"<br>"
      os.system(update+addto+tmpfile)
   if len(staff) > 2:
      print staff[9:-1]+"<br>"
      os.system(staff+addto+tmpfile)
   if len(elder) > 2:
      print elder[9:-1]+"<br>"
      os.system(elder+addto+tmpfile)
   if len(member) > 2:
      print member[9:-1]+"</h3><br>"
      os.system(member+addto+tmpfile)
   os.system("echo 'objectClass: inetOrgPerson\n\n\'"+addto+tmpfile)
   tmpname=commands.getoutput(add+host+auth+"-f "+tmpfile)
   os.system("rm "+tmpfile)
   print "<p>Click the back button below to return to previous form.</p>"
   print "<FORM><INPUT TYPE=\"button\" VALUE=\"Back\" onClick=\"history.go(-1);return true;\"></FORM>"


