#!/usr/bin/python
#This program is licensed under GPL2.
#DISCLAIMER
#This program could break your network and get you fired.
#Test on your own before using in production
#And even after testing, handle with care
#I am not responsible for vtp collapses, frame collisions and/or subsequent business bankruptcies.

import telnetlib
import getpass
import sys
import datetime
import os
import time
import socket

now = datetime.datetime.now()
date = now.strftime("%Y%m%d-%H%M%S")
uexec=[".\>"]
priv=[".\#"]

socket.setdefaulttimeout(8)

#username="cisco"
#password="cisco"
#enable="cisco"

username=getpass.getpass("Login:")
password=getpass.getpass()
enable=getpass.getpass("Enable (leave empty if none):")

if not os.path.exists(date):
	os.makedirs(date)
	os.makedirs(date+"/running")
	os.makedirs(date+"/startup")
else:
	sys.exit("The destination folder exists already. Try again.")

badhost	=open(date+"/badhost.txt","w")
badpass	=open(date+"/badpass.txt","w")
badenable=open(date+"/badenable.txt","w")

count = len(open("input.txt","r").readlines(  ))
hostsfile = open("input.txt","rU")

#LOGIN
done = 0
bad = 0
for i in hostsfile:
	try:
		host = i.strip()
		done=done+1
		print("Host %s out of %s, %s failed"% (done,count,bad))
		tn = telnetlib.Telnet(host)
		index,match,text =tn.expect([".sername."],5)

		tn.write(username+"\n")
		index,match,text =tn.expect([".assword."],5)

		tn.write(password+"\n")
		index,match,text =tn.expect([".\>",".\#"],5) #Either user EXEC or Priv EXEC
		if index < 0:
			print("Wrong login or password: "+host)
			badpass.write(i)
			bad=bad+1
			continue

		if index == 0:  #Login enable
			tn.write("enable\n")
			index,match,text =tn.expect([".assword."],5)
			tn.write(enable+"\n")
			index,match,text =tn.expect(priv,5)
			if index < 0:
				print("Enable password is wrong: "+host)
				badenable.write(i)
				bad=bad+1
				continue

		running = open(date+"/running/"+host+".txt","w")
		startup = open(date+"/startup/"+host+".txt","w")

		#GET CONFIGURATION
		tn.write("terminal length 0\n") #Write all config at once
		index,match,text =tn.expect(priv,5)
		tn.write("show running\n")
		index,match,text =tn.expect(["\nend","\n% Authorization failed"],60) #TACACS error
		if index == 1:
			print("Authorization failed: "+host)
			badhost.write(i)
			bad=bad+1
			continue

		running.write(text)
		tn.write("show startup\n")
		index,match,text=tn.expect(["\nend","\n% Authorization failed"],60) #TACACS error
		if index == 1:
			print("Authorization failed: "+host)
			badhost.write(i)
			bad=bad+1
			continue

		startup.write(text)
		tn.write("terminal length 30\n")
		tn.close()
		running.close()
		startup.close()
	except KeyboardInterrupt:
		sys.exit("Quit")
	except:
		print("Host unreachable: "+host)
		bad=bad+1
		badhost.write(i)

badhost.close()
badenable.close()
badpass.close()
hostsfile.close()