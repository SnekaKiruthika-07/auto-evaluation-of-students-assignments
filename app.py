import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Predefined test cases (input and expected output)
test_cases = [
    {"input": "5\n", "expected": "25\n"},
    {"input": "3\n", "expected": "9\n"}
]

# Directory to save student submissions
UPLOAD_FOLDER = 'submissions'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and file.filename.endswith('.py'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Evaluate the student's submission
        result = evaluate_code(filepath)
        
        return render_template('result.html', result=result)
    else:
        flash('Please upload a Python file')
        return redirect(request.url)

def evaluate_code(filepath):
    results = []
    for i, test_case in enumerate(test_cases):
        input_data = test_case["input"]
        expected_output = test_case["expected"]
        
        try:
            # Run the student's code
            process = subprocess.Popen(['python', filepath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output, error = process.communicate(input=input_data)
            
            # Compare the output with the expected output
            if output == expected_output:
                results.append(f"Test case {i+1}: Passed")
            else:
                results.append(f"Test case {i+1}: Failed. Expected '{expected_output.strip()}', got '{output.strip()}'")
        except Exception as e:
            results.append(f"Test case {i+1}: Error occurred: {str(e)}")
    
    return results

@app.route('/admin')
def view_submissions():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('admin.html', files=files)

@app.route('/evaluate/<filename>')
def evaluate_submission(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    result = evaluate_code(filepath)
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
