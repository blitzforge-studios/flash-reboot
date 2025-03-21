# Flash Debugger

> Thanks to **cold.ic** for giving us the Flash debugger files.

It works with FlashPoint. Make sure to drop this exe file into the directory:

```sh
FPSoftware\Flash\
```

And replace the launch command with:

```sh
FPSoftware\Flash\flashplayer32_0r0_465_sa_debug.exe
```

Also make sure to drop `mm.cfg` in **`%USERPROFILE%`** directory as that turns on debugging in Flash.

Then, read the logs in real time with PowerShell:

```sh
get-content "$env:APPDATA\Macromedia\Flash Player\Logs\flashlog.txt" -wait -tail 1
```
