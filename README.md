# learn-oauth-flow

# Flask GitHub OAuth Example

## Setup

1. **Register a new OAuth App on GitHub:**
   - Go to https://github.com/settings/developers
   - Click "New OAuth App"
   - Set the callback URL to: `http://localhost:5000/callback`
   - Note your Client ID and Client Secret

2. **Set environment variables:**
   - `GITHUB_CLIENT_ID`: Your GitHub OAuth app client ID
   - `GITHUB_CLIENT_SECRET`: Your GitHub OAuth app client secret
   - (Optional) `FLASK_SECRET_KEY`: Secret key for Flask session

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**
   ```bash
   export GITHUB_CLIENT_ID=your_client_id
   export GITHUB_CLIENT_SECRET=your_client_secret
   export FLASK_SECRET_KEY=your_flask_secret
   python app.py
   ```

5. **Test:**
   - Open http://localhost:5000 in your browser
   - Click "Login with GitHub" and authorize the app

## Files
- `app.py`: Main Flask app
- `requirements.txt`: Python dependencies
