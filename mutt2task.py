#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## About
# Add a mail as task to taskwarrior.
# Work in conjunction with taskopen script
#
## Usage
# add this to your .muttrc:
# macro index,pager t "<pipe-message>mutt2task.py<enter>"

import os
import sys
import email
import re
import errno
import shutil

from email.header import decode_header
from subprocess import call, Popen, PIPE

def rollback():
    print("INFO: Rolling back incomplete task/note creation:")
    call(['task', 'rc.confirmation=off', 'undo'])

home_dir = os.path.expanduser('~')

notes_folder = ""
notes_folder_pat = re.compile(r"^[^#]*\s*NOTES_FOLDER\s*=\s*(.*)$")
for line in open("%s/.taskopenrc" % home_dir, "r"):
    match = notes_folder_pat.match(line)
    if match:
        notes_folder = match.group(1).replace('"', '')

if "$HOME" in notes_folder:
    notes_folder = notes_folder.replace("$HOME", home_dir)

if not notes_folder:
    notes_folder = "%s/.tasknotes" % home_dir

try:
    os.mkdir(notes_folder, mode=0o750)  # Changed mode to octal representation
except OSError as ose:
    if ose.errno == errno.EEXIST and os.path.isdir(notes_folder):
        pass
    else:
        print("ERR: Sorry, cannot create directory \"%s\"." % notes_folder)
        raise

message = sys.stdin.read()
message = email.message_from_string(message)

body = None
html = None
for part in message.walk():
    if part.get_content_type() == "text/plain":
        if body is None:
            body = ""
        body += part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')
    elif part.get_content_type() == "text/html":
        if html is None:
            html = ""
        html += part.get_payload(decode=True).decode(part.get_content_charset(), 'ignore')

tmpfile = Popen('mktemp', stdout=PIPE, shell=True).stdout.read().strip()  # Added shell=True for Popen
out = ""
if html:
    with open(tmpfile, "wb") as f:  # Changed mode to binary write
        f.write(html.encode())

    p1 = Popen(['cat', tmpfile], stdout=PIPE)
    p2 = Popen(['elinks', '--dump'], stdin=p1.stdout, stdout=PIPE)
    out = p2.stdout.read()
else:
    out = body

with open(tmpfile, "wb") as f:  # Changed mode to binary write
    f.write(out)

message = message['Subject']

def decodeif(s, ch):
    if isinstance(s, bytes):
        return s.decode(ch or 'ASCII')
    else:
        return s

message = decode_header(message)
message = ' '.join([decodeif(t[0], t[1]) for t in message])

# customize your own taskwarrior line
# use `message' to add the subject
if message == "None":
    message = "E-Mail import: no subject specified."
else:
    message = f"E-Mail subject: {message}"

res = Popen(['task', 'add', 'pri:L', '+email', '--', message], stdout=PIPE)
match = re.match(r"^Created task (\d+).*", res.stdout.read().decode())  # Changed decode to convert bytes to string
if match:
    print(match.string.strip())
    id = match.group(1)
    uuid = Popen(['task', id, 'uuids'], stdout=PIPE).stdout.read().strip().decode()  # Changed decode to convert byte
    ret = call(['task', id, 'annotate', '--', 'email:', 'Notes'])
    if ret:
        print("ERR: Sorry, cannot annotate task with ID=%s." % id)
        rollback()

    notes_file = notes_folder + "/" + uuid
    try:
        shutil.copy(tmpfile, notes_file)
        os.remove(tmpfile)
    except:
        print("ERR: Sorry, cannot create notes file \"%s\"." % notes_file)
        rollback()

### EOF
