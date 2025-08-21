# How to Set Up and Deploy the Agentic-Interviewer Application

This guide provides instructions on how to set up and run the Agentic-Interviewer application locally for development, and how to deploy it to production using either Render or Digital Ocean.

## 1. Local Setup

Follow these steps to run the application on your local machine.

### 1.1. Backend Setup

1.  **Navigate to the backend directory:**
    ```bash
    cd Agentic-Interviewer/backend
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install django-crontab
    ```

4.  **Run the Django database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Start the Django backend server:**
    ```bash
    python manage.py runserver 8000
    ```
    The backend API will be running at `http://localhost:8000`.

### 1.2. Frontend Setup

1.  **Navigate to the frontend directory in a new terminal:**
    ```bash
    cd Agentic-Interviewer/frontend
    ```

2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```

3.  **Start the React development server:**
    ```bash
    npm run dev
    ```
    The frontend application will be accessible at `http://localhost:5173`.

## 2. Deployment

You can deploy this application using either Render (for a simpler, quicker setup) or Digital Ocean (for more control and potentially lower cost).

### 2.1. Render Deployment (Easy)

Render is a cloud platform that makes it easy to deploy web applications. This project is pre-configured for a seamless deployment on Render.

1.  **Push your code to a GitHub repository.**

2.  **Create a new "Blueprint" on Render:**
    *   Go to the [Render Dashboard](https://dashboard.render.com/) and click "New + > Blueprint".
    *   Connect your GitHub repository.
    *   Render will automatically detect and use the `render.yaml` file in your repository to configure the services.

3.  **Environment Variables:**
    *   Render will automatically generate a `SECRET_KEY` and configure the `DATABASE_URL`.
    *   You may need to add other environment variables for your application's features (e.g., `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `OPENAI_API_KEY`) in the Render dashboard.

4.  **Deploy:**
    *   Click "Apply" to start the deployment.
    *   Render will build and start your application. Your application will be available at the URL provided by Render.

### 2.2. Digital Ocean Deployment (Advanced)

This method provides more control over your server environment but requires more manual configuration.

1.  **Create a Digital Ocean Droplet:**
    *   Create a new Droplet with Ubuntu 22.04 LTS.
    *   Choose a plan with at least 1GB of RAM.
    *   Add your SSH key for secure access.

2.  **Connect to your Droplet:**
    ```bash
    ssh root@your-droplet-ip
    ```

3.  **Run the Deployment Script:**
    The easiest way to deploy is to use the provided `deploy.sh` script.
    ```bash
    curl -O https://raw.githubusercontent.com/redsteadz/Agentic-Interviewer/main/deploy.sh
    chmod +x deploy.sh
    ./deploy.sh
    ```

4.  **Configure the Server:**
    Run the `setup-server.sh` script to configure Nginx and other server components.
    ```bash
    ./setup-server.sh
    ```

5.  **Update Configuration:**
    *   **Nginx:** Edit the Nginx configuration at `/etc/nginx/sites-available/django-react-auth` and replace `your-domain.com` and `your-ip-address` with your actual values.
    *   **Environment Variables:** Edit the `.env` file at `/var/www/django-react-auth/backend/.env` and update `ALLOWED_HOSTS` with your domain/IP.

6.  **Restart Services:**
    ```bash
    sudo systemctl restart nginx
    sudo systemctl restart django-react-auth
    ```

7.  **Set Up SSL (Recommended):**
    Run the `setup-ssl.sh` script to configure a free SSL certificate from Let's Encrypt.
    ```bash
    ./setup-ssl.sh
    ```

For a more detailed step-by-step guide on manual deployment on Digital Ocean, please refer to the `DIGITAL_OCEAN_DEPLOYMENT.md` file in the repository.
