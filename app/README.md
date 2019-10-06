# dresstimator - app

This package contains the code to run the _Dresstimator_ web application. The web app is run using the Flask framework.

## Flask Development Environment

The instructions below summarize how to start the web application in development mode:

```
# Create the virtual environment
virtualenv venv-app

# Enable the virtual environment
source venv-app/bin/activate

# Install the required Python packages
pip3 install -r requirements.txt

# Run Flask in development mode
flask run
```

After executing the `flask run` command, the web framework is run in development mode. In this project, the `.flaskenv` file has been configured to run Flask on port `8080` and on host `0.0.0.0` - so that the web app is available via the external IP address on port `8080`.

```
(venv-app) ubuntu@ip-171-32-46-184:~/test/app$ flask run
 * Serving Flask app "dresstimator.py"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

## Flask Production Environment

Start by updating the Ubuntu package repositories:

```
# General update
sudo apt update
sudo apt upgrade
```

Install the `nginx` web server:

```
sudo apt install nginx
```

Check that `nginx` is running:

```
sudo systemctl status nginx
```

Remove the default enabled website value:

```
sudo rm /etc/nginx/sites-enabled/default
```

Create a new site available configuration file and link the files to the enabled site:

```
sudo touch /etc/nginx/sites-available/dresstimator
sudo ln -s /etc/nginx/sites-available/dresstimator /etc/nginx/sites-enabled/dresstimator
```

Edit the web site configuration file:

```
sudo nano /etc/nginx/sites-enabled/dresstimator
```

Add the following configuration:

```
server {
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /static {
        alias /home/ubuntu/desstimator/app/app/static;
    }
}
```

Restart `nginx` web server:

```
sudo systemctl restart nginx
```

Make sure `gunicorn` is installed. If you are using the specified virtual environment and the provided `requirements.txt` file, this should have been installed automatically. Nevertheless, the command for installation is:

```
pip3 install gunicorn
```

Finally, run `gunicorn` to serve the web app on port 8000. This is the same port `nginx` is listening on to then serve on port `80`.

```
cd ~/dresstimator/app
gunicorn flaskexample:app
```

If you want to spawn `gunicorn` as a background process use the following command:

```
cd ~/dresstimator/app
gunicorn flaskexample:app -D
```

To kill the process:

```
pkill gunicorn
```
