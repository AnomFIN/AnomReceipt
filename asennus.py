#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import queue
import shutil
from pathlib import Path
import re

# Optional deps for web scraping
try:
    import requests
    from bs4 import BeautifulSoup
    import yaml
except Exception:
    requests = None
    BeautifulSoup = None
    yaml = None

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

    def install_cli_command(self, python: Path):
        """Install kuittikones command for current user (~/.local/bin). Root also installs to /usr/local/bin."""
        try:
            self.log("[INFO] Valmistellaan 'kuittikones' komento…")
            # Install editable package to generate console_script in venv
            for line in run_stream([str(python), "-m", "pip", "install", "-e", str(ROOT)]):
                self.log(line)
            # Create user-level wrapper
            home = Path.home()
            local_bin = home / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            wrapper = local_bin / "kuittikones"
            content = (
                "#!/usr/bin/env bash\n"
                f"PY=\"{python}\"\n"
                f"exec \"$PY\" \"{MAIN_FILE}\" \"$@\"\n"
            )
            wrapper.write_text(content, encoding="utf-8")
            os.chmod(wrapper, 0o755)
            self.log(f"[OK] Asennettu käyttäjäkohtainen komento: {wrapper}")
            # Try system-wide if root
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                target = "/usr/local/bin/kuittikones"
                for line in run_stream(["bash", "-lc", f"install -m 755 '{wrapper}' '{target}' && which kuittikones || true"]):
                    self.log(line)
                self.log("[OK] Järjestelmälaajuinen komento asennettu.")
            else:
                self.log("[HINT] Lisää ~/.local/bin PATHiin, jos komento ei toimi heti.")
        except Exception as e:
            self.log(f"[WARN] Komennon asennus epäonnistui: {e}")

    def run(self):
        try:
            if self.use_venv:
                python = self.ensure_venv()
            else:
                python = Path(sys.executable)
                self.log(f"[INFO] Käytetään järjestelmän Pythonia: {python}")

            self.install_requirements(python)
            # Install kuittikones command for convenience
            self.install_cli_command(python)
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

        # Global command install row
        cmd_row = ttk.Frame(container)
        cmd_row.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(cmd_row, text="Komento:").pack(side=tk.LEFT)
        self.btn_cli = ttk.Button(cmd_row, text="Asenna 'kuittikones' komento", command=self.install_command)
        self.btn_cli.pack(side=tk.LEFT, padx=(8, 0))

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

        # Store setup (optional)
        store = ttk.LabelFrame(container, text="Myymälätiedot (valinnainen)")
        store.pack(fill=tk.X, padx=0, pady=(10, 0))
        row = ttk.Frame(store)
        row.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(row, text="Ketju:").pack(side=tk.LEFT)
        self.chain_var = tk.StringVar(value="Puuilo")
        self.chain_combo = ttk.Combobox(row, textvariable=self.chain_var, values=["Puuilo", "Tokmanni", "Motonet"], width=20)
        self.chain_combo.pack(side=tk.LEFT, padx=(6, 12))
        ttk.Label(row, text="Alue (posti/paikka):").pack(side=tk.LEFT)
        self.loc_var = tk.StringVar()
        self.loc_entry = ttk.Entry(row, textvariable=self.loc_var, width=24)
        self.loc_entry.pack(side=tk.LEFT, padx=(6, 12))
        self.btn_store_fetch = ttk.Button(row, text="Hae lähin + aukiolo", command=self.fetch_store_info)
        self.btn_store_fetch.pack(side=tk.LEFT)

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

    # --- Store info fetching (optional) ---
    def fetch_store_info(self):
        if not requests or not BeautifulSoup or not yaml:
            messagebox.showwarning("Puuttuu riippuvuuksia", "requests/beautifulsoup4/pyyaml tarvitaan tähän.")
            return
        chain = (self.chain_var.get() or "").strip()
        area = (self.loc_var.get() or "").strip()
        if not chain:
            messagebox.showwarning("Virhe", "Valitse ketju")
            return
        self.btn_store_fetch.configure(state=tk.DISABLED)
        self.status_var.set("Haetaan myymälää ja aukioloaikoja…")

        def worker():
            try:
                info = self._query_store(chain, area)
                if info:
                    self._apply_store_info(chain, info)
                    self.log("[OK] Myymälätiedot tallennettu.")
                else:
                    self.log("[WARN] Myymälätietoja ei löytynyt.")
            except Exception as e:
                self.log(f"[ERROR] Myymälähaku epäonnistui: {e}")
            finally:
                self.after(0, lambda: self.btn_store_fetch.configure(state=tk.NORMAL))
                self.after(0, lambda: self.status_var.set("Valmis aloittamaan."))

        threading.Thread(target=worker, daemon=True).start()

    def _query_store(self, chain: str, area: str) -> dict:
        # Try chain-specific pages first
        chain_l = chain.lower()
        sources = []
        if 'puuilo' in chain_l:
            sources = ['https://www.puuilo.fi/myymalat', 'https://www.puuilo.fi/yhteystiedot']
        elif 'tokmanni' in chain_l:
            sources = ['https://www.tokmanni.fi/myymalat', 'https://www.tokmanni.fi/yhteystiedot']
        elif 'motonet' in chain_l:
            sources = ['https://www.motonet.fi/kaupat', 'https://www.motonet.fi/yritys']

        headers = {'User-Agent': 'AnomReceipt/1.0 (installer)'}
        def scrape_opening_hours(text: str) -> list:
            lines = []
            # Find section around keywords
            # Extract lines with weekday names and times
            wk = r"(ma|ti|ke|to|pe|la|su|mon|tue|wed|thu|fri|sat|sun)"
            for m in re.finditer(wk + r"[^\n]{0,40}?\d{1,2}[:\.]?\d{0,2}\s?-\s?\d{1,2}[:\.]?\d{0,2}", text, flags=re.IGNORECASE):
                seg = m.group(0)
                # Normalize separators
                seg = seg.replace('.', ':')
                lines.append(seg)
            return lines[:7]

        def geocode(q: str):
            try:
                r = requests.get('https://nominatim.openstreetmap.org/search', params={'format':'json','q':q,'limit':1,'countrycodes':'fi'}, headers=headers, timeout=10)
                if r.status_code == 200 and r.json():
                    return float(r.json()[0]['lat']), float(r.json()[0]['lon'])
            except Exception:
                return None
            return None

        def hav(lat1, lon1, lat2, lon2):
            from math import radians, sin, cos, sqrt, atan2
            R = 6371000.0
            dphi = radians(lat2-lat1)
            dl = radians(lon2-lon1)
            a = sin(dphi/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dl/2)**2
            return 2*R*atan2(sqrt(a), sqrt(1-a))

        target = geocode(area) if area else None
        best = None
        for url in sources:
            try:
                rr = requests.get(url, headers=headers, timeout=12)
                if rr.status_code != 200:
                    continue
                soup = BeautifulSoup(rr.text, 'html.parser')
                txt = '\n'.join(x.get_text(' ', strip=True) for x in soup.find_all(['p','li','div','span','a']))
                # collect possible store entries with postal code
                matches = re.findall(r'([A-Za-zÅÄÖåäö0-9\-\. ]+?)\s(\d{5})\s+([A-Za-zÅÄÖåäö\- ]+)', txt)
                if not matches:
                    continue
                for m in matches:
                    address = m[0].strip()
                    postcode = m[1].strip()
                    city = m[2].strip()
                    phone_m = re.search(r'(\+358\s?\d[\d\s\-]{5,15}|0\d[\d\s\-]{5,15})', txt)
                    phone = phone_m.group(0) if phone_m else ''
                    hours_list = scrape_opening_hours(txt)
                    store_q = ' '.join([address, postcode, city, 'Suomi'])
                    if target:
                        pos = geocode(store_q)
                        dist = hav(target[0], target[1], pos[0], pos[1]) if pos else 1e12
                    else:
                        dist = 0
                    cand = {'address': address, 'city': f"{postcode} {city}", 'phone': phone, 'opening_hours': hours_list, 'dist': dist}
                    if not best or cand['dist'] < best['dist']:
                        best = cand
                if best:
                    break
            except Exception:
                continue
        # Fallback: Overpass OSM
        if not best and area:
            try:
                target = target or geocode(area)
                if target:
                    lat, lon = target
                    radius = 50000
                    chain_q = chain
                    q = f"""
                    [out:json][timeout:25];
                    (
                      node["name"~"{chain_q}",i](around:{radius},{lat},{lon});
                      way["name"~"{chain_q}",i](around:{radius},{lat},{lon});
                      relation["name"~"{chain_q}",i](around:{radius},{lat},{lon});
                    );
                    out center tags;
                    """
                    r = requests.post('https://overpass-api.de/api/interpreter', data=q.encode('utf-8'), headers=headers, timeout=25)
                    if r.status_code == 200:
                        data = r.json().get('elements', [])
                        near = None
                        for e in data:
                            tags = e.get('tags', {})
                            if not tags:
                                continue
                            clat = e.get('lat') or (e.get('center') or {}).get('lat')
                            clon = e.get('lon') or (e.get('center') or {}).get('lon')
                            if not (clat and clon):
                                continue
                            dist = hav(lat, lon, float(clat), float(clon))
                            if not near or dist < near['dist']:
                                near = {'address': tags.get('addr:street',''),
                                        'city': ' '.join([tags.get('addr:postcode',''), tags.get('addr:city','')]).strip(),
                                        'phone': tags.get('contact:phone') or tags.get('phone') or '',
                                        'opening_hours': [tags.get('opening_hours')] if tags.get('opening_hours') else [],
                                        'dist': dist}
                        best = near
            except Exception:
                pass
        if best:
            return {k:v for k,v in best.items() if k in ('address','city','phone','opening_hours')}
        return {}

    def _apply_store_info(self, chain: str, info: dict):
        # Persist to YAML template if exists
        chain_map = {
            'puuilo': ROOT / 'templates' / 'companies' / 'puuilo.yaml',
            'tokmanni': ROOT / 'templates' / 'companies' / 'tokmanni.yaml',
            'motonet': ROOT / 'templates' / 'companies' / 'motonet.yaml',
        }
        path = chain_map.get(chain.lower())
        if not path or not path.exists():
            self.log("[WARN] Ketjun template-tiedostoa ei löytynyt, ohitetaan tallennus.")
            return
        try:
            data = yaml.safe_load(path.read_text(encoding='utf-8'))
            ci = data.get('company_info', {})
            if info.get('address'): ci['address'] = info['address']
            if info.get('city'): ci['city'] = info['city']
            if info.get('phone'): ci['phone'] = info['phone']
            if info.get('opening_hours'):
                ci['opening_hours'] = info['opening_hours']
            data['company_info'] = ci
            path.write_text(yaml.dump(data, allow_unicode=True, default_flow_style=False), encoding='utf-8')
            self.log(f"[OK] Päivitetty {path}")
        except Exception as e:
            self.log(f"[ERROR] YAML-tallennus epäonnistui: {e}")

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

    def install_command(self):
        """Install kuittikones command into /usr/local/bin by symlinking venv script or writing wrapper."""
        # Ensure venv exists and package is installed so console_script is generated
        try:
            python = which_python_in_venv(VENV_DIR) if which_python_in_venv(VENV_DIR).exists() else Path(sys.executable)
            # install editable to produce console script in venv
            self.log("[INFO] Asennetaan paketti (editable) .venv:iin…")
            for line in run_stream([str(python), "-m", "pip", "install", "-e", str(ROOT)]):
                self.log(line)
            # Determine source executable
            bin_path = VENV_DIR / ("Scripts" if os.name == "nt" else "bin")
            src = bin_path / ("kuittikones.exe" if os.name == "nt" else "kuittikones")
            if not src.exists():
                self.log(f"[WARN] Ei löytynyt {src}. Luodaan wrapper.")
                # Create wrapper in project
                wrapper = ROOT / "kuittikones"
                content = (
                    "#!/usr/bin/env bash\n"
                    f"'{python}' '{MAIN_FILE}' \n"
                )
                wrapper.write_text(content, encoding="utf-8")
                os.chmod(wrapper, 0o755)
                src = wrapper
            # Install to /usr/local/bin
            target = "/usr/local/bin/kuittikones"
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                cmd = f"install -m 755 '{src}' '{target}'"
                for line in run_stream(["bash", "-lc", cmd]):
                    self.log(line)
                messagebox.showinfo("Valmis", "Komento 'kuittikones' asennettu.")
                return
            if shutil.which("pkexec"):
                self.log("[INFO] Yritetään pkexec-korotusta komennon asentamiseen…")
                cmd = f"install -m 755 '{src}' '{target}'"
                for line in run_stream(["pkexec", "bash", "-lc", cmd]):
                    self.log(line)
                messagebox.showinfo("Valmis", "Komento 'kuittikones' asennettu.")
                return
            # Fallback instructions
            instr = (
                "Aja terminaalissa root-oikeuksilla:\n\n"
                f"sudo install -m 755 '{src}' '{target}'\n"
            )
            try:
                self.clipboard_clear()
                self.clipboard_append(f"sudo install -m 755 '{src}' '{target}'")
            except Exception:
                pass
            messagebox.showinfo("Ohje", instr)
        except Exception as e:
            messagebox.showerror("Virhe", f"Komennon asennus epäonnistui: {e}")


def main():
    # Ensure sane runtime dir for Qt when run as root
    if not os.environ.get('XDG_RUNTIME_DIR'):
        os.environ['XDG_RUNTIME_DIR'] = f"/tmp/runtime-{os.getuid()}"
        try:
            os.makedirs(os.environ['XDG_RUNTIME_DIR'], exist_ok=True)
        except Exception:
            pass
    # Informative: ensure we're in project root
    os.chdir(ROOT)
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
