from ligo.skymap.io import read_sky_map
import astropy_healpix as ah
import numpy as np
from astropy import units as u
from ligo.gracedb.rest import GraceDb
import wget
from astropy.io import fits
import requests
import os
import healpy as hp


def area_90(graceid):
    # input a list of GraceIDs and return the area of the 90% probability region for each event and the mean,std of the distance

    client = GraceDb()
    areas = np.zeros(len(graceid))
    distmean = np.zeros(len(graceid))
    diststd = np.zeros(len(graceid))
    ras = np.zeros(len(graceid))
    decs = np.zeros(len(graceid))
    prob_dec_gt_m30 = np.zeros(len(graceid))

    for j in range(len(graceid)):
        name = graceid[j]

        if os.path.exists('/data/GW_events/data/{}_multiorder.fits'.format(name)):
            # If the skymap file already exists, read it directly
            skymap = read_sky_map('/data/GW_events/data/{}_multiorder.fits'.format(name), distances=True, nest=True, moc=True)

        else: 
            #Get the event skymap
            response = client.superevent(name)
            file = response.json()['links']['files']

            suffixes = ['Bilby.multiorder.fits','Bilby.offline0.multiorder.fits','bayestar.multiorder.fits']
            url_found = False
            
            for suffix in suffixes:
                url = f"{file}{suffix}"
                try:
                    print(url)
                    response = requests.get(url)
                    if response.status_code == 200:
                        url_found = True
                        break
                except Exception as e:
                    print(f'Error fetching URL {url}: {e}')

            if not url_found:
                print(f'No skymap found for event {name} at index {j}')
                exit(0) # 跳过当前事件，继续处理下一个

            print(j, name, url)
            print(wget.download(url, out = '/data/GW_events/data/{}_multiorder.fits'.format(name)))
            skymap = read_sky_map('/data/GW_events/data/{}_multiorder.fits'.format(name), distances=True, nest=True, moc=True)
            


        # Find the 90% Probability Region
        skymap.sort('PROBDENSITY', reverse=True)
        level,ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
        nside = ah.level_to_nside(level)
        pixel_area = ah.nside_to_pixel_area(nside)
        prob = pixel_area * skymap['PROBDENSITY']
        cumprob = np.cumsum(prob)
        i = cumprob.searchsorted(0.9)
        area_90 = pixel_area[:i].sum()
        areas[j] = '{:.4f}'.format(area_90.to_value(u.deg**2))
        print(area_90.to_value(u.deg**2))

        # Find the most probable ra and dec
        i = np.argmax(skymap['PROBDENSITY'])
        uniq = skymap[i]['UNIQ']
        level, ipix = ah.uniq_to_level_ipix(uniq)
        nside = ah.level_to_nside(level)
        ra, dec = ah.healpix_to_lonlat(ipix, nside, order='nested')
        ras[j] = '{:.4f}'.format(ra.deg)
        decs[j] = '{:.4f}'.format(dec.deg)

        # cauluclate the probability of dec > -30
        level,ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
        nside = ah.level_to_nside(level)
        pixel_area = ah.nside_to_pixel_area(nside)
        prob = pixel_area * skymap['PROBDENSITY']
        lon = np.zeros(len(nside))
        lat = np.zeros(len(nside))
        for k in range(len(nside)):
            lon[k], lat[k] = hp.pix2ang(nside[k], ipix[k], nest=True, lonlat=True) 
        index = np.where(lat > -30)
        prob_dec_gt_m30[j] = '{:.4f}'.format(prob[index].sum())


        # get the mean and std of the distance
        hdul = fits.open("/data/GW_events/data/{}_multiorder.fits".format(name))
        hdr = hdul[1].header
        distmean[j] = '{:.4f}'.format(hdr['DISTMEAN'])
        diststd[j] = '{:.4f}'.format(hdr['DISTSTD'])
        hdul.close()

    return areas, distmean, diststd, ras, decs, prob_dec_gt_m30
        
if __name__ == '__main__':
    graceid = ['S240107b','S240915b']
    areas, distmean, diststd, ras, decs, prob_dec_gt_m30 = area_90(graceid)
    print(areas)
    print(distmean)
    print(diststd)
    print(ras)
    print(decs)
    print(prob_dec_gt_m30)