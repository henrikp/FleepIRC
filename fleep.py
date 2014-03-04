#!/usr/bin/python

# IRC bot original code snatched from http://oreilly.com/pub/h/1968

from datetime import datetime
import requests
import sys
import socket
import string

HOST="some.irc.server"
PORT=6667
NICK="fleep"
CHANNEL="#fleep"
PASSWORD="password"

REALNAME="fleep"
# Set to true if your bot doesn't use a password
# otherwise it waits for the first notify from
# NickServer
registered = False
NICKSERVER = "NickServ"
hook_url='https://your-hook-here'
readbuffer=""

irc=socket.socket( )
print "Bot starting..."
irc.connect((HOST, PORT))
print "Sending nick"
irc.send("NICK %s\r\n" % NICK)
print "Sending user information"
irc.send("USER bot 0 * :%s\r\n" % (REALNAME))

def whoSent(line):
    return line[0][1: line[0].find("!")]

while 1:
    readbuffer = readbuffer + irc.recv(1024)
    temp = string.split(readbuffer, "\n")
    readbuffer=temp.pop()


    for line in temp:
        line = string.rstrip(line)
        line = string.split(line)


	#print (line)

	if (line[1] == "PRIVMSG" and line[2] == CHANNEL):
	    now = datetime.now()
	    time = "%02d:%02d" % (now.hour, now.minute)
	    who = whoSent(line)
	    del line[:3]
	    msg = ' '.join(line)
	    fleep = time + " <" + who + "> " + msg[1:]
	    try:
		r = requests.post(hook_url, data = {'message': fleep})
	    except Exception:
		sys.exc_clear()
	    #print msg[1:]
	    print "Status: " + str(r.status_code) + " " + str(time) + ":" + str(now.second)


	if (registered == False and line[1] == "NOTICE" and whoSent(line) == NICKSERVER):
	    irc.send("PRIVMSG NICKSERV IDENTIFY :" + PASSWORD + "\r\n")
	    irc.send("JOIN " + CHANNEL + "\r\n")
	    registered = True
	    print "We are (hopefully) registered!"

        if(line[0]=="PING"):
	    irc.send("PONG %s\r\n" % line[1])