# Banking Automation - Render Deployment Guide

## 🚀 Deploying to Render

This guide will help you deploy your Banking Automation system to Render.com successfully.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Database**: PostgreSQL database (provided by Render)

## Deployment Steps

### Step 1: Prepare Your Repository

Make sure your repository contains these files:
- `app.py` (main Flask application)
- `requirements.txt` (Python dependencies)
- `Procfile` (for web process)
- `render.yaml` (optional configuration)
- `templates/` folder with HTML files
- `static/` folder with CSS/JS files

### Step 2: Create PostgreSQL Database

1. Go to your Render dashboard
2. Click "New +" → "PostgreSQL"
3. Choose a name (e.g., "banking-db")
4. Select "Free" plan
5. Click "Create Database"
6. Wait for the database to be created
7. Copy the **External Database URL** (you'll need this)

### Step 3: Deploy Web Service

1. In Render dashboard, click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `banking-automation` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Step 4: Set Environment Variables

In your web service settings, add these environment variables:

```
DATABASE_URL = [Your PostgreSQL connection string from Step 2]
SECRET_KEY = [Generate a secure random string]
FLASK_ENV = production
PORT = 10000
```

**To generate a SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Build your application
   - Start the web service

### Step 6: Verify Deployment

1. Wait for the deployment to complete (usually 2-5 minutes)
2. Click on your service URL to access the application
3. Test the application functionality

## 🔧 Configuration Files Explained

### Procfile
```
web: gunicorn app:app
```
Tells Render how to start your web application using Gunicorn WSGI server.

### requirements.txt
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Bcrypt==1.0.1
Werkzeug==2.3.7
gunicorn==21.2.0
psycopg2-binary==2.9.7
```
Lists all Python dependencies including Gunicorn for production and psycopg2 for PostgreSQL.

### render.yaml (Optional)
Provides declarative configuration for your services. Useful for infrastructure as code.

## 🐛 Common Issues & Solutions

### Issue 1: Database Connection Error
**Error**: `psycopg2.OperationalError: could not connect to server`

**Solution**: 
- Ensure DATABASE_URL is correctly set
- Check if the database URL starts with `postgresql://` (not `postgres://`)
- Verify the database is running and accessible

### Issue 2: Build Failures
**Error**: `ModuleNotFoundError` or build timeout

**Solution**:
- Check requirements.txt has all necessary packages
- Ensure Python version compatibility
- Try clearing build cache in Render dashboard

### Issue 3: Application Won't Start
**Error**: `gunicorn: command not found`

**Solution**:
- Verify Procfile is in the root directory
- Check that gunicorn is in requirements.txt
- Ensure start command is correct

### Issue 4: Static Files Not Loading
**Error**: CSS/JS files return 404

**Solution**:
- Check static folder structure
- Verify Flask static file configuration
- Ensure files are committed to repository

## 🔒 Security Considerations

1. **Change Default Admin Password**: After deployment, change the default admin password
2. **Use Strong SECRET_KEY**: Generate a secure random secret key
3. **Environment Variables**: Never commit sensitive data to your repository
4. **HTTPS**: Render provides HTTPS by default for custom domains

## 📊 Monitoring & Maintenance

### Logs
- Access logs in Render dashboard under "Logs" tab
- Monitor for errors and performance issues

### Database Management
- Use Render's database dashboard for monitoring
- Consider upgrading to paid plan for production use

### Updates
- Push changes to your GitHub repository
- Render will automatically redeploy
- Monitor deployment logs for any issues

## 🎯 Production Recommendations

1. **Upgrade Plan**: Consider upgrading from free tier for production
2. **Custom Domain**: Add your own domain name
3. **SSL Certificate**: Automatically provided by Render
4. **Backup Strategy**: Regular database backups
5. **Monitoring**: Set up monitoring and alerting

## 📞 Support

If you encounter issues:
1. Check Render's documentation
2. Review application logs
3. Verify environment variables
4. Test locally first

## 🎉 Success!

Once deployed, your Banking Automation system will be accessible at:
`https://your-app-name.onrender.com`

Default admin credentials:
- Email: `admin@securebank.com`
- Password: `admin123`

**⚠️ Important**: Change the default admin password immediately after deployment!
