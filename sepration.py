from astropy.coordinates import SkyCoord

Aql_o = SkyCoord(40.26358, 31.09260, frame='icrs', unit='deg')
Aql_alpha = SkyCoord(40.263541585380096, 31.09258504578179, frame='icrs', unit='deg')
Aql_zeta = SkyCoord(40.263546557693154, 31.09256638804064, frame='icrs', unit='deg')

print(Aql_o.separation(Aql_alpha))
print(Aql_o.separation(Aql_zeta))