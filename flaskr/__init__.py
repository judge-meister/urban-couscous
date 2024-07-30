#!/usr/bin/env python3

# pylint: disable-msg=empty-docstring

"""
# init module for flaskr webapp

<dbname>      -  kindgirls/hegreart/femjoy/alsangels/inthecrack/alsscans
<listpage>    -  photos/models/sites/videos
<singlepage>  -  gallery/video/model
<filter>      -  site/model (works with video and gallery page)
<otherpages>  -  random/search
<option>      -  x2thumbsize
<sort>        -  alpha/latest/most/piccount


/<dbname>/<page><id>/<filter><id>/<option>/<sort>
thumbsize x2
sort order(alpha,latest,most,pics)


@app.route("/<dbname>/gallery/model/<mid>/<pid>")
@app.route("/<dbname>/gallery/site/<sid>/<pid>")
@app.route("/<dbname>/gallery/<id>")
@app.route("/<dbname>/models", methods=['POST', 'GET'])
@app.route("/<dbname>/model/<model>")
@app.route("/<dbname>/sites")
@app.route("/<dbname>/site/<site>", methods=['POST, 'GET'])
@app.route("/<dbname>/photos", methods=['POST', 'GET'])
@app.route("/<dbname>/videos", methods=['POST', 'GET'])
@app.route("/<dbname>/video/<vid>")
@app.route("/<dbname>/video/site/<sid>/<vid>")
@app.route("/<dbname>/video/model/<mid>/<vid>")
@app.route("/<dbname>/search", methods=['POST', 'GET'])
@app.route("/<dbname>/random")
@app.route("/<dbname>/edit/<table>/<id>")
@app.route("/<dbname>/")
@app.route("/<dbname>")
@app.route("/favicon.ico")
@app.route("/")
"""

from markupsafe import escape
from flask import Flask, request, session, make_response
from flask.views import View
from flaskr.factory import database_buttons, render_template, site_root, dbpage_factory, page_factory
#, file_system
from flaskr.database.errors import DatabaseMissingError

from flaskr.pages.base import do_post_get
from flaskr.pages.fs import FileSystemView
from flaskr.pages.video import VideoPageView, HtmlVideosPage, HtmlVideoPage
from flaskr.pages.model import HtmlModelsPage, HtmlModelPage
from flaskr.pages.photo import GalleryIdxPageView, GalleryPageView, HtmlPhotosPage
from flaskr.pages.site import HtmlSitesPage, HtmlSitePage
from flaskr.pages.common import DBSearchPageView, DBRandomPageView, RandomPageView, SearchPageView, RootPageView

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.secret_key = "d76df0b23782624435e4e42b9fd79b99e1b1a1c387a145ecae02683d69cf2fda"


@app.errorhandler(404)
def not_found(error):
    """"""
    print(error)
    obuttons, nbuttons, page_dict = database_buttons()
    resp = make_response(render_template('error.html',
                                         error=error,
                                         webroot="http://"+request.host.replace(':5000',''),
                                         page=page_dict,
                                         obuttons=obuttons,
                                         nbuttons=nbuttons,
                                         ), 404)
    resp.headers['X-Something'] = 'A value'
    return resp


# --------------------gallery page id id-------------------------------

app.add_url_rule("/<dbname>/gallery/<page>/<pageid>/<photoid>", view_func=GalleryPageView.as_view("gallery_page", app))
app.add_url_rule("/<dbname>/gallery/<idx>", view_func=GalleryIdxPageView.as_view("gallery_idx_page", app))

# ---------------------page--------------------------------------------

#@app.route("/<dbname>/models", methods=['POST', 'GET'])
#@app.route("/<dbname>/sites", methods=['POST', 'GET'])
#@app.route("/<dbname>/photos", methods=['POST', 'GET'])
#@app.route("/<dbname>/videos", methods=['POST', 'GET'])
#@app.route("/<dbname>/<page>", methods=['POST', 'GET'])


class DBPageView(View):
    def __init__(self, a, htmlpage):
        self.appt = a
        self.htmlpage = htmlpage

    def dispatch_request(self, dbname):
        do_post_get()
        mysite = self.htmlpage(dbname)
        mysite.set_thumb_size()
        return mysite.do_page()

app.add_url_rule("/<dbname>/models", view_func=DBPageView.as_view("models_page", app, HtmlModelsPage))
app.add_url_rule("/<dbname>/sites", view_func=DBPageView.as_view("sites_page", app, HtmlSitesPage))
app.add_url_rule("/<dbname>/photos", view_func=DBPageView.as_view("photos_page", app, HtmlPhotosPage))
app.add_url_rule("/<dbname>/videos", view_func=DBPageView.as_view("videos_page", app, HtmlVideosPage))

# ---------------------page id-----------------------------------------

#@app.route("/<dbname>/model/<modelid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/site/<siteid>", methods=['POST', 'GET'])
#@app.route("/<dbname>/video/<vid>")
#@app.route("/<dbname>/<page>/<index>", methods=['POST', 'GET'])


class DBPageIdView(View):
    def __init__(self, a, htmlpage):
        self.appt = a
        self.htmlpage = htmlpage

    def dispatch_request(self, dbname, index):
        do_post_get()
        mysite = self.htmlpage(dbname)
        mysite.set_thumb_size()
        return mysite.do_page(index)


app.add_url_rule("/<dbname>/model/<index>", view_func=DBPageIdView.as_view("modelid_page", app, HtmlModelPage))
app.add_url_rule("/<dbname>/site/<index>", view_func=DBPageIdView.as_view("siteid_page", app, HtmlSitePage))
app.add_url_rule("/<dbname>/video/<index>", view_func=DBPageIdView.as_view("videoid_page", app, HtmlVideoPage))


app.add_url_rule("/<dbname>/video/<page>/<pageid>/<vid>", view_func=VideoPageView.as_view("video_page", app))

app.add_url_rule("/<dbname>/search", view_func=DBSearchPageView.as_view("searchdb_page", app))
app.add_url_rule("/<dbname>/random", view_func=DBRandomPageView.as_view("randomdb_page", app))
app.add_url_rule("/random", view_func=RandomPageView.as_view("random_page", app))
app.add_url_rule("/search", view_func=SearchPageView.as_view("search_page", app))
app.add_url_rule("/<dbname>", view_func=RootPageView.as_view("root_page", app))

app.add_url_rule("/fs/<path:subpath>", view_func=FileSystemView.as_view("fs", app))
#app.add_url_rule("/fs", view_func=FileSystemView.as_view("fs", app, '/'))


@app.route("/favicon.ico")
@app.route("/android-chrome-512x512.png")
@app.route("/android-chrome-192x192.png")
def favicon():
    """"""
    app.logger.debug("favicon.ico handled")
    return ""


@app.route("/")
def site_index():
    """"""
    return site_root()


# ----  testing ----

class Testing(View):
    def __init__(self, a):
        self.appt = a

    def dispatch_request(self, subpath):
        #users = User.query.all()
        self.appt.logger.info("arse")
        return f'Subpath {escape(subpath)}' #render_template("users.html", objects=users)

app.add_url_rule("/path/<path:subpath>", view_func=Testing.as_view("user_list", app))

# ----------------main-------------------------------------------------

if __name__ == '__main__':

    app.run(host="0.0.0.0", port=8181)


