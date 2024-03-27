from enum import Enum


class FTConstants(Enum):

    FRANCE_TRAVAIL_FILE_NAME = "FRANCE_TRAVAIL_API"

    ACCEPTED_CRITERAS = [
        "departement, publieeDepuis, maxCreationDate, minCreationData"]

    JSON_KEYS = {  # (key,value) : (our keys, france_travail keys)
        "technical_id": "id",
        "place": "lieuTravail",
        "publication_date": "dateCreation",
        "actualisation_date": "dateActualisation",
        "sector": "romeLibelle",
        "title": "intitule",
        "contrat_type": "typeContrat",
        "experience": "experienceLibelle",
        "salary": "salaire",
        "description": "description"
    }

    HOMOGENIZED_JOBS = {
        "domestic-help-cleaning-jobs": [
            "Services domestiques",
            "Nettoyage de locaux"
        ],
        "social-work-jobs": [
            "Assistance auprès d'adultes",
            "Assistance auprès d'enfants"
        ],
        "property-jobs": [
            "Conseiller / Conseillère immobilier"
        ],
        "accounting-finance-jobs": [
            "Comptabilité"
        ],
        "healthcare-nursing-jobs": [
            "Soins d'hygiène, de confort du patient",
            "Soins infirmiers généralistes"
        ],
        "logistics-warehouse-jobs": [
            "Magasinage et préparation de commandes",
            "Conduite de transport de marchandises sur longue distance",
            "Conduite d'équipement d'usinage",
            "Conduite d'engins de déplacement des charges",
            "Conduite d'équipement de production alimentaire"
        ],
        "maintenance-jobs": [
            "Mécanique automobile et entretien de véhicules",
            "Installation et maintenance d'équipements \
                industriels et d'exploitation",
            "Maintenance des bâtiments et des locaux"
        ],
        "hospitality-catering-jobs": [
            "Service en restauration",
            "Chef / Cheffe de cuisine",
            "Personnel polyvalent en restauration",
            "Personnel de cuisine"
        ],
        "retail-jobs": [
            "Mise en rayon libre-service",
            "Vente en alimentation"
        ],
        "admin-jobs": [
            "Secrétariat"
        ],
        "teaching-jobs": [
            "Enseignement général du second degré"
        ],
        "trade-construction-jobs": [
            "Maçonnerie",
            "Montage-assemblage mécanique"
        ],
        "it-jobs": [
            "Études et développement informatique"
        ],
        "sales-jobs": [
            "Commercial / Commerciale"
        ]

    }
