#!/usr/bin/env python3
import sys
import os
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

BANNER = """
[bold purple]
███╗   ██╗███████╗███████╗██╗    ██╗██╗███████╗██╗
████╗  ██║██╔════╝██╔════╝██║    ██║██║██╔════╝██║
██╔██╗ ██║█████╗  █████╗  ██║ █╗ ██║██║█████╗  ██║
██║╚██╗██║██╔══╝  ██╔══╝  ██║███╗██║██║██╔══╝  ██║
██║ ╚████║███████╗███████╗╚███╔███╔╝██║██║     ██║
╚═╝  ╚═══╝╚══════╝╚══════╝ ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝
[/bold purple]
          [bold cyan]NeeWiFi - Linux WiFi Troubleshooter & Fixer v1.0[/bold cyan]
            [dim]A simple diagnostic tool to repair Linux WiFi issues[/dim]
"""

def is_root():
    """Check if the script is run with sudo/root privileges."""
    return os.geteuid() == 0

def run_cmd(cmd):
    """Run a shell command and return its output, code, and error."""
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def get_wifi_interfaces():
    """Identify wireless interfaces on the system."""
    interfaces = []
    # Check /sys/class/net directory for wireless interfaces
    if os.path.exists("/sys/class/net"):
        for name in os.listdir("/sys/class/net"):
            if os.path.exists(f"/sys/class/net/{name}/wireless") or name.startswith("wlan") or name.startswith("wlp"):
                interfaces.append(name)
    return interfaces

def check_internet():
    """Test ping to a public DNS IP (8.8.8.8)."""
    code, _, _ = run_cmd("ping -c 1 -W 2 8.8.8.8")
    return code == 0

def check_dns():
    """Test DNS resolution (pinging google.com)."""
    code, _, _ = run_cmd("ping -c 1 -W 2 google.com")
    return code == 0

def check_network_manager():
    """Check NetworkManager service status."""
    code, out, _ = run_cmd("systemctl is-active NetworkManager")
    return out == "active"

def check_rfkill():
    """Check if WiFi is soft or hard blocked by rfkill."""
    code, out, _ = run_cmd("rfkill list wifi")
    soft_blocked = "soft: yes" in out.lower()
    hard_blocked = "hard: yes" in out.lower()
    return soft_blocked, hard_blocked

def diagnose():
    """Run diagnostics and return status dict."""
    interfaces = get_wifi_interfaces()
    internet = check_internet()
    dns = check_dns()
    nm_active = check_network_manager()
    soft, hard = check_rfkill()
    
    return {
        "interfaces": interfaces,
        "internet": internet,
        "dns": dns,
        "nm_active": nm_active,
        "soft_blocked": soft,
        "hard_blocked": hard
    }

def print_diagnostics(status):
    """Print the diagnostic report in a beautiful table."""
    table = Table(title="📡 WiFi Diagnostic Report", border_style="purple")
    table.add_column("Audit Check", style="bold cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details")
    
    # 1. Root Check
    root_status = "[green]✔ OK[/green]" if is_root() else "[yellow]⚠ User[/yellow]"
    root_desc = "Running as root/sudo" if is_root() else "Running without sudo (fixes will be unavailable)"
    table.add_row("Root Privileges", root_status, root_desc)
    
    # 2. Interfaces
    if status["interfaces"]:
        int_status = "[green]✔ Detected[/green]"
        int_desc = f"Wireless interfaces: {', '.join(status['interfaces'])}"
    else:
        int_status = "[red]✘ Missing[/red]"
        int_desc = "No wireless adapters detected. Check if plugged in or driver missing."
    table.add_row("Wireless Cards", int_status, int_desc)
    
    # 3. NetworkManager
    nm_status = "[green]✔ Active[/green]" if status["nm_active"] else "[red]✘ Inactive[/red]"
    nm_desc = "NetworkManager service is running" if status["nm_active"] else "NetworkManager service is stopped"
    table.add_row("NetworkManager", nm_status, nm_desc)
    
    # 4. RFKILL
    if status["soft_blocked"]:
        rf_status = "[yellow]⚠ Soft Blocked[/yellow]"
        rf_desc = "WiFi is disabled in software (can be unblocked)"
    elif status["hard_blocked"]:
        rf_status = "[red]✘ Hard Blocked[/red]"
        rf_desc = "WiFi is disabled via physical hardware switch/hotkey"
    else:
        rf_status = "[green]✔ Unblocked[/green]"
        rf_desc = "No hardware or software locks detected"
    table.add_row("rfkill Block Status", rf_status, rf_desc)
    
    # 5. Connection
    if status["internet"]:
        conn_status = "[green]✔ Connected[/green]"
        conn_desc = "Successfully pinged public IP (8.8.8.8)"
    else:
        conn_status = "[red]✘ Offline[/red]"
        conn_desc = "Cannot reach internet (Ping 8.8.8.8 failed)"
    table.add_row("Internet Connection", conn_status, conn_desc)
    
    # 6. DNS
    if status["dns"]:
        dns_status = "[green]✔ Resolved[/green]"
        dns_desc = "DNS resolution is working (Ping google.com OK)"
    else:
        dns_status = "[red]✘ Resolv Error[/red]"
        dns_desc = "DNS lookup failed (Cannot resolve domain names)"
    table.add_row("DNS Lookup", dns_status, dns_desc)
    
    console.print(table)

def apply_fix(option, status):
    """Apply specific networking fix."""
    if not is_root():
        console.print("[bold red]Error:[/bold red] You must run NeeWiFi with sudo to apply fixes (e.g. [bold]sudo python3 neewifi.py[/bold]).")
        return False
        
    if option == "1":
        console.print("[yellow]Restarting NetworkManager service...[/yellow]")
        run_cmd("systemctl restart NetworkManager")
        time.sleep(2)
        return True
        
    elif option == "2":
        console.print("[yellow]Unblocking all wireless devices (rfkill)...[/yellow]")
        run_cmd("rfkill unblock all")
        time.sleep(1)
        return True
        
    elif option == "3":
        if not status["interfaces"]:
            console.print("[red]No wireless interfaces found to bring up.[/red]")
            return False
        for name in status["interfaces"]:
            console.print(f"[yellow]Bringing up interface '{name}'...[/yellow]")
            run_cmd(f"ip link set {name} up")
        time.sleep(1)
        return True
        
    elif option == "4":
        console.print("[yellow]Repairing DNS Resolver Configuration (/etc/resolv.conf)...[/yellow]")
        try:
            # Backup old resolv.conf
            if os.path.exists("/etc/resolv.conf"):
                run_cmd("cp /etc/resolv.conf /etc/resolv.conf.backup")
            # Write Google and Cloudflare public DNS
            with open("/etc/resolv.conf", "w") as f:
                f.write("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
            console.print("[green]✔ DNS servers set to 8.8.8.8 and 1.1.1.1 successfully.[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to modify resolv.conf: {str(e)}[/red]")
            return False
            
    elif option == "5":
        console.print("[yellow]Performing complete Network Stack Reset...[/yellow]")
        run_cmd("rfkill unblock all")
        run_cmd("systemctl restart NetworkManager")
        time.sleep(2)
        if status["interfaces"]:
            for name in status["interfaces"]:
                run_cmd(f"ip link set {name} up")
        return True
    
    return False

def main():
    console.print(BANNER)
    
    while True:
        status = diagnose()
        print_diagnostics(status)
        
        # Show interactive fix menu
        menu = Table(title="🛠️ NeeWiFi Repair Actions", border_style="purple", box=None)
        menu.add_column("Option", style="bold magenta", justify="center")
        menu.add_column("Action description", style="bold white")
        
        menu.add_row("1", "Restart NetworkManager (Fixes connection freezes)")
        menu.add_row("2", "Unblock WiFi (Fixes soft-blocked / disabled WiFi)")
        menu.add_row("3", "Enable wireless adapters (Brings up wlan0 interfaces)")
        menu.add_row("4", "Reset DNS settings (Fixes 'Connected but no internet' issues)")
        menu.add_row("5", "Complete Network Reset (Runs all repairs in sequence)")
        menu.add_row("6", "Run Diagnostics Again")
        menu.add_row("7", "Exit")
        
        console.print(Panel(menu, border_style="purple"))
        
        choice = console.input("[bold yellow]Choose an option to repair/diagnose (1-7): [/bold yellow]").strip()
        
        if choice in ["1", "2", "3", "4", "5"]:
            success = apply_fix(choice, status)
            if success:
                console.print("[green]✔ Fix applied. Running diagnostics again...[/green]")
                time.sleep(1.5)
            else:
                console.print("[red]❌ Could not apply fix. Check permissions or logs.[/red]")
                console.input("\nPress Enter to continue...")
        elif choice == "6":
            console.print("[yellow]Running diagnostic checks...[/yellow]")
            time.sleep(1)
        elif choice == "7":
            console.print("[green]Exiting NeeWiFi. Have a nice day![/green]")
            sys.exit(0)
        else:
            console.print("[bold red]Invalid option. Choose between 1 and 7.[/bold red]")
            time.sleep(1.5)

if __name__ == "__main__":
    main()
