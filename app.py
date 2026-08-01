import requests
from flask import redirect
from flask import Flask, render_template, request
from AI.database import database as db
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
import base64
import requests
from AI import assistant as ai
import asyncio

db.create_database()

app = Flask(__name__)

limiter = Limiter(get_remote_address, app=app, storage_uri="memory://")
print("Limiter loaded")


UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
@limiter.limit("30/minute")
def home():

    response = ""

    if request.method == "POST":

        user_message = request.form.get("message", "").strip()

        file = request.files.get("file")


        if not user_message and not file:
            return redirect("/")


        if len(user_message) > 2000:
            return "❌ Message is too long."


        if file and file.filename != "":

            print("FILE:", file.filename)

            content = file.read().decode("utf-8", errors="ignore")

            user_message = f"""
The user uploaded this file:

{content}


User question:

{user_message}
"""


        try:

            response = ai.get_response(user_message)


        except Exception as e:

            print("AI ERROR:", e)

            return render_template("ai_error.html"), 503



    chat_history = db.get_chat_history()


    return render_template(
        "index.html",
        response=response,
        chat_history=chat_history
    )
    


@app.route("/clear_all")
def clear_history():

    db.delete_memories()
    db.delete_chathistory()

    return redirect("/")


@app.route("/memory")
def memory():
    print("MEMORY PAGE OPENED")

    memories = db.get_all_memories()

    return render_template("memory.html", memories = memories)

print(app.url_map)

@app.route("/settings")
def settings():
    print("Settings PAGE OPENED")

    memory_enabled = db.get_setting("memory_enabled")


    return render_template("settings.html", memory_enabled= memory_enabled)

@app.route("/toggle_memory", methods=["POST"])
def toggle_memory():

    current = db.get_setting("memory_enabled")

    if current == "true":
        db.update_settings("memory_enabled", "false")
    else:
        db.update_settings("memory_enabled", "true")

    return redirect("/settings")

@app.route("/history")
def chat_history():
    print("History PAGE OPENED")

    chat_history = db.get_chat_history()

    return render_template("history.html", history = chat_history)

@app.route("/upload", methods = ["POST"])
def upload():

    file = request.files.get("file")

    if not file:
        print("No file")
        return redirect("/")

    filename = file.filename
 

    content = file.read().decode("utf-8", errors="ignore")
    print("Filename:", filename)
    print("Content:", content[:100])

    db.save_document(filename, content)
    print("File has been saved")

    return redirect("/knowledge")


@app.route("/documents")
def documents():

    print("DOCUMENTS PAGE OPENED")

    documents = db.get_documents()

    return render_template("documents.html", documents=documents)


@app.errorhandler(500)
def internal_error(error):

    return render_template("error.html"), 500

@app.errorhandler(404)
def internal_error(errror):

    return render_template("error.html"), 404

@app.errorhandler(429)
def ratelimit_error(error):

    return render_template("error.html", message="Too many requests. Please wait a moment and try again."), 429


print(app.url_map)

if __name__ == "__main__":
    app.run(debug=False)


    









