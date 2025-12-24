"""
Main Flask Application
AI Powered Interactive Study Assistant
FINAL STABLE VERSION
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
import os
import traceback

from config import Config
from modules.text_processor import TextProcessor
from modules.semantic_search import SemanticSearch
from modules.summarizer import Summarizer
from modules.quiz_generator import QuizGenerator
from modules.document_manager import DocumentManager

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "ai-study-assistant-secret-key"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs("data", exist_ok=True)

# --------------------------------------------------
# MODULE INITIALIZATION
# --------------------------------------------------
text_processor = TextProcessor()
semantic_search = SemanticSearch()
summarizer = Summarizer()
quiz_generator = QuizGenerator()
doc_manager = DocumentManager()

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# --------------------------------------------------
# ROUTES
# --------------------------------------------------
@app.route("/")
def index():
    documents = doc_manager.get_all_documents()
    return render_template("index.html", documents=documents)

# --------------------------------------------------
# UPLOAD DOCUMENT
# --------------------------------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        try:
            if "file" not in request.files:
                return jsonify({"error": "No file provided"}), 400

            file = request.files["file"]
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400

            if not allowed_file(file.filename):
                return jsonify({"error": "Invalid file type"}), 400

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            content = doc_manager.process_upload(filepath, filename)
            if not content or len(content.strip()) < 50:
                return jsonify({"error": "Document too short"}), 400

            processed = text_processor.preprocess(content)

            doc_id = doc_manager.save_document(
                filename,
                filepath,
                content,
                processed["token_count"],
                len(processed["sentences"])
            )

            # ✅ ONLY store doc_id in session
            session["current_doc_id"] = doc_id

            return jsonify({
                "success": True,
                "doc_id": doc_id,
                "filename": filename,
                "word_count": processed["token_count"],
                "sentence_count": len(processed["sentences"])
            })

        except Exception as e:
            print("UPLOAD ERROR:", traceback.format_exc())
            return jsonify({"error": "Upload failed"}), 500

    return render_template("upload.html")

# --------------------------------------------------
# STUDY PAGE
# --------------------------------------------------
@app.route("/study/<int:doc_id>")
def study(doc_id):
    doc = doc_manager.get_document(doc_id)
    if not doc:
        return redirect(url_for("index"))

    session["current_doc_id"] = doc_id
    return render_template("study.html", document=doc)

# --------------------------------------------------
# ASK QUESTION
# --------------------------------------------------
@app.route("/api/ask", methods=["POST"])
def ask_question():
    try:
        question = request.json.get("question", "").strip()
        if not question:
            return jsonify({"error": "No question provided"}), 400

        doc_id = session.get("current_doc_id")
        if not doc_id:
            return jsonify({"error": "No document loaded"}), 400

        doc = doc_manager.get_document(doc_id)
        content = doc[3]

        processed = text_processor.preprocess(content)
        sentences = processed["sentences"]

        semantic_search.encode_documents(sentences)
        result = semantic_search.find_answer(question)

        if not result:
            return jsonify({
                "answer": "No relevant answer found in the document.",
                "confidence": 0,
                "relevant_sections": []
            })

        return jsonify({
            "answer": result["answer"],
            "confidence": result["confidence"],
            "relevant_sections": result["relevant_sentences"]
        })

    except Exception as e:
        print("ASK ERROR:", traceback.format_exc())
        return jsonify({"error": "Failed to answer question"}), 500

# --------------------------------------------------
# SUMMARY
# --------------------------------------------------
@app.route("/api/summarize", methods=["POST"])
def summarize():
    try:
        doc_id = session.get("current_doc_id")
        if not doc_id:
            return jsonify({"error": "No document loaded"}), 400

        ratio = float(request.json.get("ratio", 0.3))

        doc = doc_manager.get_document(doc_id)
        content = doc[3]

        processed = text_processor.preprocess(content)
        sentences = processed["sentences"][:200]  # safety limit

        summary = summarizer.summarize_improved(content, sentences, ratio)
        bullet_points = summarizer.generate_bullet_points(content, sentences)

        return jsonify({
            "summary": summary,
            "bullet_points": bullet_points
        })

    except Exception as e:
        print("SUMMARY ERROR:", traceback.format_exc())
        return jsonify({"error": "Failed to generate summary"}), 500

# --------------------------------------------------
# QUIZ
# --------------------------------------------------
@app.route("/api/generate-quiz", methods=["POST"])
def generate_quiz():
    try:
        doc_id = session.get("current_doc_id")
        if not doc_id:
            return jsonify({"error": "No document loaded"}), 400

        doc = doc_manager.get_document(doc_id)
        content = doc[3]

        processed = text_processor.preprocess(content)
        sentences = processed["sentences"]

        if len(sentences) < 5:
            return jsonify({"error": "Document too short for quiz"}), 400

        data = request.json
        num_mcq = int(data.get("num_mcq", 5))
        num_short = int(data.get("num_short", 3))

        mcq = quiz_generator.generate_mcq(sentences, num_mcq)
        short = quiz_generator.generate_short_answer(sentences, num_short)

        return jsonify({
            "mcq": mcq if mcq else [],
            "short_answer": short if short else []
        })

    except Exception as e:
        print("QUIZ ERROR:", traceback.format_exc())
        return jsonify({"error": "Failed to generate quiz"}), 500

# --------------------------------------------------
# DELETE DOCUMENT
# --------------------------------------------------
@app.route("/api/delete/<int:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    doc = doc_manager.get_document(doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    filepath = doc[2]
    if os.path.exists(filepath):
        os.remove(filepath)

    doc_manager.delete_document(doc_id)

    if session.get("current_doc_id") == doc_id:
        session.pop("current_doc_id", None)

    return jsonify({"success": True})

# --------------------------------------------------
# RUN APP
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
