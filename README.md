
## Admission Counseling System Database 

This repository contains the complete implementation of a **Centralized Admission Counseling System Database**, developed as a part of the Database Management Systems (DBMS) course project. The system is modeled on real-world centralized admission procedures used in various competitive examinations such as JEE, NEET, GATE, and others. It aims to simulate the end-to-end process of candidate data management, seat allocation, counseling rounds, payment tracking, and quota distribution across academic programs and institutions.

### Project Objective

The primary objective of this project is to design and develop a relational database system that accurately captures the complexities of an admission counseling process. The system is built using database normalization principles and supports a variety of operations for managing and querying data. The project workflow involved converting an ER model to a normalized relational schema and developing sample operations that reflect real-world use cases.

---

### Methodology

#### 1. **Mini-World Definition**
A simplified abstraction of a real-world centralized admission system was defined. The system accommodates:
- Students who appear in various entrance exams
- Educational institutions offering multiple academic programs
- Multiple rounds of counseling
- Payment procedures and eligibility verification
- Preferences submitted by students

#### 2. **ER Diagram Design**
The ER model includes:
- **Strong entities**: Student, Institute, Program, Exam
- **Weak entities**: Preference, Counselling Round
- **Subclasses**: Special Counselling Round
- **Multivalued and composite attributes**
- **Various relationship types**: 1:N, M:N, and N-ary relationships such as “Eligibility,” “Payment,” and “Seat Allotment”
- **Self-referencing relationships** for institute hierarchy

#### 3. **Conversion to Relational Model**
- Each entity and relationship was mapped to relational tables with proper use of primary and foreign keys.
- Composite and multivalued attributes were decomposed into simpler relations.
- Weak entities and identifying relationships were handled using foreign key constraints.
- Subclass handling was implemented via relation extension techniques.

#### 4. **Normalization**
- **First Normal Form (1NF)**: Ensured atomicity by eliminating multivalued and composite attributes.
- **Second Normal Form (2NF)**: Removed partial dependencies in relations with composite keys.
- **Third Normal Form (3NF)**: Eliminated transitive dependencies by decomposing tables further (e.g., ZIP code to city/state mapping, DOB to Age).

#### 5. **Functional Specification**
- Designed to support all major CRUD operations.
- Enforced data integrity through key and referential constraints.
- Developed support for analysis and reporting queries.

#### 6. **Implementation of Database Operations**
- **Insertions**: Add student details, programs, exam records, counseling rounds, and preferences.
- **Retrievals**: Fetch students by exam, institutes by program, eligibility data, and payment summaries.
- **Updates**: Change seat counts, payment amounts, and address information.
- **Deletions**: Remove student preferences, unoffered programs, and withdrawn entries.

---

### Key Highlights

- Accurately models real-world admission workflows
- Supports multiple user roles: students, institutions, administrators
- Implements n-ary relationships and complex participation constraints
- Optimized through normalization to minimize redundancy and maintain consistency
- Designed to handle real-world queries like fee tracking, round-wise allocation, and eligibility checks

---

### Example Use Cases

- List all students who appeared for a specific examination
- Identify programs eligible for a student based on exam performance
- View seat allocation statistics per round and institute
- Track student payments and verify payment completion
- Modify institute seat matrices or remove withdrawn preferences

---

This project demonstrates a complete design and implementation cycle of a complex database system, adhering to best practices in conceptual modeling, relational mapping, and normalization. It reflects a practical application of database theory in solving real-world problems in educational admission systems.
