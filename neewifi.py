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
          [bold cyan]NeeWiFi - Advanced Auto-Diagnostic & Repair v2.0[/bold cyan]
            [dim]A smart interactive troubleshooter for Linux WiFi[/dim]
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

def get_wifi_details():
    """Identify wireless interfaces, their MAC addresses, and active drivers."""
    adapters = []
    if os.path.exists("/sys/class/net"):
        for name in os.listdir("/sys/class/net"):
            # Identify wireless interfaces
            is_wireless = os.path.exists(f"/sys/class/net/{name}/wireless") or name.startswith("wlan") or name.startswith("wlp")
            if is_wireless and name != "lo":
                mac = "Unknown"
                driver = "Unknown"
                state = "DOWN"
                
                # Get MAC Address
                try:
                    with open(f"/sys/class/net/{name}/address", "r") as f:
                        mac = f.read().strip()
                except Exception:
                    pass
                
                # Get Operation State (UP/DOWN)
                try:
                    with open(f"/sys/class/net/{name}/operstate", "r") as f:
                        state = f.read().strip().upper()
                except Exception:
                    pass

                # Get Driver Name from symlink
                driver_path = f"/sys/class/net/{name}/device/driver"
                if os.path.islink(driver_path):
                    driver = os.path.basename(os.readlink(driver_path))
                
                adapters.append({
                    "interface": name,
                    "mac": mac,
                    "driver": driver,
                    "state": state
                })
    return adapters

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

def run_diagnostics():
    """Perform a deep scan and return status reports."""
    adapters = get_wifi_details()
    internet = check_internet()
    dns = check_dns()
    nm_active = check_network_manager()
    soft_block, hard_block = check_rfkill()
    
    return {
        "adapters": adapters,
        "internet": internet,
        "dns": dns,
        "nm_active": nm_active,
        "soft_blocked": soft_block,
        "hard_blocked": hard_block
    }

def print_diagnostics_report(status):
    """Print the detailed diagnostic table."""
    table = Table(title="🔍 System Diagnostic Results", border_style="purple")
    table.add_column("System Check", style="bold cyan")
    table.add_column("Status", justify="center")
    table.add_column("Identified Issue / Status Details")
    
    # Privileges
    root_status = "[green]✔ Root[/green]" if is_root() else "[yellow]⚠ User[/yellow]"
    root_desc = "Root permissions verified" if is_root() else "Running without sudo. Repairs will be blocked."
    table.add_row("Execution Privilege", root_status, root_desc)
    
    # Adapters
    if status["adapters"]:
        adapt_status = "[green]✔ Detected[/green]"
        details = ", ".join([f"{a['interface']} ({a['state']})" for a in status["adapters"]])
        adapt_desc = f"Active interfaces: {details}"
    else:
        adapt_status = "[red]✘ Not Found[/red]"
        adapt_desc = "No physical wireless adapters detected on the system."
    table.add_row("Wireless Hardware", adapt_status, adapt_desc)
    
    # Service
    nm_status = "[green]✔ Running[/green]" if status["nm_active"] else "[red]✘ Stopped[/red]"
    nm_desc = "NetworkManager service is active" if status["nm_active"] else "NetworkManager service is stopped/disabled"
    table.add_row("Network Service", nm_status, nm_desc)
    
    # RF Block
    if status["soft_blocked"]:
        rf_status = "[yellow]⚠ Soft Blocked[/yellow]"
        rf_desc = "WiFi is disabled by software. Needs rfkill unblock."
    elif status["hard_blocked"]:
        rf_status = "[red]✘ Hard Blocked[/red]"
        rf_desc = "WiFi is disabled via hardware switch/button. Toggle switch on laptop."
    else:
        rf_status = "[green]✔ Unblocked[/green]"
        rf_desc = "No software/hardware locks detected."
    table.add_row("RF Block Status", rf_status, rf_desc)
    
    # Internet
    if status["internet"]:
        net_status = "[green]✔ Online[/green]"
        net_desc = "Connection to 8.8.8.8 successful."
    else:
        net_status = "[red]✘ Offline[/red]"
        net_desc = "Cannot ping public IPs. Connection down."
    table.add_row("Internet Link", net_status, net_desc)
    
    # DNS
    if status["dns"]:
        dns_status = "[green]✔ OK[/green]"
        dns_desc = "Nameserver resolution is functional."
    else:
        dns_status = "[red]✘ Failed[/red]"
        dns_desc = "Cannot resolve domain names (Connected but no internet)."
    table.add_row("DNS Resolution", dns_status, dns_desc)
    
    console.print(table)

def show_hardware_details(adapters):
    """Print details about physical wireless adapters (equivalent to image metadata details)."""
    if not adapters:
        console.print("[bold red]No wireless adapters found to display details.[/bold red]")
        return
        
    for index, a in enumerate(adapters):
        table = Table(title=f"📡 Wireless Adapter Metadata [#{index+1}]", border_style="cyan")
        table.add_column("Property", style="bold yellow")
        table.add_column("Value Details")
        
        table.add_row("Interface Name", a["interface"])
        table.add_row("MAC Address (Physical)", a["mac"])
        table.add_row("Kernel Driver In Use", a["driver"])
        table.add_row("Operational State", a["state"])
        table.add_row("Device File Path", f"/sys/class/net/{a['interface']}")
        
        console.print(table)

def apply_auto_repair(status):
    """Analyze diagnostics and automatically apply fixes in sequence."""
    if not is_root():
        console.print("[bold red]Error:[/bold red] Sudo/Root permissions required to run repair actions.")
        return
        
    console.print(Panel("[bold yellow]🔧 Initiating Auto-Repair Sequence[/bold yellow]", border_style="yellow"))
    
    repaired = False
    
    # 1. Fix Soft Blocks
    if status["soft_blocked"]:
        console.print("[yellow][*] Soft block detected. Running 'rfkill unblock all'...[/yellow]")
        run_cmd("rfkill unblock all")
        time.sleep(1)
        repaired = True
        
    # 2. Fix NetworkManager service
    if not status["nm_active"]:
        console.print("[yellow][*] NetworkManager is inactive. Running 'systemctl restart NetworkManager'...[/yellow]")
        run_cmd("systemctl restart NetworkManager")
        time.sleep(2)
        repaired = True

    # 3. Bring interfaces UP
    for a in status["adapters"]:
        if a["state"] != "UP":
            console.print(f"[yellow][*] Interface '{a['interface']}' is down. Bringing it UP...[/yellow]")
            run_cmd(f"ip link set {a['interface']} up")
            time.sleep(1)
            repaired = True

    # 4. Fix DNS if connected but no domain lookup
    if status["internet"] and not status["dns"]:
        console.print("[yellow][*] DNS failure detected. Setting nameservers to 8.8.8.8 and 1.1.1.1...[/yellow]")
        try:
            with open("/etc/resolv.conf", "w") as f:
                f.write("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
            console.print("[green]✔ DNS settings updated.[/green]")
            repaired = True
        except Exception as e:
            console.print(f"[red]Failed to fix DNS: {str(e)}[/red]")

    # 5. Generic Reset if completely offline
    if not status["internet"] and not repaired:
        console.print("[yellow][*] System is offline with no obvious software blocks. Restarting whole network stack...[/yellow]")
        run_cmd("systemctl restart NetworkManager")
        time.sleep(2)
        repaired = True

    if repaired:
        console.print("[bold green]✔ Auto-repair completed. Verifying connection status...[/bold green]")
        time.sleep(1)
    else:
        console.print("[green]✔ No auto-repair needed. No software blocks or connection issues found.[/green]")

def main():
    if not is_root():
        console.print(BANNER)
        console.print("[bold red]⚠ Access Denied:[/bold red] You must run NeeWiFi with sudo (e.g. [bold]sudo python3 neewifi.py[/bold]) to audit and fix WiFi interfaces.")
        sys.exit(1)

    while True:
        console.clear()
        console.print(BANNER)
        
        # 1. Deep Scan Diagnostics
        status = run_diagnostics()
        print_diagnostics_report(status)
        
        # 2. Interactive TUI Menu
        menu = Table(title="⚡ NeeWiFi Control Panel ⚡", border_style="purple", box=None)
        menu.add_column("Option", style="bold magenta", justify="center")
        menu.add_column("Action description", style="bold white")
        
        menu.add_row("1", "🔧 Deep Scan & Auto-Repair (स्कैन करके अपने आप ठीक करें)")
        menu.add_row("2", "📡 View Wireless Card & Driver details (मेटाडेटा देखें)")
        menu.add_row("3", "🔄 Restart NetworkManager (कनेक्शन अटकने पर चलाएं)")
        menu.add_row("4", "🔓 Unblock wireless devices (rfkill unblock)")
        menu.add_row("5", "🌐 Reset DNS Config (Connected but no internet fix)")
        menu.add_row("6", "🔍 Run Diagnostics scan again")
        menu.add_row("7", "❌ Exit Troubleshooter")
        
        console.print(Panel(menu, border_style="purple"))
        
        choice = console.input("[bold yellow]Enter your choice (1-7): [/bold yellow]").strip()
        
        if choice == "1":
            apply_auto_repair(status)
        elif choice == "2":
            show_hardware_details(status["adapters"])
        elif choice == "3":
            console.print("[yellow]Restarting NetworkManager service...[/yellow]")
            run_cmd("systemctl restart NetworkManager")
            time.sleep(2)
        elif choice == "4":
            console.print("[yellow]Unblocking all wireless interfaces...[/yellow]")
            run_cmd("rfkill unblock all")
            time.sleep(1)
        elif choice == "5":
            console.print("[yellow]Updating DNS nameservers...[/yellow]")
            try:
                with open("/etc/resolv.conf", "w") as f:
                    f.write("nameserver 8.8.8.8\nnameserver 1.1.1.1\n")
                console.print("[green]✔ DNS updated successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
        elif choice == "6":
            console.print("[yellow]Refreshing diagnostics...[/yellow]")
            time.sleep(0.5)
        elif choice == "7":
            console.print("[green]Exiting NeeWiFi. Stay connected![/green]")
            sys.exit(0)
        else:
            console.print("[bold red]Invalid choice. Choose between 1 and 7.[/bold red]")
            time.sleep(1.5)
            
        console.input("\n[dim]Press Enter to continue...[/dim]")

if __name__ == "__main__":
    main()
Px
