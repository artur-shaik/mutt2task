#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
## About
# Add a mail as task to taskwarrior.
# 
## Usage
# add this to your .muttrc:
# macro index,pager t "<pipe-message>mutt2task.py<enter>" 
 
# import libraries
import sys
import email
import re
from email.header import decode_header
from subprocess import call, Popen, PIPE
x = sys.stdin.read()
x = email.message_from_string(x)

body = None
html = None
for part in x.walk():
    if part.get_content_type() == "text/plain":
        if body is None:
            body = ""
        body += unicode(
            part.get_payload(decode=True),
            part.get_content_charset(),
            'replace'
        ).encode('utf8','replace')
    elif part.get_content_type() == "text/html":
        if html is None:
            html = ""
        html += unicode(
            part.get_payload(decode=True),
            part.get_content_charset(),
            'replace'
        ).encode('utf8','replace')

tmpfile = "/tmp/mutt2task.tmp"
out = ""
if html:
    with open(tmpfile, "w") as f:
        f.write(html)

    p1 = Popen(['cat', tmpfile], stdout=PIPE)
    p2 = Popen(['elinks', '--dump'], stdin=p1.stdout, stdout=PIPE)
    out = p2.stdout.read()
else:
    out = body

with open(tmpfile, "w") as f:
    f.write(out)

x = x['Subject']
 
# decode internationalized subject and transform ascii into utf8
x = decode_header(x)
x = ' '.join([ unicode(t[0], t[1] or 'ASCII' ) for t in x ])
x = x.encode('utf8')
 
# customize your own taskwarrior line
# use `x' to add the subject
res = Popen(['task', 'add', 'pri:L', '+mail', '--', x ], stdout=PIPE)
match = re.match("Created task (\d+)\.", res.stdout.read())
if match:
    call(['tasknote', match.group(1), 'p', tmpfile])

call(['rm', tmpfile])
