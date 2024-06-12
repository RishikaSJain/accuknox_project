# accuknox_project
## Installation Steps

1. Clone the repository:
    ```bash
    git clone https://github.com/RishikaSJain/accuknox_project
    cd social_network
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Using Docker

1. Build and run the application using Docker:
    ```bash
    docker-compose up --build
    ```

## Postman Collection

To test the API endpoints, you can import the provided Postman collection:

1. Download the postman collection(social_network\accuknox.postman_collection.json) file.
2. Open Postman.
3. Click on the "Import" button in the top left corner.
4. Select the downloaded JSON file and import it.

The collection contains requests for all available API endpoints.
