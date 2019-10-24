import os
import sys
import imghdr
from jinja2 import Environment, FileSystemLoader, Template

from yaml import load, dump
from pathlib import Path
home = str(Path.home())

DEBUG = True

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

gallery_path="Dropbox/gallery" # path under $HOME
base_path=os.path.join(home, gallery_path)
config_file = "config.yml"
site_dir="_site"

def read_config():
    with open(os.path.join(home, gallery_path, config_file), 'r') as stream:
        conf = load(stream, Loader=Loader)
    return conf

def read_galleries():
    gs = os.listdir(base_path)
    gs.sort() # sort in-place

    galleries = {}
    for g in gs:
        gallerypath = os.path.join(base_path,g) 
        if (not os.path.isdir(gallerypath) or g.startswith("_")): # ignore non-dirs and existing _site dir
            pass
        else:
            if DEBUG: print(g)
            for root, dirs, files in os.walk(gallerypath):
                galleries[g] = []
                for f in files:
                    # only add names of image files
                    if imghdr.what(os.path.join(gallerypath,f)):
                        galleries[g].append(f)

    # we now have a dict of the form {gallery1: [ list of image filenames in gallery1 ], gallery2: [...]...}
    return galleries

if __name__=="__main__":

    """ 
    # read site config file into 'conf'
    # loop over all subdirectories (containing images), ignoring _site
        (or any subdir starting with underscore)
    # create an _site directory to contain statically generated files
    4
    5
    6
    7
    8
    

    ## Templates:
    uikit, masonry layout for gallery index ("template")
    click image for fullscreen slider



    """

    conf = read_config()
    galleries = read_galleries()
    try:
        os.mkdir(os.path.join(base_path, site_dir))
    except FileExistsError as err:
        print("Site directory exists, continuing...")
    except Exception as err:
        print("Failed to create site directory - exiting: %s, %s" % (type(err), err))
        sys.exit(1)

    env = Environment(loader=FileSystemLoader('templates'), cache_size=0)
    template = env.get_template('template1/index.html')
    rndr = template.render(**conf, galleries=galleries)

    with open("_index.html", "w") as fh:
            fh.write(rndr)

    if (DEBUG):
        print(conf)
        print(galleries)
