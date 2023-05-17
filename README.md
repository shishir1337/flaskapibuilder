**API Authentication and Authorization System**

This is a Flask-based API authentication and authorization system that allows users to register, log in, and create APIs with unique keys for their endpoints. The system includes secure password hashing, validation of JSON data, and the ability to retrieve all APIs associated with a user.

**Getting Started**

To use this system, you will need to have Python, Flask, and MongoDB installed on your machine. Once you have those dependencies, you can clone the repository and run the Flask app with the command python app.py.

**User Registration**

To register a new user, send a POST request to the **/register** endpoint with a JSON payload containing the user's name, email, and password. If the email is already in use, the endpoint will return an error.

**User Login**

To log in as an existing user, send a POST request to the **/login** endpoint with a JSON payload containing the user's email and password. If the email or password is incorrect, the endpoint will return an error.

**Creating APIs**

To create a new API, send a POST request to the **/create_api** endpoint with a JSON payload containing the desired API name, endpoints, and JSON schema. The endpoint will generate a unique API name and key for the user and store the API in the MongoDB database.

**POST /create_api HTTP/1.1
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "api_name": "My API",
  "endpoints": ["endpoint1", "endpoint2"],
  "json_schema": {
    "endpoint1": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
      },
      "required": ["name", "age"]
    },
    "endpoint2": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"}
      },
      "required": ["title", "content"]
    }
  }
}
**

**Retrieving APIs**

To retrieve all APIs associated with a user, send a GET request to the **/api** endpoint with a valid access token in the request header. The endpoint will return a JSON object containing all the user's APIs.

To retrieve a single API by ID, send a GET request to the **/api/<api_id>** endpoint with a valid access token in the request header and the ID of the desired API in the URL. The endpoint will return a JSON object containing the API data.

**Creating Records**

To create a new record in an endpoint, send a POST request to the **/api/<api_name>/<endpoint>** endpoint with a valid API key in the request header and a JSON payload containing the data to be stored.

**Conclusion**

This API authentication and authorization system provides a secure and efficient way for users to manage their APIs and endpoint data. With Flask, MongoDB, and JWT token-based authentication, this system is easily scalable and adaptable to various use cases.
