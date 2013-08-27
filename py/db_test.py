#!/usr/local/bin/python

import sys, os
sys.path.append("/root/work/rts/rts_django")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rts_django.settings")
#from polls.models import Poll, Choice

from db.models import offical_load, rts_case, src_file, line_executed

if __name__ == "__main__":
	print "hello, world"

	#for item in offical_load.objects.all():
	p = offical_load(ats_load_name='load_016')
	p.save()

	case_info1 = rts_case(ats_case_id='8888001', ats_load_name=p.ats_load_name, ats_load_fk=p)
	case_info1.save()

	print "load_id load_name  datetime"
	for load in offical_load.objects.all():
		print "%-7d %-10s %-10s" % (load.id, load.ats_load_name, load.ats_timestamp)
    

