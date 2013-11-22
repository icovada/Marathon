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

badnet	=open(date+"/badhost.txt","w")
badpass	=open(date+"/badpass.txt","w")
badenable=open(date+"/badenable.txt","w")

count = len(open("input.txt","r").readlines(  ))
hostsfile = open("input.txt","rU")

#LOGIN
done = 0
bad = 0
for i in hostsfile:
	try:
		done=done+1
		print("Host %s out of %s, %s failed"% (done,count,bad))
		tn = telnetlib.Telnet(i)
		running = open(date+"/running/"+i,"w")
		startup = open(date+"/startup/"+i,"w")

		index,match,text =tn.expect([".sername."],2)

		tn.write(username+"\n")
		index,match,text =tn.expect([".assword."],2)

		tn.write(password+"\n")
		index,match,text =tn.expect([".\>",".\#"],2) #Either user EXEC or Priv EXEC
		if index < 0:
			print("Wrong login or password")
			badpass.write(i)
			continue

		if index == 0:  #Login enable
			tn.write("enable\n")
			index,match,text =tn.expect([".assword."],2)
			tn.write(enable+"\n")
			index,match,text =tn.expect(priv,2)
			if index < 0:
				print("Enable password is wrong")
				badenable.write(i)
				continue


		#GET CONFIGURATION
		tn.write("terminal length 0\n") #Write all config at once
		index,match,text =tn.expect(priv,2)
		tn.write("show running\n")
		index,match,text =tn.expect(["\nend"],10)
		running.write(text)
		tn.write("show startup\n")
		index,match,text=tn.expect(["\nend"],0)
		startup.write(text)
		tn.write("terminal length 30\n")
		tn.close()
		running.close()
		startup.close()
	except:
		badnet.write(i)

badnet.close()
badenable.close()
badpass.close()
hostsfile.close()