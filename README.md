# CS2 Inventory Tracker

A comprehensive web application for tracking your Counter-Strike 2 inventory value, price changes, and profit/loss over time.

## Features

- **Automatic Inventory Sync**: Fetch your CS2 inventory directly from Steam API
- **Real-time Price Tracking**: Automatically update item prices from Steam Market
- **Price History Charts**: Visualize how your inventory value changes over time
- **Profit/Loss Alerts**: Get notified when items gain or lose significant value
- **Detailed Analytics**: Track total value, profit/loss, and individual item performance
- **Modern Web Interface**: Clean, responsive UI with dark mode theme
- **Background Updates**: Automatic price updates at configurable intervals

## Screenshots

The tracker provides:
- Dashboard with total inventory value and profit/loss
- Price alert notifications for significant changes
- Interactive charts showing value history
- Detailed item list with current prices and profit/loss
- Easy purchase price management

## Prerequisites

- Python 3.8 or higher
- Steam API key ([Get one here](https://steamcommunity.com/dev/apikey))
- Your Steam ID ([Find it here](https://www.steamidfinder.com/))
- Public Steam inventory (Privacy Settings → Game Details → Inventory must be public)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Cs2-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Steam credentials:
   ```env
   STEAM_API_KEY=your_steam_api_key_here
   STEAM_ID=your_steam_id_here
   ```

## Configuration

The `.env` file supports the following configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `STEAM_API_KEY` | Your Steam Web API key | Required |
| `STEAM_ID` | Your Steam ID (17-digit number) | Required |
| `DATABASE_URL` | SQLite database path | `sqlite:///./cs2_tracker.db` |
| `UPDATE_INTERVAL_MINUTES` | How often to update prices automatically | `60` |
| `PRICE_ALERT_THRESHOLD` | Percentage change to trigger alerts | `10.0` |

## Usage

1. **Start the application**
   ```bash
   python main.py
   ```

   The server will start at `http://localhost:8000`

2. **Open your browser**
   Navigate to `http://localhost:8000`

3. **Sync your inventory**
   - Click "Sync Inventory" to fetch your items from Steam
   - This will load all CS2 items from your inventory

4. **Update prices**
   - Click "Update Prices" to fetch current market prices
   - Prices will also update automatically every hour (configurable)

5. **Set purchase prices**
   - For each item, you can set the price you paid for it
   - This allows the tracker to calculate your profit/loss accurately

## How It Works

### Data Collection

1. **Inventory Sync**: The app uses the Steam API to fetch your CS2 inventory items
2. **Price Fetching**: Current market prices are retrieved from the Steam Community Market
3. **Historical Tracking**: Prices are stored in a SQLite database for trend analysis
4. **Alert Generation**: Significant price changes trigger alerts based on your threshold

### Background Processing

The application runs a background scheduler that:
- Updates all item prices every 60 minutes (configurable)
- Creates price history records for trend analysis
- Generates alerts when prices change significantly
- Creates inventory snapshots for value tracking

### API Endpoints

The FastAPI backend provides these endpoints:

- `POST /api/sync` - Sync inventory from Steam
- `POST /api/update-prices` - Update all item prices
- `GET /api/summary` - Get inventory summary statistics
- `GET /api/items` - Get all inventory items
- `GET /api/items/{item_id}/price-history` - Get price history for an item
- `GET /api/inventory-history` - Get total inventory value history
- `GET /api/alerts` - Get price change alerts
- `PUT /api/items/{item_id}/purchase-price` - Update item purchase price

## Project Structure

```
Cs2-tracker/
├── main.py                 # FastAPI application and endpoints
├── config.py               # Configuration and settings
├── database.py             # Database models and schema
├── steam_api.py            # Steam API integration
├── price_service.py        # Price fetching service
├── tracker_service.py      # Main business logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration (create from .env.example)
├── .env.example            # Example environment file
├── .gitignore             # Git ignore rules
└── static/                 # Frontend files
    ├── index.html         # Main HTML page
    ├── styles.css         # Styling
    └── app.js             # Frontend JavaScript
```

## Database Schema

The application uses SQLite with the following tables:

- **inventory_items**: Stores CS2 items with current and purchase prices
- **price_history**: Historical price data for trend analysis
- **price_alerts**: Alerts for significant price changes
- **inventory_snapshots**: Total inventory value over time

## Important Notes

### Steam API Rate Limits

- The Steam Market API has rate limits (~20 requests per minute)
- The app includes built-in rate limiting with a 3-second delay between requests
- Large inventories may take several minutes to update

### Inventory Privacy

Your Steam inventory must be set to **Public** for the tracker to work:
1. Go to Steam Privacy Settings
2. Set "Game details" to Public
3. Ensure "Inventory" is also set to Public

### Price Accuracy

- Prices are fetched from the Steam Community Market
- Prices may vary from third-party marketplaces
- Items that aren't marketable won't have price data
- Steam Market prices include Steam's 15% fee

## Troubleshooting

### "Failed to fetch inventory"
- Check that your Steam ID is correct
- Ensure your inventory is set to Public
- Verify you have CS2 items in your inventory

### "Failed to update prices"
- Check your internet connection
- Steam Market API may be temporarily unavailable
- Rate limiting may be in effect (wait a few minutes)

### No price data for items
- Some items may not be marketable on Steam
- Newly released items may not have market data yet
- Check that the item can be sold on Steam Market

## Future Enhancements

Possible features for future versions:
- Multiple account support
- Export data to CSV/PDF
- Mobile app
- Email notifications for alerts
- Integration with third-party marketplaces (CSFloat, Buff, etc.)
- Portfolio comparison and analytics
- Trading history integration

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is provided as-is for personal use. Please respect Steam's API Terms of Service.

## Disclaimer

This is an unofficial tool and is not affiliated with Valve or Steam. Use at your own risk. The accuracy of prices and data is not guaranteed.

## Support

For questions or issues:
1. Check the Troubleshooting section above
2. Review your `.env` configuration
3. Check the application logs
4. Open an issue on GitHub

---

Built with Python, FastAPI, and Chart.js