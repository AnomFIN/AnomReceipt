#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import queue
import shutil
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception as e:
    print("Tkinter ei ole käytettävissä: ", e)
    sys.exit(1)


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"
REQ_FILE = ROOT / "requirements.txt"
MAIN_FILE = ROOT / "main.py"


def which_python_in_venv(venv_dir: Path) -> Path:
    if os.name == "nt":
        cand = venv_dir / "Scripts" / "python.exe"
    else:
        cand = venv_dir / "bin" / "python"
    return cand


def which_pip_in_venv(venv_dir: Path) -> Path:
    if os.name == "nt":
        cand = venv_dir / "Scripts" / "pip.exe"
    else:
        cand = venv_dir / "bin" / "pip"
    return cand


def run_stream(cmd, cwd=None, env=None):
    """Run a command and yield lines of combined stdout/stderr."""
    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    assert process.stdout is not None
    for line in process.stdout:
        yield line.rstrip("\n")
    rc = process.wait()
    if rc != 0:
        raise subprocess.CalledProcessError(rc, cmd)


class InstallerThread(threading.Thread):
    def __init__(self, use_venv: bool, log_q: queue.Queue, auto_run: bool = True):
        super().__init__(daemon=True)
        self.use_venv = use_venv
        self.log_q = log_q
        self.auto_run = auto_run
        self.error = None

    def log(self, msg: str):
        self.log_q.put(msg)

    def ensure_venv(self) -> Path:
        self.log("[INFO] Luodaan virtuaaliympäristö (.venv) jos tarpeen…")
        py = which_python_in_venv(VENV_DIR)
        if not py.exists():
            # Create venv
            self.log("[RUN] python -m venv .venv")
            for line in run_stream([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=str(ROOT)):
                self.log(line)
        else:
            self.log("[OK] .venv löytyi, käytetään olemassaolevaa.")
        # Re-check
        py = which_python_in_venv(VENV_DIR)
        if not py.exists():
            raise RuntimeError(".venv ei ole käytettävissä/onnistunut.")
        return py

    def pip_path(self, venv_dir: Path) -> Path:
        pip = which_pip_in_venv(venv_dir)
        if not pip.exists():
            # Try python -m pip
            return None
        return pip

    def pip_run(self, python: Path, args):
        cmd = [str(python), "-m", "pip"] + list(args)
        self.log(f"[RUN] {' '.join(cmd)}")
        for line in run_stream(cmd, cwd=str(ROOT)):
            self.log(line)

    def install_requirements(self, python: Path):
        # Upgrade pip first
        self.log("[INFO] Päivitetään pip…")
        self.pip_run(python, ["install", "--upgrade", "pip", "setuptools", "wheel"]) 

        if REQ_FILE.exists():
            self.log("[INFO] Asennetaan riippuvuudet requirements.txt:stä…")
            self.pip_run(python, ["install", "-r", str(REQ_FILE)])
        else:
            self.log("[WARN] requirements.txt puuttuu, ohitetaan riippuvuuksien asennus.")

        # Validate with pip check
        self.log("[INFO] Tarkistetaan ympäristö (pip check)…")
        try:
            self.pip_run(python, ["check"])  # Ensures deps resolve
        except subprocess.CalledProcessError:
            self.log("[WARN] pip check raportoi ongelmia, jatketaan kuitenkin.")

        # Optional: verify USB-tulostuksen backendit
        try:
            self.log("[INFO] Tarkistetaan USB-tulostuksen riippuvuudet…")
            # Check PyUSB
            for line in run_stream([str(python), "-c", "import usb, sys; print('PyUSB OK')"]):
                self.log(line)
        except Exception:
            self.log("[WARN] PyUSB puuttuu tai ei lataudu. Yritetään asentaa pyusb…")
            try:
                self.pip_run(python, ["install", "pyusb>=1.2.1"]) 
            except Exception as e:
                self.log(f"[WARN] pyusb asennus epäonnistui: {e}")
        # Libusb presence hint (best-effort)
        if os.name != "nt":
            try:
                # Try to load via python to hint availability
                code = (
                    "import ctypes;\n"
                    "import ctypes.util;\n"
                    "lib = ctypes.util.find_library('usb-1.0');\n"
                    "print('libusb-1.0:', bool(lib), lib)\n"
                )
                for line in run_stream([str(python), "-c", code]):
                    self.log(line)
            except Exception:
                pass
            self.log("[HINT] Jos USB-tulostus ei toimi, asenna järjestelmäpaketit: 'sudo apt-get install libusb-1.0-0' ja tarvittaessa udev-säännöt laitteelle.")

    def run_main(self, python: Path):
        if not MAIN_FILE.exists():
            raise RuntimeError("main.py puuttuu projektin juuresta.")
        self.log("[INFO] Käynnistetään sovellus: main.py…")
        # Inherit current env; ensure working directory is project root
        # Use a new process detached so installer UI can close
        creationflags = 0
        kwargs = {}
        if os.name == "nt":
            creationflags = 0x00000008  # CREATE_NEW_CONSOLE
            kwargs["creationflags"] = creationflags
        # Start the app
        subprocess.Popen([str(python), str(MAIN_FILE)], cwd=str(ROOT), **kwargs)
        self.log("[OK] Sovellus käynnistetty.")

    def run(self):
        try:
            if self.use_venv:
                python = self.ensure_venv()
            else:
                python = Path(sys.executable)
                self.log(f"[INFO] Käytetään järjestelmän Pythonia: {python}")

            self.install_requirements(python)
            self.run_main(python)
            self.log("[DONE] Valmis.")
        except Exception as e:
            self.error = e
            self.log(f"[ERROR] {e}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asennus – AnomReceipt")
        self.geometry("800x480")
        self.minsize(640, 360)

        # State
        self.log_q: queue.Queue[str] = queue.Queue()
        self.worker: InstallerThread | None = None

        # UI
        self._build_ui()

        # Auto-start: use .venv by default (create if missing)
        self.after(200, self.start_install_automatically)

    def _build_ui(self):
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Options row
        opts = ttk.Frame(container)
        opts.pack(fill=tk.X, pady=(0, 8))

        self.use_venv_var = tk.BooleanVar(value=True)
        self.chk_venv = ttk.Checkbutton(
            opts,
            text="Luo ja käytä .venv-ympäristöä",
            variable=self.use_venv_var,
        )
        self.chk_venv.pack(side=tk.LEFT)

        self.btn_start = ttk.Button(opts, text="Käynnistä asennus", command=self.start_install)
        self.btn_start.pack(side=tk.LEFT, padx=(8, 0))

        self.btn_cancel = ttk.Button(opts, text="Keskeytä", command=self.cancel_install, state=tk.DISABLED)
        self.btn_cancel.pack(side=tk.LEFT, padx=(8, 0))

        # USB help row
        usb_row = ttk.Frame(container)
        usb_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(usb_row, text="USB-tuki:").pack(side=tk.LEFT)
        self.btn_udev = ttk.Button(usb_row, text="Asenna udev-sääntö (Epson USB)", command=self.install_udev_rule)
        self.btn_udev.pack(side=tk.LEFT, padx=(8, 0))
        self.btn_libusb = ttk.Button(usb_row, text="Asenna libusb (järjestelmä)", command=self.install_libusb)
        self.btn_libusb.pack(side=tk.LEFT, padx=(8, 0))

        # Log area
        log_frame = ttk.Frame(container)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.txt = tk.Text(log_frame, wrap=tk.NONE, state=tk.DISABLED, height=20)
        self.txt.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        yscroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.txt.yview)
        yscroll.pack(fill=tk.Y, side=tk.RIGHT)
        self.txt.configure(yscrollcommand=yscroll.set)

        # Footer
        self.status_var = tk.StringVar(value="Valmis aloittamaan.")
        status = ttk.Label(container, textvariable=self.status_var)
        status.pack(fill=tk.X, pady=(8, 0))

    def log(self, line: str):
        self.txt.configure(state=tk.NORMAL)
        self.txt.insert(tk.END, line + "\n")
        self.txt.see(tk.END)
        self.txt.configure(state=tk.DISABLED)

    def poll_logs(self):
        try:
            while True:
                line = self.log_q.get_nowait()
                self.log(line)
        except queue.Empty:
            pass
        # Re-schedule if worker alive
        if self.worker and self.worker.is_alive():
            self.after(100, self.poll_logs)
        else:
            # Final drain
            try:
                while True:
                    line = self.log_q.get_nowait()
                    self.log(line)
            except queue.Empty:
                pass
            self.btn_start.configure(state=tk.NORMAL)
            self.btn_cancel.configure(state=tk.DISABLED)
            self.chk_venv.configure(state=tk.NORMAL)
            if self.worker and self.worker.error:
                self.status_var.set("Virhe asennuksessa. Tarkista loki.")
                messagebox.showerror("Virhe", f"Asennus epäonnistui:\n{self.worker.error}")
            else:
                self.status_var.set("Valmis. Sovellus käynnistetty taustalla.")

    def start_install_automatically(self):
        # If user hasn't started yet, auto-start for automation
        if self.btn_start["state"] == tk.NORMAL:
            self.start_install()

    def start_install(self):
        # Disable UI while running
        self.btn_start.configure(state=tk.DISABLED)
        self.btn_cancel.configure(state=tk.NORMAL)
        self.chk_venv.configure(state=tk.DISABLED)
        self.status_var.set("Asennus käynnissä…")

        use_venv = self.use_venv_var.get()
        # If .venv exists, keep checkbox checked automatically
        if which_python_in_venv(VENV_DIR).exists():
            self.use_venv_var.set(True)
            use_venv = True

        self.worker = InstallerThread(use_venv=use_venv, log_q=self.log_q)
        self.worker.start()
        self.after(100, self.poll_logs)

    def cancel_install(self):
        # Best-effort cancel: not trivial to kill subprocess tree portably.
        # We just notify the user; they can close window. Keeping simple to avoid extra deps.
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(
                "Ei tuettu",
                "Keskeytys ei ole täysin tuettu. Voit sulkea ikkunan tarvittaessa.",
            )

    def install_udev_rule(self):
        # Only relevant on Linux
        if os.name == "nt":
            messagebox.showinfo("Ei tuettu", "udev-säännöt koskevat vain Linuxia.")
            return

        rule_content = (
            "# ESC/POS Epson USB printers\n"
            "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"04b8\", MODE=\"0666\"\n"
            "# Optional specific TM-T70II product id\n"
            "SUBSYSTEM==\"usb\", ATTR{idVendor}==\"04b8\", ATTR{idProduct}==\"0202\", MODE=\"0666\"\n"
        )

        # Write temp rule file
        tmp_path = ROOT / "99-escpos-epson.rules"
        try:
            tmp_path.write_text(rule_content, encoding="utf-8")
        except Exception as e:
            messagebox.showerror("Virhe", f"Väliaikaisen sääntö-tiedoston luonti epäonnistui: {e}")
            return

        target = "/etc/udev/rules.d/99-escpos-epson.rules"
        cmd = f"install -m 644 '{tmp_path}' '{target}' && udevadm control --reload-rules && udevadm trigger"

        def log_run(cmd_list):
            try:
                for line in run_stream(cmd_list):
                    self.log(line)
                return True
            except Exception as e:
                self.log(f"[ERROR] {e}")
                return False

        # If root, do it directly
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.log("[INFO] Asennetaan udev-sääntö root-oikeuksilla…")
            ok = log_run(["bash", "-lc", cmd])
            if ok:
                self.status_var.set("udev-sääntö asennettu. Irrota ja liitä USB uudelleen.")
                messagebox.showinfo("Valmis", "udev-sääntö asennettu. Irrota ja liitä USB-kaapeli uudelleen.")
            else:
                messagebox.showerror("Virhe", "udev-säännön asennus epäonnistui. Katso loki.")
            return

        # Try pkexec for GUI elevation
        if shutil.which("pkexec"):
            self.log("[INFO] Yritetään pkexec-korotusta udev-säännön asentamiseksi…")
            ok = log_run(["pkexec", "bash", "-lc", cmd])
            if ok:
                self.status_var.set("udev-sääntö asennettu. Irrota ja liitä USB uudelleen.")
                messagebox.showinfo("Valmis", "udev-sääntö asennettu. Irrota ja liitä USB-kaapeli uudelleen.")
                return
            else:
                self.log("[WARN] pkexec epäonnistui tai peruttiin.")

        # Fallback: show instructions
        instr = (
            "Käynnistä terminaalissa seuraava komento root-oikeuksilla:\n\n"
            f"sudo bash -lc \"{cmd}\"\n\n"
            "Tämän jälkeen irrota ja liitä USB-kaapeli uudelleen."
        )
        try:
            self.clipboard_clear()
            self.clipboard_append(f"sudo bash -lc \"{cmd}\"")
        except Exception:
            pass
        messagebox.showinfo("Ohje", instr)

    def install_libusb(self):
        # Linux only
        if os.name == "nt":
            messagebox.showinfo("Ei tuettu", "libusb-asennus koskee vain Linuxia.")
            return
        self.log("[INFO] Asennetaan libusb-1.0-0…")

        def log_run(cmd_list):
            try:
                for line in run_stream(cmd_list):
                    self.log(line)
                return True
            except Exception as e:
                self.log(f"[ERROR] {e}")
                return False

        cmd = "apt-get update && apt-get install -y libusb-1.0-0"

        if hasattr(os, "geteuid") and os.geteuid() == 0:
            ok = log_run(["bash", "-lc", cmd])
            if ok:
                self.status_var.set("libusb asennettu.")
                messagebox.showinfo("Valmis", "libusb asennettu.")
            else:
                messagebox.showerror("Virhe", "libusb-asennus epäonnistui. Katso loki.")
            return

        if shutil.which("pkexec"):
            self.log("[INFO] Yritetään pkexec-korotusta libusb-asennukseen…")
            ok = log_run(["pkexec", "bash", "-lc", cmd])
            if ok:
                self.status_var.set("libusb asennettu.")
                messagebox.showinfo("Valmis", "libusb asennettu.")
                return
            else:
                self.log("[WARN] pkexec epäonnistui tai peruttiin.")

        instr = (
            "Aja terminaalissa yksi rivi:\n\n"
            "sudo bash -lc 'apt-get update && apt-get install -y libusb-1.0-0'"
        )
        try:
            self.clipboard_clear()
            self.clipboard_append("sudo bash -lc 'apt-get update && apt-get install -y libusb-1.0-0'")
        except Exception:
            pass
        messagebox.showinfo("Ohje", instr)


def main():
    # Informative: ensure we're in project root
    os.chdir(ROOT)
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
