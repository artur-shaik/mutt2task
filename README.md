Slight modification of already existed mutt2task script: https://gist.github.com/noqqe/6562350, as well as tasknote(https://github.com/mikebobroski/tasknote) script.

Based on this blogpost: http://www.nixternal.com/mark-e-mails-in-mutt-as-tasks-in-taskwarrior/

This script creates task in taskwarrior from email within mutt. The subject of email becomes task name, and the body exports to tasknote.

You need elinks(http://elinks.or.cz/) installed, to make dump of html emails.

# Install

Copy files to bin directory, and chmod +x them. Then add this to your .muttrc:

    macro index,pager t "<pipe-message>mutt2task.py<enter>"

# Usage

Just press t on email or inside email.
