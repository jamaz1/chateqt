"""Offline module to prepare embeddings."""

import logging
from pathlib import Path
import shutil

import requests
import typer

from chateqt.core import Crawler, Parser, generate_embeddings

app = typer.Typer()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

default_data_folder_path = Path(*Path(__file__).parts[:-4]) / "data"


# TODO: make it download HAI report as well.  # noqa: FIX002, TD002, TD003
@app.command()
def download(output_folder_path: str | None = None) -> None:
    """Download the data from the web and save it to the data folder."""
    if output_folder_path is None:
        output_folder_path = Path(default_data_folder_path) / "raw"

    shutil.rmtree(output_folder_path, ignore_errors=True)

    logger.info("Download AI Index Report 2024.")
    filename = output_folder_path / "base" / "index_info.pdf"
    filename.parent.mkdir(parents=True, exist_ok=True)
    url = "https://aiindex.stanford.edu/wp-content/uploads/2024/05/HAI_AI-Index-Report-2024.pdf"
    response = requests.get(url, timeout=60)
    filename.write_bytes(response.content)
    logger.info(f"AI Index Report 2024 downloaded and saved to {filename}.")

    logger.info("Downloading company specific data.")
    crawler = Crawler()
    companies_output_path = output_folder_path / "companies"
    companies_output_path.parent.mkdir(parents=True, exist_ok=True)
    crawler.crawl(companies_output_path)
    logger.info(f"Data downloaded successfully and saved to {output_folder_path}.")


@app.command()
def get_embeddings(
    input_folder_path: str | None = None,
    output_path: str | None = None,
) -> None:
    """Generate embeddings for the input data."""
    parser = Parser()

    if input_folder_path is None:
        raw_data_folder_path = default_data_folder_path / "raw"

    if output_path is None:
        embeddings_folder_path = default_data_folder_path / "embeddings"

    base_documents = parser.parse_documents(
        folder_path=raw_data_folder_path / "base",
    )
    generate_embeddings(
        documents=base_documents,
        output_path=embeddings_folder_path / "base",
    )

    companies_documents = parser.parse_documents(
        folder_path=raw_data_folder_path / "companies",
    )
    generate_embeddings(
        documents=companies_documents,
        output_path=embeddings_folder_path / "companies",
    )
