# grading-framework-exams

1. Export data from Moodle: 
   - store the exam dates in `data/termine_YYYY-MM-DD.csv`. ("Leere Zeitfenster einbeziehen: Nein". → "Einzufügende Daten": Datum, Startzeit, Endzeit, Vorname, Nachname, E-Mail-Adresse, Nutzername, Teilnehmer-ID.)
   - store the topics and study profiles in `data/themen_YYYY-MM-DD.csv`. ("Alle Antworten anzeigen" → "Herunterladen" → as ~.csv~.)
2. Modify the `dates` and `topics` variables in the `main` function of `make_list.py` according to the filenames in step 1.
3. Run `make_list.py`. The script creates `data/list.csv` and `data/list_students_without_topic.csv`.
4. Run `make_reports.py`. The script reads `list.csv` and creates a report for each student (using `data/template.docx`) and a list of the exams ordered by date and time in `/reports`.
