from flask import Flask,request, render_template, redirect, jsonify
import mysql.connector
import datetime
from flask_uploads import UploadSet, UploadNotAllowed, configure_uploads, IMAGES #Il faut installer flask-uploads avec pip (pip install flask-uploads)

#S'il y a des problèmes au lancé du site, installer une version antérieure de markupsafe (pip uninstall markupsafe) puis (pip install markupsafe==1.1.1)
app = Flask(__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="projet_python"
)

app.config['UPLOADED_PHOTOS_DEST'] = 'static'
app.config['UPLOADED_PHOTOS_ALLOW'] = IMAGES
app.config['UPLOADED_PHOTOS_MAX_SIZE'] = 16 * 1024 * 1024  # 16MB max size
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

# Route pour la page d'accueil
@app.route('/')
def index():
    return render_template('audioverse.html')

# Endpoint pour récupérer les playlists en tant que JSON
@app.route('/api/playlists')
def get_playlists():
    try:
        cursor = db.cursor()
        cursor.execute("SELECT Playlist.* FROM Playlist")
        playlists = cursor.fetchall()
        cursor.close()


        # Conversion des résultats en une liste de dictionnaires
        playlist_data = []
        for playlist in playlists:
            playlist_dict = {
                'id': playlist[0],
                'name': playlist[1],
                'description': playlist[2],
                'date_creation': playlist[3].strftime('%Y-%m-%d'),  # Conversion de la date en format string
                'image': playlist[4]
            }
            playlist_data.append(playlist_dict)

        return jsonify(playlist_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/erreur-upload')
def error():
    return render_template('erreur-format-de-fichier.html')

@app.route('/playlist/<int:id_playlist>')
def playlist(id_playlist):
    return render_template('playlist.html', id_playlist=id_playlist)

@app.route('/api/playlist/<int:id_playlist>')
def get_playlist(id_playlist):
    try:
        # Récupération de la playlist
        cursor = db.cursor()
        cursor.execute("SELECT id_playlist, nom, description, date_creation, image_upload FROM Playlist WHERE id_playlist=%s", (id_playlist,))
        playlist = cursor.fetchone()
        cursor.close()

        if not playlist:
            return jsonify({'error': 'Playlist not found'}), 404

        playlist_dict = {
            'id': playlist[0],
            'name': playlist[1],
            'description': playlist[2],
            'date_creation': playlist[3].strftime('%Y-%m-%d'),  # Conversion de la date en format string
            'image': playlist[4],
            'songsinplaylist': [],
            'songsnotinplaylist': []
        }

        # Récupération des chansons dans la playlist
        cursor = db.cursor()
        cursor.execute("SELECT chansons.*, playlist_chansons.id_chanson, playlist_chansons.id_playlist FROM Playlist INNER JOIN playlist_chansons ON playlist_chansons.id_playlist = playlist.id_playlist INNER JOIN chansons ON playlist_chansons.id_chanson = chansons.id_chanson WHERE playlist.id_playlist=%s", (id_playlist,))
        chansons = cursor.fetchall()
        cursor.close()

        # Récupération des chansons non présentes dans la playlist
        cursor = db.cursor()
        cursor.execute("SELECT chansons.*, playlist_chansons.id_chanson, playlist_chansons.id_playlist FROM Playlist INNER JOIN playlist_chansons ON playlist_chansons.id_playlist = playlist.id_playlist RIGHT JOIN chansons ON playlist_chansons.id_chanson = chansons.id_chanson WHERE playlist.id_playlist=%s IS NULL", (id_playlist,))
        chansonspasdansplaylist = cursor.fetchall()
        cursor.close()

        for chanson in chansons:
            chanson_dict = {
                'id': chanson[11],
                'name': chanson[2],
                'id_playlist': chanson[12],
            }
            playlist_dict['songsinplaylist'].append(chanson_dict)

        for chanson in chansonspasdansplaylist:
            chanson_dict = {
                'id': chanson[0],
                'name': chanson[2]
            }
            playlist_dict['songsnotinplaylist'].append(chanson_dict)

        return jsonify(playlist_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/playlist/new')
def playlistcreate():
    cursor = db.cursor()
    cursor.execute("SELECT MAX(id_playlist) FROM playlist")
    lastplaylist = cursor.fetchone()
    
    cursor.close()

    return render_template('new-playlist-form.html', newid=lastplaylist[0]+1)
    
@app.route('/playlist/new/post', methods=['POST'])
def playlistnewpost():
    id_playlist = int(request.form['id_playlist'])
    nom = request.form['nom']
    description = request.form['description']

    app.config['UPLOADED_PHOTOS_DEST'] = 'static/playlists_img' # Modification de la destination
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)
    image = request.files.get('image')
    if image:
        try:
            filename = photos.save(image)
            image = filename
        except UploadNotAllowed:
            return redirect('/erreur-upload')
    
    date = datetime.date.today()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Playlist VALUES(%s, %s, %s, %s, %s)", (id_playlist, nom, description, date, image, ))
    db.commit()
    cursor.close()
    id_playlist = str(id_playlist)
    return redirect('/playlist/'+id_playlist)
    
@app.route('/playlist/edit/<int:id_playlist>')
def playlistedit(id_playlist):
    cursor = db.cursor()
    cursor.execute("SELECT playlist.* FROM Playlist WHERE playlist.id_playlist=%s", (id_playlist,))
    playlist = cursor.fetchone()
    cursor.close()

    return render_template('playlist-edit-form.html', playlist=playlist)
    
@app.route('/playlist/edit/post', methods=['POST'])
def playlisteditpost():
    id_playlist = int(request.form['id_playlist'])
    nom = request.form['nom']
    description = request.form['description']

    app.config['UPLOADED_PHOTOS_DEST'] = 'static/playlists_img' # Modification de la destination
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)
    image = request.files.get('image')
    if image:
        try:
            filename = photos.save(image)
            image = filename
        except UploadNotAllowed:
            return redirect('/erreur-upload')
    if not image:
        cursor = db.cursor()
        cursor.execute("UPDATE Playlist SET nom=%s, description=%s WHERE id_playlist=%s", (nom, description, id_playlist))
        db.commit()
        cursor.close()
        id_playlist = str(id_playlist)
        return redirect('/playlist/'+id_playlist)
    if image:
        cursor = db.cursor()
        cursor.execute("UPDATE Playlist SET nom=%s, description=%s, image_upload=%s WHERE id_playlist=%s", (nom, description, image, id_playlist))
        db.commit()
        cursor.close()
        id_playlist = str(id_playlist)
        return redirect('/playlist/'+id_playlist)

@app.route('/playlist/delete/<int:id_playlist>')
def playlistdelete(id_playlist):
    cursor = db.cursor()

    cursor.execute("DELETE FROM Playlist_chansons WHERE id_playlist=%s", (id_playlist,))
    db.commit()

    cursor.execute("DELETE FROM Playlist WHERE playlist.id_playlist=%s", (id_playlist,))
    db.commit()
    cursor.close()

    return redirect('/')


@app.route('/add/<int:id_playlist>/<int:id_chanson>')
def add(id_chanson, id_playlist):
    cursor = db.cursor()
    cursor.execute("INSERT INTO playlist_chansons VALUES(%s,%s)", (id_playlist,id_chanson))
    db.commit()
    cursor.close()
    return redirect('/playlist/'+str(id_playlist))

@app.route('/remove/<int:id_playlist>/<int:id_chanson>')
def remove(id_chanson, id_playlist):
    cursor = db.cursor()
    cursor.execute("DELETE FROM playlist_chansons WHERE id_playlist=%s AND id_chanson=%s", (id_playlist,id_chanson))
    db.commit()
    cursor.close()
    return redirect('/playlist/'+str(id_playlist))

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

@app.route('/sons/new')
def newsons():
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Albums INNER JOIN Artistes ON Artistes.id_artiste=Albums.id_artiste GROUP BY Albums.id_album")
    albums = cursor.fetchall()

    cursor.execute("SELECT * FROM Genres")
    genres = cursor.fetchall()

    cursor.execute("SELECT MAX(id_chanson) FROM chansons")
    lastchanson = cursor.fetchone()
    
    cursor.close()

    return render_template('new-son-form.html', albums=albums, newid=lastchanson[0]+1, genres=genres)

@app.route('/sons/new/post', methods=['POST'])
def newsonspost():
    id_chanson = int(request.form['id_chanson'])
    titre = request.form['titre']
    description = request.form['description']
    duree = request.form['duree']
    directeur_artistique = request.form['directeur_artistique']
    producteur = request.form['producteur']
    label = request.form['label']
    id_album = int(request.form['id_album'])
    id_genre = int(request.form['id_genre'])

    app.config['UPLOADED_PHOTOS_DEST'] = 'static/chansons_img' # Modification de la destination
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    cover = request.files.get('cover')
    if cover:
        try:
            filename = photos.save(cover)
            cover = filename
        except UploadNotAllowed:
            return redirect('/erreur-upload')
    

    cursor = db.cursor()

    cursor.execute("SELECT id_artiste FROM Albums WHERE id_album=%s", (id_album, ))
    artiste = cursor.fetchone()
    id_artiste = artiste[0]

    cursor.execute("INSERT INTO Chansons VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (id_chanson, description, titre, cover, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre))
    db.commit()
    cursor.close()
    return redirect('/sons')

   

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

    cursor.execute("SELECT titre FROM Albums WHERE id_album=%s", (chanson[9],))
    album = cursor.fetchone()[0]

    cursor.execute("SELECT titre FROM Genres WHERE id_genre=%s", (chanson[10],))
    genre = cursor.fetchone()[0]

    return render_template('chanson.html', chanson=chanson, artiste=artiste, album=album, genre=genre)

@app.route('/chanson/edit/<int:id_chanson>')
def chansonedit(id_chanson):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM Chansons WHERE chansons.id_chanson=%s", (id_chanson,))
    chanson = cursor.fetchone()

    cursor.execute("SELECT * FROM Artistes")
    artistes = cursor.fetchall()

    cursor.execute("SELECT * FROM Albums")
    albums = cursor.fetchall()

    cursor.execute("SELECT * FROM Genres")
    genres = cursor.fetchall()

    cursor.close()

    return render_template('chanson-edit-form.html', chanson=chanson, artistes=artistes, albums=albums, genres=genres)

@app.route('/chanson/edit/post', methods=['POST'])
def chansoneditpost():
    id_chanson = int(request.form['id_chanson'])
    titre = request.form['titre']
    description = request.form['description']
    duree = request.form['duree']
    directeur_artistique = request.form['directeur_artistique']
    producteur = request.form['producteur']
    label = request.form['label']
    id_artiste = int(request.form['id_artiste'])
    id_album = int(request.form['id_album'])
    id_genre = int(request.form['id_genre'])

    app.config['UPLOADED_PHOTOS_DEST'] = 'static/chansons_img' # Modification de la destination
    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

    cover = request.files.get('cover')
    if cover:
        try:
            filename = photos.save(cover)
            cover = filename
        except UploadNotAllowed:
            return redirect('/erreur-upload')
    if not cover:
        cursor = db.cursor()
        cursor.execute("UPDATE Chansons SET description=%s, titre=%s, duree=%s, directeur_artistique=%s, producteur=%s, label=%s, id_artiste=%s, id_album=%s, id_genre=%s WHERE id_chanson=%s", (description, titre, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre, id_chanson))
        db.commit()
        cursor.close()
        id_chanson = str(id_chanson)
        return redirect('/chanson/'+id_chanson)

    if cover:
        cursor = db.cursor()
        cursor.execute("UPDATE Chansons SET description=%s, titre=%s, cover=%s, duree=%s, directeur_artistique=%s, producteur=%s, label=%s, id_artiste=%s, id_album=%s, id_genre=%s WHERE id_chanson=%s", (description, titre, cover, duree, directeur_artistique, producteur, label, id_artiste, id_album, id_genre, id_chanson))
        db.commit()
        cursor.close()
        id_chanson = str(id_chanson)
        return redirect('/chanson/'+id_chanson)
    
@app.route('/chanson/delete/<int:id_chanson>')
def chansondelete(id_chanson):
    cursor = db.cursor()

    cursor.execute("DELETE FROM Playlist_chansons WHERE id_chanson=%s", (id_chanson,))
    db.commit()

    cursor.execute("DELETE FROM chansons WHERE chansons.id_chanson=%s", (id_chanson,))
    db.commit()
    cursor.close()

    return redirect('/sons')

@app.route('/albums')
def albums():
    cursor = db.cursor()
    cursor.execute("SELECT albums.id_album, albums.cover, albums.titre, artistes.nom AS nom_artiste, genres.titre, COUNT(chansons.id_chanson) AS nombre_de_musique, albums.id_artiste FROM chansons INNER JOIN artistes ON chansons.id_artiste = artistes.id_artiste INNER JOIN genres ON chansons.id_genre = genres.id_genre INNER JOIN albums ON chansons.id_album = albums.id_album GROUP BY albums.id_album ORDER BY artistes.id_artiste")
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
    return render_template('album.html', id_album=id_album)

# Endpoint pour afficher les détails d'un album
@app.route('/api/album/<int:id_album>')
def get_album(id_album):
    try:
        # Récupérer les informations de l'album
        cursor = db.cursor()
        cursor.execute("SELECT Albums.*, Artistes.nom AS nom_artiste, Genres.titre AS nom_genre FROM Albums JOIN Artistes ON Albums.id_artiste = Artistes.id_artiste JOIN Genres ON Albums.id_genre = Genres.id_genre WHERE Albums.id_album = %s", (id_album,))
        album = cursor.fetchone()

        if not album:
            return jsonify({'error': 'Album not found'}), 404

        # Récupérer les chansons de l'album
        cursor.execute("SELECT Chansons.* FROM Chansons WHERE Chansons.id_album = %s", (id_album,))
        chansons = cursor.fetchall()
        cursor.close()

        album_data = {
            'id': album[0],
            'title': album[1],
            'image': album[2],
            'artist': album[9],
            'genre': album[10],
            'release_year': album[3],
            'artistic_director': album[4],
            'producers': album[5],
            'label': album[6],
            'songs': []
        }

        for chanson in chansons:
            chanson_data = {
                'id': chanson[0],
                'title': chanson[2]
            }
            album_data['songs'].append(chanson_data)

        return jsonify(album_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
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

