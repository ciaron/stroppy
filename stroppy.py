import os
import jinja2
from yaml import load, dump
from pathlib import Path
home = str(Path.home())

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

gallery_path="Dropbox/gallery"
config_file = "config.yml"
abspath=os.path.join(home, gallery_path)

def read_config():
    with open(os.path.join(home, gallery_path, config_file), 'r') as stream:
        conf = load(stream, Loader=Loader)
    return conf

if __name__=="__main__":

    """ 
    1 read site config file into 'conf'
    2 create an _site directory to contain statically generated files
    3 loop over all subdirectories (containing images), ignoring _site
        (or any subdir starting with underscore)
    

    ## Templates:
    uikit, masonry layout for gallery index ("template")
    click image for fullscreen slider



    """

    conf = read_config()
    print(conf)

    gallerydirs = os.listdir(abspath)
    gallerydirs.sort() # sort in-place

    for g in gallerydirs:
        if (not os.path.isdir(os.path.join(abspath,g))):
            gallerydirs.remove(g)

    print(gallerydirs)
    galleries = {key: [] for key in gallerydirs}
    print(galleries)
    # now make a galleries dict of the form
    # {gallerydir1: [img1.jpg, img2.jpg, img3.JPG], gallerydir2: [...]} etc

