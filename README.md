# Asce722spectra

Get the Multi-period response spectrum for a site for use with ASCE 7-22.Free to use.
Data source is USGS (ASCE 7-22 Database) and OpenStreetMaps. Authors do not assume any responsibility or liability for its accuracy. 
Use of the output of this program does not imply approval by the governing building code bodies responsible for building code 
approval and interpretation for the building site described by latitude/longitude location.

Written by HXB

Accepts both late long pair or an address.

2/17/2024  Accepts an estimated shear wave velocity and computes the governing spectra based an upper bound, lower bound and estimated site class.  Extensive revisions to code to write the governing spectra to file. 
2/18/2024  Revised to compute sds and sd1 per ASCE 7-22 Section 21.4 where the shear wave velocity is estimated.
3/27/2024  Added option to lookup local variation of SDS and SD1 around site.
11/1/2024  Added default siteclass and interpolated spectra based on measured shear wave velocity.
