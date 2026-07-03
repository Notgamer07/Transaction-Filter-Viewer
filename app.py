import os
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD


def format_indian_currency(amount):
    """Formats a float into the Indian numbering system format (Rs.

    1,00,00,000.00).
    """
    if pd.isna(amount) or amount == 0:
        return "Rs. 0.00"

    s = f"{amount:.2f}"
    parts = s.split(".")
    whole = parts[0]
    decimal = parts[1]

    negative = "-" if whole.startswith("-") else ""
    if negative:
        whole = whole[1:]

    if len(whole) <= 3:
        return f"{negative}Rs. {whole}.{decimal}"
    else:
        last_three = whole[-3:]
        remaining = whole[:-3]
        out = []
        while len(remaining) > 2:
            out.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            out.insert(0, remaining)
        return f"{negative}Rs. {','.join(out)},{last_three}.{decimal}"


def parse_bank_statement(file_path):
    """Parses the bank statement CSV, cleans narration timestamps, and

    prepares numeric columns for mathematical analysis.
    """
    df = pd.read_csv(file_path, skiprows=8)

    # Clean completely empty spacer columns
    df = df.dropna(how="all", axis=1)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.columns = [col.strip() for col in df.columns]

    if "NARRATION" in df.columns:
        df["NARRATION"] = df["NARRATION"].fillna("").astype(str)
        # Remove time in the middle of narration (e.g., /21:05:50/)
        df["NARRATION"] = df["NARRATION"].apply(
            lambda x: re.sub(r"/\d{2}:\d{2}:\d{2}/", "/", x)
        )

    # Convert numeric values cleanly for arithmetic ops
    for col in ["WITHDRAWAL(DR)", "DEPOSIT(CR)"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.replace("Cr", "")
                .str.replace("Dr", "")
                .str.strip()
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Determine Debit or Credit type
    def determine_type(row):
        dr_val = row.get("WITHDRAWAL(DR)", 0)
        cr_val = row.get("DEPOSIT(CR)", 0)
        if dr_val > 0:
            return "Debit"
        if cr_val > 0:
            return "Credit"
        return "Unknown"

    df["Type"] = df.apply(determine_type, axis=1)
    return df


class AccountStatementApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Account Statement Analyzer")
        self.root.geometry("1100x650")

        self.df = None
        self._build_ui()

    def _build_ui(self):
        # --- Top Section: File Import ---
        import_frame = ttk.LabelFrame(
            self.root, text=" 1. Import Account Statement (CSV) ", padding=15
        )
        import_frame.pack(fill="x", padx=15, pady=10)

        self.drop_zone = tk.Label(
            import_frame,
            text="Drag & Drop your CSV file here\n— or —",
            bg="#f0f4f8",
            fg="#555555",
            font=("Arial", 11, "italic"),
            bd=2,
            relief="groove",
            height=3,
        )
        self.drop_zone.pack(fill="x", side="top", pady=(0, 10))

        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self.handle_drop)

        browse_btn = ttk.Button(
            import_frame, text="Browse File System", command=self.browse_file
        )
        browse_btn.pack()

        # --- Middle Section: Filters ---
        filter_frame = ttk.LabelFrame(
            self.root, text=" 2. Filters & View Controls ", padding=15
        )
        filter_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(filter_frame, text="Search Narration Text:").grid(
            row=0, column=0, sticky="w", padx=5
        )
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.update_table())
        self.search_entry = ttk.Entry(
            filter_frame, textvariable=self.search_var, width=30
        )
        self.search_entry.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(filter_frame, text="Transaction Type:").grid(
            row=0, column=2, sticky="w", padx=(20, 5)
        )
        self.type_filter_var = tk.StringVar(value="All")
        self.type_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.type_filter_var,
            values=["All", "Debits Only", "Credits Only"],
            state="readonly",
            width=15,
        )
        self.type_combo.grid(row=0, column=3, padx=5, sticky="w")
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        self.color_coding_var = tk.BooleanVar(value=False)
        self.color_check = ttk.Checkbutton(
            filter_frame,
            text="Enable Color Coding (Debits: Green | Credits: Red)",
            variable=self.color_coding_var,
            command=self.update_table,
        )
        self.color_check.grid(row=0, column=4, padx=(20, 5), sticky="w")

        # --- Summary Panel ---
        self.summary_frame = ttk.Frame(self.root, padding=5)
        self.summary_frame.pack(fill="x", padx=15, pady=5)

        self.withdrawal_label = ttk.Label(
            self.summary_frame,
            text="Total Withdrawals: Rs. 0.00",
            font=("Arial", 11, "bold"),
            foreground="#d32f2f",
        )
        self.withdrawal_label.pack(side="left", padx=(5, 30))

        self.deposit_label = ttk.Label(
            self.summary_frame,
            text="Total Deposits: Rs. 0.00",
            font=("Arial", 11, "bold"),
            foreground="#388e3c",
        )
        self.deposit_label.pack(side="left", padx=5)

        # --- Bottom Section: Data View (Treeview) ---
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            table_frame,
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode="extended",
        )
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.tag_configure("debit_color", foreground="red")
        self.tree.tag_configure("credit_color", foreground="green")

    def load_csv(self, file_path):
        try:
            file_path = file_path.strip("{}")
            if not file_path.lower().endswith(".csv"):
                raise ValueError("Selected file is not a CSV.")

            self.df = parse_bank_statement(file_path)
            self.drop_zone.config(
                text=f"Loaded: {os.path.basename(file_path)}", bg="#e1f5fe"
            )
            self.setup_table_headers()
            self.update_table()
        except Exception as e:
            messagebox.showerror(
                "Error Loading File", f"Could not read CSV file.\nDetails: {str(e)}"
            )

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_csv(file_path)

    def handle_drop(self, event):
        if event.data:
            self.load_csv(event.data)

    def setup_table_headers(self):
        if self.df is None:
            return
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"

        for col in self.df.columns:
            # --- CUSTOM HEADING NAMES WITH SIGN SIGNALS ---
            display_text = col
            if "WITHDRAWAL" in col.upper():
                display_text = "(-) WITHDRAWAL(DR)"
            elif "DEPOSIT" in col.upper():
                display_text = "(+) DEPOSIT(CR)"

            self.tree.heading(col, text=display_text, anchor="w")

            if col == "NARRATION":
                self.tree.column(col, width=450, minwidth=300, anchor="w")
            elif col in ["Type", "CHQ.NO."]:
                self.tree.column(col, width=80, minwidth=60, anchor="w")
            else:
                self.tree.column(col, width=130, minwidth=100, anchor="w")

    def update_table(self):
        if self.df is None:
            return

        self.tree.delete(*self.tree.get_children())

        search_query = self.search_var.get().strip().lower()
        type_filter = self.type_filter_var.get()
        use_colors = self.color_coding_var.get()

        narration_col = next(
            (c for c in self.df.columns if "narration" in c.lower()),
            self.df.columns[0],
        )

        filtered_withdrawal_total = 0.0
        filtered_deposit_total = 0.0

        for _, row in self.df.iterrows():
            narration_text = str(row[narration_col]).lower()

            if search_query and search_query not in narration_text:
                continue

            tx_type = row["Type"]
            if type_filter == "Debits Only" and tx_type != "Debit":
                continue
            if type_filter == "Credits Only" and tx_type != "Credit":
                continue

            filtered_withdrawal_total += row.get("WITHDRAWAL(DR)", 0.0)
            filtered_deposit_total += row.get("DEPOSIT(CR)", 0.0)

            row_values = []
            for col in self.df.columns:
                val = row[col]
                # Format math values with explicit signs across rows
                if col == "WITHDRAWAL(DR)" and isinstance(val, (int, float)):
                    row_values.append(f"- {val:,.2f}" if val > 0 else "")
                elif col == "DEPOSIT(CR)" and isinstance(val, (int, float)):
                    row_values.append(f"+ {val:,.2f}" if val > 0 else "")
                else:
                    row_values.append(str(val))

            row_tags = ()
            if use_colors:
                if tx_type == "Debit":
                    row_tags = ("debit_color",)
                elif tx_type == "Credit":
                    row_tags = ("credit_color",)

            self.tree.insert("", "end", values=row_values, tags=row_tags)

        self.withdrawal_label.config(
            text=f"Total Withdrawals: {format_indian_currency(filtered_withdrawal_total)}"
        )
        self.deposit_label.config(
            text=f"Total Deposits: {format_indian_currency(filtered_deposit_total)}"
        )


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = AccountStatementApp(root)
    root.mainloop()