from gracedb.func.crossmatch_mq import crossmatch_mq
from gracedb.func.area_90 import area_90
from astropy.io import ascii
import numpy as np
import astropy.cosmology.units as cu
import astropy.units as u
from astropy.cosmology import WMAP9

if __name__ == '__main__':

    #read the events csv
    event = 'events1'
    events = ascii.read('/data/GW_events/{}.csv'.format(event),format='csv')
    graceid = events['superevent_id']
    print(graceid)
    areas, distmean, diststd, ra, dec, prob_dec_gt_m30 = area_90(graceid)
    match_num = crossmatch_mq(graceid, out_file='{}_withoutfilter_mq_all'.format(event))
    events.add_column(areas, name='area_90')
    events.add_column(distmean, name='distmean')
    events.add_column(diststd, name='diststd')
    events.add_column(ra, name='ra')
    events.add_column(dec, name='dec')
    events.add_column(prob_dec_gt_m30, name='prob_dec_gt_m30')
    events.add_column(match_num, name='match_num')
    d = events['distmean'] * u.Mpc
    z = d.to(cu.redshift, cu.redshift_distance(WMAP9, kind="comoving", zmax=1200))
    events.add_column(z, name='zmean')
    events.write('/data/GW_events/{}_without_filter.csv'.format(event), format='csv', overwrite=True)
    index = np.where(areas < 100)
    events = events[index]
    print(events)
    events.write('/data/GW_events/{}_filtered.csv'.format(event), format='csv', overwrite=True)

    #crossmatch with mq catalog
    if len(index)>0:
        crossmatch_mq(events['superevent_id'], out_file='{}_mq_matched'.format(event))
    else:
        print('No events have area_90 < 100deg^2')



