# ChatEQT

This chatbot runs a RAG-based framework using LangChain. It is enriched with information about AI impact on society based on the AI Index Report 2024, as well as with company data within the EQT X's fund. The purpose of the bot is to assist users in understanding how AI impacts the industry and the different companies in the fund.

# Installation

1. The package can be installed as

```
# install project package
pip install -e ".[dev"]

# Run post-installation setup
crawl4ai-setup

# Verify crawl4ai installation
crawl4ai-doctor
```

2. Create a `.env` file in the root folder of the project and add a `GOOGLE_API_KEY` key.

# Usage

Before the application can be started, the data and the embeddings need to be prepared. This can be easily achieved using the CLI:

1. First, download the index report and scrape companies data:

```
chateqt offline download
```

2. Second, generate embeddings:

```
chateqt offline get-embeddings
```

3. Finally, run the bot:

```
chateqt online run
```

# Future improvements and additional features

-   **Evaluation**: Develop benchmarks to measure chatbot accuracy, relevance, and response quality using real-world queries and frameworks such as `DeepEval`.

-   **Testing**: Implement unit and integration tests to ensure the chatbot correctly processes PDFs, generated embeddings, etc. without failures.

-   **Scalability**: Design the system to handle increasing loads efficiently.

-   **Observability**: Introduce logging, monitoring, and alerting to track chatbot performance, errors, and user interactions (storing questions/answers).

-   **Memory**: Implement short-term and long-term memory to retain context across user interactions for a more personalized experience.

-   **Caching**: Use caching strategies to store frequently accessed data and speed up response times for repeated queries.

-   **Improved scraping**: Enhance PDF parsing techniques with better text extraction (e.g. tables) as well as improved web-scraping techniques for more efficient data retrieval.

-   **Handle images**: Integrate vision models to extract and allow for image analysis of charts/plots in different reports.
