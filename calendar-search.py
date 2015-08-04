#!/usr/bin/env python
# -*- coding: utf-8 -*-

# read/search entries in Jolla calendar db.
# runs this script as root (with sudo) because the calendar db is located at a protected place.
# https://together.jolla.com/question/53418/search-in-calendar-app/

# This code is placed into public domain.

# version 1.00 31.07.2015  rolfa  first version
# version 1.01 31.07.2015  rolfa  ordered results
# version 1.02 03.08.2015  rolfa  raw_input

'''
EXAMPLES
========

Interactive search: sudo calendar-search.py

List all entries: sudo calendar-search.py "%"

List birthdays: sudo calendar-search.py "%" | grep "BIRTHDAY"

List entries containing "lunch" and "paul" (in that order): sudo calendar-search.py "lunch%paul"
'''


'''
HOW TO ACTIVATE SUDO
====================
as root:

usermod -a -G wheel nemo

pkcon install sudo
pkcon install nano
EDITOR="nano" visudo

  ## Uncomment to allow members of group wheel to execute any command
  %wheel ALL=(ALL) ALL

reboot

Test as nemo:
ls /home/nemo/.local/share/system/privileged
  -> fails
sudo ls /home/nemo/.local/share/system/privileged
  -> works
'''

import os, sys, sqlite3

if os.geteuid() != 0:
    exit('This script needs root privileges, please try again using "sudo".')

cal_file = '/home/nemo/.local/share/system/privileged/Calendar/mkcal/db'

like_base = '''
(summary like '%%%s%%' or location like '%%%s%%' or description like '%%%s%%')
'''

sql_base = '''
select date(datestartlocal, 'unixepoch') start, '' end, category, summary, location, description FROM components where %s and category = 'BIRTHDAY' and DateDeleted = 0
union all
select datetime(datestartlocal, 'unixepoch') start, datetime(dateendduelocal, 'unixepoch') end, category, summary, location, description FROM components where %s and category <> 'BIRTHDAY' and DateDeleted = 0
order by category desc, start
'''

try:
    db = sqlite3.connect(cal_file)
except Exception as e:
    exit('could not open calendar DB: %s' % e)

while True:

    if len(sys.argv) > 1:
        searchtext = sys.argv[1]
        sys.argv[1] = ''
    else:
        searchtext = raw_input('Searchtext (empty to exit): ')
    
    if not searchtext: break

    like = like_base % (searchtext, searchtext, searchtext)
    sql = sql_base % (like, like)

    try:
        rows = db.execute(sql).fetchall()
    except Exception as e:
        exit('error while accessing calendar db: %s' % e)
    
    for row in rows:
        for el in row:
            print '%s\t' % el.encode('utf-8'),
        print

    print 'hits: %s\n' % len(rows)

try:
  db.close()
except Exception as e:
  pass
