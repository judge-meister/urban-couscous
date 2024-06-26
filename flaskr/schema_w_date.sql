BEGIN TRANSACTION;
PRAGMA foreign_keys=OFF;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS default_sort;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS videos;
DROP TABLE IF EXISTS photos;
CREATE TABLE IF NOT EXISTS models 
      ( id int PRIMARY KEY NOT NULL, 
        name text,        /* model name */
        thumb text        /* model thumbnail */
      );
CREATE TABLE IF NOT EXISTS sites  
      ( id int PRIMARY KEY, 
        name text,        /* site name */
        location text     /* site folder location */
      );
CREATE TABLE IF NOT EXISTS photos 
      ( id int NOT NULL, 
        model_id int NOT NULL, /* model id */
        site_id int,      /* site id */
        name text,        /* photo set name */
        location text,    /* photo set folder location */
        thumb text,       /* photo set thumbnail */
        count int,        /* count of images in set */
        pdate text,       /* date yyyy-mm-dd */
        PRIMARY KEY (id, model_id, site_id)
        FOREIGN KEY (model_id) REFERENCES models(id)
        FOREIGN KEY (site_id) REFERENCES sites(id)
      );
CREATE TABLE IF NOT EXISTS videos 
      ( id int NOT NULL,
        model_id int NOT NULL, /* model id */
        site_id int,      /* site id */
        name text,        /* video name */
        filename text,    /* video filename */
        thumb text,       /* video thumbnail */
        poster text,      /* video poster */
        width int,        /* video width (px) */
        height int,       /* video height (px) */
        length double,    /* video length (seconds) */
        vdate text,       /* date yyyy-mm-dd */
        PRIMARY KEY (id, model_id, site_id), 
        FOREIGN KEY (model_id) REFERENCES models(id)
        FOREIGN KEY (site_id) REFERENCES sites(id)
      );
CREATE TABLE IF NOT EXISTS config 
      ( id int PRIMARY KEY NOT NULL, 
        webroot text,     /* webroot for pics etc (eg. http://gallery) */
        rootpath text,    /* root path to files in database relative to webroot (eg. /zstuff/zdata/stuff.backup/kindgirls) */
        title text,       /* title for page (eg. KindGirls) */
        images text,      /* relative location of thumbnails for photo sets */
        thumbs text,      /* relative location of thumbnails for videos */
        videos text,      /* relative location of video files */
        thumbs0 text,     /* seems to be used in photos, site and sites ?? */
        models text       /* relative location of thumbnails for models */
      );

CREATE TABLE IF NOT EXISTS default_sort
      ( id int PRIMARY KEY NOT NULL,
        photos text,      /* default sort order for photos pages */
        models text,      /* default sort order for models pages */
        model  text,
        videos text,      /* default sort order for videos pages */
        sites  text,      /* sites pages */
        site   text,
        search text
        /* - alpha / ralpha    id / rid    date / rdate    most / least    pics / rpics*/
      );
COMMIT;

# config - id, rootpath, title, images, thumbs, videos
# models - id, name, thumb
# sites  - id, name, location
# photos - id, model_id, site_id, name, location, thumb, count
# videos - id, model_id, site_id, name, filename, thumb, poster, width, height, length

# defaut_sort - photos, videos, sites
# - options are - alpha, id, date, piccount (all asc or desc)
#               - alpha / ralpha    id / rid    date / rdate    most / least
