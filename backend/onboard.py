#!/usr/bin/env python3
"""
Orchestratorr Onboarding Wizard

Interactive CLI to collect service credentials and URLs, validate connections,
and securely store configuration in .env file.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table


class OnboardingWizard:
    """Interactive onboarding wizard for orchestratorr configuration."""

    def __init__(self, project_root: Path):
        """Initialize the wizard with project root path."""
        self.console = Console()
        self.project_root = project_root
        self.env_path = project_root / ".env"
        self.config = {}

    def welcome(self) -> None:
        """Display welcome message."""
        self.console.print(
            Panel(
                "[bold cyan]🎬 Welcome to Orchestratorr Onboarding[/bold cyan]\n"
                "Let's set up your media server configuration.\n"
                "You'll be prompted for each service's URL and API key.",
                border_style="cyan",
            )
        )
        self.console.print()

    def test_connection(self, url: str, api_key: str, service_name: str) -> bool:
        """
        Test connection to a service.

        Args:
            url: Service URL
            api_key: Service API key
            service_name: Name of the service (for logging)

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Ensure URL doesn't have trailing slash for consistency
            url = url.rstrip("/")
            headers = {"X-Api-Key": api_key}

            # Most *arr services have a /api/system/status endpoint
            response = requests.get(
                f"{url}/api/system/status",
                headers=headers,
                timeout=5,
            )

            if response.status_code == 200:
                self.console.print(f"[green]✓ {service_name} connection successful[/green]")
                return True
            elif response.status_code == 401:
                self.console.print(f"[red]✗ {service_name}: Unauthorized (invalid API key)[/red]")
                return False
            else:
                self.console.print(
                    f"[red]✗ {service_name}: HTTP {response.status_code}[/red]"
                )
                return False
        except requests.exceptions.ConnectionError:
            self.console.print(f"[red]✗ {service_name}: Cannot connect to {url}[/red]")
            return False
        except requests.exceptions.Timeout:
            self.console.print(f"[red]✗ {service_name}: Connection timeout[/red]")
            return False
        except Exception as e:
            self.console.print(f"[red]✗ {service_name}: Error - {e}[/red]")
            return False

    def prompt_service(
        self,
        service_name: str,
        default_url: str,
        required: bool = True,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Prompt user for a service's configuration.

        Args:
            service_name: Name of the service
            default_url: Default URL
            required: Whether service is required

        Returns:
            Tuple of (url, api_key) or (None, None) if skipped
        """
        self.console.print(f"\n[bold]{service_name}[/bold]")
        self.console.print(f"(Default URL: {default_url})")

        # Skip option for optional services
        if not required:
            if Confirm.ask(f"Configure {service_name}?", default=False):
                pass  # Continue with prompts
            else:
                self.console.print(f"[dim]Skipping {service_name}[/dim]")
                return None, None

        # Prompt for URL
        url = Prompt.ask(f"{service_name} URL", default=default_url)

        # Prompt for API key
        api_key = Prompt.ask(
            f"{service_name} API Key",
            password=True,
        )

        if not api_key:
            self.console.print("[red]API key cannot be empty[/red]")
            return self.prompt_service(service_name, default_url, required)

        # Test connection
        if Confirm.ask("Test connection?", default=True):
            if not self.test_connection(url, api_key, service_name):
                if Confirm.ask("Continue anyway?", default=False):
                    return url, api_key
                else:
                    return self.prompt_service(service_name, default_url, required)

        return url, api_key

    def run(self) -> None:
        """Run the onboarding wizard."""
        self.welcome()

        # Required: Radarr
        radarr_url, radarr_key = self.prompt_service(
            "Radarr",
            "http://localhost:7878",
            required=True,
        )
        if radarr_url:
            self.config["RADARR_URL"] = radarr_url
            self.config["RADARR_API_KEY"] = radarr_key

        # Optional services
        sonarr_url, sonarr_key = self.prompt_service(
            "Sonarr",
            "http://localhost:8989",
            required=False,
        )
        if sonarr_url:
            self.config["SONARR_URL"] = sonarr_url
            self.config["SONARR_API_KEY"] = sonarr_key

        lidarr_url, lidarr_key = self.prompt_service(
            "Lidarr",
            "http://localhost:8686",
            required=False,
        )
        if lidarr_url:
            self.config["LIDARR_URL"] = lidarr_url
            self.config["LIDARR_API_KEY"] = lidarr_key

        prowlarr_url, prowlarr_key = self.prompt_service(
            "Prowlarr",
            "http://localhost:9696",
            required=False,
        )
        if prowlarr_url:
            self.config["PROWLARR_URL"] = prowlarr_url
            self.config["PROWLARR_API_KEY"] = prowlarr_key

        # Ask for FastAPI host/port
        self.console.print("\n[bold]FastAPI Server Configuration[/bold]")
        fastapi_host = Prompt.ask(
            "FastAPI Host",
            default="0.0.0.0",
        )
        fastapi_port = Prompt.ask(
            "FastAPI Port",
            default="8000",
        )
        self.config["FASTAPI_HOST"] = fastapi_host
        self.config["FASTAPI_PORT"] = fastapi_port

        # Ask for frontend URL
        self.console.print("\n[bold]Frontend Configuration[/bold]")
        frontend_url = Prompt.ask(
            "Frontend URL",
            default="http://localhost:5173",
        )
        self.config["FRONTEND_URL"] = frontend_url

        allowed_origins = Prompt.ask(
            "Allowed Origins (comma-separated)",
            default="http://localhost:5173,http://localhost:3000",
        )
        self.config["ALLOWED_ORIGINS"] = allowed_origins

        # Save configuration
        self.save_env()

    def save_env(self) -> None:
        """Save configuration to .env file with secure permissions."""
        self.console.print("\n[bold]Saving configuration...[/bold]")

        # Check if .env already exists
        if self.env_path.exists():
            if not Confirm.ask(f".env already exists. Overwrite?", default=False):
                self.console.print("[yellow]Keeping existing .env[/yellow]")
                return

        # Build .env content
        lines = [
            "# Orchestratorr Configuration",
            "# Generated by onboarding wizard",
            "",
            "# ============================================================================",
            "# Radarr Configuration",
            "# ============================================================================",
        ]

        if "RADARR_URL" in self.config:
            lines.extend([
                f"RADARR_URL={self.config['RADARR_URL']}",
                f"RADARR_API_KEY={self.config['RADARR_API_KEY']}",
            ])

        lines.extend([
            "",
            "# ============================================================================",
            "# Sonarr Configuration (Optional)",
            "# ============================================================================",
        ])

        if "SONARR_URL" in self.config:
            lines.extend([
                f"SONARR_URL={self.config['SONARR_URL']}",
                f"SONARR_API_KEY={self.config['SONARR_API_KEY']}",
            ])

        lines.extend([
            "",
            "# ============================================================================",
            "# Lidarr Configuration (Optional)",
            "# ============================================================================",
        ])

        if "LIDARR_URL" in self.config:
            lines.extend([
                f"LIDARR_URL={self.config['LIDARR_URL']}",
                f"LIDARR_API_KEY={self.config['LIDARR_API_KEY']}",
            ])

        lines.extend([
            "",
            "# ============================================================================",
            "# Prowlarr Configuration (Optional)",
            "# ============================================================================",
        ])

        if "PROWLARR_URL" in self.config:
            lines.extend([
                f"PROWLARR_URL={self.config['PROWLARR_URL']}",
                f"PROWLARR_API_KEY={self.config['PROWLARR_API_KEY']}",
            ])

        lines.extend([
            "",
            "# ============================================================================",
            "# FastAPI Server Configuration",
            "# ============================================================================",
            f"FASTAPI_HOST={self.config.get('FASTAPI_HOST', '0.0.0.0')}",
            f"FASTAPI_PORT={self.config.get('FASTAPI_PORT', '8000')}",
            f"FASTAPI_RELOAD=true",
            "",
            "# ============================================================================",
            "# Frontend Configuration",
            "# ============================================================================",
            f"FRONTEND_URL={self.config.get('FRONTEND_URL', 'http://localhost:5173')}",
            f"ALLOWED_ORIGINS={self.config.get('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000')}",
            "",
            "# ============================================================================",
            "# Logging Configuration",
            "# ============================================================================",
            "LOG_LEVEL=INFO",
            "",
        ])

        content = "\n".join(lines)

        # Write .env file
        self.env_path.write_text(content)

        # Secure permissions: only owner can read/write (chmod 600)
        os.chmod(self.env_path, 0o600)

        # Display summary
        self.console.print()
        self.console.print(
            Panel(
                f"[green]✓ Configuration saved[/green]\n"
                f"[cyan]Location:[/cyan] {self.env_path.absolute()}\n"
                f"[cyan]Permissions:[/cyan] 0600 (owner read/write only)\n"
                f"[yellow]⚠ Never commit this file to version control![/yellow]",
                border_style="green",
            )
        )

        # Show summary table
        self.console.print("\n[bold]Configuration Summary:[/bold]")
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Service", style="cyan")
        table.add_column("URL", style="green")
        table.add_column("API Key", style="green")

        for service in ["RADARR", "SONARR", "LIDARR", "PROWLARR"]:
            url_key = f"{service}_URL"
            api_key = f"{service}_API_KEY"
            if url_key in self.config:
                table.add_row(
                    service,
                    self.config[url_key],
                    "••••••••" if self.config.get(api_key) else "Not set",
                )

        self.console.print(table)
        self.console.print()
        self.console.print("[bold cyan]Ready to start![/bold cyan]")
        self.console.print("Run: [yellow]python backend/main.py[/yellow]")


def main():
    """Entry point for the onboarding wizard."""
    # Get project root (parent of backend directory)
    project_root = Path(__file__).parent.parent

    wizard = OnboardingWizard(project_root)
    try:
        wizard.run()
    except KeyboardInterrupt:
        print("\n[red]Onboarding cancelled[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
