import os
import sys
import re
from shutil import copy
from collections import OrderedDict
import imghdr
from jinja2 import Environment, FileSystemLoader, Template
from slugify import slugify
from yaml import load, dump
from pathlib import Path
home = str(Path.home())

DEBUG = True
COPY = False # whether to copy image files - only needed for first time runs

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

gallery_path="Dropbox/gallery" # path under $HOME
base_path=os.path.join(home, gallery_path)
config_file = "config.yml"
site_dir="_site"
delim = "__" # delimiter for leading ordering

def read_config():
    # read the YAML config file into "conf" object
    with open(os.path.join(home, gallery_path, config_file), 'r') as stream:
        conf = load(stream, Loader=Loader)
    #if DEBUG: print(conf)
    return conf

def read_galleries():
    gs = os.listdir(base_path)
    gs.sort() # sort in-place

    galleries = OrderedDict()
    for g in gs: # gallery names, i.e. directory names
        try:
            cleanname = re.split(delim,g)[1]
        except: # cannot split
            cleanname = re.split(delim,g)[0]
        slug = slugify(cleanname)

        gallerypath = os.path.join(base_path, g) 
        if (not os.path.isdir(gallerypath) or g.startswith("_")): # ignore non-dirs and existing _site dir
            pass
        else:
            for root, dirs, files in os.walk(gallerypath):
                galleries[slug] = {'name': cleanname, 'dir': g, 'images': {}}
                files.sort()
                for imagefilename in files:

                    if imghdr.what(os.path.join(gallerypath, imagefilename)): # is an image file
                        galleries[slug]['images'][imagefilename] = {}
                        descriptorfilename = os.path.join(gallerypath, os.path.splitext(imagefilename)[0] + ".md")
                        if (os.path.exists(descriptorfilename)):
                            # there's an .md file matching this filename
                            with open(descriptorfilename) as stream:
                                c = load(stream, Loader=Loader)
                                for datakey,datavalue in c.items(): # add all the data to the image metadata
                                    galleries[slug]['images'][imagefilename][datakey] = datavalue
                                    #print(datakey, datavalue)

    # we now have a dict of the form:
    # {gallery_slug: 
    #           { name:        <name of directory, i.e. gallery>,
    #             description: <gallery desc from gallery.md in src dir (if exists)>
    #             images:      { imagefilename1: { title: <image title from imagename.md
    #                                              description: <image description from imagename.md (if exists)>
    #                                    } 
    #                   imagefilename2: {
    #                                    }  
    #                 }
    #
    #
    #
    return galleries

def copy_images(gallery):
    # copy images files from source galleries to gallery-slug/images/
    
    dst = os.path.join(base_path, site_dir, gallery, "images")
    print(dst)

    for i in galleries[gallery]['images']:
        src = os.path.join(base_path, galleries[gallery]["dir"], i)
        copy(src, dst)

def renderHTML(template, galleries):
    # render the first gallery to the main index.html
    first = next(iter(galleries))
    rndr = template.render(**conf, slug=first, galleries=galleries)
    with open(os.path.join(base_path, site_dir, "index.html"), "w") as fh:
        fh.write(rndr)

    # loop over galleries rendering <gallery-slug>.html for each
    for gallery in iter(galleries):
        rndr = template.render(**conf, slug=gallery, galleries=galleries)
        try:
            os.makedirs(os.path.join(base_path, site_dir, gallery, "images"))
        except:
            pass
        with open(os.path.join(base_path, site_dir, gallery, "index.html"), "w") as fh:
            fh.write(rndr)

if __name__=="__main__":

    """ 
    # read site config file into 'conf'
    # loop over all subdirectories (containing images), ignoring _site
        (or any subdir starting with underscore)
    # create an _site directory to contain statically generated files
    4
    5
    6
    ## Templates:
    uikit, masonry layout for gallery index ("template")
    click image for fullscreen slider

    """

    conf = read_config()
    galleries = read_galleries()
    print(galleries)

    # create site directory...
    try:
        os.mkdir(os.path.join(base_path, site_dir))
    except FileExistsError as err:
        #print("Site directory exists, continuing...")
        pass
    except Exception as err:
        print("Failed to create site directory - exiting: %s, %s" % (type(err), err))
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(os.path.join('templates', conf['template'])), cache_size=0)
    template = env.get_template('content.html')

    renderHTML(template, galleries)

    # ...populate site directory with the image folders (copy)
    if COPY:
        for gallery in galleries:
          copy_images(gallery)

    #if (DEBUG):
    #    print(conf)
    #    print(galleries)
