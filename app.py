from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from mongoengine import connect, Document, StringField
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from jsonschema import validate, ValidationError
import random
import string
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/mydatabase'
app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Replace with your own secret key
mongo = PyMongo(app)
jwt = JWTManager(app)
CORS(app)

def validate_json(data, schema):
    try:
        validate(data, schema)
        return True
    except ValidationError:
        return False

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data['email']
    password = data['password']
    name = data['name']

    # Check if the email already exists
    if mongo.db.users.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'})

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Insert the user into the database
    user_id = mongo.db.users.insert_one({'name': name, 'email': email, 'password': hashed_password}).inserted_id

    return jsonify({'message': 'User registered successfully', 'user_id': str(user_id)})



# User login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Find the user by email
    user = mongo.db.users.find_one({'email': email})

    # Check if the user exists
    if not user:
        return jsonify({'error': 'Invalid email or password'})

    # Check if the password is correct
    if not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'})

    # Generate a token (you can use a more secure method for production)
    access_token = create_access_token(identity=str(user['_id']))

    # Save the token in the database
    mongo.db.tokens.insert_one({'user_id': user['_id'], 'token': access_token})

    return jsonify({'message': 'Login successful', 'access_token': access_token})

# Function to generate a unique API name
def generate_unique_api_name(api_name):
    # Remove spaces and convert to lowercase
    api_name = api_name.replace(" ", "").lower()

    # Check if the API name already exists
    existing_api = mongo.db.apis.find_one({'api_name': api_name})
    if not existing_api:
        return api_name

    # Generate a random suffix
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return api_name + "_" + suffix

# Function to generate unique endpoints
def generate_unique_endpoints(endpoints):
    unique_endpoints = []
    for endpoint in endpoints:
        unique_endpoint = generate_unique_endpoint(endpoint)
        unique_endpoints.append(unique_endpoint)
    return unique_endpoints

# Function to generate a unique endpoint name
def generate_unique_endpoint(endpoint):
    # Remove spaces and convert to lowercase
    endpoint = endpoint.replace(" ", "").lower()

    # Check if the endpoint already exists
    existing_endpoint = mongo.db.apis.find_one({'endpoints': endpoint})
    if not existing_endpoint:
        return endpoint

    # Generate a random suffix
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return endpoint + "_" + suffix


# Create API
@app.route('/create_api', methods=['POST'])
@jwt_required()
def create_api():
    data = request.get_json()
    api_name = data['api_name']
    endpoints = data['endpoints']
    json_schema = data['json_schema']

    # Generate a unique API name
    api_name = generate_unique_api_name(api_name)

    # Generate unique endpoints
    unique_endpoints = generate_unique_endpoints(endpoints)

    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Generate a unique API key
    api_key = str(ObjectId())

    # Insert the API into the database along with the user ID
    api_id = mongo.db.apis.insert_one({'api_name': api_name, 'api_key': api_key, 'endpoints': unique_endpoints, 'json_schema': json_schema, 'user_id': user_id}).inserted_id

    return jsonify({'message': 'API created successfully', 'api_name': api_name, 'api_key': api_key, 'endpoints': unique_endpoints})


# Retrieve all APIs for the user
@app.route('/api', methods=['GET'])
@jwt_required()
def get_user_apis():
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Retrieve the APIs associated with the user ID
    apis = list(mongo.db.apis.find({'user_id': user_id}))

    # Prepare the response data
    response = []
    for api in apis:
        api_data = {
            'api_id': str(api['_id']),
            'api_name': api['api_name'],
            'api_key': api['api_key'],
            'endpoints': api['endpoints']
        }
        response.append(api_data)

    return jsonify({'apis': response})



# Retrieve a single API by ID
@app.route('/api/<api_id>', methods=['GET'])
@jwt_required()
def get_api(api_id):
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Retrieve the API associated with the given ID and user ID
    api = mongo.db.apis.find_one({'_id': ObjectId(api_id), 'user_id': user_id})

    if not api:
        return jsonify({'error': 'API not found'})

    # Prepare the response data
    response = {
        'api_id': str(api['_id']),
        'api_name': api['api_name'],
        'api_key': api['api_key'],
        'endpoints': api['endpoints']
    }

    return jsonify({'api': response})

# Delete an API
@app.route('/api/<api_id>', methods=['DELETE'])
@jwt_required()
def delete_api(api_id):
    # Get the user ID from the JWT token
    user_id = get_jwt_identity()

    # Find the API associated with the given ID and user ID
    api = mongo.db.apis.find_one({'_id': ObjectId(api_id), 'user_id': user_id})

    if not api:
        return jsonify({'error': 'API not found or you do not have permission to delete it'})

    # Delete the API
    mongo.db.apis.delete_one({'_id': ObjectId(api_id), 'user_id': user_id})

    # Delete the endpoints and their records
    for endpoint in api['endpoints']:
        # Delete the endpoint
        mongo.db.apis.delete_one({'api_name': api['api_name'], 'endpoints': endpoint})

        # Delete the records in the endpoint collection
        mongo.db[endpoint].delete_many({})

    return jsonify({'message': 'API deleted successfully'})


# Create a new record or multiple records in an endpoint
@app.route('/api/<api_name>/<endpoint>', methods=['POST'])
def create_record(api_name, endpoint):
    # Check if the API name and API key are valid
    api = mongo.db.apis.find_one({'api_name': api_name, 'api_key': request.headers.get('api_key')})
    if not api:
        return jsonify({'error': 'Invalid API name or API key'})

    # Check if the endpoint exists in the API
    if endpoint not in api['endpoints']:
        return jsonify({'error': 'Invalid endpoint'})

    # Get the JSON schema for validation
    json_schema = api['json_schema'][endpoint]

    # Validate the request data against the JSON schema
    data = request.get_json()
    if isinstance(data, list):  # If the request contains multiple data items
        for item in data:
            if not validate_json(item, json_schema):
                return jsonify({'error': 'Invalid request data'})
        
        # Insert the records into the endpoint collection
        record_ids = []
        for item in data:
            record_id = mongo.db[endpoint].insert_one(item).inserted_id
            record_ids.append(str(record_id))
        
        return jsonify({'message': 'Records created successfully', 'record_ids': record_ids})
    else:  # If the request contains a single data item
        if not validate_json(data, json_schema):
            return jsonify({'error': 'Invalid request data'})

        # Insert the record into the endpoint collection
        record_id = mongo.db[endpoint].insert_one(data).inserted_id

        return jsonify({'message': 'Record created successfully', 'record_id': str(record_id)})


# Read records from an endpoint
@app.route('/api/<api_name>/<endpoint>', methods=['GET'])
def read_records(api_name, endpoint):
    api = mongo.db.apis.find_one({'api_name': api_name, 'api_key': request.headers.get('api_key')})
    if not api:
        return jsonify({'error': 'Invalid API name or API key'})

    if endpoint not in api['endpoints']:
        return jsonify({'error': 'Invalid endpoint'})

    # Get the page and per_page parameters from the query string
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Calculate the starting index and ending index for pagination
    start_index = (page - 1) * per_page
    end_index = start_index + per_page

    # Retrieve records from the endpoint collection
    records = []

    filter_param = request.args.get('q')

    if filter_param:
        try:
            filter_dict = eval(filter_param)
            records = list(mongo.db[endpoint].find(filter_dict).skip(start_index).limit(per_page))
        except:
            return jsonify({'error': 'Invalid filter parameter'})
    else:
        records = list(mongo.db[endpoint].find().skip(start_index).limit(per_page))

    # Sort records if 'sort' query parameter is provided
    sort_param = request.args.get('sort')
    if sort_param:
        sort_dict = {}
        sort_fields = sort_param.split(',')
        for field in sort_fields:
            if field.startswith('-'):
                sort_dict[field[1:]] = -1  # Sort in descending order
            else:
                sort_dict[field] = 1  # Sort in ascending order
        records.sort(key=lambda x: tuple(x.get(field) for field in sort_fields), reverse=False)

    for record in records:
        record['_id'] = str(record['_id'])

    return jsonify({'data': records})



# Read a record from an endpoint by ID
@app.route('/api/<api_name>/<endpoint>/<record_id>', methods=['GET'])
def read_record(api_name, endpoint, record_id):
    # Check if the API name and API key are valid
    api = mongo.db.apis.find_one({'api_name': api_name, 'api_key': request.headers.get('api_key')})
    if not api:
        return jsonify({'error': 'Invalid API name or API key'})

    # Check if the endpoint exists in the API
    if endpoint not in api['endpoints']:
        return jsonify({'error': 'Invalid endpoint'})

    # Retrieve the record from the endpoint collection
    record = mongo.db[endpoint].find_one({'_id': ObjectId(record_id)})

    if not record:
        return jsonify({'error': 'Record not found'})

    # Convert ObjectId to string for JSON serialization
    record['_id'] = str(record['_id'])

    return jsonify({'data': record})


# Update a record in an endpoint
@app.route('/api/<api_name>/<endpoint>/<record_id>', methods=['PUT'])
def update_record(api_name, endpoint, record_id):
    # Check if the API name and API key are valid
    api = mongo.db.apis.find_one({'api_name': api_name, 'api_key': request.headers.get('api_key')})
    if not api:
        return jsonify({'error': 'Invalid API name or API key'})

    # Check if the endpoint exists in the API
    if endpoint not in api['endpoints']:
        return jsonify({'error': 'Invalid endpoint'})

    # Check if the record exists in the endpoint collection
    record = mongo.db[endpoint].find_one({'_id': ObjectId(record_id)})
    if not record:
        return jsonify({'error': 'Record not found'})

    # Validate the request data against the JSON schema
    json_schema = api['json_schema'][endpoint]
    data = request.get_json()
    if not validate_json(data, json_schema):
        return jsonify({'error': 'Invalid request data'})

    # Update the record in the endpoint collection
    mongo.db[endpoint].update_one({'_id': ObjectId(record_id)}, {'$set': data})

    return jsonify({'message': 'Record updated successfully'})


# Delete a record from an endpoint
@app.route('/api/<api_name>/<endpoint>/<record_id>', methods=['DELETE'])
def delete_record(api_name, endpoint, record_id):
    # Check if the API name and API key are valid
    api = mongo.db.apis.find_one({'api_name': api_name, 'api_key': request.headers.get('api_key')})
    if not api:
        return jsonify({'error': 'Invalid API name or API key'})

    # Check if the endpoint exists in the API
    if endpoint not in api['endpoints']:
        return jsonify({'error': 'Invalid endpoint'})

    # Check if the record exists in the endpoint collection
    record = mongo.db[endpoint].find_one({'_id': ObjectId(record_id)})
    if not record:
        return jsonify({'error': 'Record not found'})

    # Delete the record from the endpoint collection
    mongo.db[endpoint].delete_one({'_id': ObjectId(record_id)})

    return jsonify({'message': 'Record deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)