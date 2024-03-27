import src.apiDataCollection.jobsProcess as jP
import pytest


@pytest.fixture
def FT_job():
    return {
        "technical_id": "171SBBC",
        "place": {
            "libelle": "01 - BOURG EN BRESSE",
            "latitude": 46.206576,
            "longitude": 5.241985,
            "codePostal": "01000",
            "commune": "01053"
        },
        "publication_date": "2024-03-25T11:56:13.000Z",
        "actualisation_date": "2024-03-25T13:41:47.000Z",
        "sector": "Mise en rayon libre-service",
        "title": "Employ\u00e9  de rayon alimentaire H/F",
        "contrat_type": "CDD",
        "experience": "D\u00e9butant accept\u00e9",
        "salary": {
            "libelle": "Mensuel de 1800 Euros sur 12 mois"
        },
        "description": "Besoin d'un renfort pour le rayon alimentaire.\nMissions confi\u00e9es :\n- Garantir l'attractivit\u00e9 du rayon tout en respectant l'implantation, la qualit\u00e9, la rotation des produits et la gestion de stocks\n- Accueillir et conseiller les clients du rayon\n- Effectuer le r\u00e9approvisionnement \n\nPort de charges r\u00e9gulier\n\nPoste de travail de 5h \u00e0 11h sur 6 jours du lundi au samedi\nContrat minimum de 3 mois qui peut \u00e9voluer dans le temps\n\n"
    }


@pytest.fixture
def FT_jobs_process():
    return jP.FTJobsProcess()


def test_process_sector(FT_job, FT_jobs_process):
    FT_job = FT_jobs_process._process_activity(FT_job)
    assert (FT_job["sector"] == "retail-jobs")
