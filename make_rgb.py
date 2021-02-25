from imageio import imsave
from astropy.visualization import make_lupton_rgb
from astropy.io.fits import open
from glob import glob
import os

sami = open("9008500001_vst_60.fits")[1].data
gids = sami["CATID"]

# http://mips.as.arizona.edu/~cnaw/sun_2006.html
# weights = 10**(0.4*np.array([4.48, 4.67, 5.36]))
# print(weights/np.min(weights))
bands = ['i','r','g']
weights = [1., 1.19124201, 2.24905461]
pixelscales = dict(kids=0.2, hsc=0.168, panstarrs=0.25)
# Extra (arbitrary) factors of 0.25 and 0.1 for KiDS and PanSTARRS being shallower than HSC
surveys = {
    "kids": ("{gid}_*_sci.fits", 0, 0.25*1e9, None),
    "hsc": ("{gid}_HSC-{band}.fits", 1, 1e9, "FLUXMAG0"),
    "panstarrs": ("{gid}_PS_*.stk.{band}.unconv.fits", 0, 0.1*0.1, "EXPTIME"),
}
for survey, (filename_format, hdu, factor_unit, factor_name) in surveys.items():
    factor = factor_unit*pixelscales[path]**2
    is_hsc = survey == "hsc"
    do_glob = filename_format.count('*') > 0
    cutoutdirs = ["cutouts"] + (["cutouts-pdr2"] if is_hsc else [])
    for cutoutdir in cutoutdirs:
        path_full = "/".join([survey, cutoutdir, "small"])
        for gid in gids:
            try:
                img_paths = {
                    band: os.path.join(
                        path_full,
                        band,
                        filename_format.format(path_full=path_full, band=band, gid=gid)
                    )
                    for band in bands
                }
                if do_glob:
                    for band, img_path in img_paths.items():
                        img_paths[band] = glob(img_path)[0]
                imgs = {
                    band: open(img_path, ignore_missing_end=True)
                    for band, img_path in img_paths.items()
                }
                for band, img in imgs.items():
                    imgs[band] = img[hdu].data*(
                    1./img[0].header.get(factor_name) if factor_name is not None else 1)
                rgb = make_lupton_rgb(
                    imgs['i']*weights[0]*factor,
                    imgs['r']*weights[1]*factor,
                    imgs['g']*weights[2]*factor,
                    minimum=0, stretch=8e-4, Q=10)
                imsave(f"{path_full}/rgb/{gid}_rgb.png", rgb[::-1,:,:])
            except Exception as err:
                print("Failed with exception: {}; img_paths={}".format(err, img_paths))
