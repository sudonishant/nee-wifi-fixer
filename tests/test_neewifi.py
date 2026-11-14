import subprocess
import unittest
from unittest.mock import patch

import neewifi


class RunCommandTests(unittest.TestCase):
    def test_run_cmd_disables_shell_and_preserves_metacharacters_as_one_argument(self):
        args = ["ip", "link", "set", "wlan0;id", "up"]
        completed = subprocess.CompletedProcess(args=args, returncode=0, stdout="ok\n", stderr="")

        with patch.object(neewifi.subprocess, "run", return_value=completed) as run:
            result = neewifi.run_cmd(args)

        self.assertEqual(result, (0, "ok", ""))
        run.assert_called_once_with(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=8,
        )

    def test_auto_repair_passes_interface_name_as_single_argv_element(self):
        status = {
            "soft_blocked": False,
            "nm_active": True,
            "adapters": [{"interface": "wlan0;id", "state": "DOWN"}],
            "internet": True,
            "dns": True,
        }

        with patch.object(neewifi, "is_root", return_value=True), \
                patch.object(neewifi, "run_cmd") as run, \
                patch.object(neewifi.time, "sleep"), \
                patch.object(neewifi.console, "print"):
            neewifi.apply_auto_repair(status)

        run.assert_called_once_with(["ip", "link", "set", "wlan0;id", "up"])


class PipelineReplacementTests(unittest.TestCase):
    def test_gateway_lookup_keeps_first_default_route_match(self):
        routes = (
            "default via 192.0.2.1 dev wlan0\n"
            "default via 192.0.2.2 dev wlan1\n"
            "192.0.2.0/24 dev wlan0 proto kernel\n"
        )

        with patch.object(neewifi, "run_cmd", return_value=(1, routes, "")) as run:
            gateway = neewifi.get_gateway_ip()

        self.assertEqual(gateway, "192.0.2.1")
        run.assert_called_once_with(["ip", "route", "show"])

    def test_log_lookup_filters_case_insensitively_and_keeps_last_twelve_matches(self):
        lines = [f"noise {index}" for index in range(4)]
        lines.extend(f"WiFi firmware event {index}" for index in range(13))
        output = "\n".join(lines)

        with patch.object(neewifi, "run_cmd", return_value=(0, output, "")) as run, \
                patch.object(neewifi, "Panel", side_effect=lambda body, **_: body), \
                patch.object(neewifi.console, "print") as print_console:
            neewifi.view_system_logs()

        run.assert_called_once_with(["dmesg"])
        shown_body = print_console.call_args_list[-1].args[0]
        self.assertEqual(
            shown_body.splitlines(),
            [f"WiFi firmware event {index}" for index in range(1, 13)],
        )


if __name__ == "__main__":
    unittest.main()
