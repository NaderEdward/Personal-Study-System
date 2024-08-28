from collections import OrderedDict
from datetime import date
from cs50 import SQL
import requests  # type: ignore[no-any-return]
from re import search
import csv
import os

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///school.db")


def get_doc_names():
    doc_names = []
    with open("docs/doc_names.csv", "r") as list_doc_names:
        reader = csv.reader(list_doc_names)
        for row in reader:
            if row:
                doc_names.append(row)
    return doc_names


# Check if doc_name in doc_names if not added then add it
def add_doc_name(doc_name):
    doc_names = get_doc_names()
    # No Previous Documents
    for name in doc_names:
        if doc_name == name[0]:
            return True
    # if not added then add it
    with open("docs/doc_names.csv", "a") as list_doc_names:
        writer = csv.writer(list_doc_names)
        writer.writerow([doc_name])
    return False


# Read func
def doc_read(doc_name):
    with open(f"docs/{doc_name}.txt", "r") as doc_r:
        doc = doc_r.read()
    return doc


# Write func
def doc_write(doc_name, text):
    with open(f"docs/{doc_name}.txt", "w") as doc_w:
        doc_w.write(f"{text}")
    return doc_read(doc_name)


# Get assessments by subject
def get_assessments(subject, info=None, date=None):
    if info:
        quiz_matches = []
        exam_matches = []
        quizes = reversed(db.execute("SELECT * FROM quizes"))
        exams = reversed(db.execute("SELECT * FROM exams"))
        for quiz in quizes:
            item = search(f".*{info}.*", quiz["info"])
            if item:
                quiz_matches.append(quiz)
        ###
        for exam in exams:
            item = search(f".*{info}.*", exam["info"])
            if item:
                exam_matches.append(exam)
        ###
        return quiz_matches, exam_matches
    elif date:
        quizes = reversed(db.execute("SELECT * FROM quizes WHERE date = ?", date))
        exams = reversed(db.execute("SELECT * FROM exams WHERE date = ?", date))
        return quizes, exams
    else:
        quizes = reversed(db.execute("SELECT * FROM quizes WHERE subject = ?", subject))
        exams = reversed(db.execute("SELECT * FROM exams WHERE subject = ?", subject))
        return quizes, exams
        ###


# Add a new assessment
def add_assessment(assessment_type, subject, grade, mistakes, info):
    try:
        num, denom = grade.split("/")
    except (ValueError, AttributeError):
        return 0
    percent = round((float(num) / float(denom)) * 100, 2)
    date_ = date.today()
    if not info or not subject or not mistakes:
        return None
    if assessment_type == "quiz":
        db.execute(
            "INSERT INTO quizes (subject, grade, percent, mistakes, info, date) VALUES (?,?,?,?,?,?)",
            subject,
            grade,
            percent,
            mistakes,
            info,
            date_,
        )
    else:
        db.execute(
            "INSERT INTO exams (subject, grade, percent, mistakes, info, date) VALUES (?,?,?,?,?,?)",
            subject,
            grade,
            percent,
            mistakes,
            info,
            date_,
        )
    return 1
    ###


# get percentage data of exams for a given subject
def get_percentages(subject=None, count=None):
    if not subject and not count:
        past_5_exams = db.execute("SELECT * FROM exams")[:5]
        percentages = []
        subjects = []
        for exam in past_5_exams:
            percentages.append(exam["percent"])
            subjects.append(exam["subject"])
        percentages = get_reverse_list(reversed(percentages))
        subjects = get_reverse_list(reversed(subjects))
        return percentages, subjects
    ###
    elif not subject and count:
        past_n_exams = db.execute("SELECT * FROM exams")[:count]
        percentages = []
        subjects = []
        for exam in past_n_exams:
            percentages.append(exam["percent"])
            subjects.append(exam["subject"])
        percentages = get_reverse_list(reversed(percentages))
        subjects = get_reverse_list(reversed(subjects))
        return percentages, subjects
    ###
    exams = db.execute("SELECT * FROM exams WHERE subject = ?", subject)
    percentages = []
    subjects = []
    for exam in exams:
        percentages.append(exam["percent"])
        subjects.append(exam["subject"])
    percentages = get_reverse_list(reversed(percentages))
    subjects = get_reverse_list(reversed(subjects))
    return percentages, subjects
    ##


# Subjects Page #


# Add new subject
def add_subject(name, subjects_list):
    if name:
        if name in subjects_list:
            return False
        db.execute(
            "INSERT INTO subjects (name, n_topics, topics_file) VALUES (?,?,?)",
            name.title(),
            0,
            f"topics/__{name.upper()}__.csv",
        )
        with open(f"topics/__{name.upper()}__.csv", "w") as topic_file_csv:
            writer = csv.DictWriter(
                topic_file_csv, fieldnames=["topic", "difficulty", "strength"]
            )
            writer.writeheader()
        subjects_list.append(name.title())
        get_subjects_list(subjects_list)
        return name.title()
    else:
        return False
    ###


# Remove subject
def remove_subject(subject, subject_list):
    topics_file = db.execute("SELECT topics_file FROM subjects WHERE name = ?", subject)
    try:
        db.execute("DELETE FROM subjects WHERE name = ?", subject)
        os.remove(topics_file[0]["topics_file"])
    except (FileNotFoundError, IndexError):
        return False
    subject_list.remove(subject)
    get_subjects_list(subject_list)
    return subject.title()
    ###


# Add topic
def add_topic(subject, topic, difficulty, strength):
    try:
        _1, _2 = strength.split("/")
        _3, _4 = difficulty.split("/")
    except (ValueError, AttributeError):
        return None
    if os.path.exists(f"topics/__{subject.upper()}__.csv"):
        with open(f"topics/__{subject.upper()}__.csv", "a") as topic_file_csv:
            appender = csv.DictWriter(
                topic_file_csv, fieldnames=["topic", "difficulty", "strength"]
            )
            appender.writerow(
                {"topic": topic, "difficulty": difficulty, "strength": strength}
            )
    else:
        with open(f"topics/__{subject.upper()}__.csv", "w") as topic_file_csv:
            writer = csv.DictWriter(
                topic_file_csv, fieldnames=["topic", "difficulty", "strength"]
            )
            writer.writeheader()
            writer.writerow(
                {"topic": topic, "difficulty": difficulty, "strength": strength}
            )
        return topic
    ###


# Remove topic
def remove_topic_(topics_file, r_topic):
    if r_topic and topics_file:
        with open(f"topics/__{topics_file}__.csv", "r") as topics_file_csv:
            reader = csv.DictReader(topics_file_csv)
            topics = [topic for topic in reader if topic["topic"] != r_topic]
        with open(f"topics/__{topics_file}__.csv", "w") as topics_file_csv:
            writer = csv.DictWriter(
                topics_file_csv, fieldnames=["topic", "difficulty", "strength"]
            )
            writer.writeheader()
            for topic_ in topics:
                writer.writerow(topic_)
        return True
    else:
        return False
    ###


# Edit topics_file by topic (check)
def edit_topic(topic, topics_file, difficulty, strength):
    if topic and topics_file and difficulty and strength:
        with open(f"topics/__{topics_file}__.csv", "r") as topics_file_csv:
            reader = csv.DictReader(topics_file_csv)
            topics = [topic for topic in reader]
        with open(f"topics/__{topics_file}__.csv", "w") as topics_file_csv:
            writer = csv.DictWriter(
                topics_file_csv, fieldnames=["topic", "difficulty", "strength"]
            )
            writer.writeheader()
            for topic_ in topics:
                if topic_["topic"] == topic:
                    writer.writerow(
                        {"topic": topic, "difficulty": difficulty, "strength": strength}
                    )
                else:
                    writer.writerow(topic_)
        return True
    else:
        return False
    ###


# grade topics based on weakness
def grade_weaknesses(subject):
    gradings = {}
    moderate = []
    weak = []
    topics = get_topics(subject)
    for topic in topics:
        num_strength, denom_strength = topic["strength"].split("/")
        num_difficulty, denom_difficulty = topic["difficulty"].split("/")
        ###
        strength_fraction = float(num_strength) / float(denom_strength)
        difficulty_fraction = float(num_difficulty) / float(denom_difficulty)
        ###
        weakness_formula = difficulty_fraction * strength_fraction
        ###
        if strength_fraction >= 0.9:
            pass
        elif weakness_formula < 0.36:
            weak.append(topic)
        elif weakness_formula < 0.49:
            moderate.append(topic)
    gradings["Weak"] = weak
    gradings["Moderate"] = moderate
    return gradings


# Get topics for a given subject
def get_topics(subject):
    topics_file = db.execute("SELECT topics_file FROM subjects WHERE name =?", subject)
    if topics_file:
        with open(topics_file[0]["topics_file"], "r") as topics_file_csv:
            reader = csv.DictReader(topics_file_csv)
            topics = [topic for topic in reader]
        return topics
    else:
        return []
    ##


# Get quote for home page
def get_fact():
    api_url = "https://api.api-ninjas.com/v1/facts"
    response = requests.get(
        api_url, headers={"X-Api-Key": "pH7JDdWIkIYMMRmDM7r05Q==O0DXEgZuUgQXRe0k"}
    )
    if response.status_code == requests.codes.ok:
        #
        fact = response.text.removeprefix('[{"fact": "').removesuffix('"}]')
        if len(fact) > 174:
            get_fact()
        return fact
    else:
        return ("Error:", response.status_code, response.text)
    ###


# get items todo
def get_todo_items():
    items = []
    with open("docs/todo.csv", "r") as todo_file_csv:
        reader = csv.DictReader(todo_file_csv)
        for row in reader:
            items.append(
                {"item": row["item"].capitalize(), "importance": row["importance"]}
            )
    if items:
        items = sorted(items, key=lambda x: x["importance"], reverse=True)
        return items
    else:
        return []
    ##


# add item to the to do list csv
def add_to_todo(item, importance):
    if item:
        if not importance:
            importance = 0
        with open("docs/todo.csv", "a") as todo_file_csv:
            writer = csv.DictWriter(todo_file_csv, fieldnames=["item", "importance"])
            writer.writerow({"item": item.lower().strip(), "importance": importance})
        return True
    return False
    ###


# Remove from the to do list
def remove_from_todo(item):
    if item:
        item = item.removeprefix("check-").lower().strip()
        with open("docs/todo.csv", "r") as todo_file_csv:
            reader = csv.DictReader(todo_file_csv)
            rows = [row for row in reader if row["item"] != item]
        with open("docs/todo.csv", "w") as todo_file_csv:
            writer = csv.DictWriter(todo_file_csv, fieldnames=["item", "importance"])
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return True
    return False
    ###


# classify percentages
def classify_percentages(percentages):
    classifications = {"Excellent": 0, "Good": 0, "Average": 0, "Below Average": 0}
    for percentage in percentages:
        if percentage >= 90:
            classifications["Excellent"] += 1
        elif percentage >= 80:
            classifications["Good"] += 1
        elif percentage >= 70:
            classifications["Average"] += 1
        else:
            classifications["Below Average"] += 1
    counts = [
        classifications["Excellent"],
        classifications["Good"],
        classifications["Average"],
        classifications["Below Average"],
    ]
    labels = ["Excellent", "Good", "Average", "Below Average"]
    return labels, counts


# Reset docs
def reset_docs():
    for doc_name in get_doc_names():
        os.remove(f"docs/{doc_name[0]}.txt")
    with open("docs/doc_names.csv", "w") as _:
        pass
    ###


# Reset subjects
def reset_subjects():
    subjects_list = get_subjects_list()
    db.execute("DELETE FROM subjects")
    for subject in subjects_list:
        if subject:
            os.remove(f"topics/__{subject.upper()}__.csv")
    ##


# Get reverse list of documents
def get_reverse_list(list):
    r_list = []
    for item in list:
        r_list.append(item)
    return r_list


# get reverse dict
def get_reverse_dict(dict):
    reversed_dict = OrderedDict(reversed(list(dict.items())))
    f_dict = {}
    for key in reversed_dict.keys():
        f_dict[key] = reversed_dict[key]
    return f_dict


# check main subjects list
def check_subjects(subjects_list):
    subjects_ = db.execute("SELECT name FROM subjects")
    subjects = []
    for _ in subjects_:
        subjects.append(_["name"])
    for subject in subjects_list:
        if subject not in subjects:
            with open(f"topics/__{subject.upper()}__.csv", "w") as topic_file_csv:
                writer = csv.DictWriter(
                    topic_file_csv, fieldnames=["topic", "difficulty", "strength"]
                )
                writer.writeheader()
            db.execute(
                "INSERT INTO subjects (name, n_topics, topics_file) VALUES (?,?,?)",
                subject,
                0,
                f"topics/__{subject.upper()}__.csv",
            )


# get subjects from subjects_list.csv
def get_subjects_list(list=None):
    if list:
        with open("subjects_list.csv", "w") as f:
            writer = csv.writer(f)
            for _ in range(len(list)):
                writer.writerow([list[_]])
        return list
    else:
        subjects_list = []
        with open("subjects_list.csv", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                if row:
                    subjects_list.append(row[0])
        return subjects_list
