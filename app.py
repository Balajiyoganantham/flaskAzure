import os
from flask import Flask, request, jsonify
import pyodbc

app = Flask(__name__)

# Database connection string
conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=azure-flask-db-server.database.windows.net;'  # Your server name
    'DATABASE=StudentDB;'  # Your database name
    'UID=Balaji;'  # Your username
    'PWD=Monica@@@@@4;'  # Your password
)

# Function to establish a database connection
def get_db_connection():
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        raise Exception(f"Database connection failed: {e}")

# Test connection route
@app.route('/test-connection', methods=['GET'])
def test_connection():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'message': 'Connection successful!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get all students
@app.route('/students', methods=['GET'])
def get_students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students')
        students = []
        for row in cursor.fetchall():
            students.append({
                'id': row[0],
                'name': row[1],
                'age': row[2]
            })
        conn.close()
        return jsonify(students)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get a single student by ID
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students WHERE ID = ?', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify({
                'id': row[0],
                'name': row[1],
                'age': row[2]
            })
        return jsonify({'error': 'Student not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Create a new student
@app.route('/students', methods=['POST'])
def create_student():
    if not request.json or not 'name' in request.json or not 'age' in request.json:
        return jsonify({'error': 'Name and age are required'}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Students (Name, Age) VALUES (?, ?)',
            (request.json['name'], request.json['age'])
        )
        conn.commit()
        cursor.execute('SELECT @@IDENTITY')
        new_id = cursor.fetchone()[0]
        conn.close()
        return jsonify({
            'id': new_id,
            'name': request.json['name'],
            'age': request.json['age']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update a student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    if not request.json:
        return jsonify({'error': 'No data provided'}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students WHERE ID = ?', (id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Student not found'}), 404
        update_fields = []
        params = []
        if 'name' in request.json:
            update_fields.append('Name = ?')
            params.append(request.json['name'])
        if 'age' in request.json:
            update_fields.append('Age = ?')
            params.append(request.json['age'])
        if update_fields:
            params.append(id)
            cursor.execute(
                f'UPDATE Students SET {", ".join(update_fields)} WHERE ID = ?',
                tuple(params)
            )
            conn.commit()
        conn.close()
        return jsonify({'message': 'Student updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Delete a student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Students WHERE ID = ?', (id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Student not found'}), 404
        cursor.execute('DELETE FROM Students WHERE ID = ?', (id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
