import csv
import os
from datetime import datetime
from core.borrow import list_all_borrowed
from core.students import find_student
from core.books import find_book

def export_borrow_report_to_csv():

    os.makedirs("exports", exist_ok=True)
    

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/borrow_report_{timestamp}.csv"
    

    borrow_records = list_all_borrowed()
    
    if not borrow_records:
        return None, "No borrow records to export."
    

    export_data = []
    for record in borrow_records:
        student = find_student(record["student_id"]) or {}
        book = find_book(record["book_id"]) or {}
        
        export_data.append({
            "Borrow ID": record.get("borrow_id", ""),
            "Student ID": record.get("student_id", ""),
            "Student Name": student.get("name", "Unknown"),
            "Book ID": record.get("book_id", ""),
            "Book Title": book.get("title", "Unknown"),
            "Borrow Date": record.get("borrow_date", ""),
            "Due Date": record.get("due_date", ""),
            "Return Date": record.get("return_date", "Not Returned"),
            "Fine Amount": record.get("fine_amount", 0),
            "Fine Paid": "Yes" if record.get("fine_paid", 0) == 1 else "No"
        })
    

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Borrow ID", "Student ID", "Student Name", "Book ID", "Book Title", 
                      "Borrow Date", "Due Date", "Return Date", "Fine Amount", "Fine Paid"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(export_data)
    
    return filename, f"Successfully exported {len(export_data)} records."


def export_borrow_report_to_txt():
    
    os.makedirs("exports", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/borrow_report_{timestamp}.txt"
    
    borrow_records = list_all_borrowed()
    
    if not borrow_records:
        return None, "No borrow records to export."
    
    with open(filename, 'w', encoding='utf-8') as txtfile:

        txtfile.write("="*80 + "\n")
        txtfile.write("LIBRARY MANAGEMENT SYSTEM - BORROW/RETURN REPORT\n")
        txtfile.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        txtfile.write("="*80 + "\n\n")
        
        for i, record in enumerate(borrow_records, 1):
            student = find_student(record["student_id"]) or {}
            book = find_book(record["book_id"]) or {}
            
            txtfile.write(f"Record #{i}\n")
            txtfile.write("-"*40 + "\n")
            txtfile.write(f"Borrow ID:     {record.get('borrow_id', '')}\n")
            txtfile.write(f"Student ID:    {record.get('student_id', '')}\n")
            txtfile.write(f"Student Name:  {student.get('name', 'Unknown')}\n")
            txtfile.write(f"Book ID:       {record.get('book_id', '')}\n")
            txtfile.write(f"Book Title:    {book.get('title', 'Unknown')}\n")
            txtfile.write(f"Borrow Date:   {record.get('borrow_date', '')}\n")
            txtfile.write(f"Due Date:      {record.get('due_date', '')}\n")
            txtfile.write(f"Return Date:   {record.get('return_date', 'Not Returned')}\n")
            txtfile.write(f"Fine Amount:   ₹{record.get('fine_amount', 0)}\n")
            txtfile.write(f"Fine Paid:     {'Yes' if record.get('fine_paid', 0) == 1 else 'No'}\n")
            txtfile.write("\n")
        
        # Write summary
        txtfile.write("="*80 + "\n")
        txtfile.write("SUMMARY\n")
        txtfile.write("="*80 + "\n")
        
        total_records = len(borrow_records)
        active_borrows = len([r for r in borrow_records if r.get('return_date') is None])
        returned = total_records - active_borrows
        total_fine = sum(r.get('fine_amount', 0) for r in borrow_records)
        
        txtfile.write(f"Total Borrow Records: {total_records}\n")
        txtfile.write(f"Active Borrows:       {active_borrows}\n")
        txtfile.write(f"Returned Books:       {returned}\n")
        txtfile.write(f"Total Fine Collected: ₹{total_fine}\n")
        txtfile.write("="*80 + "\n")
    
    return filename, f"Successfully exported {len(borrow_records)} records."


def export_currently_borrowed_to_csv():
    
    os.makedirs("exports", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/currently_borrowed_{timestamp}.csv"
    
    from core.borrow import list_currently_borrowed
    borrow_records = list_currently_borrowed()
    
    if not borrow_records:
        return None, "No currently borrowed books."
    
    export_data = []
    for record in borrow_records:
        student = find_student(record["student_id"]) or {}
        book = find_book(record["book_id"]) or {}
        
        export_data.append({
            "Borrow ID": record.get("borrow_id", ""),
            "Student ID": record.get("student_id", ""),
            "Student Name": student.get("name", "Unknown"),
            "Book ID": record.get("book_id", ""),
            "Book Title": book.get("title", "Unknown"),
            "Borrow Date": record.get("borrow_date", ""),
            "Due Date": record.get("due_date", ""),
            "Fine (if overdue)": record.get("fine_amount", 0)
        })
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["Borrow ID", "Student ID", "Student Name", "Book ID", "Book Title", 
                      "Borrow Date", "Due Date", "Fine (if overdue)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(export_data)
    
    return filename, f"Successfully exported {len(export_data)} currently borrowed books."