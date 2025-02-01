"""Main entry point for insights generation"""

import sys
from pathlib import Path
import click
import structlog
from .services.weekly_insights import WeeklyInsightsGenerator

logger = structlog.get_logger(__name__)

@click.group()
def cli():
    """Minecraft resource insights generator"""
    pass

@cli.command()
@click.option(
    "--base-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Base directory containing the data files"
)
def generate_weekly(base_dir: Path):
    """Generate weekly insights report"""
    try:
        generator = WeeklyInsightsGenerator(base_dir)
        report = generator.generate_weekly_report()
        logger.info("weekly_report_generated",
                   timestamp=report.timestamp)
        
    except Exception as e:
        logger.error("failed_to_generate_report", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    cli() 