import pymysql


def execute_update(connection, update_type):
    """Execute predefined update operations with cascading updates"""
    try:
        with connection.cursor() as cursor:
            if update_type == 1:  # Change Number of Seats in Program
                print("\nUpdate Number of Seats in Program")
                program_id = input("Enter Program ID: ")
                category = input("Enter Category: ")
                institute_name = input("Enter Institute Name: ")

                # Show current seats for the given program, category, and institute
                cursor.execute("""
                    SELECT Seats 
                    FROM NumberSeats_CategoryWise 
                    WHERE Program_ID = %s AND Category = %s AND Institute_Name = %s
                """, (program_id, category, institute_name))
                result = cursor.fetchone()

                if result:
                    print(f"Current number of seats in program for this institute: {result[0]}")
                    new_seats = int(input("Enter new number of seats: "))

                    # Begin transaction
                    cursor.execute("START TRANSACTION")

                    # Update seats in NumberSeats_CategoryWise for the specific institute
                    cursor.execute("""
                        UPDATE NumberSeats_CategoryWise 
                        SET Seats = %s 
                        WHERE Program_ID = %s AND Category = %s AND Institute_Name = %s
                    """, (new_seats, program_id, category, institute_name))

                    # Recalculate total seats for the program across all institutes
                    cursor.execute("""
                        SELECT SUM(Seats) 
                        FROM NumberSeats_CategoryWise 
                        WHERE Program_ID = %s AND Category = %s
                    """, (program_id, category))
                    total_program_seats = cursor.fetchone()[0] or 0

                    # Update total seats in NumberSeats_in_Program
                    cursor.execute("""
                        UPDATE NumberSeats_in_Program 
                        SET Seats = %s 
                        WHERE Program_ID = %s AND Category = %s
                    """, (total_program_seats, program_id, category))

                    # Recalculate total seats for the institute across all programs
                    cursor.execute("""
                        SELECT SUM(Seats) 
                        FROM NumberSeats_CategoryWise 
                        WHERE Institute_Name = %s AND Category = %s
                    """, (institute_name, category))
                    total_institute_seats = cursor.fetchone()[0] or 0

                    # Update total seats in NumberSeats_in_Institute
                    cursor.execute("""
                        INSERT INTO NumberSeats_in_Institute 
                        (Institute_Name, Category, Seats) 
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE Seats = VALUES(Seats)
                    """, (institute_name, category, total_institute_seats))

                    # Commit the transaction
                    connection.commit()
                    print("Seats updated successfully across all related tables.")
                else:
                    print("No matching record found for the given program, category, and institute.")

            elif update_type == 2:  # Update Payment Amount
                print("\nUpdate Payment Amount")
                student_id = input("Enter Student ID: ")
                exam_name = input("Enter Exam Name: ")
                
                cursor.execute("START TRANSACTION")
                
                cursor.execute("""
                    SELECT p.*, s.FirstName, s.LastName 
                    FROM Payment p
                    JOIN Student s ON p.Student_ID = s.Student_ID
                    WHERE p.Student_ID = %s AND p.Name_of_Exam = %s
                """, (student_id, exam_name))
                payments = cursor.fetchall()
                
                if payments:
                    print("\nExisting payments for student:")
                    print(f"Student: {payments[0][-2]} {payments[0][-1]}")
                    for payment in payments:
                        print(f"Institute: {payment[1]}, Program: {payment[2]}, Current Amount: {payment[4]}")
                    
                    institute = input("Enter Institute Name: ")
                    program = input("Enter Program ID: ")
                    new_amount = float(input("Enter new payment amount: "))
                    
                    cursor.execute("""
                        UPDATE Payment 
                        SET Amount = %s, Payment_Date = CURRENT_DATE
                        WHERE Student_ID = %s AND Institute_Name = %s 
                        AND Program_ID = %s AND Name_of_Exam = %s
                    """, (new_amount, student_id, institute, program, exam_name))
                    
                    connection.commit()
                    print("Payment record updated successfully.")
                else:
                    print("No payment records found for this student and exam.")

            elif update_type == 3:  # Modify Exam Date
                print("\nUpdate Exam Date")
                exam_name = input("Enter Exam Name: ")
                
                cursor.execute("START TRANSACTION")
                
                cursor.execute("""
                    SELECT e.Date_of_Examination, cr.Round_ID, cr.Start_Date, cr.End_Date
                    FROM Exam e
                    LEFT JOIN Counselling_Round cr ON e.Name_of_Exam = cr.Name_of_Exam
                    WHERE e.Name_of_Exam = %s
                """, (exam_name,))
                results = cursor.fetchall()
                
                if results:
                    current_date = results[0][0]
                    print(f"Current exam date: {current_date}")
                    print("\nRelated counselling rounds:")
                    for result in results:
                        if result[1]:  # If there are counselling rounds
                            print(f"Round {result[1]}: {result[2]} to {result[3]}")
                    
                    new_date = input("Enter new exam date (YYYY-MM-DD): ")
                    
                    # Update exam date
                    cursor.execute("""
                        UPDATE Exam 
                        SET Date_of_Examination = %s 
                        WHERE Name_of_Exam = %s
                    """, (new_date, exam_name))
                    
                    # Adjust counselling round dates if needed
                    adjust = input("Do you want to adjust counselling round dates? (y/n): ")
                    if adjust.lower() == 'y':
                        for result in results:
                            if result[1]:
                                round_id = result[1]
                                new_start = input(f"Enter new start date for round {round_id} (YYYY-MM-DD): ")
                                new_end = input(f"Enter new end date for round {round_id} (YYYY-MM-DD): ")
                                
                                cursor.execute("""
                                    UPDATE Counselling_Round
                                    SET Start_Date = %s, End_Date = %s
                                    WHERE Round_ID = %s
                                """, (new_start, new_end, round_id))
                    
                    connection.commit()
                    print("Exam date and related counselling rounds updated successfully.")
                else:
                    print("Exam not found.")

            elif update_type == 4:  # Update Student's Address
                print("\nUpdate Student's Address")
                student_id = input("Enter Student ID: ")
                
                cursor.execute("START TRANSACTION")
                
                cursor.execute("""
                    SELECT s.*, a.Area, a.City, a.State 
                    FROM Student s 
                    JOIN Address a ON s.Zip = a.Zip 
                    WHERE s.Student_ID = %s
                """, (student_id,))
                result = cursor.fetchone()
                
                if result:
                    print("\nCurrent address details:")
                    print(f"Street: {result[8]}")
                    print(f"ZIP: {result[9]}")
                    print(f"Area: {result[10]}")
                    print(f"City: {result[11]}")
                    print(f"State: {result[12]}")
                    
                    new_street = input("Enter new street (or press enter to keep current): ")
                    
                    # Loop until a valid ZIP code is provided
                    new_zip = input("Enter new ZIP code (or press enter to keep current): ")
                    while new_zip:
                        cursor.execute("SELECT 1 FROM Address WHERE Zip = %s", (new_zip,))
                        if cursor.fetchone():
                            break  # ZIP code exists, exit loop
                        print("New ZIP not found in database. Please enter an existing ZIP code.")
                        new_zip = input("Enter new ZIP code (or press enter to keep current): ")
                    
                    # Update student address
                    updates = []
                    params = []
                    if new_street:
                        updates.append("Street = %s")
                        params.append(new_street)
                    if new_zip:
                        updates.append("Zip = %s")
                        params.append(new_zip)
                    
                    if updates:
                        params.append(student_id)
                        cursor.execute(f"""
                            UPDATE Student 
                            SET {', '.join(updates)}
                            WHERE Student_ID = %s
                        """, tuple(params))
                        
                        connection.commit()
                        print("Address updated successfully.")
                    else:
                        print("No changes made to address.")
                else:
                    print("Student not found.")



            elif update_type == 5:  # Update Seat Allotment Status
                print("\nUpdate Seat Allotment Status")
                student_id = input("Enter Student ID: ")
                round_id = input("Enter Round ID: ")
                
                cursor.execute("START TRANSACTION")
                
                cursor.execute("""
                    SELECT sa.*, s.FirstName, s.LastName, p.Name
                    FROM Seat_Alloted sa
                    JOIN Student s ON sa.Student_ID = s.Student_ID
                    JOIN Program p ON sa.Program_ID = p.Program_ID
                    WHERE sa.Student_ID = %s AND sa.Round_ID = %s
                """, (student_id, round_id))
                result = cursor.fetchone()
                
                if result:
                    print(f"\nStudent: {result[-2]} {result[-1]}")
                    print(f"Institute: {result[1]}")
                    print(f"Program: {result[-1]}")
                    print(f"Current status: {result[4]}")
                    
                    print("\nAvailable statuses: Confirmed, Withdrawn, Pending")
                    new_status = input("Enter new status: ")
                    
                    cursor.execute("""
                        UPDATE Seat_Alloted 
                        SET Seat_Status = %s 
                        WHERE Student_ID = %s AND Round_ID = %s AND Institute_Name = %s AND Program_ID = %s
                    """, (new_status, student_id, round_id, result[1], result[2]))
                    
                    # # If status is Withdrawn, update available seats
                    # if new_status == 'Withdrawn':
                    #     # Get student category
                    #     cursor.execute("""
                    #         SELECT Category 
                    #         FROM Gives_Exam ge
                    #         JOIN Counselling_Round cr ON ge.Exam = cr.Name_of_Exam
                    #         WHERE cr.Round_ID = %s AND ge.Student_ID = %s
                    #     """, (round_id, student_id))
                    #     category = cursor.fetchone()[0]
                        
                    #     # Increase available seats
                    #     cursor.execute("""
                    #         UPDATE NumberSeats_CategoryWise 
                    #         SET Seats = Seats + 1
                    #         WHERE Program_ID = %s AND Institute_Name = %s AND Category = %s
                    #     """, (result[2], result[1], category))
                    
                    connection.commit()
                    print("Seat status updated successfully.")
                else:
                    print("Seat allotment record not found.")

            elif update_type == 6:  # Update Institute Parent Name
                print("\nUpdate Institute Parent Name")
                institute_name = input("Enter Institute Name: ")
                
                cursor.execute("START TRANSACTION")
                
                cursor.execute("""
                    SELECT i.*, GROUP_CONCAT(t.Type) as Types
                    FROM Institute i
                    LEFT JOIN Types t ON i.Name = t.Institute_Name
                    WHERE i.Name = %s
                    GROUP BY i.Name
                """, (institute_name,))
                result = cursor.fetchone()
                
                if result:
                    print(f"\nCurrent details:")
                    print(f"Parent Institute: {result[1]}")
                    print(f"Ranking: {result[2]}")
                    print(f"Types: {result[6]}")
                    
                    new_parent = input("Enter new parent institute name: ")
                    
                    # Verify new parent exists
                    cursor.execute("SELECT 1 FROM Institute WHERE Name = %s", (new_parent,))
                    if cursor.fetchone() or new_parent == institute_name:
                        cursor.execute("""
                            UPDATE Institute 
                            SET Parent_Institute_Name = %s 
                            WHERE Name = %s
                        """, (new_parent, institute_name))
                        
                        connection.commit()
                        print("Parent institute updated successfully.")
                    else:
                        print("New parent institute not found in database.")
                else:
                    print("Institute not found.")

    except Exception as e:
        print(f"Error during update: {e}")
        connection.rollback()

def execute_update_menu(connection):
    """Display update menu and handle user choice"""
    while True:
        print("\nUpdate Operations:")
        print("1. Change the Number of Seats in a Program")
        print("2. Update the Payment Amount")
        print("3. Modify Exam Date")
        # print("4. Change the Start Date of a Counselling Round")
        print("4. Update Student's Address")
        print("5. Update Seat Allotment Status")
        print("6. Update Institute Parent Name")
        print("9. Go back to main menu")

        choice = input("Enter your choice (1-9): ")
        
        if choice == '9':
            break
        elif choice.isdigit() and 1 <= int(choice) <= 8:
            execute_update(connection, int(choice))
        else:
            print("Invalid choice. Please try again.")
        
def execute_query(connection, query, params=None):
    """Execute a query and handle the results."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                for row in results:
                    print(row)
            else:
                connection.commit()
                print("Operation successful.")
    except Exception as e:
        print(f"Error: {e}")

def get_table_columns(connection, table_name):
    """Get column information for a specific table."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            return columns
    except Exception as e:
        print(f"Error getting table structure: {e}")
        return None


def get_table_columns(connection, table_name):
    """Retrieve column information for a given table."""
    query = f"""
    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY, EXTRA 
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = '{table_name}' AND TABLE_SCHEMA = DATABASE();
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

# def execute_query(connection, query, params):
#     """Execute a query with given parameters."""
#     with connection.cursor() as cursor:
#         cursor.execute(query, params)
#         connection.commit()
#         print("Query executed successfully.")

def check_foreign_key(connection, table_name, column, value):
    """Check if a foreign key value exists in the referenced table."""
    query = f"SELECT COUNT(*) FROM {table_name} WHERE {column} = %s"
    with connection.cursor() as cursor:
        cursor.execute(query, (value,))
        return cursor.fetchone()[0] > 0

def insert_student(connection):
    """Insert a new student record while maintaining integrity."""
    print("Insert into Student Table")
    columns = get_table_columns(connection, 'Student')
    if not columns:
        return
    
    data = {}
    for col in columns:
        field_name = col[0]
        is_nullable = col[2]  # Whether the column allows NULL values
        
        if field_name == 'Student_ID':
            while True:
                value = input(f"Enter {field_name} (unique ID): ")
                if value.isdigit():
                    data[field_name] = int(value)
                    break
                print("Invalid ID. Please enter a numeric value.")
        
        elif field_name == 'Zip':
            while True:
                zip_value = input(f"Enter {field_name} (must exist in Address table): ")
                if check_foreign_key(connection, 'Address', 'Zip', zip_value):
                    data[field_name] = zip_value
                    break
                print("Invalid Zip. Please provide a valid value from Address table.")
        
        elif field_name == 'Date_of_Birth':
            while True:
                dob = input(f"Enter {field_name} (must exist in Date_of_Birth table): ")
                if check_foreign_key(connection, 'Date_of_Birth', 'Date_of_Birth', dob):  # Check against the Date_of_Birth table
                    data[field_name] = dob
                    break
                print("Invalid Date of Birth. Please provide a valid value from Date_of_Birth table.")
        
        else:
            value = input(f"Enter {field_name}: ")
            data[field_name] = value if value.strip() else None
    
    # Build the INSERT query
    columns_str = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO Student ({columns_str}) VALUES ({placeholders})"
    execute_query(connection, query, tuple(data.values()))
    
def insert_institute(connection):
    """Insert a new institute record while maintaining integrity."""
    print("Insert into Institute Table")
    columns = get_table_columns(connection, 'Institute')
    if not columns:
        return

    data = {}
    for col in columns:
        field_name = col[0]
        if field_name == 'Zip':
            while True:
                zip_value = input(f"Enter {field_name} (must exist in Address table): ")
                if check_foreign_key(connection, 'Address', 'Zip', zip_value):
                    data[field_name] = zip_value
                    break
                print("Invalid Zip. Please provide a valid value from Address table.")
        elif field_name == 'Parent_Institute_Name':
            value = input(f"Enter {field_name} (or leave blank for none): ")
            if value and not check_foreign_key(connection, 'Institute', 'Name', value):
                print("Invalid Parent Institute Name.")
            else:
                data[field_name] = value if value.strip() else None
        else:
            value = input(f"Enter {field_name}: ")
            data[field_name] = value if value.strip() else None
    
    # Build the INSERT query
    columns_str = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO Institute ({columns_str}) VALUES ({placeholders})"
    execute_query(connection, query, tuple(data.values()))

def insert_program(connection):
    """Insert a new program record while maintaining integrity."""
    print("Insert into Program Table")
    columns = get_table_columns(connection, 'Program')
    if not columns:
        return

    data = {}
    for col in columns:
        field_name = col[0]
        value = input(f"Enter {field_name}: ")
        data[field_name] = value if value.strip() else None
    
    # Build the INSERT query
    columns_str = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO Program ({columns_str}) VALUES ({placeholders})"
    execute_query(connection, query, tuple(data.values()))

def delete_from_table(connection):
    """Delete data from a table with cascading deletes."""
    table_name = input("Enter the table name: ")
    condition = input("Enter the condition for deletion (e.g., id=1): ")
    confirm = input(f"Are you sure you want to delete records from {table_name} where {condition}? (yes/no): ")
    if confirm.lower() == 'yes':
        query = f"DELETE FROM {table_name} WHERE {condition}"
        execute_query(connection, query)
        print(f"Record(s) deleted from {table_name}.")
    else:
        print("Operation canceled.")

def clear_table(connection):
    """Clear all data from a table."""
    table_name = input("Enter the table name to clear: ")
    confirm = input(f"Are you sure you want to delete all records from {table_name}? (yes/no): ")
    if confirm.lower() == 'yes':
        query = f"DELETE FROM {table_name}"
        execute_query(connection, query)
        print(f"All records cleared from {table_name}.")
    else:
        print("Operation canceled.")

def clear_database(connection):
    """Clear all data from the database while maintaining table structure."""
    confirm = input("Are you sure you want to clear the entire database? (yes/no): ")
    if confirm.lower() == 'yes':
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET FOREIGN_KEY_CHECKS=0;")  # Disable foreign key checks
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                for table in tables:
                    cursor.execute(f"DELETE FROM {table[0]};")
                cursor.execute("SET FOREIGN_KEY_CHECKS=1;")  # Enable foreign key checks
                connection.commit()
            print("Database cleared.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Operation canceled.")
               
def display_tables(connection):
    """Display all available tables and allow user to select one to view."""
    try:
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            
            if not tables:
                print("No tables found in the database.")
                return
            
            print("\nAvailable Tables:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")
            
            print("\nOptions:")
            print("0. Go back")
            print("A. Display all tables' content")
            choice = input("\nEnter table number to view its content or 'A' for all tables: ").strip()
            
            if choice.lower() == 'a':
                display_all_tables(connection, tables)
            elif choice.isdigit():
                choice = int(choice)
                if choice == 0:
                    return
                if 1 <= choice <= len(tables):
                    display_table_content(connection, tables[choice-1][0])
                else:
                    print("Invalid table number.")
            else:
                print("Invalid choice.")
                
    except Exception as e:
        print(f"Error: {e}")

def display_table_content(connection, table_name):
    """Display the content of a specific table with formatted output."""
    try:
        with connection.cursor() as cursor:
            # Get column names
            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            # Get table content
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            if not rows:
                print(f"\nTable '{table_name}' is empty.")
                return
            
            # Calculate column widths for formatting
            col_widths = [len(str(col)) for col in column_names]
            for row in rows:
                for i, val in enumerate(row):
                    col_widths[i] = max(col_widths[i], len(str(val)))
            
            # Print table header
            print(f"\nTable: {table_name}")
            print("-" * (sum(col_widths) + (3 * len(col_widths)) + 1))
            header = "| "
            for i, col in enumerate(column_names):
                header += f"{col:<{col_widths[i]}} | "
            print(header)
            print("-" * (sum(col_widths) + (3 * len(col_widths)) + 1))
            
            # Print table content
            for row in rows:
                row_str = "| "
                for i, val in enumerate(row):
                    row_str += f"{str(val):<{col_widths[i]}} | "
                print(row_str)
            print("-" * (sum(col_widths) + (3 * len(col_widths)) + 1))
            print(f"Total rows: {len(rows)}")
            
    except Exception as e:
        print(f"Error displaying table {table_name}: {e}")

def display_all_tables(connection, tables):
    """Display the content of all tables in the database."""
    print("\nDisplaying all tables' content:")
    print("=" * 50)
    
    for table in tables:
        display_table_content(connection, table[0])
        print("\n" + "=" * 50)

def execute_predefined_query(connection):
    """Execute predefined queries based on user choice."""
    print("Select a query to execute:")
    queries = [
        "Retrieve all students and their corresponding address details.",
        "List programs offered by a specific institute along with their details.",
        "Find students eligible for admission in a specific program and institute through a particular exam.",
        "Get the count of seats available category-wise for a specific program in an institute.",
        "Retrieve payment details for students who made payments for a particular exam."
    ]
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        query = """
        SELECT S.Student_ID, S.FirstName, S.LastName, A.Area, A.City, A.State 
        FROM Student S
        JOIN Address A ON S.Zip = A.Zip;
        """
    elif choice == 2:
        institute_name = input("Enter institute name: ")
        query = """
        SELECT I.Name AS Institute_Name, P.Program_ID, P.Name AS Program_Name, P.Duration, P.Degree 
        FROM Institute I
        JOIN Offers_Program OP ON I.Name = OP.Institute_Name
        JOIN Program P ON OP.Program = P.Program_ID
        WHERE I.Name = %s;
        """
        execute_query(connection, query, (institute_name,))
        return
    elif choice == 3:
        exam = input("Enter the exam name: ")
        program = input("Enter the program ID: ")
        institute = input("Enter the institute name: ")
        query = """
        SELECT E.Student_ID, S.FirstName, S.LastName, E.Program, E.Institute 
        FROM Eligibility_for_Admission E
        JOIN Student S ON E.Student_ID = S.Student_ID
        WHERE E.Exam = %s AND E.Program = %s AND E.Institute = %s;
        """
        execute_query(connection, query, (exam, program, institute))
        return
    elif choice == 4:
        program_id = input("Enter program ID: ")
        institute_name = input("Enter institute name: ")
        query = """
        SELECT N.Category, N.Seats 
        FROM NumberSeats_CategoryWise N
        WHERE N.Program_ID = %s AND N.Institute_Name = %s;
        """
        execute_query(connection, query, (program_id, institute_name))
        return
    elif choice == 5:
        exam_name = input("Enter exam name: ")
        query = """
        SELECT P.Student_ID, S.FirstName, S.LastName, P.Payment_Date, P.Amount, P.Institute_Name, P.Program_ID 
        FROM Payment P
        JOIN Student S ON P.Student_ID = S.Student_ID
        WHERE P.Name_of_Exam = %s;
        """
        execute_query(connection, query, (exam_name,))
        return
    else:
        print("Invalid choice.")
        return

    execute_query(connection, query)

def insert (connection):
    """Insert data into tables based on user choice."""
    print("Select a table to insert data into:")
    tables = [
        "Student",
        "Institute",
        "Program",
    ]
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        insert_student(connection)
    elif choice == 2:
        insert_institute(connection)
    elif choice == 3:
        insert_program(connection)
    else:
        print("Invalid choice. Please try again.")
            
def main():
    """Main function to manage menu-driven database operations."""
    connection = pymysql.connect(
        host='localhost',
        user='newuser',
        password='StrongPass@123',
        database='DnAproject'
    )

    while True:
        print("\nMenu:")
        print("1. Execute predefined query")
        print("2. Insert into table")
        # print("3. Delete from table (with cascading)")
        # print("3. Clear table")
        print("3. Clear database")
        print("4. Display tables")
        print("5. Update records")
        print("6. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            execute_predefined_query(connection)
        elif choice == '2':
            insert(connection)
        elif choice == '3':
            clear_database(connection)
        elif choice == '4':
            display_tables(connection)
        elif choice == '5':
            execute_update_menu(connection)
        elif choice == '6':
            break
        else:
            print("Invalid choice. Please try again.")
    connection.close()

if __name__ == "__main__":
    main()





































