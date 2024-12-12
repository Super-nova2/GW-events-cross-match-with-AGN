import mastcasjobs
from astropy.io import ascii
from astropy.table import unique

# MAST CasJobs credentials
user = "supernova"
pwd = "sbs1rqlb6x"

jobs = mastcasjobs.MastCasJobs(username=user, password=pwd, context="PanSTARRS_DR2",request_type='POST')

# get the table of events
events = ascii.read('/data/GW_events/events2_mq_matched.csv',format='csv')
jobs.drop_table_if_exists('O4b_events_mq_matched')
jobs.drop_table_if_exists('O4b_events_mq_matched_PS1')
jobs.upload_table('O4b_events_mq_matched', events)


query="""SELECT d.Name, d.RAJ2000, d.DEJ2000, d.z, d.Type, d.Distance,
o.objID, o.gMeanKronMag, o.rMeanKronMag,o.nDetections,
soa.primaryDetection
 INTO mydb.[O4b_events_mq_matched_PS1]
 FROM mydb.[O4b_events_mq_matched] d
CROSS APPLY dbo.fGetNearbyObjEq(d.RAJ2000, d.DEJ2000, 1.0/60.0) as x
JOIN MeanObjectView o on o.ObjID=x.ObjId
LEFT JOIN StackObjectAttributes AS soa ON soa.objID = x.objID
WHERE o.nDetections>5
AND soa.primaryDetection>0
AND o.gMeanKronMag < 22
AND o.rMeanKronMag < 22
AND o.gMeanKronMag > 0
AND o.rMeanKronMag > 0
AND o.decMean > -30
"""
# query="""SELECT d.Name, d.RAJ2000, d.DEJ2000, d.z, d.Type, d.Distance,
# o.objID, o.gMeanKronMag, o.rMeanKronMag,o.nDetections
#  INTO mydb.[O4b_events_mq_matched_PS1]
#  FROM mydb.[O4b_events_mq_matched] d
# CROSS APPLY dbo.fGetNearestObjEq(d.RAJ2000, d.DEJ2000, 3.0/60.0) as x
# JOIN MeanObjectView o on o.ObjID=x.ObjId
# WHERE o.gMeanKronMag < 22
# AND o.rMeanKronMag < 22
# AND o.gMeanKronMag > 0
# AND o.rMeanKronMag > 0
# AND o.decMean > -30
# """
# query="""SELECT d.Name, d.RAJ2000, d.DEJ2000, d.z, d.Type, d.Distance,
# o.objID, o.gMeanKronMag, o.rMeanKronMag,o.nDetections
#  INTO mydb.[O4b_events_mq_matched_PS1]
#  FROM mydb.[O4b_events_mq_matched] d
# CROSS APPLY dbo.fGetNearestObjEq(d.RAJ2000, d.DEJ2000, 3.0/60.0) as x
# JOIN MeanObjectView o on o.ObjID=x.ObjId
# WHERE o.decMean > -30
# """
print(query)
jobs.quick(query, task_name='filter with g/r mag')
events_filtered = jobs.fast_table('O4b_events_mq_matched_PS1', verbose=True)
print(len(events_filtered))

index = []
for i in range(len(events_filtered)):
    # if events_filtered['gMeanKronMag'][i] == -999 and events_filtered['rMeanKronMag'][i] == -999:
    #     index.append(i)
    events_filtered['Name'][i] = events_filtered['Name'][i].replace('_',' ')

unq_events_filtered = unique(events_filtered, keys=['Name'])
print(len(unq_events_filtered))

# unq_events_filtered.write('/data/GW_events/events2_mq_matched_PS1_nondetection.csv', format='csv', overwrite=True)