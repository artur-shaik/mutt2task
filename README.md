Slight modification of already existed mutt2task(https://gist.github.com/noqqe/6562350) script.

Dependencies:
  - taskopen(https://github.com/ValiValpas/taskopen) script
  - elinks(http://elinks.or.cz/).

Based on this blogpost: http://www.nixternal.com/mark-e-mails-in-mutt-as-tasks-in-taskwarrior/

This script creates task in taskwarrior from email within mutt. The subject of email becomes task name, and the body exports to taskopen note.

# Install

Change your location to script directory, and then link it:

```
ln -s $pwd/mutt2task.py ~/bin/
```

Then add this to your .muttrc:

```
macro index,pager t "<pipe-message>mutt2task.py<enter>"
```

# Usage

Just press t on email or inside email.
