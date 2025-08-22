# To-Do Label Printer

A Flask web application for generating and printing to-do labels using Brother QL printers.

## Features

- **Web Interface**: Clean, responsive web interface for creating labels
- **Label Generation**: Generate labels with titles, descriptions, and tasks
- **Brother QL Printer Support**: Direct printing to Brother QL series printers
- **Docker Support**: Containerized deployment with Docker
- **Performance Optimized**: Efficient font sizing and text wrapping algorithms

## Quick Start

### Using Docker (Recommended)

1. **Pull the Docker image**:
   ```bash
   docker pull ghcr.io/micahfocht/brother_ql_todo:latest
   ```

2. **Run the container**:
   ```bash
   docker run -d -p 5000:5000 \
     -v $(pwd)/printer_settings.json:/app/printer_settings.json \
     ghcr.io/micahfocht/brother_ql_todo:latest
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:5000`

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

3. **Access the application**:
   Open your browser and go to `http://localhost:5000`

## Configuration

### Printer Settings

1. Navigate to `/settings` in the web interface
2. Enter your Brother QL printer's IP address
3. Select your printer model
4. Save the settings

### Environment Variables

- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port to run the application on (default: 5000)

## Docker Deployment

### Build Locally

```bash
# Build the image
docker build -t brother_ql_todo .

# Run the container
docker run -d -p 5000:5000 brother_ql_todo
```

### Using Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  label-printer:
    image: ghcr.io/micahfocht/brother_ql_todo:latest
    ports:
      - "5000:5000"
    volumes:
      - ./printer_settings.json:/app/printer_settings.json
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Then run:
```bash
docker-compose up -d
```

## API Endpoints

- `GET /` - Main label creation interface
- `POST /` - Generate label preview
- `GET /label.png` - Generate label image
- `POST /print` - Print label to configured printer
- `GET /settings` - Printer configuration interface
- `POST /settings` - Save printer settings

## Development

### Project Structure

```
.
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container definition
├── .dockerignore          # Docker build exclusions
├── .github/
│   └── workflows/
│       └── docker-build.yml    # GitHub Actions workflow
└── README.md              # This file
```

### Running Tests

```bash
# Run the application in development mode
python main.py

# The application will be available at http://localhost:5000
```

## Troubleshooting

### Common Issues

1. **Timeout errors**: The application has been optimized to handle titles containing "application" efficiently
2. **Printer connection issues**: Ensure your Brother QL printer is on the same network and accessible
3. **Font rendering issues**: The application includes system font dependencies in the Docker image

### Debug Mode

To enable debug logging, modify the Flask app initialization:

```python
app.run(debug=True)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please check the license file for details.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainers.