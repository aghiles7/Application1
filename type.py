import pandas as pd
import matplotlib.pyplot as plt
import io

def create_type_incident_plots(df):
    # Extraire la première date de début du fichier Excel
    date_debut = df['Date de début'].min()
    date_str = pd.to_datetime(date_debut).strftime('%d %B %Y')

    def determine_qualification(row):
        if row['Qualification opérateur'] == 'Erreur caméra' and row['Qualifié'] == 'Oui':
            return 'Erreur caméra'
        elif pd.isna(row['Qualification opérateur']) and row['Qualifié'] == 'Non':
            return 'À qualifier'
        elif row['Qualification opérateur'] == 'Pas d\'incident':
            return 'Fausse alarme'
        elif row['Détection modèle'] != row['Qualification opérateur']:
            return 'Catégorie erronée'
        elif row['Détection modèle'] == row['Type de qualification']:
            return 'À qualifier'
        else:
            return row['Type de qualification']

    df['Type de qualification'] = df.apply(determine_qualification, axis=1)

    # Compter le nombre d'incidents par type et par qualification
    incident_counts = df.groupby(['Détection modèle', 'Type de qualification']).size().unstack(fill_value=0)

    # Ajouter la qualification "À qualifier" si elle n'existe pas déjà
    if 'À qualifier' not in incident_counts.columns:
        incident_counts['À qualifier'] = 0

    # Définir l'ordre des types d'incidents comme dans le graphique
    incident_order = ['Véhicule lent', 'Véhicule arrêté', 'Congestion', 'Contresens', 'Cycliste', 'Objet', 'Piéton', 'Animal', 'Fumée']

    # Réorganiser les données selon l'ordre défini
    incident_counts = incident_counts.reindex(incident_order)

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

    # Créer le premier graphique à barres empilées
    fig, ax = plt.subplots(figsize=(12, 6))

    # Ordre des colonnes selon les couleurs définies
    column_order = ['Avéré', 'Catégorie erronée', 'Fausse alarme', 'Erreur caméra', 'À qualifier', 'Filtré Web', 'Inhibé Web']

    bottom = pd.Series(0, index=incident_counts.index)
    for col in column_order:
        if col in incident_counts.columns:
            ax.bar(incident_counts.index, incident_counts[col], bottom=bottom, label=col, color=colors[col])
            bottom += incident_counts[col]

    # Personnaliser le graphique
    plt.title(f"Nombre d'incidents par type d'incident - {date_str}")
    plt.xlabel("Type d'incident")
    plt.ylabel("Nombre")
    plt.legend(title='', loc='upper right', bbox_to_anchor=(1.25, 1))
    plt.xticks(rotation=45, ha='right')

    # Ajuster la mise en page
    plt.tight_layout()

    # Sauvegarder le graphique dans un buffer en mémoire
    img_buffer_1 = io.BytesIO()
    plt.savefig(img_buffer_1, format='png', dpi=300)
    img_buffer_1.seek(0)

    # Créer le deuxième graphique sans 'Filtré Web' et 'Inhibé Web'
    fig, ax = plt.subplots(figsize=(12, 6))

    # Exclure les colonnes 'Filtré Web' et 'Inhibé Web'
    column_order_reduced = ['Avéré', 'Catégorie erronée', 'Fausse alarme', 'Erreur caméra', 'À qualifier']

    bottom = pd.Series(0, index=incident_counts.index)
    for col in column_order_reduced:
        if col in incident_counts.columns:
            ax.bar(incident_counts.index, incident_counts[col], bottom=bottom, label=col, color=colors[col])
            bottom += incident_counts[col]

    # Personnaliser le graphique
    plt.title(f"Nombre d'incidents par type d'incident (sans Filtré Web et Inhibé Web) - {date_str}")
    plt.xlabel("Type d'incident")
    plt.ylabel("Nombre")
    plt.legend(title='', loc='upper right', bbox_to_anchor=(1.25, 1))
    plt.xticks(rotation=45, ha='right')

    # Ajuster la mise en page
    plt.tight_layout()

    # Sauvegarder le deuxième graphique dans un buffer en mémoire
    img_buffer_2 = io.BytesIO()
    plt.savefig(img_buffer_2, format='png', dpi=300)
    img_buffer_2.seek(0)

    return [img_buffer_1, img_buffer_2]
