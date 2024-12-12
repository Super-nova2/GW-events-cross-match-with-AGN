from astropy.coordinates import SkyCoord
from ligo.skymap.io import read_sky_map
from ligo.skymap.postprocess import crossmatch
from astropy import units as u
import astropy.cosmology.units as cu
from astropy.cosmology import WMAP9
from astropy.table import Table, vstack
from astropy import table
from astropy.io import ascii
import os
import numpy as np

def crossmatch_mq(gracedbid, out_file):

    #get the catalogue
    cat = ascii.read('/data/milliquas.csv', format='csv')
    z = cat['z'] * cu.redshift
    dis = z.to(u.Mpc, cu.redshift_distance(WMAP9, kind="luminosity"))
    cat.add_column(dis,name='Distance')
    coordinates = SkyCoord(cat['RAJ2000']*u.deg, cat['DEJ2000']*u.deg,cat['Distance'])
    res = Table()   #the matched catalogue of all events
    match_num = np.zeros(len(gracedbid),dtype=int)  #the number of matched AGNs for each event

    for j in range(len(gracedbid)):
        #read skymap
        name = gracedbid[j]
        
        if os.path.exists('/data/GW_events/match_mq/{}.csv'.format(name)):
            match_tab = ascii.read('/data/GW_events/match_mq/{}.csv'.format(name), format='csv')
            match_num[j] = len(match_tab)
            if match_num[j] == 0:
                continue
        else:
            skymap = read_sky_map('/data/GW_events/data/{}_multiorder.fits'.format(name), distances=True, nest=True, moc=True)
            result = crossmatch(skymap, coordinates)
            match_tab = cat[result.searched_prob_vol < 0.9]  #the matched catalogue of each event
            match_tab.write('/data/GW_events/match_mq/{}.csv'.format(name), format='csv', overwrite=True)
            match_num[j] = len(match_tab)
        if j==0:
            res = match_tab
        else:
            res = vstack([res, match_tab], join_type='exact')
        
        


    #save the catlogue
    res = table.unique(res, keys='Name')
    res.write('/data/GW_events/{}.csv'.format(out_file), format='csv', overwrite=True)

    return match_num


if __name__ == '__main__':
    graceid = ['S240919bn', 'S240924a']
    match_num = crossmatch_mq(graceid, 'mq_matched')
