from flask import Flask, request, jsonify
import heapq

app = Flask(__name__)

# Global heap to store meetings across requests
meetings_heap = []

@app.route("/")
def home_page():
    return "Welcome to the home page!"

@app.route('/schedule', methods=['GET', 'POST'])
def new_schedule():
    if request.method == 'POST':
        new_schedule = request.get_json()
        title = new_schedule.get('title')
        start = int(new_schedule.get('start'))
        duration = int(new_schedule.get('duration'))
        
        # Calculate end_time with proper hour handling
        end_time = start + duration
        
        # Handle minute overflow (e.g., 1340 + 30 = 1410, but 1350 + 20 = 1410 not 1370)
        start_hour = start // 100
        start_min = start % 100
        
        end_min = start_min + duration
        end_hour = start_hour
        
        # Loop to handle minute overflow
        while end_min >= 60:
            end_min -= 60
            end_hour += 1
        
        end_time = end_hour * 100 + end_min
        
        # Check for overlaps - loop through each meeting in the heap
        has_conflict = False
        conflict_title = ""
        
        for meeting in meetings_heap:
            existing_start = meeting[0]
            existing_end = meeting[1]
            existing_title = meeting[2]
            
            # Check if new meeting overlaps with existing meeting
            # For each minute, check if there's overlap
            if start < existing_end and end_time > existing_start:
                has_conflict = True
                conflict_title = existing_title
                break
        
        # If there's a conflict, return error
        if has_conflict:
            return jsonify({
                "error": "Conflict detected",
                "message": f"Meeting '{title}' conflicts with existing meeting '{conflict_title}'"
            }), 400
        
        # No conflict - add to heap
        meeting_tuple = (start, end_time, title)
        heapq.heappush(meetings_heap, meeting_tuple)
        
        # Return all meetings in JSON format
        return jsonify({
            "message": "Meeting scheduled successfully",
            "meetings": [
                {"start": m[0], "end": m[1], "title": m[2]} 
                for m in sorted(meetings_heap)
            ]
        }), 201
    
    elif request.method == 'GET':
        # Return all scheduled meetings
        return jsonify({
            "meetings": [
                {"start": m[0], "end": m[1], "title": m[2]} 
                for m in sorted(meetings_heap)
            ]
        })

if __name__ == '__main__':
    app.run(debug=True)