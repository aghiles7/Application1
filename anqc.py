import pandas as pd
import matplotlib.pyplot as plt
import io

def create_cgqc_plots(df):
    # Filtrer les données pour ne garder que les incidents de type "Véhicule arrêté"
    df_animal = df[df['Détection modèle'] == 'Animal']

    # Compter le nombre d'incidents par caméra et par type de qualification
    incident_counts = df_animal.groupby(['Caméra', 'Type de qualification']).size().unstack(fill_value=0)

    # Liste complète des caméras
    all_cameras = df['Caméra'].unique()

    # Définir l'ordre des types de qualification
    qualification_order = ['Avéré', 'Catégorie erronée', 'Fausse alarme', 'Erreur caméra', 'À qualifier', 'Filtré Web', 'Inhibé Web']

    # Réindexer incident_counts pour inclure toutes les caméras et remplir les valeurs manquantes avec 0
    incident_counts = incident_counts.reindex(all_cameras, fill_value=0)

    # Réindexer pour inclure tous les types de qualification même s'ils n'ont pas de données pour certaines caméras
    incident_counts = incident_counts.reindex(columns=qualification_order, fill_value=0)

    # Définir les couleurs pour chaque type de qualification
    colors = {
        'Avéré': 'darkgreen',
        'Catégorie erronée': 'lightgreen',
        'Fausse alarme': 'red',
        'Erreur caméra': 'orange',
        'À qualifier': 'blue',
        'Filtré Web': 'darkgray',
        'Inhibé Web': 'lightgray'
    }

    # Extraire la date minimale et la formater
    date_str = pd.to_datetime(df['Date de début'].min(), errors='coerce').strftime('%d %B %Y') if 'Date de début' in df.columns else "Date non disponible"

    # Fonction pour créer le graphique avec l'ordre spécifique
    def create_graph(data, title):
        fig, ax = plt.subplots(figsize=(12, 6))
        bottom = pd.Series(0, index=data.index)
        
        for qualif in qualification_order:
            if qualif in data.columns:
                ax.bar(data.index, data[qualif], bottom=bottom, label=qualif, color=colors[qualif])
                bottom += data[qualif]

        plt.title(title)
        plt.xlabel('Caméra')
        plt.ylabel("Nombre d'incidents")
        plt.legend(title='Type de qualification', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=90)
        plt.tight_layout()
        
        # Sauvegarder le graphique dans un fichier
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close(fig)
        return img_buffer

    # Diviser les caméras en deux parties pour l'affichage
    total_cameras = len(incident_counts)
    half_cameras = total_cameras // 2  # Division entière

    # Créer les deux parties du graphique
    part1_buffer = create_graph(incident_counts.iloc[:half_cameras], 
                                f"Nombre d'incidents Animal par type de qualification et par caméra (Partie 1) - {date_str}")

    part2_buffer = create_graph(incident_counts.iloc[half_cameras:], 
                                f"Nombre d'incidents Animal par type de qualification et par caméra (Partie 2) - {date_str}")

    # Retourner les buffers des images générées
    return [part1_buffer, part2_buffer]
