
import os
from flask import session, request

from flaskr.database.errors import DatabaseMissingError
from flaskr.database.utils import get_config, DatabaseTables
from flaskr.common.utils import human_time

def get_page_num(page):
    """"""
    if 'page' in session:
        page = session['page']
    return page


class PageInfo:
    def __init__(self, tagdicts, name, filtid=''):
        self.name = name
        self.tagdicts = tagdicts
        self.filtcol = '' if filtid=='' else name
        self.filtid = filtid


class PageBuilder:
    def __init__(self, info, htmlpageclass):
        self.info = info
        self.htmlpage = htmlpageclass

    def build(self):
        """self.info.name
           self.info.filtcol
           self.info.filtid
           self.info.tagdicts
        """
        pgnum = get_page_num(1)
        order = self.htmlpage.get_order(self.info.name)

        items = self.htmlpage.getitems(order)

        tagdicts = []
        x=0
        for tagdictfunc in self.info.tagdicts:
            tagdicts.append(tagdictfunc(items[x], self.info.filtcol, self.info.filtid, pgnum))
            x=x+1

        links = self.htmlpage.heading(self.info.name)
        page_dict = self.htmlpage.init_page_dict('', True, self.info.name, links)
        page_dict['search'] = True
        return page_dict, tagdicts


class HtmlSite:

    def __init__(self, dbname=''):
        """"""
        #error_occured = False
        self.dbname = dbname
        if dbname != '':
            self.db = DatabaseTables(dbname)
            try:
                self.config = get_config(dbname)
            except DatabaseMissingError:
                #error_occured = True
                raise
        else:
            self.db = None
            self.config = None
        self.pg = {'next':-1, 'prev':-1}

    def set_dbname(self, name):
        self.dbname = name

    def set_thumb_size(self):
        """"""
        if 'thumbsize' in session:
            if 'thumb_h' not in session:
                session['thumb_h'] = self.config['thumbsize']
            if session['thumbsize'] == "large":
                self.config['thumb_h'] = self.config['thumbsize']
            elif session['thumbsize'] == "small":
                self.config['thumb_h'] = self.config['thumbsize'] / 1.5


    def heading(self, page=None):
        """"""
        links = {
            "photos": {"href": f"/{self.dbname}/photos", "title": "Photos", 'class':'', 'rows': self.db.photos_table().row_count() },
            "models": {"href": f"/{self.dbname}/models", "title": "Girls",  'class':'', 'rows': self.db.models_table().row_count() },
            "sites":  {"href": f"/{self.dbname}/sites",  "title": "Sites",  'class':'', 'rows':  self.db.sites_table().row_count()-1 },
            "videos": {"href": f"/{self.dbname}/videos", "title": "Videos", 'class':'', 'rows': self.db.videos_table().row_count() }
            }

        if page is not None:
            if page == "site":
                page = "sites"
            if page == "model":
                page = "models"
            links[page]['class'] = " w3-dark-grey "

        return links


    #def getConfig(self):
    #    """"""
    #    return self.config

    def get_order(self, page):
        """"""
        if 'order' in session:
            order = session['order']
        else:
            # get default from db
            sql = f"SELECT {page} FROM default_sort;"
            order = self.db.sort_table().get_single_result(sql,1)[0]

        return order



    def page_range(self, num, total, pgcount=0):
        """"""
        if pgcount == 0:
            pgcount = self.config['pgcount']
        self.pg = {'next': num+1 if (num * pgcount) < total else 0,
                   'prev': num-1 if (num - 1) > 0 else 0}
        return (num-1)*pgcount, (num*pgcount)


    def moddict(self, models, _filtval='', _filtid='', pgnum=1):
        """"""
        cmodels = self.db.models_table().get_model_set_count()
        mdicts = []
        sidx, eidx = self.page_range(pgnum, len(models))
        for idx,name,thumb in models[sidx:eidx]:
            thumburl = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['models']}{thumb}"
            mdicts.append({'href': f"/{self.dbname}/model/{idx}",
                           'src': thumburl,
                           'name': name,
                           'height': self.config['thumb_h'],
                           'count': cmodels[idx]}
                           )
        return mdicts


    def galdict(self, photos, filtval='', filtid='', pgnum=1):
        """"""
        filterurl=""
        if filtval != '':
            filterurl = f"/{filtval}/{filtid}"
        gdict = []
        sidx, eidx = self.page_range(pgnum, len(photos))
        for gallery in photos[sidx:eidx]:
            #idx, model_id, site_id, name, location, thumb, count, pdate = gallery
            idx, _, _, name, location, thumb, count, _ = gallery
            thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thumb}"
            #name = name.replace('_', ' ')[:50]
            gdict.append({'href': f"/{self.dbname}/gallery{filterurl}/{idx}",
                          'src': thumb,
                          'name': name.replace('_', ' ')[:50],
                          'height': self.config['thumb_h'],
                          'count': count,
                          'basename': os.path.basename(location)}
                          )
        return gdict


    def viddict(self, videos, filtval='', filtid='', pgnum=1):
        """"""
        filterurl=""
        if filtval != '':
            filterurl=f"/{filtval}/{filtid}"
        vdicts = []
        sidx, eidx = self.page_range(pgnum, len(videos), self.config['vpgcount'])
        for vid in videos[sidx:eidx]:
            #idx, model_id, site_id, name, filename, thumb, poster, width, height, length, vdate = vid
            idx, _, _, name, filename, thumb, _, width, height, length, _ = vid
            thumb_url = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{thumb}"
            vdicts.append({'href':f"/{self.dbname}/video{filterurl}/{idx}",
                           'src':thumb_url,
                           'name':name,
                           'theight':self.config['thumb_h'],
                           'w': width,
                           'h': height,
                           'mlen':human_time(length),
                           'basename': os.path.basename(filename)}
                           )
        return vdicts


    def sitdict(self, sites, _filtval='', _filtid='', _pgnum=1):
        """"""
        #sites_count = {}
        csites = self.db.sites_table().get_sites_set_count()
        ordered_sites = {}
        sdict = []
        for idx,name,_location in sites:
            try:
                pid,_,_,_,_,thm = self.db.photos_table().select_where_order_by('site_id', idx, 'id', 'desc')[0][:6]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['images']}/{self.config['thumbs0']}/{thm}"
                ordered_sites[int(pid)] = {'href':f"/{self.dbname}/site/{idx}", 'src':thumb, 'name':name, 'height':self.config['thumb_h']}
                sdict.append({'href':f"/{self.dbname}/site/{idx}",
                              'src':thumb,
                              'name':name,
                              'height':self.config['thumb_h'],
                              'count': csites[idx]}
                              )
            except IndexError:
                vname = self.db.videos_table().select_where_order_by('site_id', idx, 'id', 'desc')[0][5]
                thumb = f"{self.config['webroot']}{self.config['rootpath']}/{self.config['thumbs']}/{vname}"
                ordered_sites[1] = {'href':f"/{self.dbname}/site/{idx}", 'src':thumb, 'name':name, 'height':self.config['thumb_h']}
                sdict.append({'href':f"/{self.dbname}/site/{idx}",
                              'src':thumb,
                              'name':name,
                              'height':self.config['thumb_h'],
                              'count': csites[idx]}
                              )
        return sdict


    def init_page_dict(self, title, plaintitle, ptype, links):
        """"""
        return {
            'title':title, 'db':self.dbname, 'heading':self.config['title'],
            'plaintitle':plaintitle, 'navigation':links, 'type':ptype, 'pg':self.pg,
            'url': request.base_url
        }

    def search_all_tables(self, term):
        """"""
        sites = self.db.sites_table().select_where_like('name', term)
        models = self.db.models_table().select_where_like('name', term)
        photos = self.db.photos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc')
        videos = self.db.videos_table().select_where_like_group_order('name', term, 'id', 'id', 'desc')

        modeldicts = self.moddict(models)
        galldicts = self.galdict(photos)
        viddicts = self.viddict(videos)
        sitedicts = self.sitdict(sites)

        return modeldicts, galldicts, viddicts, sitedicts