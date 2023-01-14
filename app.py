from flask import Flask, render_template, request, flash, redirect, url_for, session
import logging
import app_config
from flask_session import Session
import msal
from werkzeug.middleware.proxy_fix import ProxyFix
from song_operations import get_songs, add_song, get_song_by_id, delete_song_by_id, update_song_by_id


app = Flask(__name__)
app.config.from_object(app_config)
Session(app)
logging.basicConfig(level=logging.INFO)


app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    songs = get_songs()
    return render_template('index.html', user=session["user"], version=msal.__version__, songs=songs)


@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)


@app.route(app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))


def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result


@app.route('/create', methods=['POST', 'GET'])
def create_song():
    if not session.get("user"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']

        if not title:
            flash('Title is required!')
        elif not artist:
            flash('Artist is required!')
        else:
            add_song({"Name": title, "Artist": artist})
            return redirect(url_for('index'))
    return render_template('create.html', title='Add a new song')


@app.route('/song/<int:song_id>')
def get_song(song_id):
    if not session.get("user"):
        return redirect(url_for("login"))
    results = get_song_by_id(song_id)

    return render_template('song.html', songs=results)


@app.route('/song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    if not session.get("user"):
        return redirect(url_for("login"))
    delete_song_by_id(song_id)
    return redirect(url_for('index'))


@app.route('/song/<int:song_id>/update', methods=['POST', 'GET'])
def update_song(song_id):
    if not session.get("user"):
        return redirect(url_for("login"))
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        if not title:
            flash('Title is required!')
        elif not artist:
            flash('Artist is required!')
        else:
            update_song_by_id({"Name": title, "Artist": artist}, song_id)
            return redirect(url_for('index'))
    return render_template('create.html', title='Update a song')


app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template


# main driver function
if __name__ == '__main__':
    app.run()
