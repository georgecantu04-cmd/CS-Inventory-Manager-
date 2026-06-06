# CS2 Inventory Tracker - Windows Installation Guide

Follow these steps to get your CS2 Inventory Tracker up and running!

## Step 1: Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or 3.12 (click the big yellow button)
3. **IMPORTANT**: When installing, check the box that says "Add Python to PATH"
4. Click "Install Now"
5. Wait for installation to complete

To verify Python is installed:
- Open Command Prompt (press Windows key, type "cmd", press Enter)
- Type: `python --version`
- You should see something like "Python 3.11.x"

## Step 2: Get Your Steam Credentials

### Get Steam API Key
1. Go to https://steamcommunity.com/dev/apikey
2. Log in with your Steam account
3. Enter a domain name (you can use "localhost" or any name)
4. Click "Register"
5. **Copy your API key** - you'll need this later!

### Get Your Steam ID
1. Go to https://www.steamidfinder.com/
2. Enter your Steam profile URL or username
3. **Copy your Steam ID** (the 17-digit number) - you'll need this later!

### Make Your Inventory Public
1. Go to Steam > Profile > Edit Profile > Privacy Settings
2. Set "Game details" to **Public**
3. Set "Inventory" to **Public**
4. Click "Save"

## Step 3: Download the Project

If you haven't already:
1. Go to https://github.com/georgecantu04-cmd/Cs2-tracker
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to a location you can find (like your Desktop or Documents)
5. Open the extracted "Cs2-tracker" folder

## Step 4: Set Up the Project

1. **Open Command Prompt in the project folder**:
   - In the File Explorer, navigate to the Cs2-tracker folder
   - Click on the address bar at the top
   - Type `cmd` and press Enter
   - A Command Prompt window will open in that folder

2. **Create a virtual environment**:
   ```cmd
   python -m venv venv
   ```
   (This creates an isolated Python environment for the project)

3. **Activate the virtual environment**:
   ```cmd
   venv\Scripts\activate
   ```
   You should see `(venv)` appear at the start of your command line

4. **Install the required packages**:
   ```cmd
   pip install -r requirements.txt
   ```
   This will take a minute or two. You'll see lots of text as packages are downloaded and installed.

## Step 5: Configure Your Settings

1. **Create your configuration file**:
   - In the Cs2-tracker folder, find the file named `.env.example`
   - Right-click it and select "Open with" > "Notepad"
   - You'll see this:
     ```
     STEAM_API_KEY=your_steam_api_key_here
     STEAM_ID=your_steam_id_here
     ```

2. **Add your credentials**:
   - Replace `your_steam_api_key_here` with your actual Steam API key (from Step 2)
   - Replace `your_steam_id_here` with your actual Steam ID (from Step 2)
   - Example:
     ```
     STEAM_API_KEY=ABC123XYZ456DEF789
     STEAM_ID=76561198012345678
     ```

3. **Save the file as `.env`**:
   - Click File > Save As
   - In the "File name" box, type: `.env` (including the dot at the start)
   - In "Save as type", select "All Files (*.*)"
   - Click Save
   - Close Notepad

## Step 6: Run the Application

1. **Make sure your virtual environment is still activated** (you should see `(venv)` in Command Prompt)
   - If not, run: `venv\Scripts\activate`

2. **Start the tracker**:
   ```cmd
   python main.py
   ```

3. **Wait for it to start**:
   - You'll see some text appearing
   - Wait until you see something like: "Uvicorn running on http://0.0.0.0:8000"
   - This means it's ready!

## Step 7: Use the Tracker

1. **Open your web browser** (Chrome, Firefox, Edge, etc.)

2. **Go to**: `http://localhost:8000`

3. **You should see the CS2 Inventory Tracker interface!**

4. **Click "Sync Inventory"** to load your CS2 items

5. **Click "Update Prices"** to get current market prices

## Common Issues & Solutions

### "Python is not recognized..."
- You need to install Python and make sure "Add to PATH" was checked
- Restart your computer after installing Python

### "pip is not recognized..."
- Make sure your virtual environment is activated: `venv\Scripts\activate`
- You should see `(venv)` at the start of your command line

### "Failed to fetch inventory"
- Check that your Steam ID is correct
- Make sure your Steam inventory is set to Public
- Make sure you have CS2 items in your inventory

### "ModuleNotFoundError"
- Make sure you ran: `pip install -r requirements.txt`
- Make sure your virtual environment is activated

### Can't create .env file
- Windows hides file extensions by default
- In File Explorer: View > Show > File name extensions
- Then you can rename .env.example to .env

## Stopping the Application

- In the Command Prompt window, press `Ctrl + C`
- This will stop the server

## Running it Again Later

1. Open Command Prompt in the Cs2-tracker folder
2. Activate virtual environment: `venv\Scripts\activate`
3. Run: `python main.py`
4. Open browser to: `http://localhost:8000`

---

Need more help? Check the main README.md file or open an issue on GitHub!
