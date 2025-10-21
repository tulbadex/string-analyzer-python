# String Analyzer API

A FastAPI-based REST API service that analyzes strings and stores their computed properties.

## Features

- **String Analysis**: Computes length, palindrome status, unique characters, word count, SHA-256 hash, and character frequency
- **CRUD Operations**: Create, read, update, and delete string records
- **Advanced Filtering**: Filter strings by multiple criteria
- **Natural Language Queries**: Query strings using natural language patterns
- **In-Memory Storage**: Fast, lightweight data storage

## API Endpoints

### 1. Create/Analyze String
```
POST /strings
Content-Type: application/json

{
  "value": "string to analyze"
}
```

### 2. Get Specific String
```
GET /strings/{string_value}
```

### 3. Get All Strings with Filtering
```
GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
```

### 4. Natural Language Filtering
```
GET /strings/filter-by-natural-language?query=all%20single%20word%20palindromic%20strings
```

### 5. Delete String
```
DELETE /strings/{string_value}
```

## Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```
5. Access API documentation at: http://localhost:8000/docs

## Deployment

### Ubuntu Server Deployment

1. Copy files to your server
2. Make deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```
3. Run deployment script:
   ```bash
   ./deploy.sh
   ```

The deployment script will:
- Install Python 3.11, Nginx, and dependencies
- Set up systemd service
- Configure Nginx reverse proxy
- Start all services

### Manual Deployment Steps

1. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3.11 python3.11-pip python3.11-venv nginx
   ```

2. **Setup Application**:
   ```bash
   sudo mkdir -p /var/www/string-analyzer-api
   cd /var/www/string-analyzer-api
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Create Systemd Service**:
   ```bash
   sudo nano /etc/systemd/system/string-analyzer.service
   ```
   
   Add the service configuration from `deploy.sh`

4. **Configure Nginx**:
   ```bash
   sudo nano /etc/nginx/sites-available/string-analyzer
   ```
   
   Add the Nginx configuration from `deploy.sh`

5. **Start Services**:
   ```bash
   sudo systemctl enable string-analyzer
   sudo systemctl start string-analyzer
   sudo systemctl restart nginx
   ```

## Natural Language Query Examples

- `"all single word palindromic strings"` → word_count=1, is_palindrome=true
- `"strings longer than 10 characters"` → min_length=11
- `"strings containing the letter z"` → contains_character=z
- `"palindromic strings that contain the first vowel"` → is_palindrome=true, contains_character=a

## Error Responses

- `400 Bad Request`: Invalid request body or missing 'value' field
- `404 Not Found`: String does not exist
- `409 Conflict`: String already exists
- `422 Unprocessable Entity`: Invalid data type for 'value' field

## Testing

Test the API using curl:

```bash
# Create a string
curl -X POST "http://localhost:8000/strings" \
     -H "Content-Type: application/json" \
     -d '{"value": "hello world"}'

# Get all strings
curl "http://localhost:8000/strings"

# Filter strings
curl "http://localhost:8000/strings?is_palindrome=true"

# Natural language query
curl "http://localhost:8000/strings/filter-by-natural-language?query=single%20word%20palindromic%20strings"
```

## License

MIT License