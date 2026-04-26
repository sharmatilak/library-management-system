import tkinter as tk
from tkinter import ttk, messagebox
from core.auth import verify_admin, add_admin
from core.books import (
    load_books, add_book, update_book, delete_book, find_book, search_books, 
    is_valid_isbn, is_valid_year
)
from core.students import (
    load_students, add_student, update_student, delete_student, find_student, 
    search_students, is_valid_phone, is_valid_email
)
from core.borrow import (
    borrow_book, return_book, list_currently_borrowed, list_all_borrowed,
    books_borrowed_by_student, who_borrowed_book, get_overdue_books, 
    calculate_fine, collect_fine, BORROW_DAYS, FINE_PER_DAY
)

def center_window(win, w=800, h=600):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")

def signup_screen(parent):
    win = tk.Toplevel(parent)
    win.title("Create Admin")
    center_window(win, 300, 200)

    tk.Label(win, text="New Username").pack(pady=5)
    u_entry = tk.Entry(win)
    u_entry.pack()

    tk.Label(win, text="New Password").pack(pady=5)
    p_entry = tk.Entry(win, show="*")
    p_entry.pack()

    def on_signup():
        username = u_entry.get().strip()
        password = p_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Username and password required.")
            return
        if add_admin(username, password):
            messagebox.showinfo("Success", "Admin account created. You can now log in.")
            win.destroy()
        else:
            messagebox.showerror("Error", "Username already exists.")
    
    tk.Button(win, text="Sign Up", command=on_signup).pack(pady=10)

class LoginWindow:
    def __init__(self, root):
        self.root = root
        root.title("Admin Login")
        center_window(root, 300, 200)

        tk.Label(root, text="Username").pack(pady=5)
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()

        tk.Label(root, text="Password").pack(pady=5)
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()

        tk.Button(root, text="Login", command=self.attempt_login).pack(pady=5)
        tk.Button(root, text="Sign Up", command=self.open_signup).pack(pady=5)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if verify_admin(username, password):
            messagebox.showinfo("Login Success", f"Welcome {username}!")
            self.root.destroy()
            main_app_root = tk.Tk()
            LibraryApp(main_app_root)
            main_app_root.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")
    
    def open_signup(self):
        signup_screen(self.root)

class LibraryApp:
    def __init__(self, root):
        self.root = root
        root.title("Library Books Management System")
        center_window(root, 1100, 700)

        # Menu bar
        menubar = tk.Menu(root)
        root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True, padx=8, pady=8)

        self.create_dashboard_tab()
        self.create_books_tab()
        self.create_students_tab()
        self.create_borrow_tab()
        self.create_reports_tab()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            login_root = tk.Tk()
            LoginWindow(login_root)
            login_root.mainloop()

    def show_about(self):
        messagebox.showinfo("About", 
            "Library Books Management System\n\n"
            f"Borrow Period: {BORROW_DAYS} days\n"
            f"Fine: ₹{FINE_PER_DAY}/day after due date")

    # Dashboard Tab
    def create_dashboard_tab(self):
        self.dashboard_tab = ttk.Frame(self.nb)
        self.nb.add(self.dashboard_tab, text="Dashboard")
        
        stats_frame = ttk.Frame(self.dashboard_tab)
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.stats_vars = {}
        stats = [
            ("Total Books", "total_books"),
            ("Total Students", "total_students"),
            ("Active Borrows", "active_borrows"),
            ("Overdue Books", "overdue_books")
        ]
        
        for i, (label, key) in enumerate(stats):
            frame = ttk.Frame(stats_frame, relief="ridge", padding=10)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            
            ttk.Label(frame, text=label, font=('Arial', 12)).pack()
            self.stats_vars[key] = tk.StringVar(value="Loading...")
            ttk.Label(frame, textvariable=self.stats_vars[key], font=('Arial', 24, 'bold')).pack()
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        
        ttk.Button(self.dashboard_tab, text="Refresh Dashboard", command=self.update_dashboard).pack(pady=10)
        self.update_dashboard()
    
    def update_dashboard(self):
        books = load_books()
        students = load_students()
        active_borrows = list_currently_borrowed()
        overdue = get_overdue_books()
        
        self.stats_vars["total_books"].set(str(len(books)))
        self.stats_vars["total_students"].set(str(len(students)))
        self.stats_vars["active_borrows"].set(str(len(active_borrows)))
        self.stats_vars["overdue_books"].set(str(len(overdue)))

    # Books Tab
    def create_books_tab(self):
        self.books_tab = ttk.Frame(self.nb)
        self.nb.add(self.books_tab, text="Books")
        
        ctrl = ttk.Frame(self.books_tab)
        ctrl.pack(fill="x", pady=6)
        
        ttk.Button(ctrl, text="Add Book", command=self.open_add_book).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Edit Selected", command=self.open_edit_book).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Delete Selected", command=self.delete_selected_book).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_books).pack(side="left", padx=4)
        
        ttk.Label(ctrl, text="Search:").pack(side="left", padx=(12,4))
        self.book_search_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.book_search_var, width=30).pack(side="left")
        ttk.Button(ctrl, text="Go", command=self.search_books_action).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Show All", command=self.refresh_books).pack(side="left", padx=4)
        
        cols = ("ID", "Title", "Author", "Year", "ISBN", "Total Copies", "Available", "Status")
        self.book_tree = ttk.Treeview(self.books_tab, columns=cols, show="headings")
        widths = [60, 320, 180, 80, 140, 90, 90, 90]
        for c, w in zip(cols, widths):
            self.book_tree.heading(c, text=c)
            self.book_tree.column(c, width=w, anchor="w")
        self.book_tree.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.refresh_books()
    
    def refresh_books(self):
        for r in self.book_tree.get_children():
            self.book_tree.delete(r)
        for b in load_books():
            available = b.get("available_copies", 0)
            status = "Borrowed" if available == 0 else "Available"
            self.book_tree.insert("", "end", values=(
                b["book_id"], b["title"], b.get("author",""), 
                b.get("year",""), b.get("isbn",""), 
                b.get("total_copies",1), available, status
            ))
    
    def open_add_book(self):
        win = tk.Toplevel(self.root)
        win.title("Add Book")
        center_window(win, 400, 280)
        
        labels = ["Title*", "Author", "Year", "ISBN", "Total Copies"]
        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=35)
            e.grid(row=i, column=1, padx=8, pady=8)
            entries[lab.lower().replace("*", "")] = e
        
        entries["total copies"].insert(0, "1")
        
        def on_add():
            try:
                title = entries["title"].get().strip()
                if not title:
                    messagebox.showerror("Error", "Title required")
                    return
                author = entries["author"].get().strip()
                year = entries["year"].get().strip()
                if year and not is_valid_year(year):
                    messagebox.showerror("Error", "Year must be 4 digits.")
                    return
                isbn = entries["isbn"].get().strip()
                if isbn and not is_valid_isbn(isbn):
                    messagebox.showerror("Error", "ISBN must be 10-13 digits.")
                    return
                total_copies = entries["total copies"].get().strip()
                if not total_copies.isdigit() or int(total_copies) < 1:
                    messagebox.showerror("Error", "Total copies must be a positive number.")
                    return
                
                bid = add_book(title, author, year, isbn, int(total_copies))
                messagebox.showinfo("Success", f"Book added with ID {bid}")
                win.destroy()
                self.refresh_books()
                self.update_dashboard()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(win, text="Add Book", command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=12)
    
    def open_edit_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a book to edit")
            return
        vals = self.book_tree.item(sel[0])["values"]
        bid = vals[0]
        book = find_book(bid)
        if not book:
            messagebox.showerror("Error", "Book not found")
            return
        
        win = tk.Toplevel(self.root)
        win.title("Edit Book")
        center_window(win, 400, 280)
        
        labels = [("Title", "title"), ("Author", "author"), ("Year", "year"), ("ISBN", "isbn"), ("Total Copies", "total_copies")]
        entries = {}
        for i, (lab, key) in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=35)
            e.grid(row=i, column=1, padx=8, pady=8)
            e.insert(0, str(book.get(key, "")))
            entries[key] = e
        
        def on_save():
            try:
                title = entries["title"].get().strip()
                author = entries["author"].get().strip()
                year = entries["year"].get().strip()
                if year and not is_valid_year(year):
                    messagebox.showerror("Error", "Year must be 4 digits.")
                    return
                isbn = entries["isbn"].get().strip()
                if isbn and not is_valid_isbn(isbn):
                    messagebox.showerror("Error", "ISBN must be 10-13 digits.")
                    return
                total_copies = entries["total_copies"].get().strip()
                if total_copies and (not total_copies.isdigit() or int(total_copies) < 1):
                    messagebox.showerror("Error", "Total copies must be a positive number.")
                    return
                
                update_book(bid, title=title, author=author, year=year, isbn=isbn, 
                           total_copies=int(total_copies) if total_copies else None)
                messagebox.showinfo("Success", "Book updated")
                win.destroy()
                self.refresh_books()
                self.update_dashboard()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(win, text="Save Changes", command=on_save).grid(row=len(labels), column=0, columnspan=2, pady=12)
    
    def delete_selected_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a book to delete")
            return
        vals = self.book_tree.item(sel[0])["values"]
        bid = vals[0]
        
        active = list_currently_borrowed()
        if any(r["book_id"] == bid for r in active):
            messagebox.showerror("Error", "Book is currently borrowed. Can't delete.")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected book?"):
            delete_book(bid)
            self.refresh_books()
            self.update_dashboard()
    
    def search_books_action(self):
        q = self.book_search_var.get().strip()
        res = search_books(q)
        borrowed_ids = {r["book_id"] for r in list_currently_borrowed()}
        for r in self.book_tree.get_children():
            self.book_tree.delete(r)
        for b in res:
            available = b.get("available_copies", 0)
            status = "Borrowed" if available == 0 and b["book_id"] in borrowed_ids else "Available"
            self.book_tree.insert("", "end", values=(
                b["book_id"], b["title"], b.get("author",""), 
                b.get("year",""), b.get("isbn",""), 
                b.get("total_copies",1), available, status
            ))

    # Students Tab
    def create_students_tab(self):
        self.students_tab = ttk.Frame(self.nb)
        self.nb.add(self.students_tab, text="Students")
        
        ctrl = ttk.Frame(self.students_tab)
        ctrl.pack(fill="x", pady=6)
        
        ttk.Button(ctrl, text="Add Student", command=self.open_add_student).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Edit Selected", command=self.open_edit_student).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Delete Selected", command=self.delete_selected_student).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_students).pack(side="left", padx=4)
        
        ttk.Label(ctrl, text="Search:").pack(side="left", padx=(12,4))
        self.student_search_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.student_search_var, width=30).pack(side="left")
        ttk.Button(ctrl, text="Go", command=self.search_students_action).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Show All", command=self.refresh_students).pack(side="left", padx=4)
        
        cols = ("ID", "Name", "Branch", "Semester", "Phone", "Email")
        self.student_tree = ttk.Treeview(self.students_tab, columns=cols, show="headings")
        widths = [60, 200, 120, 100, 120, 180]
        for c, w in zip(cols, widths):
            self.student_tree.heading(c, text=c)
            self.student_tree.column(c, width=w, anchor="w")
        self.student_tree.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.refresh_students()
    
    def refresh_students(self):
        for r in self.student_tree.get_children():
            self.student_tree.delete(r)
        for s in load_students():
            self.student_tree.insert("", "end", values=(
                s["student_id"], s["name"], s.get("branch",""), 
                s.get("semester",""), s.get("phone",""), s.get("email","")
            ))
    
    def open_add_student(self):
        win = tk.Toplevel(self.root)
        win.title("Add Student")
        center_window(win, 400, 260)
        
        labels = ["Name*", "Branch", "Semester", "Phone", "Email"]
        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=35)
            e.grid(row=i, column=1, padx=8, pady=8)
            entries[lab.lower().replace("*", "")] = e

        def on_add():
            try:
                name = entries["name"].get().strip()
                if not name:
                    messagebox.showerror("Error", "Name required.")
                    return
                branch = entries["branch"].get().strip()
                semester = entries["semester"].get().strip()
                phone = entries["phone"].get().strip()
                if phone and not is_valid_phone(phone):
                    messagebox.showerror("Error", "Phone must be 10 digits.")
                    return
                email = entries["email"].get().strip()
                if email and not is_valid_email(email):
                    messagebox.showerror("Error", "Invalid email.")
                    return
                
                sid = add_student(name, branch, semester, phone, email)
                messagebox.showinfo("Success", f"Student added with ID {sid}")
                win.destroy()
                self.refresh_students()
                self.update_dashboard()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(win, text="Add Student", command=on_add).grid(row=len(labels), column=0, columnspan=2, pady=10)
    
    def open_edit_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a student to edit")
            return
        vals = self.student_tree.item(sel[0])["values"]
        sid = vals[0]
        s = find_student(sid)
        if not s:
            messagebox.showerror("Error", "Student not found")
            return
        
        win = tk.Toplevel(self.root)
        win.title("Edit Student")
        center_window(win, 400, 260)
        
        labels = [("Name", "name"), ("Branch", "branch"), ("Semester", "semester"), ("Phone", "phone"), ("Email", "email")]
        entries = {}
        for i, (lab, key) in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, padx=8, pady=8, sticky="w")
            e = ttk.Entry(win, width=35)
            e.grid(row=i, column=1, padx=8, pady=8)
            e.insert(0, s.get(key, ""))
            entries[key] = e

        def on_save():
            try:
                name = entries["name"].get().strip()
                branch = entries["branch"].get().strip()
                semester = entries["semester"].get().strip()
                phone = entries["phone"].get().strip()
                if phone and not is_valid_phone(phone):
                    messagebox.showerror("Error", "Phone must be 10 digits.")
                    return
                email = entries["email"].get().strip()
                if email and not is_valid_email(email):
                    messagebox.showerror("Error", "Invalid email.")
                    return
                
                update_student(sid, name=name, branch=branch, semester=semester, phone=phone, email=email)
                messagebox.showinfo("Success", "Student updated")
                win.destroy()
                self.refresh_students()
            except ValueError as e:
                messagebox.showerror("Error", str(e))
        
        ttk.Button(win, text="Save Changes", command=on_save).grid(row=len(labels), column=0, columnspan=2, pady=10)
    
    def delete_selected_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a student to delete")
            return
        vals = self.student_tree.item(sel[0])["values"]
        sid = vals[0]
        
        active = list_currently_borrowed()
        if any(r["student_id"] == sid for r in active):
            messagebox.showerror("Error", "Student has borrowed books. Can't delete.")
            return
        
        if messagebox.askyesno("Confirm", "Delete selected student?"):
            delete_student(sid)
            self.refresh_students()
            self.update_dashboard()
    
    def search_students_action(self):
        q = self.student_search_var.get().strip()
        res = search_students(q)
        for r in self.student_tree.get_children():
            self.student_tree.delete(r)
        for s in res:
            self.student_tree.insert("", "end", values=(
                s["student_id"], s["name"], s.get("semester",""), 
                s.get("phone",""), s.get("email","")
            ))

    # Borrow Tab 
    def create_borrow_tab(self):
        self.borrow_tab = ttk.Frame(self.nb)
        self.nb.add(self.borrow_tab, text="Borrow / Return")
        
        ctrl = ttk.Frame(self.borrow_tab)
        ctrl.pack(fill="x", pady=6)
        
        ttk.Label(ctrl, text="Student ID:").pack(side="left", padx=(4,6))
        self.borrow_student_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.borrow_student_var, width=12).pack(side="left")
        
        ttk.Label(ctrl, text="Book ID:").pack(side="left", padx=(8,6))
        self.borrow_book_var = tk.StringVar()
        ttk.Entry(ctrl, textvariable=self.borrow_book_var, width=12).pack(side="left")
        
        ttk.Button(ctrl, text="Borrow", command=self.borrow_action).pack(side="left", padx=8)
        ttk.Button(ctrl, text="Return", command=self.return_action).pack(side="left", padx=8)
        ttk.Button(ctrl, text="Refresh", command=self.refresh_borrow_tree).pack(side="left", padx=8)
        
        fine_frame = ttk.Frame(self.borrow_tab)
        fine_frame.pack(fill="x", pady=6)
        
        ttk.Label(fine_frame, text="Borrow ID for Fine:").pack(side="left", padx=(4,6))
        self.fine_borrow_var = tk.StringVar()
        ttk.Entry(fine_frame, textvariable=self.fine_borrow_var, width=12).pack(side="left")
        ttk.Button(fine_frame, text="Pay Fine", command=self.pay_fine_action).pack(side="left", padx=8)
        ttk.Label(fine_frame, text=f"Info: {BORROW_DAYS} days, ₹{FINE_PER_DAY}/day fine").pack(side="left", padx=(20,4))
        
        cols = ("BorrowID", "StudentID", "StudentName", "BookID", "BookTitle", "BorrowDate", "DueDate", "ReturnDate", "Fine")
        self.borrow_tree = ttk.Treeview(self.borrow_tab, columns=cols, show="headings")
        widths = [80, 90, 200, 90, 200, 100, 100, 100, 80]
        for c, w in zip(cols, widths):
            self.borrow_tree.heading(c, text=c)
            self.borrow_tree.column(c, width=w, anchor="w")
        self.borrow_tree.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.refresh_borrow_tree()
    
    def borrow_action(self):
        sid = self.borrow_student_var.get().strip()
        bid = self.borrow_book_var.get().strip()
        if not sid or not bid:
            messagebox.showerror("Error", "Student ID and Book ID required")
            return
        try:
            ok, msg = borrow_book(int(sid), int(bid))
            if ok:
                messagebox.showinfo("Success", msg)
                self.refresh_borrow_tree()
                self.refresh_books()
                self.update_dashboard()
            else:
                messagebox.showerror("Error", msg)
        except ValueError:
            messagebox.showerror("Error", "Invalid ID format")
    
    def return_action(self):
        sid = self.borrow_student_var.get().strip()
        bid = self.borrow_book_var.get().strip()
        if not sid or not bid:
            messagebox.showerror("Error", "Student ID and Book ID required")
            return
        try:
            ok, msg = return_book(student_id=int(sid), book_id=int(bid))
            if ok:
                messagebox.showinfo("Success", msg)
                self.refresh_borrow_tree()
                self.refresh_books()
                self.update_dashboard()
            else:
                messagebox.showerror("Error", msg)
        except ValueError:
            messagebox.showerror("Error", "Invalid ID format")
    
    def pay_fine_action(self):
        borrow_id = self.fine_borrow_var.get().strip()
        if not borrow_id:
            messagebox.showerror("Error", "Borrow ID required")
            return
        if collect_fine(int(borrow_id)):
            messagebox.showinfo("Success", "Fine paid successfully!")
            self.refresh_borrow_tree()
        else:
            messagebox.showerror("Error", "Could not process fine payment.")
    
    def refresh_borrow_tree(self):
        for r in self.borrow_tree.get_children():
            self.borrow_tree.delete(r)
        for br in list_all_borrowed():
            s = find_student(br["student_id"]) or {}
            b = find_book(br["book_id"]) or {}
            fine = br.get("fine_amount", 0)
            if fine > 0 and not br.get("fine_paid", 0):
                fine_display = f"₹{fine} (Unpaid)"
            elif fine > 0:
                fine_display = f"₹{fine} (Paid)"
            else:
                fine_display = "-"
            
            self.borrow_tree.insert("", "end", values=(
                br.get("borrow_id",""),
                br.get("student_id",""),
                s.get("name",""),
                br.get("book_id",""),
                b.get("title",""),
                br.get("borrow_date",""),
                br.get("due_date",""),
                br.get("return_date","Not returned"),
                fine_display
            ))

    # Reports Tab
    def create_reports_tab(self):
        self.reports_tab = ttk.Frame(self.nb)
        self.nb.add(self.reports_tab, text="Reports")
        
        ctrl = ttk.Frame(self.reports_tab)
        ctrl.pack(fill="x", pady=6)
        
        ttk.Button(ctrl, text="Currently Borrowed", command=self.show_currently_borrowed).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Available Books", command=self.show_available_books).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Overdue Books", command=self.show_overdue_books).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Students & Borrows", command=self.show_students_borrows).pack(side="left", padx=6)
        
        # Export buttons
        ttk.Separator(ctrl, orient='vertical').pack(side="left", padx=10, fill='y')
        ttk.Button(ctrl, text="📄 Export All to CSV", command=self.export_all_to_csv).pack(side="left", padx=6)
        ttk.Button(ctrl, text="📝 Export All to TXT", command=self.export_all_to_txt).pack(side="left", padx=6)
        ttk.Button(ctrl, text="📋 Export Current to CSV", command=self.export_current_to_csv).pack(side="left", padx=6)
        
        self.report_box = tk.Text(self.reports_tab, wrap="none")
        self.report_box.pack(fill="both", expand=True, padx=8, pady=8)
        
        scrollbar = ttk.Scrollbar(self.report_box)
        scrollbar.pack(side="right", fill="y")
        self.report_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.report_box.yview)
    
    def show_currently_borrowed(self):
        self.report_box.delete("1.0", "end")
        lines = ["CURRENTLY BORROWED BOOKS\n", "="*40 + "\n"]
        for r in list_currently_borrowed():
            s = find_student(r["student_id"]) or {}
            b = find_book(r["book_id"]) or {}
            due = r.get("due_date", "")
            fine = calculate_fine(r["borrow_date"])
            fine_msg = f" (Fine: ₹{fine})" if fine > 0 else ""
            lines.append(f'{s.get("name","Unknown")} (ID: {r["student_id"]})\n   → {b.get("title","Unknown")} (ID: {r["book_id"]})\n   Due: {due}{fine_msg}\n')
        if len(lines) == 2:
            lines.append("No currently borrowed books.\n")
        self.report_box.insert("1.0", "".join(lines))
    
    def show_available_books(self):
        self.report_box.delete("1.0", "end")
        lines = ["AVAILABLE BOOKS\n", "="*40 + "\n"]
        for b in load_books():
            available = b.get("available_copies", 0)
            if available > 0:
                lines.append(f'{b["book_id"]} - {b.get("title","")} by {b.get("author","")} (Available: {available})\n')
        if len(lines) == 2:
            lines.append("No available books.\n")
        self.report_box.insert("1.0", "".join(lines))
    
    def show_overdue_books(self):
        self.report_box.delete("1.0", "end")
        overdue = get_overdue_books()
        lines = ["OVERDUE BOOKS\n", "="*40 + "\n"]
        for r in overdue:
            s = find_student(r["student_id"]) or {}
            b = find_book(r["book_id"]) or {}
            fine = calculate_fine(r["borrow_date"])
            lines.append(f'{s.get("name","Unknown")} (ID: {r["student_id"]})\n   → {b.get("title","Unknown")} (ID: {r["book_id"]})\n   Due: {r.get("due_date","")}\n   Fine: ₹{fine}\n')
        if len(lines) == 2:
            lines.append("No overdue books.\n")
        self.report_box.insert("1.0", "".join(lines))
    
    def show_students_borrows(self):
        self.report_box.delete("1.0", "end")
        students = load_students()
        lines = ["STUDENT BORROWING HISTORY\n", "="*40 + "\n"]
        for s in students:
            borrows = books_borrowed_by_student(s["student_id"])
            if borrows:
                lines.append(f'\n{s["student_id"]} - {s["name"]}:\n')
                for br in borrows:
                    b = find_book(br["book_id"]) or {}
                    status = "Returned" if br.get("return_date") else "Not returned"
                    fine = br.get("fine_amount", 0)
                    fine_msg = f" (Fine: ₹{fine})" if fine > 0 else ""
                    lines.append(f'   • {br["book_id"]} - {b.get("title","Unknown")}\n     Borrowed: {br.get("borrow_date","")}\n     Due: {br.get("due_date","")}\n     {status}{fine_msg}\n')
        if len(lines) == 2:
            lines.append("No borrow records.\n")
        self.report_box.insert("1.0", "".join(lines))
    
    def export_all_to_csv(self):
        from core.exporter import export_borrow_report_to_csv
        filename, msg = export_borrow_report_to_csv()
        if filename:
            messagebox.showinfo("Export Successful", f"{msg}\nSaved to: {filename}")
        else:
            messagebox.showwarning("No Data", msg)

    def export_all_to_txt(self):
        from core.exporter import export_borrow_report_to_txt
        filename, msg = export_borrow_report_to_txt()
        if filename:
            messagebox.showinfo("Export Successful", f"{msg}\nSaved to: {filename}")
        else:
            messagebox.showwarning("No Data", msg)

    def export_current_to_csv(self):
        from core.exporter import export_currently_borrowed_to_csv
        filename, msg = export_currently_borrowed_to_csv()
        if filename:
            messagebox.showinfo("Export Successful", f"{msg}\nSaved to: {filename}")
        else:
            messagebox.showwarning("No Data", msg)

def main():
    from core.db import init_db
    from core.auth import seed_admin
    init_db()
    seed_admin()
    
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()