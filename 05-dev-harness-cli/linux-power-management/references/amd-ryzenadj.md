# AMD RyzenAdj inspection and rollback

Load this reference only when RyzenAdj or `ryzen_smu` is present.

## Inspection

1. Locate the binary and determine whether it is package-owned:

   ```bash
   command -v ryzenadj
   rpm -qf "$(command -v ryzenadj)"
   stat "$(command -v ryzenadj)"
   lsmod
   modinfo ryzen_smu
   ```

2. Discover persistence rather than assuming a one-time command:

   ```bash
   systemctl list-unit-files --type=service --no-pager
   systemctl list-timers --all --no-pager
   systemctl show ryzenadj.service -p FragmentPath -p UnitFileState -p ActiveState -p ExecStart
   journalctl -u ryzenadj.service -b --no-pager
   ```

   From each `FragmentPath` and `ExecStart`, read the unit, wrapper, and sourced configuration. Also inspect likely timer units, `/usr/lib/systemd/system-sleep/`, and `/etc/udev/rules.d/` for references to RyzenAdj.

3. Record each limit independently:

   - `STAPM`: sustained package-power target;
   - `FAST`: short burst limit;
   - `SLOW`: longer burst/average limit;
   - `APU_SLOW`: APU limit;
   - `Tctl`: thermal ceiling;
   - performance flags such as `--max-performance`.

   Values passed to RyzenAdj are commonly milliwatts, while wrapper configs may store watts and multiply by 1000. Preserve the unit conversion exactly.

4. Read live SMU settings with privileges:

   ```bash
   sudo ryzenadj --info
   ```

   Do not prompt for or guess a password. If unattended `sudo -n` fails, state that live SMU readback remains unverified.

## Rollback decision table

| Goal | Action |
|---|---|
| Restore firmware/vendor behavior | Stop and disable every RyzenAdj service/timer, remove or disable all boot/sleep/udev reapplication hooks, then reboot. Keep a backup of configs/scripts until post-reboot verification. |
| Keep RyzenAdj with quieter limits | Edit the single source configuration, apply once, read back with `ryzenadj --info`, and wait beyond the timer interval to prove persistence. |
| Change only scheduler preference | Leave wattage limits unchanged and select the intended TuneD/power profile; verify governor and EPP afterward. |

Prefer an audited installer-provided removal mode when it demonstrably removes every file it created. Read that branch before running it; do not trust the option name alone.

## Verification

After rollback or retuning:

1. Check unit/timer enablement and the timer list.
2. Confirm no remaining sleep or udev hook invokes the apply wrapper.
3. Reboot if the goal is firmware defaults; stopping a oneshot does not undo limits already written into the SMU.
4. Read live limits with `ryzenadj --info` when available.
5. Measure package power, temperatures, clocks, and top CPU consumers under a comparable workload.
6. Wait longer than any former reapplication interval and verify again.
