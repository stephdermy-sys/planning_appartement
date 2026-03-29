from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


# Création base

def init_db():

    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prenom TEXT,
        date_debut TEXT,
        date_fin TEXT,
        commentaire TEXT,
        statut TEXT DEFAULT ''
    )
    """)

    conn.commit()
    conn.close()


init_db()


# Calcul statut automatique

def calcul_statut(date_debut, date_fin, statut):

    if statut == "Annulé":
        return "Annulé"

    aujourd_hui = datetime.today().date()

    debut = datetime.strptime(
        date_debut,
        "%Y-%m-%d"
    ).date()

    fin = datetime.strptime(
        date_fin,
        "%Y-%m-%d"
    ).date()

    if aujourd_hui < debut:
        return "À venir"

    if debut <= aujourd_hui <= fin:
        return "En cours"

    return "Passé"


# PAGE PRINCIPALE

@app.route("/")
def index():

    tri = request.args.get("tri", "date")
    ordre = request.args.get("ordre", "asc")

    if ordre == "asc":
        direction = "ASC"
        prochain_ordre = "desc"
    else:
        direction = "DESC"
        prochain_ordre = "asc"

    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()

    # TRI

    if tri in ["prenom", "prénom"]:

        query = f"""
        SELECT * FROM reservations
        ORDER BY prenom {direction}
        """

    elif tri == "statut":

        query = f"""
        SELECT * FROM reservations
        ORDER BY statut {direction}
        """

    else:

        query = f"""
        SELECT * FROM reservations
        ORDER BY date_debut {direction}
        """

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    reservations = []

    for r in rows:

        statut = calcul_statut(
            r[2],
            r[3],
            r[5]
        )

        reservations.append({
            "id": r[0],
            "prenom": r[1],
            "date_debut": r[2],
            "date_fin": r[3],
            "commentaire": r[4],
            "statut": statut
        })

    return render_template(
        "index.html",
        reservations=reservations,
        ordre=prochain_ordre
    )


# AJOUTER

@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():

    if request.method == "POST":

        prenom = request.form["prenom"]
        date_debut = request.form["date_debut"]
        date_fin = request.form["date_fin"]
        commentaire = request.form["commentaire"]

        conn = sqlite3.connect("reservations.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO reservations
            (prenom, date_debut, date_fin, commentaire, statut)
            VALUES (?, ?, ?, ?, '')
            """,
            (
                prenom,
                date_debut,
                date_fin,
                commentaire
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("ajouter.html")


# ANNULER

@app.route("/annuler/<int:id>")
def annuler(id):

    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE reservations
        SET statut='Annulé'
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


# SUPPRIMER

@app.route("/supprimer/<int:id>")
def supprimer(id):

    conn = sqlite3.connect("reservations.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM reservations
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":

    app.run(debug=True)