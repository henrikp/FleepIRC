#!/usr/bin/python

The MIT License (MIT)

Copyright (c) 2014 Henrik Pihl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

# IRC bot original code snatched from http://oreilly.com/pub/h/1968

from datetime import datetime
import requests
import sys
import socket
import string
import re

HOST="some.irc.server"
NICK="fleep"
CHANNEL="#fleep"
PASSWORD="password"
PORT=6667

REALNAME="fleep"
# Set to true if your bot doesn't use a password
# otherwise it waits for the first notify from
# NickServ
registered = False
NICKSERVER = "NickServ"
hook_url='https://fleep.io/hook/KJCT0Nm1QeqZFhH-oQd9jA/plain'
readbuffer=""

irc=socket.socket()
print "Bot starting..."
irc.connect((HOST, PORT))
print "Sending nick"
irc.send("NICK %s\r\n" % NICK)
print "Sending user information"
irc.send("USER bot 0 * :%s\r\n" % (REALNAME))
if registered == True:
    irc.send("JOIN " + CHANNEL + "\r\n")

_lowclean_rc = re.compile('[\x00-\x08\x0b-\x0c\x0e-\x1f]')
def clean_low_bytes(s):
    r"""Clean raw bytes not allowed in XML.

    >>> clean_low_bytes('\x00\x01\x08\x09\x0a\x0b\x0c\x0d\x0e ')
    '\t\n\r '
    >>> clean_low_bytes(u'\x00\x01\x08\x09\x0a\x0b\x0c\x0d\x0e ')
    u'\t\n\r '
    """
    res = _lowclean_rc.sub('', s)
    if res != s:
	print ("clean_low_bytes modified: " + str(s))
    return res

def debug(time, who, msg):
    print "Time: " + str(time)
    print "Who: " + str(who)
    print "Msg: " + str(msg) 

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

	if line[1] == "PRIVMSG" and line[2] == CHANNEL:
	    now = datetime.now()
	    time = "%02d:%02d" % (now.hour, now.minute)
	    seconds = "%02d" % now.second
	    who = whoSent(line)
	    if line[3] == ":\x01ACTION":
		del line[:4]
		msg = ' '.join(line)
		# skip the final \x01 byte
		fleep = "* " + who + " " + msg[:len(msg)-1]
	    else:
		del line[:3]
		msg = ' '.join(line)
		# skip the initial colon
		fleep = msg[1:]
	    #debug(time, who, msg)
	    try:
		r = requests.post(hook_url + "/" + who, data = {'message': clean_low_bytes(fleep)}, timeout = 1)
	    except RequestException:
		sys.exc_clear()
	    print "Status: " + str(r.status_code) + " " + str(time) + ":" + seconds

	if registered == False and line[1] == "NOTICE" and whoSent(line) == NICKSERVER:
	    irc.send("PRIVMSG NICKSERV IDENTIFY :" + PASSWORD + "\r\n")
	    irc.send("JOIN " + CHANNEL + "\r\n")
	    registered = True
	    print "We are (hopefully) registered!"

        if line[0]=="PING":
	    irc.send("PONG %s\r\n" % line[1])