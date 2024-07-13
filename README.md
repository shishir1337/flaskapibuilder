### Flask API Builder

This project provides a framework for rapidly building and managing APIs with Flask.

#### User Registration

**Endpoint:** `/register`

**Method:** POST

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "johndoe@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "6153e72ebc25b346a1c7ce84"
}
```

#### User Login

**Endpoint:** `/login`

**Method:** POST

**Request Body:**
```json
{
  "email": "johndoe@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Create API

**Endpoint:** `/create_api`

**Method:** POST

**Request Body:**
```json
{
  "api_name": "My API",
  "endpoints": ["users", "products"],
  "json_schema": {
    "users": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"},
        "age": {"type": "integer"}
      },
      "required": ["name", "email"]
    },
    "products": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "price": {"type": "number"},
        "quantity": {"type": "integer"}
      },
      "required": ["name", "price"]
    }
  }
}
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "API created successfully",
  "api_name": "myapi",
  "api_key": "6153e7b5bc25b346a1c7ce85",
  "endpoints": ["users", "products"]
}
```

#### Retrieve User APIs

**Endpoint:** `/api`

**Method:** GET

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "apis": [
    {
      "api_id": "6153e7b5bc25b346a1c7ce86",
      "api_name": "myapi",
      "api_key": "6153e7b5bc25b346a1c7ce85",
      "endpoints": ["users", "products"]
    }
  ]
}
```

#### Retrieve a Single API

**Endpoint:** `/api/<api_id>`

**Method:** GET

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "api": {
    "api_id": "6153e7b5bc25b346a1c7ce86",
    "api_name": "myapi",
    "api_key": "6153e7b5bc25b346a1c7ce85",
    "endpoints": ["users", "products"]
  }
}
```

#### Delete API

**Endpoint:** `/api/<api_id>`

**Method:** DELETE

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "API deleted successfully"
}
```

#### Create Record(s)

**Endpoint:** `/api/<api_name>/<endpoint>`

**Method:** POST

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "data": [
    {"name": "John Doe", "email": "johndoe@example.com", "age": 25},
    {"name": "Jane Smith", "email": "janesmith@example.com", "age": 30}
  ]
}
```

**Response:**
```json
{
  "message": "Records created successfully",
  "record_ids": ["6153e7b5bc25b346a1c7ce87", "6153e7b5bc25b346a1c7ce88"]
}
```

#### Read Records

**Endpoint:** `/api/<api_name>/<endpoint>`

**Method:** GET

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `page` (optional): Page number for pagination (e.g., `page=2&per_page=4`)
- `limit` (optional): Number of records per page
- `filter` (optional): Filter criteria as key-value pairs (e.g., `filter=name:John Doe`)
- `sort` (optional): Sort criteria as key-value pairs (e.g., `sort=age:desc`)

**Response:**
```json
{
  "records": [
    {"_id": "6153e7b5bc25b346a1c7ce87", "name": "John Doe", "email": "johndoe@example.com", "age": 25},
    {"_id": "6153e7b5bc25b346a1c7ce88", "name": "Jane Smith", "email": "janesmith@example.com", "age": 30}
  ],
  "total_records": 2,
  "page": 1,
  "total_pages": 1
}
```

#### Read Record

**Endpoint:** `/api/<api_name>/<endpoint>/<record_id>`

**Method:** GET

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "record": {"_id": "6153e7b5bc25b346a1c7ce87", "name": "John Doe", "email": "johndoe@example.com", "age": 25}
}
```

#### Update Record

**Endpoint:** `/api/<api_name>/<endpoint>/<record_id>`

**Method:** PUT

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "John Updated",
  "age": 26
}
```

**Response:**
```json
{
  "message": "Record updated successfully"
}
```

#### Delete Record

**Endpoint:** `/api/<api_name>/<endpoint>/<record_id>`

**Method:** DELETE

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Record deleted successfully"
}
```

---

### Usage

To use this project effectively, ensure you have Flask installed. You can clone the repository and configure your environment variables as specified in `config.py`. For more details, refer to the full documentation in the repository.

---

This structure provides clear, organized documentation that users can easily follow to understand and integrate your Flask API Builder into their projects. Adjust the structure and content as needed to fit your specific project details and style preferences.
