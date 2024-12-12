from astropy.io import ascii
import pandas as pd

mq = pd.read_csv('/data/GW_events/events2_mq_matched.csv')
dec_gtm30 = mq[mq['DEJ2000'] > -30]
dec_gtm30.to_csv('/data/GW_events/events2_mq_matched_dec_gtm30.csv', index=False)
print(len(dec_gtm30))