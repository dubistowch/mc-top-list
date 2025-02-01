"""Main entry point for insights generation"""

import sys
from pathlib import Path
import click
import structlog
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
from .services.generator import WeeklyInsightsGenerator

logger = structlog.get_logger(__name__)

class InsightsHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for insights server"""
    
    def __init__(self, *args, **kwargs):
        # 必須在呼叫父類別的 __init__ 之前設定 directory
        kwargs["directory"] = str(Path.cwd() / "public")
        super().__init__(*args, **kwargs)
    
    def do_GET(self) -> None:
        """Override do_GET to handle paths correctly"""
        # 如果是根路徑，重定向到 index.html
        if self.path == "/":
            self.path = "/index.html"
        
        # 確保路徑在 public 目錄下
        file_path = Path(self.directory) / self.path.lstrip("/")
        if not file_path.is_file():
            self.send_error(404, "File not found")
            return
        
        return super().do_GET()
    
    def log_message(self, format: str, *args) -> None:
        """Override log message to use structlog"""
        logger.info(
            "http_request",
            path=self.path,
            method=self.command,
            status=args[1]
        )

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
        generator.generate_weekly()
        logger.info("generation_completed")
        
    except Exception as e:
        logger.error("generation_failed", error=str(e))
        sys.exit(1)

@cli.command()
@click.option(
    "--base-dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=Path.cwd(),
    help="Base directory containing the data files"
)
def clean(base_dir: Path):
    """Clean up generated files"""
    try:
        generator = WeeklyInsightsGenerator(base_dir)
        generator.clean()
        logger.info("cleanup_completed")
        
    except Exception as e:
        logger.error("cleanup_failed", error=str(e))
        sys.exit(1)

@cli.command()
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port to run the server on"
)
@click.option(
    "--no-browser",
    is_flag=True,
    help="Don't open browser automatically"
)
def serve(port: int, no_browser: bool):
    """Start a development server"""
    try:
        # 確保 public 目錄存在
        public_dir = Path.cwd() / "public"
        if not public_dir.exists():
            logger.error("public_dir_not_found", path=str(public_dir))
            logger.info("Please run 'python -m insights generate-weekly' first")
            sys.exit(1)
        
        # 建立伺服器
        server_address = ("", port)
        httpd = HTTPServer(server_address, InsightsHTTPRequestHandler)
        
        # 開啟瀏覽器（除非指定 --no-browser）
        if not no_browser:
            webbrowser.open(f"http://localhost:{port}")
        
        logger.info("server_started",
                   port=port,
                   url=f"http://localhost:{port}")
        
        # 啟動伺服器
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("server_stopped")
        sys.exit(0)
    except Exception as e:
        logger.error("server_error", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    cli() 