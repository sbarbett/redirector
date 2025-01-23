import sqlite3
import os
import requests
import json

DB_PATH = "data/database.db"
STATIC_IMG_PATH = "static/img"

def create_table():
    """Create the redirects table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS redirects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            route TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT NOT NULL,
            target_url TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def list_redirects():
    """List all redirects in JSON format."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, route, title, author, description, image, target_url FROM redirects")
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dictionaries
    redirects = [
        {
            "id": row[0],
            "route": row[1],
            "title": row[2],
            "author": row[3],
            "description": row[4],
            "image": row[5],
            "target_url": row[6]
        }
        for row in rows
    ]

    # Output JSON
    print(json.dumps({"redirects": redirects}, indent=4))

def delete_redirect():
    """Delete a redirect."""
    list_redirects()
    redirect_id = input("Enter the ID of the redirect to delete: ")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM redirects WHERE id = ?", (redirect_id,))
    conn.commit()
    conn.close()
    print("Redirect deleted.")

def add_or_modify_redirect(modify=False):
    """Add or modify a redirect."""
    if modify:
        list_redirects()
        redirect_id = input("Enter the ID of the redirect to modify: ")
    else:
        redirect_id = None

    route = input("Enter the route (e.g., /my-awesome-redirect): ").strip("/")
    title = input("Enter the title: ")
    author = input("Enter the author: ")
    description = input("Enter the description: ")
    image_url = input("Enter the image URL: ")
    target_url = input("Enter the target URL: ")

    # Download and save the image
    image_filename = f"{route}.png"
    image_path = os.path.join(STATIC_IMG_PATH, image_filename)
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(image_path, "wb") as f:
            f.write(response.content)
        print(f"Image saved to {image_path}")
    else:
        print("Failed to download the image.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if modify:
        cursor.execute("""
            UPDATE redirects
            SET route = ?, title = ?, author = ?, description = ?, image = ?, target_url = ?
            WHERE id = ?
        """, (route, title, author, description, image_filename, target_url, redirect_id))
    else:
        cursor.execute("""
            INSERT INTO redirects (route, title, author, description, image, target_url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (route, title, author, description, image_filename, target_url))
    conn.commit()
    conn.close()
    print("Redirect added/modified.")

def main():
    create_table()
    while True:
        print("\nRedirect Manager:")
        print("1. List current redirects")
        print("2. Delete redirect")
        print("3. Add redirect")
        print("4. Modify redirect")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            list_redirects()
        elif choice == "2":
            delete_redirect()
        elif choice == "3":
            add_or_modify_redirect()
        elif choice == "4":
            add_or_modify_redirect(modify=True)
        elif choice == "5":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()

