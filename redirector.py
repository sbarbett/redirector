from flask import Flask, render_template_string, request, redirect, abort, url_for, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import sqlite3
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Adjust headers for reverse proxy
DB_PATH = "data/database.db"

# Get ROOT_REDIRECT and from the environment
ROOT_REDIRECT = os.getenv("ROOT_REDIRECT", "https://github.com")

def get_redirect_metadata(route):
    """Fetch metadata for a given route from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, description, image, target_url FROM redirects WHERE route = ?", (route,))
    result = cursor.fetchone()
    conn.close()
    return result

# Root route: 302 redirect to GitHub page
@app.route("/")
def root_redirect():
    return redirect(ROOT_REDIRECT, code=302)

@app.route("/<route>")
def redirect_with_metadata(route):
    metadata = get_redirect_metadata(route)
    if not metadata:
        abort(404)

    # Check if the "debug" query parameter is present
    debug_mode = request.args.get('debug', 'false').lower() == 'true'

    title, author, description, image_filename, target_url = metadata
    # Use url_for to dynamically generate the full URL for the image
    image_url = url_for('static', filename=f'img/{image_filename}', _external=True)

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="author" content="{author}">
        <meta name="description" content="{description}">
        <meta name="robots" content="index, follow">
        <meta property="og:type" content="website">
        <meta property="og:site_name" content="{title}">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:image" content="{image_url}">
        <meta property="og:url" content="{request.url}">
        <meta property="og:locale" content="en_US">
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{title}">
        <meta name="twitter:description" content="{description}">
        <meta name="twitter:image" content="{image_url}">
        <meta name="twitter:image:alt" content="{description}">
        <meta name="theme-color" content="#007bff">
        <link rel="canonical" href="{request.url}">
        <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
        <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
        <link rel="manifest" href="/{route}/manifest.json">
        {"<meta http-equiv='refresh' content='0; url=" + target_url + "'>" if not debug_mode else ""}
    </head>
    <body>
        <p>If you are not redirected automatically, click <a href="{target_url}">here</a>.</p>
    </body>
    </html>
    """

    return render_template_string(html)

@app.route("/<route>/manifest.json")
def dynamic_manifest(route):
    """Serve a dynamic manifest.json based on the route's metadata."""
    metadata = get_redirect_metadata(route)
    if not metadata:
        abort(404)

    title, author, description, image_filename, target_url = metadata
    image_url = url_for('static', filename=f'img/{image_filename}', _external=True)

    # Create the manifest.json dynamically
    manifest = {
        "name": title,
        "short_name": title[:12],  # Limit short name length
        "description": description,
        "start_url": f"/{route}",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#007bff",
        "icons": [
            {
                "src": image_url,
                "sizes": "180x180",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9199)

