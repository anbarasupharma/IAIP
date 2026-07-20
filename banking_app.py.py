import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
class OnlineBankingSystem(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("ShieldPharma Finance – Corporate Banking")
        self.geometry("950x620")
        self.resizable(False, False)

        # ── Cross-platform font ──────────────────────────────────────────────
        if sys.platform == "win32":
            self.F = "Segoe UI"
        elif sys.platform == "darwin":
            self.F = "Helvetica Neue"
        else:
            self.F = "Helvetica"

        # ── Colour palette ───────────────────────────────────────────────────
        self.BG      = "#f8fafc"
        self.SURFACE = "#ffffff"
        self.PRIMARY = "#1e3a8a"
        self.ACCENT  = "#2563eb"
        self.TEXT    = "#334155"
        self.MUTED   = "#64748b"
        self.OK      = "#16a34a"
        self.ERR     = "#dc2626"

        self.configure(bg=self.BG)

        self.current_user  = None
        self._active_nav   = None
        self._nav_btns     = {}

        self._init_db()
        self._setup_styles()

        self.container = tk.Frame(self, bg=self.BG)
        self.container.pack(fill="both", expand=True)

        self.show_login()

    # =========================================================================
    # DATABASE
    # =========================================================================
    def _init_db(self):
        """Creates tables if they do not already exist."""
        with sqlite3.connect("banking_data.db") as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    balance  REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transactions (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    username   TEXT NOT NULL,
                    timestamp  TEXT NOT NULL,
                    trans_type TEXT NOT NULL,
                    amount     REAL NOT NULL,
                    balance    REAL NOT NULL,
                    FOREIGN KEY(username) REFERENCES users(username)
                );
            """)

    def _db(self):
        """Returns a new SQLite connection (caller must close / use context)."""
        return sqlite3.connect("banking_data.db")

    def _balance(self):
        """Fetches the current user's balance from the database."""
        with self._db() as db:
            row = db.execute("SELECT balance FROM users WHERE username=?",
                             (self.current_user,)).fetchone()
        return row[0] if row else 0.0

    # =========================================================================
    # STYLES
    # =========================================================================
    def _setup_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Treeview",
                    background=self.SURFACE, foreground=self.TEXT,
                    fieldbackground=self.SURFACE, rowheight=30,
                    font=(self.F, 10))
        s.configure("Treeview.Heading",
                    background=self.PRIMARY, foreground="white",
                    font=(self.F, 10, "bold"))
        s.map("Treeview.Heading", background=[("active", self.ACCENT)])

    # =========================================================================
    # SHARED HELPERS
    # =========================================================================
    def _clear(self):
        """Destroys all widgets inside the main container."""
        for w in self.container.winfo_children():
            w.destroy()

    def _header(self, parent, subtitle=""):
        """Blue branded header strip reused across login / register cards."""
        h = tk.Frame(parent, bg=self.PRIMARY, height=80)
        h.pack(fill="x")
        h.pack_propagate(False)
        tk.Label(h, text="ShieldPharma Finance",
                 font=(self.F, 15, "bold"), fg="white",
                 bg=self.PRIMARY).pack(pady=(14, 2))
        if subtitle:
            tk.Label(h, text=subtitle, font=(self.F, 9),
                     fg="#bfdbfe", bg=self.PRIMARY).pack()

    def _entry(self, parent, mask=False):
        """Standard styled Entry widget."""
        e = tk.Entry(parent, font=(self.F, 11), bg=self.BG, fg=self.TEXT,
                     bd=0, highlightthickness=1, highlightbackground="#cbd5e1",
                     relief="flat")
        if mask:
            e.config(show="•")
        e.pack(fill="x", padx=40, ipady=7)
        return e

    def _label(self, parent, text, size=10, bold=False, color=None, pad_y=(8, 2)):
        weight = "bold" if bold else "normal"
        fg = color or self.MUTED
        tk.Label(parent, text=text, font=(self.F, size, weight),
                 fg=fg, bg=self.SURFACE).pack(anchor="w", padx=40, pady=pad_y)

    def _err_label(self, parent):
        """Returns an inline error label (starts hidden)."""
        lbl = tk.Label(parent, text="", font=(self.F, 9),
                       fg=self.ERR, bg=self.SURFACE)
        lbl.pack(pady=(5, 0))
        return lbl

    # =========================================================================
    # SCREEN 1 — LOGIN
    # =========================================================================
    def show_login(self):
        self._clear()

        card = tk.Frame(self.container, bg=self.SURFACE, bd=0,
                        highlightbackground="#e2e8f0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=460)

        self._header(card, subtitle="Secure Corporate Access")

        tk.Label(card, text="Sign In to Your Account",
                 font=(self.F, 13, "bold"), fg=self.TEXT,
                 bg=self.SURFACE).pack(pady=(22, 14))

        self._label(card, "Username")
        ent_user = self._entry(card)

        self._label(card, "Password")
        ent_pwd = self._entry(card, mask=True)

        lbl_err = self._err_label(card)

        # ── Handler ─────────────────────────────────────────────────────────
        def do_login(event=None):
            uname = ent_user.get().strip()
            pwd   = ent_pwd.get().strip()

            # FIX 7 – inline error, no popup for basic validation
            if not uname or not pwd:
                lbl_err.config(text="⚠  Both fields are required.")
                return

            with self._db() as db:
                row = db.execute("SELECT password FROM users WHERE username=?",
                                 (uname,)).fetchone()

            if row and row[0] == pwd:
                self.current_user = uname
                self.show_dashboard()
            else:
                lbl_err.config(text="⚠  Invalid username or password.")
                ent_pwd.delete(0, tk.END)
                ent_pwd.focus_set()

        # FIX 1 – Enter key navigation
        ent_user.bind("<Return>", lambda e: ent_pwd.focus_set())
        ent_pwd.bind("<Return>", do_login)
        ent_user.focus_set()  # FIX 3 – auto-focus

        tk.Button(card, text="Access Account",
                  font=(self.F, 11, "bold"), bg=self.ACCENT, fg="white",
                  activebackground=self.PRIMARY, activeforeground="white",
                  bd=0, cursor="hand2", command=do_login).pack(
                  fill="x", padx=40, pady=(16, 10), ipady=10)

        tk.Button(card, text="New Pharmacy Partner? Register Here",
                  font=(self.F, 9, "underline"), bg=self.SURFACE,
                  fg=self.ACCENT, activebackground=self.SURFACE,
                  activeforeground=self.PRIMARY, bd=0, cursor="hand2",
                  command=self.show_register).pack(pady=4)

    # =========================================================================
    # SCREEN 2 — REGISTER
    # =========================================================================
    def show_register(self):
        self._clear()

        card = tk.Frame(self.container, bg=self.SURFACE, bd=0,
                        highlightbackground="#e2e8f0", highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=590)

        self._header(card, subtitle="Create Corporate Account")

        tk.Label(card, text="Account Registration",
                 font=(self.F, 13, "bold"), fg=self.TEXT,
                 bg=self.SURFACE).pack(pady=(18, 10))

        # FIX 5 – username hint; FIX 6 – password hint
        self._label(card, "Username  (min 3 chars, no spaces)")
        ent_user = self._entry(card)

        self._label(card, "Password  (min 6 characters)")
        ent_pwd = self._entry(card, mask=True)

        # FIX 2 – confirm password field
        self._label(card, "Confirm Password")
        ent_cpwd = self._entry(card, mask=True)

        self._label(card, "Initial Deposit ($)")
        ent_dep = self._entry(card)
        ent_dep.insert(0, "0.00")

        lbl_err = self._err_label(card)

        # ── Handler ─────────────────────────────────────────────────────────
        def do_register(event=None):
            uname   = ent_user.get().strip()
            pwd     = ent_pwd.get().strip()
            cpwd    = ent_cpwd.get().strip()
            dep_str = ent_dep.get().strip()

            # --- Validation chain ---
            if not all([uname, pwd, cpwd, dep_str]):
                lbl_err.config(text="⚠  All fields are mandatory."); return

            # FIX 5
            if len(uname) < 3:
                lbl_err.config(text="⚠  Username must be at least 3 characters."); return
            if " " in uname:
                lbl_err.config(text="⚠  Username must not contain spaces."); return

            # FIX 6
            if len(pwd) < 6:
                lbl_err.config(text="⚠  Password must be at least 6 characters."); return

            # FIX 2
            if pwd != cpwd:
                lbl_err.config(text="⚠  Passwords do not match.")
                ent_cpwd.delete(0, tk.END)
                ent_cpwd.focus_set(); return

            try:
                deposit = float(dep_str)
                if deposit < 0:
                    raise ValueError
            except ValueError:
                lbl_err.config(text="⚠  Deposit must be a valid non-negative number."); return

            try:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                with self._db() as db:
                    db.execute("INSERT INTO users VALUES (?,?,?)",
                               (uname, pwd, deposit))
                    db.execute("INSERT INTO transactions "
                               "(username,timestamp,trans_type,amount,balance) "
                               "VALUES (?,?,?,?,?)",
                               (uname, ts, "Account Opened", deposit, deposit))
                    db.commit()
                messagebox.showinfo("Success",
                                    "Account created! You may now log in.")
                self.show_login()
            except sqlite3.IntegrityError:
                lbl_err.config(text="⚠  Username already taken. Choose another.")

        # FIX 1 – Enter key chain through all fields
        ent_user.bind("<Return>",  lambda e: ent_pwd.focus_set())
        ent_pwd.bind("<Return>",   lambda e: ent_cpwd.focus_set())
        ent_cpwd.bind("<Return>",  lambda e: ent_dep.focus_set())
        ent_dep.bind("<Return>",   do_register)
        ent_user.focus_set()  # FIX 3

        tk.Button(card, text="Create Account",
                  font=(self.F, 11, "bold"), bg=self.ACCENT, fg="white",
                  activebackground=self.PRIMARY, activeforeground="white",
                  bd=0, cursor="hand2", command=do_register).pack(
                  fill="x", padx=40, pady=(16, 8), ipady=10)

        tk.Button(card, text="← Return to Login",
                  font=(self.F, 9, "underline"), bg=self.SURFACE,
                  fg=self.MUTED, activebackground=self.SURFACE,
                  activeforeground=self.TEXT, bd=0, cursor="hand2",
                  command=self.show_login).pack(pady=4)

    # =========================================================================
    # SCREEN 3 — DASHBOARD SHELL (sidebar + content area)
    # =========================================================================
    def show_dashboard(self):
        self._clear()
        self._nav_btns   = {}
        self._active_nav = None

        # ── Sidebar ─────────────────────────────────────────────────────────
        sidebar = tk.Frame(self.container, bg=self.PRIMARY, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="ShieldPharma",
                 font=(self.F, 13, "bold"), fg="white",
                 bg=self.PRIMARY).pack(pady=(26, 2), padx=20, anchor="w")
        tk.Label(sidebar, text="Finance Portal",
                 font=(self.F, 9), fg="#93c5fd",
                 bg=self.PRIMARY).pack(padx=20, anchor="w")
        tk.Frame(sidebar, bg="#2d4da0", height=1).pack(
            fill="x", padx=15, pady=12)

        # ── Content pane ─────────────────────────────────────────────────────
        self.content_view = tk.Frame(self.container, bg=self.BG)
        self.content_view.pack(side="right", fill="both", expand=True)

        # ── Nav button factory ───────────────────────────────────────────────
        def make_nav(label, key, cmd):
            def on_click():
                self._set_active_nav(key)
                cmd()

            btn = tk.Button(sidebar, text=label,
                            font=(self.F, 10), fg="#93c5fd", bg=self.PRIMARY,
                            activebackground=self.ACCENT, activeforeground="white",
                            bd=0, anchor="w", padx=20, pady=11,
                            cursor="hand2", relief="flat", command=on_click)
            btn.pack(fill="x")

            # Hover — respects active state (FIX 4)
            btn.bind("<Enter>", lambda e: btn.config(bg="#1e40af")
                     if self._active_nav != key else None)
            btn.bind("<Leave>", lambda e: btn.config(
                     bg=self.ACCENT if self._active_nav == key else self.PRIMARY))

            self._nav_btns[key] = btn

        make_nav("  📊   Overview & Balance",   "overview",  self.view_overview)
        make_nav("  💰   Deposit Funds",         "deposit",   self.view_deposit)
        make_nav("  💸   Withdraw Funds",        "withdraw",  self.view_withdraw)
        make_nav("  📋   Transaction History",   "history",   self.view_history)

        tk.Frame(sidebar, bg=self.PRIMARY).pack(fill="both", expand=True)

        # FIX 13 – logout confirmation
        def do_logout():
            if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
                self.current_user = None
                self.show_login()

        tk.Button(sidebar, text="  🔓   Logout",
                  font=(self.F, 10, "bold"), fg="#fca5a5", bg="#7f1d1d",
                  activebackground=self.ERR, activeforeground="white",
                  bd=0, anchor="w", padx=20, pady=11, cursor="hand2",
                  command=do_logout).pack(fill="x", side="bottom")

        # Boot on overview
        self._set_active_nav("overview")
        self.view_overview()

    def _set_active_nav(self, key):
        """FIX 4 – highlights the clicked nav button; resets the rest."""
        self._active_nav = key
        for k, btn in self._nav_btns.items():
            btn.config(fg="#93c5fd", bg=self.PRIMARY, font=(self.F, 10))
        if key in self._nav_btns:
            self._nav_btns[key].config(fg="white", bg=self.ACCENT,
                                       font=(self.F, 10, "bold"))

    # =========================================================================
    # SHARED TOP-BAR (rendered at the top of every content view)
    # =========================================================================
    def _clear_content(self):
        for w in self.content_view.winfo_children():
            w.destroy()

        bar = tk.Frame(self.content_view, bg=self.SURFACE, height=60,
                       bd=0, highlightbackground="#e2e8f0", highlightthickness=1)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        tk.Label(bar, text=f"  {self.current_user.upper()}",
                 font=(self.F, 11, "bold"), fg=self.TEXT,
                 bg=self.SURFACE).pack(side="left", padx=18, pady=18)

        # Live balance in top-bar
        tk.Label(bar, text=f"Balance: ${self._balance():,.2f}",
                 font=(self.F, 10, "bold"), fg=self.PRIMARY,
                 bg=self.SURFACE).pack(side="left", padx=8, pady=18)

        tk.Label(bar, text=datetime.now().strftime("%A, %b %d, %Y"),
                 font=(self.F, 10), fg=self.MUTED,
                 bg=self.SURFACE).pack(side="right", padx=28, pady=18)

        self.ws = tk.Frame(self.content_view, bg=self.BG)
        self.ws.pack(fill="both", expand=True, padx=38, pady=26)

    # =========================================================================
    # VIEW A – OVERVIEW
    # =========================================================================
    def view_overview(self):
        self._clear_content()

        tk.Label(self.ws, text="Account Overview",
                 font=(self.F, 16, "bold"), fg=self.TEXT,
                 bg=self.BG).pack(anchor="w", pady=(0, 16))

        # ── Big balance card ─────────────────────────────────────────────────
        bc = tk.Frame(self.ws, bg=self.SURFACE, bd=0,
                      highlightbackground="#e2e8f0", highlightthickness=1)
        bc.pack(fill="x", ipady=18, pady=(0, 16))

        tk.Label(bc, text="CURRENT LIQUID BALANCE",
                 font=(self.F, 9, "bold"), fg=self.MUTED,
                 bg=self.SURFACE).pack(anchor="w", padx=28, pady=(16, 3))
        tk.Label(bc, text=f"${self._balance():,.2f}",
                 font=(self.F, 30, "bold"), fg=self.PRIMARY,
                 bg=self.SURFACE).pack(anchor="w", padx=28)
        tk.Label(bc, text="Available for withdrawal",
                 font=(self.F, 9), fg=self.MUTED,
                 bg=self.SURFACE).pack(anchor="w", padx=28, pady=(2, 14))

        # ── Info cards row ───────────────────────────────────────────────────
        row = tk.Frame(self.ws, bg=self.BG)
        row.pack(fill="x")

        with self._db() as db:
            tx_count = db.execute(
                "SELECT COUNT(*) FROM transactions WHERE username=? "
                "AND trans_type != 'Account Opened'",
                (self.current_user,)).fetchone()[0]
            last_row = db.execute(
                "SELECT timestamp FROM transactions WHERE username=? "
                "ORDER BY id DESC LIMIT 1",
                (self.current_user,)).fetchone()

        def info_card(label, value):
            c = tk.Frame(row, bg=self.SURFACE, bd=0,
                         highlightbackground="#e2e8f0", highlightthickness=1)
            c.pack(side="left", fill="both", expand=True, ipady=10, padx=(0, 10))
            tk.Label(c, text=label, font=(self.F, 9, "bold"),
                     fg=self.MUTED, bg=self.SURFACE).pack(
                     anchor="w", padx=20, pady=(14, 3))
            tk.Label(c, text=value, font=(self.F, 14, "bold"),
                     fg=self.TEXT, bg=self.SURFACE).pack(anchor="w", padx=20)

        info_card("ACCOUNT HOLDER", self.current_user.upper())
        info_card("TOTAL TRANSACTIONS", str(tx_count))
        info_card("LAST ACTIVITY", last_row[0] if last_row else "—")

    # =========================================================================
    # VIEW B – DEPOSIT
    # =========================================================================
    def view_deposit(self):
        self._clear_content()

        tk.Label(self.ws, text="Deposit Funds",
                 font=(self.F, 16, "bold"), fg=self.TEXT,
                 bg=self.BG).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(self.ws, bg=self.SURFACE, bd=0,
                        highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(fill="x", ipady=28)

        tk.Label(card, text="CURRENT BALANCE",
                 font=(self.F, 9, "bold"), fg=self.MUTED,
                 bg=self.SURFACE).pack(anchor="w", padx=40, pady=(22, 2))

        # FIX 8 & 9 – live balance label, updated in-place after deposit
        bal_lbl = tk.Label(card, text=f"${self._balance():,.2f}",
                           font=(self.F, 22, "bold"), fg=self.PRIMARY,
                           bg=self.SURFACE)
        bal_lbl.pack(anchor="w", padx=40, pady=(0, 16))

        tk.Label(card, text="Enter Amount to Deposit ($)",
                 font=(self.F, 11, "bold"), fg=self.TEXT,
                 bg=self.SURFACE).pack(anchor="w", padx=40, pady=(0, 4))

        ent = tk.Entry(card, font=(self.F, 14), bg=self.BG, fg=self.TEXT,
                       bd=0, highlightthickness=1,
                       highlightbackground="#cbd5e1", relief="flat")
        ent.pack(fill="x", padx=40, ipady=8, pady=(0, 4))
        ent.focus_set()  # FIX 3

        lbl_err = tk.Label(card, text="", font=(self.F, 9),
                           fg=self.ERR, bg=self.SURFACE)
        lbl_err.pack(anchor="w", padx=40)

        def do_deposit(event=None):
            try:
                amount = float(ent.get().strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                lbl_err.config(text="⚠  Enter a valid positive amount."); return

            cur = self._balance()
            new = cur + amount
            ts  = datetime.now().strftime("%Y-%m-%d %H:%M")

            with self._db() as db:
                db.execute("UPDATE users SET balance=? WHERE username=?",
                           (new, self.current_user))
                db.execute("INSERT INTO transactions "
                           "(username,timestamp,trans_type,amount,balance) "
                           "VALUES (?,?,?,?,?)",
                           (self.current_user, ts, "Deposit", amount, new))
                db.commit()

            messagebox.showinfo("Deposit Successful",
                                f"Deposited:    ${amount:,.2f}\n"
                                f"New Balance:  ${new:,.2f}")
            ent.delete(0, tk.END)
            # FIX 8 – refresh balance in-place, no screen switch
            bal_lbl.config(text=f"${self._balance():,.2f}")
            lbl_err.config(text="")

        ent.bind("<Return>", do_deposit)  # FIX 1

        tk.Button(card, text="✅  Confirm Deposit",
                  font=(self.F, 11, "bold"), bg=self.OK, fg="white",
                  activebackground="#15803d", activeforeground="white",
                  bd=0, cursor="hand2", command=do_deposit).pack(
                  anchor="w", padx=40, pady=(14, 0), ipady=10, ipadx=16)

    # =========================================================================
    # VIEW C – WITHDRAW
    # =========================================================================
    def view_withdraw(self):
        self._clear_content()

        tk.Label(self.ws, text="Withdraw Funds",
                 font=(self.F, 16, "bold"), fg=self.TEXT,
                 bg=self.BG).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(self.ws, bg=self.SURFACE, bd=0,
                        highlightbackground="#e2e8f0", highlightthickness=1)
        card.pack(fill="x", ipady=28)

        tk.Label(card, text="AVAILABLE BALANCE",
                 font=(self.F, 9, "bold"), fg=self.MUTED,
                 bg=self.SURFACE).pack(anchor="w", padx=40, pady=(22, 2))

        # FIX 8 & 9 – live balance label
        bal_lbl = tk.Label(card, text=f"${self._balance():,.2f}",
                           font=(self.F, 22, "bold"), fg=self.PRIMARY,
                           bg=self.SURFACE)
        bal_lbl.pack(anchor="w", padx=40, pady=(0, 16))

        tk.Label(card, text="Enter Amount to Withdraw ($)",
                 font=(self.F, 11, "bold"), fg=self.TEXT,
                 bg=self.SURFACE).pack(anchor="w", padx=40, pady=(0, 4))

        ent = tk.Entry(card, font=(self.F, 14), bg=self.BG, fg=self.TEXT,
                       bd=0, highlightthickness=1,
                       highlightbackground="#cbd5e1", relief="flat")
        ent.pack(fill="x", padx=40, ipady=8, pady=(0, 4))
        ent.focus_set()  # FIX 3

        lbl_err = tk.Label(card, text="", font=(self.F, 9),
                           fg=self.ERR, bg=self.SURFACE)
        lbl_err.pack(anchor="w", padx=40)

        def do_withdraw(event=None):
            try:
                amount = float(ent.get().strip())
                if amount <= 0:
                    raise ValueError
            except ValueError:
                lbl_err.config(text="⚠  Enter a valid positive amount."); return

            cur = self._balance()

            # Error handling: insufficient funds
            if amount > cur:
                lbl_err.config(
                    text=f"⚠  Insufficient funds!  Available: ${cur:,.2f}"); return

            new = cur - amount
            ts  = datetime.now().strftime("%Y-%m-%d %H:%M")

            with self._db() as db:
                db.execute("UPDATE users SET balance=? WHERE username=?",
                           (new, self.current_user))
                db.execute("INSERT INTO transactions "
                           "(username,timestamp,trans_type,amount,balance) "
                           "VALUES (?,?,?,?,?)",
                           # store as negative so history shows the sign
                           (self.current_user, ts, "Withdrawal", -amount, new))
                db.commit()

            messagebox.showinfo("Withdrawal Successful",
                                f"Withdrawn:    ${amount:,.2f}\n"
                                f"New Balance:  ${new:,.2f}")
            ent.delete(0, tk.END)
            # FIX 8 – refresh in-place
            bal_lbl.config(text=f"${self._balance():,.2f}")
            lbl_err.config(text="")

        ent.bind("<Return>", do_withdraw)  # FIX 1

        tk.Button(card, text="💸  Confirm Withdrawal",
                  font=(self.F, 11, "bold"), bg=self.ERR, fg="white",
                  activebackground="#b91c1c", activeforeground="white",
                  bd=0, cursor="hand2", command=do_withdraw).pack(
                  anchor="w", padx=40, pady=(14, 0), ipady=10, ipadx=16)

    # =========================================================================
    # VIEW D – TRANSACTION HISTORY
    # =========================================================================
    def view_history(self):
        self._clear_content()

        tk.Label(self.ws, text="Transaction History",
                 font=(self.F, 16, "bold"), fg=self.TEXT,
                 bg=self.BG).pack(anchor="w", pady=(0, 8))

        # ── FIX 11 – Filter bar ──────────────────────────────────────────────
        fbar = tk.Frame(self.ws, bg=self.BG)
        fbar.pack(fill="x", pady=(0, 8))

        tk.Label(fbar, text="Filter:", font=(self.F, 10, "bold"),
                 fg=self.MUTED, bg=self.BG).pack(side="left")

        fvar = tk.StringVar(value="All")

        def refresh(_=None):
            for row in tree.get_children():
                tree.delete(row)
            ftype = fvar.get()
            with self._db() as db:
                if ftype == "All":
                    rows = db.execute(
                        "SELECT timestamp,trans_type,amount,balance "
                        "FROM transactions WHERE username=? ORDER BY id DESC",
                        (self.current_user,)).fetchall()
                else:
                    rows = db.execute(
                        "SELECT timestamp,trans_type,amount,balance "
                        "FROM transactions WHERE username=? "
                        "AND trans_type=? ORDER BY id DESC",
                        (self.current_user, ftype)).fetchall()

            for i, (ts, tt, amt, bal) in enumerate(rows):
                sign  = "+" if amt >= 0 else "−"
                f_amt = f"{sign}${abs(amt):,.2f}"
                f_bal = f"${bal:,.2f}"
                even  = (i % 2 == 0)

                # FIX 10 – colour-coded rows
                if tt in ("Deposit", "Account Opened"):
                    tag = "dep_e" if even else "dep_o"
                elif tt == "Withdrawal":
                    tag = "wd_e"  if even else "wd_o"
                else:
                    tag = "pl_e"  if even else "pl_o"

                tree.insert("", "end",
                            values=(ts, tt, f_amt, f_bal), tags=(tag,))

        for lbl in ["All", "Deposit", "Withdrawal"]:
            tk.Radiobutton(fbar, text=lbl, variable=fvar, value=lbl,
                           font=(self.F, 9), fg=self.TEXT, bg=self.BG,
                           activebackground=self.BG, selectcolor=self.BG,
                           command=refresh).pack(side="left", padx=8)

        # ── Table ────────────────────────────────────────────────────────────
        wrap = tk.Frame(self.ws, bg=self.SURFACE, bd=0,
                        highlightbackground="#e2e8f0", highlightthickness=1)
        wrap.pack(fill="both", expand=True)

        vsb = ttk.Scrollbar(wrap, orient="vertical")
        vsb.pack(side="right", fill="y")

        cols = ("Timestamp", "Type", "Amount", "Balance")
        tree = ttk.Treeview(wrap, columns=cols, show="headings",
                            yscrollcommand=vsb.set)
        tree.pack(fill="both", expand=True)
        vsb.config(command=tree.yview)

        for col, text, width, anchor in [
            ("Timestamp", "DATE & TIME",         180, "center"),
            ("Type",      "TYPE",                170, "w"),
            ("Amount",    "AMOUNT ($)",           155, "e"),
            ("Balance",   "RUNNING BALANCE ($)",  155, "e"),
        ]:
            tree.heading(col, text=text)
            tree.column(col, width=width, anchor=anchor)

        # FIX 10 – green / red colour tags
        tree.tag_configure("dep_e", background="#f0fdf4", foreground="#15803d")
        tree.tag_configure("dep_o", background="#dcfce7", foreground="#15803d")
        tree.tag_configure("wd_e",  background="#fff1f2", foreground="#dc2626")
        tree.tag_configure("wd_o",  background="#ffe4e6", foreground="#dc2626")
        tree.tag_configure("pl_e",  background="#ffffff")
        tree.tag_configure("pl_o",  background="#f8fafc")

        refresh()   # initial load


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = OnlineBankingSystem()
    app.mainloop()