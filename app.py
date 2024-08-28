from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from datetime import date
from functions import *
from AI import *  # make it more direct
import json
import csv

# Configure application
app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Global vars
subjects_list = get_subjects_list(
    ["English", "Math", "Biology", "Chemistry", "Physics"]
)
check_subjects(subjects_list)


###
# General functions
@app.route("/remove_assessment", methods=["POST"])
def remove_assessment():
    assessment = json.loads(request.data.decode())["input"]
    subject, date, info, assessment_type = assessment.split(",")
    if assessment_type == "Exam":
        db.execute(
            "DELETE FROM exams WHERE (subject, date, info) = (?,?,?)",
            subject,
            date,
            info,
        )
    else:
        db.execute(
            "DELETE FROM quizes WHERE (subject, date, info) = (?,?,?)",
            subject,
            date,
            info,
        )
    return "success"


###
@app.route("/remove_topic", methods=["POST"])
def remove_topic():
    topic_details = json.loads(request.data.decode())["input"]
    subject, topic = topic_details.split(",")
    remove_topic_(subject.upper(), topic)
    return "success"


###
@app.route("/remove_doc", methods=["POST"])
def remove_doc():
    doc_name = json.loads(request.data.decode())["input"]
    # Remove the doc from the docs directory
    os.remove(f"docs/{doc_name}.txt")
    # Remove the doc from the doc_names.csv file
    try:
        with open("docs/doc_names.csv", "r") as file:
            reader = csv.reader(file)
            rows = list(reader)
        with open("docs/doc_names.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows([row for row in rows if row[0] != doc_name])
    except IndexError:
        return "error"
    return "success"


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        # Get today's date
        today = date.today()
        day_of_week = today.weekday()
        weekdays = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        # Get education quote
        fact = get_fact()
        # get todos list
        todos = get_todo_items()
        # get classifications of percentages for last 20 exams
        percentages, _ = get_percentages(count=20)
        classifications, counts = classify_percentages(percentages)
        ###
        return render_template(
            "home.html",
            date=today,
            weekday=weekdays[day_of_week],
            fact=fact,
            items=todos,
            classifications=classifications,
            counts=counts,
        )
    else:
        item = request.form.get("item")
        importance = request.form.get("importance")
        ###
        if item:
            result = add_to_todo(item, importance)
            if not result:
                return render_template(
                    "apology.html", msg="Please enter all the fields"
                )
            return redirect("/")
        ###
        for item in get_todo_items():
            item = "check-{}".format(item["item"])
            if request.form.get(item) == "on":
                result = remove_from_todo(item)
                if not result:
                    return render_template(
                        "apology.html", msg="Please enter all the fields"
                    )
        return redirect("/")
        ###


@app.route("/assessments", methods=["GET", "POST"])
def assessments():
    subjects_list = get_subjects_list()
    # Get list of assessments
    if request.method == "GET":
        quizes_5 = get_reverse_list(reversed(db.execute("SELECT * FROM quizes")))[:5]
        exams_5 = get_reverse_list(reversed(db.execute("SELECT * FROM exams")))[:5]
        percentages, subjects_percent = get_percentages()
        return render_template(
            "assessments.html",
            subjects=subjects_list,
            quizes=quizes_5,
            exams=exams_5,
            values=percentages,
            subjects_percent=subjects_percent,
        )
    else:
        try:
            selected_subject = request.form.get("subject")
            ###
            assessment_type = request.form.get("assessment_type")
            new_subject = request.form.get("new_subject")
            new_grade = request.form.get("new_grade")
            new_mistakes = request.form.get("new_mistakes")
            new_info = request.form.get("new_info")
            ###
            remove_assessment = request.form.get("remove_assessment")
            ###
            find_assessment_info = request.form.get("find_assessment_info")
            find_assessment_date = request.form.get("find_assessment_date")
        except AttributeError:
            return render_template("apology.html", msg="Please fill in all the fields")
        ###
        if (
            not selected_subject
            and not assessment_type
            and not new_subject
            and not new_grade
            and not new_mistakes
            and not new_info
            and not remove_assessment
            and not find_assessment_info
            and not find_assessment_date
        ):
            return render_template(
                "apology.html", msg="Please fill in/select all the fields"
            )
        ###
        if selected_subject:
            percentages, subjects_percent = get_percentages(selected_subject)
            quizes, exams = get_assessments(selected_subject)
            return render_template(
                "assessments.html",
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                values=percentages,
                subjects_percent=subjects_percent,
                subject_title=selected_subject,
            )
        elif remove_assessment:
            db.execute("DELETE FROM exams WHERE info = ?", remove_assessment)
            db.execute("DELETE FROM quizes WHERE info = ?", remove_assessment)
            ###
            return redirect("/assessments")
        elif find_assessment_info:
            quizes, exams = get_assessments(subject=None, info=find_assessment_info)
            return render_template(
                "assessments.html",
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                values=[],
                subjects_percent=[],
            )
        elif find_assessment_date:
            quizes, exams = get_assessments(subject=None, date=find_assessment_date)
            return render_template(
                "assessments.html",
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                values=[],
                subjects_percent=[],
            )
        else:
            result = add_assessment(
                assessment_type, new_subject, new_grade, new_mistakes, new_info
            )
            if result == 0:
                return render_template(
                    "apology.html", msg="The grade should be in the format of X/Y"
                )
            elif not result:
                return render_template(
                    "apology.html", msg="Please fill in/select all the fields"
                )
            quizes, exams = get_assessments(new_subject)
            percentages, subjects_percent = get_percentages(new_subject)
            return render_template(
                "assessments.html",
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                values=percentages,
                subjects_percent=subjects_percent,
                subject_title=new_subject,
            )


@app.route("/subjects", methods=["GET", "POST"])
def subjects():
    # Get list of subjects
    if request.method == "GET":
        subjects_list = get_subjects_list()
        return render_template(
            "subjects.html",
            subjects=subjects_list,
            values=[],
            gradings={"Moderate": [], "Weak": []},
        )
    else:
        subjects_list = get_subjects_list()
        try:
            selected_subject = request.form.get("selected_subject")
            ###
            new_name = request.form.get("new_name")
            ###
            topic = request.form.get("new_topic")
            topics_subject = request.form.get("new_topic_subject")
            strength = request.form.get("new_strength")
            difficulty = request.form.get("new_difficulty")
            ###
            remove_subject_ = request.form.get("remove_subject")
            ###
            edit_topic_subject = request.form.get("edit_topic_subject")
            edit_topic_ = request.form.get("edit_topic")
            edit_strength = request.form.get("edit_strength")
            edit_difficulty = request.form.get("edit_difficulty")
        except AttributeError:
            return render_template("apology.html", msg="Please fill in all the fields")
        ###
        if (
            not selected_subject
            and not new_name
            and not topic
            and not topics_subject
            and not strength
            and not difficulty
            and not remove_subject_
            and not edit_topic_subject
            and not edit_topic_
            and not edit_strength
            and not edit_difficulty
        ):
            return render_template(
                "apology.html", msg="Please fill in/select all the fields"
            )
        if selected_subject:
            quizes, exams = get_assessments(selected_subject)
            topics = get_topics(selected_subject)
            gradings = grade_weaknesses(selected_subject)
            return render_template(
                "subjects.html",
                subject=selected_subject,
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                topics=topics,
                gradings=gradings,
            )
        elif new_name:
            new_subject = add_subject(new_name, get_subjects_list())
            if new_subject:
                quizes, exams = get_assessments(new_subject)
                gradings = grade_weaknesses(selected_subject)
                return render_template(
                    "subjects.html",
                    subject=new_subject,
                    subjects=get_subjects_list(),
                    quizes=quizes,
                    exams=exams,
                    gradings=gradings,
                )
            return render_template(
                "apology.html",
                msg="Please fill in/select all the fields or the subject name is already used",
            )
        elif topic:
            result = add_topic(topics_subject, topic, difficulty, strength)
            if not result:
                return render_template(
                    "apology.html",
                    msg="Difficulty and strength should be in the format of X/Y",
                )
            quizes, exams = get_assessments(selected_subject)
            topics = get_topics(topics_subject)
            gradings = grade_weaknesses(selected_subject)
            if not topics:
                return render_template(
                    "apology.html", msg="Please fill in/select all the fields"
                )
            return render_template(
                "subjects.html",
                subject=topics_subject,
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                topics=topics,
                gradings=gradings,
            )
        elif remove_subject_:
            subjects_list = get_subjects_list()
            result = remove_subject(remove_subject_, subjects_list)
            if not result:
                return render_template("apology.html", msg="Subject does not exist")
            return render_template(
                "subjects.html",
                subjects=subjects_list,
                values=[],
                gradings={"Moderate": [], "Weak": []},
            )
        elif edit_topic_:
            topics_ = []
            for topic in get_topics(edit_topic_subject):
                topics_.append(topic["topic"])
            if edit_topic_ not in topics_:
                return render_template("apology.html", msg="Topic does not exist")
            edit_topic(edit_topic_, edit_topic_subject, edit_difficulty, edit_strength)
            quizes, exams = get_assessments(edit_topic_subject)
            topics = get_topics(edit_topic_subject)
            gradings = grade_weaknesses(selected_subject)
            if not topics:
                return render_template(
                    "apology.html", msg="Please fill in/select all the fields"
                )
            return render_template(
                "subjects.html",
                subject=edit_topic_subject,
                subjects=subjects_list,
                quizes=quizes,
                exams=exams,
                topics=topics,
                gradings=gradings,
            )


@app.route("/docs", methods=["GET", "POST"])
def docs():
    # Select or make new docs
    if request.method == "GET":
        session["cur_doc"] = None
        doc_names = get_doc_names()
        return render_template("docs.html", doc_names=doc_names, doc=None)
        ###
    else:
        selected_doc = request.form.get("selected_doc_name")
        new_doc_name = request.form.get("doc_name")
        edited_txt = request.form.get("edited_txt")
        remove = request.form.get("remove")
        ###
        if new_doc_name:
            if add_doc_name(new_doc_name):
                return render_template(
                    "apology.html", msg="Name of document already exists"
                )
            session["cur_doc"] = new_doc_name
            return render_template(
                "docs.html",
                doc=doc_write(new_doc_name, ""),
                new_document=True,
                doc_name=new_doc_name,
            )
        elif edited_txt:
            selected_doc = session["cur_doc"]
            doc_write(selected_doc, edited_txt)
            return redirect("/docs")
        elif remove:
            return redirect("/docs")
        else:
            try:
                session["cur_doc"] = selected_doc.strip()
            except AttributeError:
                return render_template(
                    "apology.html", msg="Please select/state a valid document"
                )
            return render_template(
                "docs.html",
                doc=doc_read(selected_doc),
                new_document=False,
                doc_name=selected_doc,
            )


@app.route("/AI", methods=["GET", "POST"])
def AI():
    if request.method == "GET":
        # reset the context
        reset_context()
        session["AI_character"] = None
        return render_template("AI.html", chat_logs=[])
    else:
        # Send context to the AI along with the query
        count = 1
        query = request.form.get("query")
        ###
        if not query:
            return render_template("apology.html", msg="Please enter a query")
        if query == "RESET":
            reset_context()
        elif query == "EXIT":
            reset_context()
            return redirect("/")
        elif "RECORD" in query:
            if len(query) >= 8:
                try:
                    time = int(query.replace("RECORD", "").strip())
                except:
                    return render_template("apology.html", msg="Invalid recording time")
                
                response = live_chat(query, record=time)
                if not response:
                    return render_template(
                        "apology.html",
                        msg="Failed to record audio, please try again later",
                    )
            else:
                live_chat(query)
        # Send the query to the AI and the persona selected
        else:
            live_chat(query)
        # Get the chat log
        chat_log = get_chat_log(count)
        styles = [None]
        messages = []
        for dict in chat_log:
            styles.append(read_dict(dict.keys())[0])
            messages.append(read_dict(dict.values())[0])
        # Display the chat log
        return render_template("AI.html", chat_logs=messages, styles=styles)


# Functions
@app.route("/reset")
def reset():
    db.execute("DELETE FROM quizes;")
    db.execute("DELETE FROM exams;")
    db.execute("DELETE FROM subjects;")
    reset_subjects()
    check_subjects(subjects_list)
    get_subjects_list(["English", "Math", "Biology", "Chemistry", "Physics"])
    reset_docs()
    reset_context()
    with open("docs/todo.csv", "w") as reset_todo:
        writer = csv.DictWriter(reset_todo, fieldnames=["item", "importance"])
        writer.writeheader()
    return redirect("/")
