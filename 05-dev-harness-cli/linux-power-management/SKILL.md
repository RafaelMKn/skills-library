---
name: linux-power-management
description: "Use when diagnosing Linux power, heat, fan, or CPU."
version: 1.0.0
metadata:
  hermes:
    tags: [linux, power, thermal, cpu, laptop, tuned, ryzenadj]
    category: linux
---

# Linux power management

Diagnose excessive fan noise, temperature, consumption, battery drain, or unexpected performance modes without confusing live demand with configured limits.

## Workflow

1. **Identify hardware and the active policy before interpreting symptoms.** Read `hostnamectl`, `lscpu`, the CPU scaling driver/governor, energy-performance preference, AMD P-State mode, ACPI platform profile, and the active TuneD or power-profiles-daemon profile.

   Useful probes:

   ```bash
   hostnamectl
   lscpu
   tuned-adm active
   tuned-adm recommend
   systemctl is-active tuned tuned-ppd power-profiles-daemon auto-cpufreq tlp.service
   ```

   Read these files when present:

   ```text
   /sys/devices/system/cpu/cpufreq/policy0/scaling_driver
   /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
   /sys/devices/system/cpu/cpufreq/policy0/energy_performance_preference
   /sys/devices/system/cpu/amd_pstate/status
   /sys/firmware/acpi/platform_profile
   ```

2. **Measure live demand separately from policy.** Capture `uptime`, processes sorted by CPU, per-core clocks, and `sensors`. Report load, CPU/GPU temperature, package power, and the actual processes consuming CPU. A loud fan under Steam, Wine, browsers, builds, or agent subprocesses is not evidence that a power profile alone is faulty.

   Do not treat a sensor's instantaneous `PPT` reading as a configured wattage cap. Label it as current package power; obtain configured limits from the controlling tool or its configuration.

3. **Inventory every power-management layer.** Check TuneD, power-profiles-daemon, TLP, auto-cpufreq, `cpupower`, custom Systemd units/timers, sleep hooks, udev power-supply rules, and manually installed binaries. Use `systemctl show <unit> -p FragmentPath -p UnitFileState -p ActiveState -p ExecStart` to locate the real implementation, then read the files with `read_file`.

4. **Reconstruct manual changes from durable evidence.** Search shell history for the relevant tool names and inspect script files referenced there. Compare installation scripts, live unit files, timer cadence, configuration values, and journal execution. Shell history proves commands were entered; live files and service state prove what persists now.

5. **For RyzenAdj systems, load [references/amd-ryzenadj.md](references/amd-ryzenadj.md).** Inspect configured STAPM/FAST/SLOW/APU limits, temperature ceiling, `--max-performance`, module state, and all reapplication triggers. Run `ryzenadj --info` only with sufficient privileges; if noninteractive `sudo` requires a password, report the readback as unverified rather than inferring it from a successful oneshot service.

6. **Explain the diagnosis before modifying root-owned state.** Separate:
   - configured sustained and burst limits;
   - current measured package power;
   - CPU governor/EPP policy;
   - workload-driven heat;
   - persistence mechanisms that will overwrite a temporary adjustment.

7. **Confirm the rollback target.** Distinguish between restoring vendor defaults, keeping a lower custom cap, or only selecting `balanced`/`power-saver`. Back up exact custom configs and hooks before edits. Root-level power changes require explicit scope confirmation because an incomplete rollback can leave conflicting controllers active.

8. **Verify after the change and after reboot when firmware defaults matter.** Confirm active profiles, governor/EPP, enabled timers and units, absence or intended presence of sleep/udev triggers, configured tool readback, live temperature/package power, and workload. A command returning zero is not enough when another timer can reapply the old values minutes later.

## Pitfalls

- Inspect processes before blaming the profile — live compilers, browsers, games, Wine, or agents can legitimately hold all cores at boost and keep the fan loud.
- Do not call an instantaneous wattage reading a limit — telemetry reports current draw, while STAPM/FAST/SLOW or firmware settings define ceilings.
- Audit timers, boot units, sleep hooks, and udev rules together — disabling only one trigger lets another silently restore the old override.
- Treat comments such as “factory value” in a custom script as an unverified claim — vendor defaults must come from firmware reset/readback or authoritative hardware documentation.
- Sample again after diagnostic/browser subprocesses settle — the inspection itself can create short-lived CPU spikes that distort a single process snapshot.
- Do not claim RyzenAdj limits were read back when `ryzenadj --info` lacked privileges — configuration files show intent, not necessarily the current SMU state.
