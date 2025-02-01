from setuptools import setup, find_packages

setup(
    name="mc-top-list",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "pyyaml",
        "click",
        "jinja2",
        "structlog",
    ],
    entry_points={
        "console_scripts": [
            "scraper=scraper.cli:cli",
            "insights=insights.cli:cli",
        ],
    },
) 