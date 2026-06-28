"""Seed default users and demo data."""
from werkzeug.security import generate_password_hash
from models import db, User, Student, Teacher, Course, Attendance, Fee, Result


def seed_database():
    if User.query.count() == 0:
        defaults = [
            ("admin", "admin123", "admin"),
            ("teacher", "teacher123", "teacher"),
            ("student", "student123", "student"),
        ]
        for u, p, r in defaults:
            db.session.add(User(username=u, password=generate_password_hash(p), role=r))

    if Course.query.count() == 0:
        for name, code, dur, dept in [
            ("Computer Science", "CS", "4 Years", "Engineering"),
            ("Business Administration", "BBA", "3 Years", "Management"),
            ("Mechanical Engineering", "ME", "4 Years", "Engineering"),
            ("Data Science", "DS", "2 Years", "Science"),
        ]:
            db.session.add(Course(name=name, code=code, duration=dur, department=dept))

    if Teacher.query.count() == 0:
        for n, e, p, s, d in [
            ("Dr. Sarah Johnson", "sarah@edu.com", "9876543210", "Algorithms", "Engineering"),
            ("Prof. Michael Chen", "michael@edu.com", "9876543211", "Database Systems", "Engineering"),
            ("Dr. Priya Sharma", "priya@edu.com", "9876543212", "Marketing", "Management"),
        ]:
            db.session.add(Teacher(name=n, email=e, phone=p, subject=s, department=d))

    if Student.query.count() == 0:
        demo = [
            ("CS2024001", "Aarav Patel", "aarav@edu.com", "9991110001", "Male", "2003-05-12",
             "Computer Science", "4", "Engineering", "Mumbai, India", "Rajesh Patel", "9991112221", "O+", "2024-08-01", "Paid", 8.7),
            ("CS2024002", "Sophia Williams", "sophia@edu.com", "9991110002", "Female", "2004-02-18",
             "Computer Science", "2", "Engineering", "London, UK", "James Williams", "9991112222", "A+", "2024-08-01", "Pending", 9.1),
            ("BBA2024010", "Liam Garcia", "liam@edu.com", "9991110003", "Male", "2003-11-09",
             "Business Administration", "3", "Management", "Madrid, Spain", "Carlos Garcia", "9991112223", "B+", "2024-07-15", "Partial", 7.8),
            ("DS2024021", "Ananya Singh", "ananya@edu.com", "9991110004", "Female", "2002-09-22",
             "Data Science", "1", "Science", "Delhi, India", "Vikram Singh", "9991112224", "AB+", "2024-09-10", "Paid", 9.4),
            ("ME2024033", "Noah Brown", "noah@edu.com", "9991110005", "Male", "2003-03-15",
             "Mechanical Engineering", "2", "Engineering", "Toronto, Canada", "Daniel Brown", "9991112225", "O-", "2024-08-20", "Pending", 6.9),
            ("CS2024003", "Mia Rossi", "mia@edu.com", "9991110006", "Female", "2004-06-30",
             "Computer Science", "1", "Engineering", "Rome, Italy", "Marco Rossi", "9991112226", "A-", "2024-09-01", "Paid", 8.2),
        ]
        for d in demo:
            db.session.add(Student(
                roll_no=d[0], name=d[1], email=d[2], phone=d[3], gender=d[4], dob=d[5],
                course=d[6], semester=d[7], department=d[8], address=d[9],
                guardian_name=d[10], guardian_contact=d[11], blood_group=d[12],
                admission_date=d[13], fee_status=d[14], cgpa=d[15]
            ))
        db.session.commit()

        # demo attendance + fees + results for first student
        for s in Student.query.all():
            db.session.add(Fee(student_id=s.id, amount=50000,
                               paid=50000 if s.fee_status == "Paid" else (25000 if s.fee_status == "Partial" else 0),
                               status=s.fee_status, date="2024-09-01"))
            for i, st in enumerate(["Present", "Present", "Absent", "Late", "Present"]):
                db.session.add(Attendance(student_id=s.id, date=f"2024-09-0{i+1}", status=st))
            for subj, inn, ex in [("Mathematics", 38, 72), ("Physics", 35, 68), ("Programming", 42, 80)]:
                total = inn + ex
                pct = round(total / 1.5, 2)
                grade = "A+" if pct >= 90 else "A" if pct >= 80 else "B" if pct >= 70 else "C"
                db.session.add(Result(student_id=s.id, subject=subj, internal=inn,
                                      external=ex, total=total, percentage=pct, grade=grade))

    db.session.commit()
