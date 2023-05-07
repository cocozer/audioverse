from flask import Flask, render_template
import mysql.connector

app = Flask(__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="projet_python"
)

@app.route('/')
def index():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Playlist")
    playlists = cursor.fetchall()
    cursor.execute("SELECT * FROM Chansons")
    chansons = cursor.fetchall()
    cursor.close()
    return render_template('audioverse.html', playlists=playlists, chansons=chansons)

@app.route('/sons')
def sons():
    cursor = db.cursor()
    cursor.execute("SELECT Chansons.*, Genres.titre, Artistes.nom AS nom_artiste, Albums.titre AS titre_album FROM Chansons JOIN Genres ON Chansons.id_genre = Genres.id_genre LEFT JOIN Artistes ON Chansons.id_artiste = Artistes.id_artiste LEFT JOIN Albums ON Chansons.id_album = Albums.id_album ORDER BY Genres.titre")
    chansons = cursor.fetchall()
    cursor.close()

    chansons_par_genre = {}
    for chanson in chansons:
        print(chanson)
        if chanson[11] not in chansons_par_genre:
            chansons_par_genre[chanson[11]] = []
        chansons_par_genre[chanson[11]].append(chanson)

    return render_template('liste_sons.html', chansons_par_genre=chansons_par_genre)

@app.route('/artistes')
def artistes():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Artistes")
    artistes = cursor.fetchall()
    cursor.close()

    return render_template('liste_artistes.html', artistes=artistes)

@app.route('/chanson/<int:id_chanson>')
def chanson(id_chanson):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Chansons WHERE id_chanson=%s", (id_chanson,))
    chanson = cursor.fetchone()

    cursor.execute("SELECT nom FROM Artistes WHERE id_artiste=%s", (chanson[8],))
    artiste = cursor.fetchone()[0]
    print(artiste)

    cursor.execute("SELECT titre FROM Albums WHERE id_album=%s", (chanson[9],))
    album = cursor.fetchone()[0]

    cursor.execute("SELECT titre FROM Genres WHERE id_genre=%s", (chanson[10],))
    genre = cursor.fetchone()[0]

    return render_template('chanson.html', chanson=chanson, artiste=artiste, album=album, genre=genre)


@app.route('/albums')
def albums():
    cursor = db.cursor()
    cursor.execute("SELECT Albums.id_album, Albums.cover, Albums.titre, Artistes.nom AS nom_artiste, Genres.titre, COUNT(chansons.id_chanson) as nombre_de_musiques, Albums.id_artiste FROM Albums JOIN Genres ON Albums.id_genre = Genres.id_genre LEFT JOIN Artistes ON Albums.id_artiste = Artistes.id_artiste LEFT JOIN chansons ON Albums.id_album = chansons.id_album ORDER BY Artistes.id_artiste")
    albums = cursor.fetchall()
    cursor.close()

    albums_par_artiste = {}
    for album in albums:
        print(albums)
        if album[6] not in albums_par_artiste:
            albums_par_artiste[album[6]] = []
        albums_par_artiste[album[6]].append(album)

    return render_template('liste_albums.html', albums_par_artiste=albums_par_artiste)

@app.route('/album/<int:id_album>')
def album(id_album):
    cursor = db.cursor()
    cursor.execute("SELECT Albums.*, Artistes.nom AS nom_artiste, Genres.titre AS nom_genre FROM Albums JOIN Artistes ON Albums.id_artiste = Artistes.id_artiste JOIN Genres ON Albums.id_genre = Genres.id_genre WHERE Albums.id_album = %s", (id_album,))
    album = cursor.fetchone()
    print(album)
    cursor.close()

    cursor = db.cursor()
    cursor.execute("SELECT Chansons.* FROM Chansons WHERE Chansons.id_album = %s", (id_album,))
    chansons = cursor.fetchall()
    cursor.close()

    return render_template('album.html', album=album, chansons=chansons)

@app.route('/artiste/<int:id_artiste>')
def artiste(id_artiste):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Artistes WHERE id_artiste = %s", (id_artiste,))
    artiste = cursor.fetchone()

    cursor.execute("SELECT Albums.*, Genres.titre AS nom_genre FROM Albums JOIN Genres ON Albums.id_genre = Genres.id_genre WHERE Albums.id_artiste = %s", (id_artiste,))
    albums = cursor.fetchall()
    print(albums)

    cursor.execute("SELECT Chansons.*, Albums.titre AS nom_album FROM Chansons JOIN Albums ON Chansons.id_album = Albums.id_album WHERE Chansons.id_artiste = %s", (id_artiste,))
    chansons = cursor.fetchall()

    cursor.close()

    return render_template('artiste.html', artiste=artiste, albums=albums, chansons=chansons)


if __name__ == '__main__':
    app.run(debug=True)


#Exemple d'insert de musique et albums
#INSERT INTO Albums (id_album,titre, cover, annee_sortie, directeur_artistique, producteurs, label, id_artiste, id_genre) VALUES ('2','A Night at the Opera', 'queen_cover.jpg', 1975, 'Roy Thomas Baker', 'Roy Thomas Baker, Queen', 'EMI, Elektra', 1, 1);
#INSERT INTO Chansons (id_chanson,titre, description, cover, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre) VALUES ('2','Bohemian Rhapsody', 'Single de l\'album "A Night at the Opera" sorti en 1975', 'https://example.com/bohemian_rhapsody_cover.jpg', '00:05:54', 'Roy Thomas Baker', 'Queen', 'EMI Records', 2, 2, 2);
# INSERT INTO Chansons (id_chanson, titre, description, cover, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre)
# VALUES ('6', 'Somebody to Love', 'Premier single de lalbum A Night at the Opera sorti en 1976', 'https://example.com/somebody_to_love_cover.jpg', '00:04:58', 'Roy Thomas Baker', 'Queen', 'EMI Records', 2, 2, 2);

# INSERT INTO Chansons (id_chanson, titre, description, cover, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre)
# VALUES ('7', 'Good Old-Fashioned Lover Boy', 'Single de lalbum A Day at the Races sorti en 1977', 'https://example.com/good_old_fashioned_lover_boy_cover.jpg', '00:02:54', 'Roy Thomas Baker', 'Queen', 'EMI Records', 2, 2, 2);

# INSERT INTO Chansons (id_chanson, titre, description, cover, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre)
# VALUES ('8', 'Im in Love with My Car', 'Face B du single Bohemian Rhapsody sorti en 1975', 'https://example.com/im_in_love_with_my_car_cover.jpg', '00:03:05', 'Roy Thomas Baker', 'Queen', 'EMI Records', 2, 2, 2);

