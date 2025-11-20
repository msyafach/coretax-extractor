"""
Auto-Update System for Coretax Extractor
Complete auto-update solution with GitHub integration
Combines backend logic and UI in one self-contained module
"""

import os
import sys
import json
import tempfile
import zipfile
import subprocess
import threading
from pathlib import Path
from typing import Optional, Tuple

import requests
import flet as ft


# ============================================================================
# BACKEND: UpdateChecker Class
# ============================================================================

class UpdateChecker:
    """Handle auto-update functionality via GitHub Releases."""
    
    def __init__(self):
        """Initialize the update checker."""
        self.version_file = self._get_resource_path('version.json')
        self.config = self._load_version_config()
        
    def _get_resource_path(self, relative_path: str) -> str:
        """Get absolute path to resource, works for dev and PyInstaller."""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def _load_version_config(self) -> dict:
        """Load version configuration from JSON file."""
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load version config: {e}")
    
    def get_current_version(self) -> str:
        """Get current application version."""
        return self.config.get('version', '0.0.0')
    
    def check_for_updates(self) -> Tuple[bool, Optional[dict]]:
        """
        Check if a new version is available on GitHub.
        
        Returns:
            Tuple of (update_available, release_info)
        """
        try:
            github_repo = self.config.get('github_repo')
            if not github_repo:
                raise Exception("GitHub repository not configured")
            
            # GitHub API endpoint for latest release
            api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
            
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            
            # Extract version from tag (remove 'v' prefix if present)
            latest_version = release_data['tag_name'].lstrip('v')
            current_version = self.get_current_version()
            
            # Compare versions
            if self._is_newer_version(latest_version, current_version):
                # Find the asset to download
                asset_name = self.config.get('asset_name', 'CoretaxExtractor.zip')
                asset_url = None
                asset_size = 0
                
                for asset in release_data.get('assets', []):
                    if asset['name'] == asset_name:
                        asset_url = asset['browser_download_url']
                        asset_size = asset['size']
                        break
                
                if not asset_url:
                    raise Exception(f"Asset '{asset_name}' not found in release")
                
                release_info = {
                    'version': latest_version,
                    'download_url': asset_url,
                    'asset_size': asset_size,
                    'release_notes': release_data.get('body', 'No release notes available'),
                    'published_at': release_data.get('published_at', ''),
                }
                
                return True, release_info
            
            return False, None
            
        except requests.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"Update check failed: {str(e)}")
    
    def _is_newer_version(self, latest: str, current: str) -> bool:
        """Compare version strings (simple numeric comparison)."""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad with zeros if lengths differ
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts += [0] * (max_len - len(latest_parts))
            current_parts += [0] * (max_len - len(current_parts))
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_update(self, url: str, progress_callback=None) -> Optional[str]:
        """
        Download update file from URL.
        
        Args:
            url: Download URL
            progress_callback: Optional callback(downloaded_bytes, total_bytes)
        
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            # Create temp file
            temp_dir = tempfile.gettempdir()
            zip_path = os.path.join(temp_dir, 'coretax_update.zip')
            
            downloaded = 0
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            return zip_path
            
        except Exception as e:
            return None
    
    def prepare_update(self, zip_path: str) -> Tuple[bool, Optional[str]]:
        """
        Extract update ZIP file.
        
        Args:
            zip_path: Path to downloaded ZIP file
        
        Returns:
            Tuple of (success, extract_path)
        """
        try:
            temp_dir = tempfile.gettempdir()
            extract_path = os.path.join(temp_dir, 'coretax_update_extracted')
            
            # Remove old extraction if exists
            if os.path.exists(extract_path):
                import shutil
                shutil.rmtree(extract_path)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            return True, extract_path
            
        except Exception as e:
            return False, None
    
    def create_update_script(self, extract_path: str) -> Optional[str]:
        """
        Create batch script to apply update.
        
        Args:
            extract_path: Path to extracted update files
        
        Returns:
            Path to update script or None if failed
        """
        try:
            # Get current application directory
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.abspath(".")
            
            # Create update script
            temp_dir = tempfile.gettempdir()
            script_path = os.path.join(temp_dir, 'apply_update.bat')
            
            script_content = f"""@echo off
echo Applying Coretax Extractor Update...
timeout /t 2 /nobreak >nul

echo Copying new files...
xcopy /E /I /Y "{extract_path}\\*" "{app_dir}"

echo Update complete!
echo Restarting application...
timeout /t 2 /nobreak >nul

start "" "{os.path.join(app_dir, 'CoretaxExtractor.exe')}"

echo Cleaning up...
del "%~f0"
"""
            
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            return script_path
            
        except Exception as e:
            return None
    
    def apply_update(self, script_path: str) -> bool:
        """
        Launch update script.
        
        Args:
            script_path: Path to update script
        
        Returns:
            True if script launched successfully
        """
        try:
            # Launch script in detached process
            subprocess.Popen(
                [script_path],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=True
            )
            return True
        except Exception as e:
            return False


# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================


def create_update_button(app_instance):
    """
    Create update button for header.
    
    Args:
        app_instance: Instance of CoretaxExtractorApp
    
    Returns:
        ft.IconButton: Update button component
    """
    RSM_BLUE = "#0099D8"
    
    return ft.IconButton(
        icon=ft.Icons.SYSTEM_UPDATE,
        icon_color=RSM_BLUE,
        tooltip="Check for Updates",
        on_click=lambda e: check_for_updates(app_instance, e),
        icon_size=20,
    )


def check_for_updates(app_instance, e=None):
    """Check for application updates from GitHub."""
    # RSM Colors
    RSM_GREY = "#5A6670"
    RSM_GREEN = "#2E8B3E"
    RSM_BLUE = "#0099D8"
    
    # Show checking dialog
    checking_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.SYSTEM_UPDATE, color=RSM_BLUE),
            ft.Text("Checking for Updates"),
        ]),
        content=ft.Column([
            ft.ProgressRing(),
            ft.Container(height=8),
            ft.Text("Please wait..."),
        ], tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )
    
    app_instance.page.overlay.append(checking_dialog)
    checking_dialog.open = True
    app_instance.page.update()
    
    # Check for updates in background thread
    def check_updates_thread():
        try:
            checker = UpdateChecker()
            current_version = checker.get_current_version()
            update_available, release_info = checker.check_for_updates()
            
            # Close checking dialog
            checking_dialog.open = False
            app_instance.page.update()
            
            if update_available and release_info:
                _show_update_available_dialog(app_instance, release_info, checker)
            else:
                _show_no_update_dialog(app_instance, current_version)
                
        except Exception as ex:
            checking_dialog.open = False
            app_instance.page.update()
            _show_update_error_dialog(app_instance, str(ex))
    
    thread = threading.Thread(target=check_updates_thread, daemon=True)
    thread.start()


def _show_update_available_dialog(app_instance, release_info: dict, checker: UpdateChecker):
    """Show dialog when update is available."""
    RSM_GREY = "#5A6670"
    RSM_GREEN = "#2E8B3E"
    RSM_BLUE = "#0099D8"
    
    current_version = checker.get_current_version()
    new_version = release_info['version']
    
    # Format file size
    size_mb = release_info.get('asset_size', 0) / (1024 * 1024)
    size_text = f"{size_mb:.1f} MB" if size_mb > 0 else "Unknown size"
    
    # Format release notes
    notes = release_info.get('release_notes', 'No release notes available')
    if len(notes) > 300:
        notes = notes[:300] + "..."
    
    def start_download(e):
        dialog.open = False
        app_instance.page.update()
        _download_and_install_update(app_instance, release_info, checker)
    
    def cancel_update(e):
        dialog.open = False
        app_instance.page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.NEW_RELEASES, color=RSM_GREEN),
            ft.Text("Update Available!"),
        ]),
        content=ft.Column([
            ft.Text(
                f"A new version is available: v{new_version}",
                weight=ft.FontWeight.BOLD,
            ),
            ft.Text(f"Current version: v{current_version}", size=12, color=RSM_GREY),
            ft.Container(height=8),
            ft.Text(f"Download size: {size_text}", size=12),
            ft.Container(height=12),
            ft.Text("What's new:", weight=ft.FontWeight.BOLD, size=13),
            ft.Container(
                content=ft.Text(notes, size=12, selectable=True),
                padding=8,
                bgcolor="#F5F5F5",
                border_radius=4,
            ),
        ], tight=True, width=450, scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Later", on_click=cancel_update),
            ft.ElevatedButton(
                "Download & Install",
                icon=ft.Icons.DOWNLOAD,
                on_click=start_download,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=RSM_GREEN,
                ),
            ),
        ],
    )
    
    app_instance.page.overlay.append(dialog)
    dialog.open = True
    app_instance.page.update()


def _show_no_update_dialog(app_instance, current_version: str):
    """Show dialog when no update is available."""
    RSM_GREY = "#5A6670"
    RSM_BLUE = "#0099D8"
    
    def close_dialog(e):
        dialog.open = False
        app_instance.page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=RSM_BLUE),
            ft.Text("Up to Date"),
        ]),
        content=ft.Column([
            ft.Text(f"You are running the latest version (v{current_version})"),
            ft.Container(height=4),
            ft.Text("No updates available at this time.", size=12, color=RSM_GREY),
        ], tight=True),
        actions=[
            ft.TextButton("OK", on_click=close_dialog),
        ],
    )
    
    app_instance.page.overlay.append(dialog)
    dialog.open = True
    app_instance.page.update()


def _show_update_error_dialog(app_instance, error_message: str):
    """Show dialog when update check fails."""
    RSM_GREY = "#5A6670"
    
    def close_dialog(e):
        dialog.open = False
        app_instance.page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400),
            ft.Text("Update Check Failed"),
        ]),
        content=ft.Column([
            ft.Text("Could not check for updates."),
            ft.Container(height=8),
            ft.Text(f"Error: {error_message}", size=11, color=RSM_GREY),
            ft.Container(height=8),
            ft.Text(
                "Please check your internet connection or try again later.",
                size=12,
            ),
        ], tight=True, width=400),
        actions=[
            ft.TextButton("OK", on_click=close_dialog),
        ],
    )
    
    app_instance.page.overlay.append(dialog)
    dialog.open = True
    app_instance.page.update()


def _download_and_install_update(app_instance, release_info: dict, checker: UpdateChecker):
    """Download and install the update."""
    RSM_GREY = "#5A6670"
    RSM_GREEN = "#2E8B3E"
    RSM_BLUE = "#0099D8"
    
    # Progress dialog
    progress_text = ft.Text("Preparing download...", size=13)
    progress_bar = ft.ProgressBar(width=400, value=0, color=RSM_BLUE)
    
    def cancel_download(e):
        dialog.open = False
        app_instance.page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.DOWNLOAD, color=RSM_BLUE),
            ft.Text("Downloading Update"),
        ]),
        content=ft.Column([
            progress_text,
            ft.Container(height=8),
            progress_bar,
        ], tight=True, width=400),
        actions=[
            ft.TextButton("Cancel", on_click=cancel_download),
        ],
    )
    
    app_instance.page.overlay.append(dialog)
    dialog.open = True
    app_instance.page.update()
    
    # Download in background thread
    def download_thread():
        try:
            download_url = release_info['download_url']
            
            def update_progress(downloaded, total):
                if total > 0:
                    progress = downloaded / total
                    progress_bar.value = progress
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total / (1024 * 1024)
                    progress_text.value = f"Downloaded {mb_downloaded:.1f} MB of {mb_total:.1f} MB"
                    app_instance.page.update()
            
            # Download the update
            zip_path = checker.download_update(download_url, update_progress)
            
            if zip_path:
                progress_text.value = "Extracting update..."
                progress_bar.value = None  # Indeterminate
                app_instance.page.update()
                
                # Extract the update
                success, extract_path = checker.prepare_update(zip_path)
                
                if success and extract_path:
                    # Create update script
                    script_path = checker.create_update_script(extract_path)
                    
                    if script_path:
                        dialog.open = False
                        app_instance.page.update()
                        _show_restart_dialog(app_instance, script_path, checker)
                    else:
                        raise Exception("Failed to create update script")
                else:
                    raise Exception("Failed to extract update")
            else:
                raise Exception("Download failed")
                
        except Exception as ex:
            dialog.open = False
            app_instance.page.update()
            _show_update_error_dialog(app_instance, f"Download failed: {str(ex)}")
    
    thread = threading.Thread(target=download_thread, daemon=True)
    thread.start()


def _show_restart_dialog(app_instance, script_path: str, checker: UpdateChecker):
    """Show dialog to restart and apply update."""
    RSM_GREEN = "#2E8B3E"
    
    def apply_update(e):
        # Launch update script and close application
        if checker.apply_update(script_path):
            # Close the application
            app_instance.page.window.destroy()
        else:
            dialog.open = False
            app_instance.page.update()
            _show_update_error_dialog(app_instance, "Failed to launch update installer")
    
    def cancel(e):
        dialog.open = False
        app_instance.page.update()
    
    dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Icon(ft.Icons.RESTART_ALT, color=RSM_GREEN),
            ft.Text("Ready to Install"),
        ]),
        content=ft.Column([
            ft.Text("The update has been downloaded successfully."),
            ft.Container(height=8),
            ft.Text(
                "The application will close and the update will be installed automatically.",
                size=12,
            ),
            ft.Container(height=8),
            ft.Text(
                "Click 'Install Now' to continue.",
                weight=ft.FontWeight.BOLD,
            ),
        ], tight=True, width=400),
        actions=[
            ft.TextButton("Cancel", on_click=cancel),
            ft.ElevatedButton(
                "Install Now",
                icon=ft.Icons.SYSTEM_UPDATE,
                on_click=apply_update,
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE,
                    bgcolor=RSM_GREEN,
                ),
            ),
        ],
    )
    
    app_instance.page.overlay.append(dialog)
    dialog.open = True
    app_instance.page.update()
