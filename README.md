# Local Landmarks Explorer

Local Landmarks Explorer is a web application that displays local landmarks on an interactive map using Flask, Vanilla JS, and Wikipedia data. It allows users to explore landmarks in different areas, search for specific locations, and filter landmarks by category.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Caching System](#caching-system)
- [Deployment](#deployment)
  - [Replit (Recommended)](#replit-recommended)
  - [Azure](#azure)
  - [AWS](#aws)
  - [Google Cloud Platform (GCP)](#google-cloud-platform-gcp)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- Interactive map displaying local landmarks
- User location tracking
- Search functionality for specific landmarks or locations
- Category-based filtering of landmarks
- Caching system for improved performance
- Responsive design for various screen sizes

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## Installation

To install Local Landmarks Explorer, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/local-landmarks-explorer.git
   cd local-landmarks-explorer
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   FLASK_APP=main.py
   FLASK_ENV=development
   ```

## Usage

To run the Local Landmarks Explorer, follow these steps:

1. Start the Flask server:
   ```
   flask run
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Use the map to explore landmarks:
   - Pan and zoom the map to discover landmarks in different areas
   - Click on a marker to see more information about the landmark
   - Use the search functionality to find specific landmarks or locations
   - Filter landmarks by category using the legend

## Technologies Used

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Map: Leaflet.js
- Data Source: Wikipedia API
- CSS Framework: Tailwind CSS
- Deployment: Replit

## Caching System

Local Landmarks Explorer implements a caching system to improve performance and reduce API calls to Wikipedia. The caching system includes:

- In-memory caching using Python's `lru_cache` decorator
- File-based caching for persistent storage between server restarts
- Automatic cache expiration and cleanup to ensure data freshness

## Deployment

This section provides instructions for deploying the Local Landmarks Explorer on various platforms. While we recommend using Replit for its simplicity and integration with this project, we also provide instructions for other cloud platforms.

### Replit (Recommended)

Replit is the recommended platform for deploying this project due to its ease of use and integration with the development process.

1. Fork the project on Replit.
2. Click on the "Run" button to start the Flask server.
3. Replit will automatically handle the deployment and provide you with a URL to access your application.

### Azure

To deploy on Microsoft Azure:

1. Create an Azure account and install the Azure CLI.
2. Create an App Service plan:
   ```
   az appservice plan create --name myAppServicePlan --resource-group myResourceGroup --sku B1 --is-linux
   ```
3. Create a web app:
   ```
   az webapp create --resource-group myResourceGroup --plan myAppServicePlan --name <your-app-name> --runtime "PYTHON|3.8" --deployment-local-git
   ```
4. Set up environment variables:
   ```
   az webapp config appsettings set --resource-group myResourceGroup --name <your-app-name> --settings FLASK_APP=main.py
   ```
5. Deploy your code:
   ```
   git remote add azure <deployment-local-git-url>
   git push azure main
   ```

### AWS

To deploy on Amazon Web Services (AWS):

1. Create an AWS account and install the AWS CLI.
2. Create an Elastic Beanstalk application:
   ```
   eb init -p python-3.8 local-landmarks-explorer --region us-west-2
   ```
3. Create an environment:
   ```
   eb create local-landmarks-env
   ```
4. Deploy your application:
   ```
   eb deploy
   ```
5. Set environment variables:
   ```
   eb setenv FLASK_APP=main.py
   ```

### Google Cloud Platform (GCP)

To deploy on Google Cloud Platform:

1. Create a GCP account and install the Google Cloud SDK.
2. Create a new project:
   ```
   gcloud projects create <your-project-id>
   ```
3. Enable the App Engine API:
   ```
   gcloud app create --project=<your-project-id>
   ```
4. Deploy your application:
   ```
   gcloud app deploy
   ```
5. Set environment variables:
   ```
   gcloud app update --set-env-vars FLASK_APP=main.py
   ```

Remember to update your `requirements.txt` file and include a `Procfile` or `app.yaml` file as needed for each platform. Also, ensure that your application is configured to use environment variables for any sensitive information or configuration that may differ between development and production environments.

## Contributing

Contributions to the Local Landmarks Explorer project are welcome. Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Create a new Pull Request

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

If you have any questions or feedback, please open an issue on the GitHub repository.

Thank you for using Local Landmarks Explorer!
