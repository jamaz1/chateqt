import asyncio
from pathlib import Path

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import yaml


class Crawler:
    def __init__(self) -> None:
        self._load_companies()

    def _load_companies(self) -> None:
        with open(Path(__file__).parent / "companies.yaml") as f:
            self._companies = yaml.safe_load(f)

    def _save_result(self, output_path: Path, page_content: list[str]) -> None:
        with open(output_path, "w") as f:
            f.write(page_content)

    async def _crawl_and_extract(self, urls: list[str]) -> None:
        run_cfg = CrawlerRunConfig(
            word_count_threshold=15,
            excluded_tags=["nav", "footer", "a", "img", "script", "style"],
            exclude_external_links=True,
            only_text=True,
        )

        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun_many(
                urls=urls,
                config=run_cfg,
            )

        return [result.markdown for result in result]

    def crawl(
        self,
        output_folder_path: Path,
        companies: dict[list[str]] | None = None,
    ) -> None:
        """Crawl the companies' websites and save the results to the data folder."""
        if companies is None:
            companies = self._companies

        for company, urls in companies.items():
            result = asyncio.run(self._crawl_and_extract(urls=urls))
            # loop = asyncio.get_event_loop()
            # result = loop.run_until_complete(self._crawl(urls))

            for i, page_content in enumerate(result):
                output_path = output_folder_path / f"{company}-{i+1}.md"
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                self._save_result(
                    output_path=output_path,
                    page_content=page_content,
                )


if __name__ == "__main__":
    data_path = Path(*Path(__file__).parts[:-4]) / "data"
    raw_data_folder_path = data_path / "raw"
    embeddings_folder_path = data_path / "embeddings"

    crawler = Crawler()
    crawler.crawl(output_folder_path=raw_data_folder_path / "companies")
