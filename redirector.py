from flask import Flask, render_template_string, request, abort
import sqlite3

app = Flask(__name__)
DB_PATH = "data/database.db"

def get_redirect_metadata(route):
    """Fetch metadata for a given route from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, description, image, target_url FROM redirects WHERE route = ?", (route,))
    result = cursor.fetchone()
    conn.close()
    return result

@app.route("/<route>")
def redirect_with_metadata(route):
    metadata = get_redirect_metadata(route)
    if not metadata:
        abort(404)

    title, author, description, image, target_url = metadata
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="author" content="{author}">
        <meta name="description" content="{description}">
        <meta property="og:title" content="{title}">
        <meta property="og:description" content="{description}">
        <meta property="og:image" content="/static/img/{image}">
        <meta http-equiv="refresh" content="0; url={target_url}">
    </head>
    <body>
        <p>If you are not redirected automatically, click <a href="{target_url}">here</a>.</p>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9199)

