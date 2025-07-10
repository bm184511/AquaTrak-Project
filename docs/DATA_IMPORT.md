# Data Import System Documentation

## Overview

The AquaTrak Data Import System provides comprehensive capabilities for importing data from various sources and formats into the platform's database. This system supports multiple data types, formats, and import methods to ensure flexibility and compatibility with diverse data sources.

## Architecture

### Core Components

1. **BaseDataImporter**: Abstract base class defining the interface for all importers
2. **Specialized Importers**: Format-specific importers (CSV, JSON, API, Satellite, etc.)
3. **DataImportManager**: Orchestrates imports and manages import operations
4. **API Endpoints**: RESTful API for data import operations
5. **Validation & Transformation**: Data validation and format transformation

### Import Flow

```
Data Source → Validation → Transformation → Database Import → Result Reporting
```

## Supported Data Formats

### 1. CSV (Comma-Separated Values)

**Use Cases**: IoT sensor data, environmental measurements, water quality data

**Features**:
- Field mapping support
- Data type validation
- Coordinate validation
- Date range validation
- Custom delimiters
- Multiple encodings

**Example Configuration**:
```python
field_mapping = {
    'device_id': 'sensor_id',
    'timestamp': 'time',
    'consumption': 'water_usage'
}
```

### 2. JSON (JavaScript Object Notation)

**Use Cases**: API responses, configuration data, complex nested data

**Features**:
- Nested object support
- Array processing
- Schema validation
- Flexible structure handling

### 3. GeoJSON (Geographic JSON)

**Use Cases**: Geographic data, spatial analysis, mapping data

**Features**:
- Coordinate validation
- Geometry processing
- Spatial indexing
- CRS support

### 4. API Data

**Use Cases**: Real-time data, external services, weather data

**Features**:
- Authentication support
- Rate limiting
- Error handling
- Pagination support
- Multiple HTTP methods

**Example Configuration**:
```python
api_config = {
    'url': 'https://api.weather.com/data',
    'method': 'GET',
    'api_key': 'your_api_key',
    'header_name': 'Authorization',
    'params': {
        'location': 'New York',
        'units': 'metric'
    }
}
```

### 5. Satellite Data

**Use Cases**: Remote sensing, environmental monitoring, land use analysis

**Features**:
- Multiple satellite types (Sentinel, Landsat, MODIS)
- Band processing
- Index calculation (NDVI, NDWI, EVI, etc.)
- Cloud cover assessment
- Resolution handling

**Supported Formats**:
- GeoTIFF (.tif, .tiff)
- JPEG 2000 (.jp2)
- HDF (.hdf)
- NetCDF (.nc)

### 6. Sensor Data

**Use Cases**: IoT devices, real-time monitoring, equipment data

**Features**:
- Device identification
- Time series processing
- Quality metrics
- Status monitoring

### 7. Weather Data

**Use Cases**: Climate analysis, weather monitoring, forecasting

**Features**:
- Multiple weather parameters
- Temporal analysis
- Location-based data
- Forecast integration

### 8. GIS Data

**Use Cases**: Spatial analysis, mapping, geographic data

**Features**:
- Shapefile support
- Spatial indexing
- Coordinate transformation
- Attribute processing

## Module-Specific Importers

### IoT Water Consumption

**Data Structure**:
```python
{
    'device_id': 'string',
    'timestamp': 'datetime',
    'consumption': 'float',
    'flow_rate': 'float',
    'pressure': 'float',
    'temperature': 'float',
    'quality_metrics': {
        'ph': 'float',
        'turbidity': 'float',
        'conductivity': 'float',
        'dissolved_oxygen': 'float'
    },
    'location': {
        'lat': 'float',
        'lng': 'float'
    }
}
```

**Supported Formats**: CSV, JSON, API

### Environmental Health

**Data Structure**:
```python
{
    'location': {
        'lat': 'float',
        'lng': 'float',
        'address': 'string'
    },
    'timestamp': 'datetime',
    'air_quality': {
        'pm25': 'float',
        'pm10': 'float',
        'no2': 'float',
        'o3': 'float',
        'co': 'float',
        'so2': 'float',
        'aqi': 'float'
    },
    'water_quality': {
        'ph': 'float',
        'turbidity': 'float',
        'conductivity': 'float',
        'dissolved_oxygen': 'float',
        'temperature': 'float'
    },
    'soil_quality': {
        'ph': 'float',
        'organic_matter': 'float',
        'nitrogen': 'float',
        'phosphorus': 'float',
        'potassium': 'float',
        'heavy_metals': {
            'lead': 'float',
            'cadmium': 'float',
            'mercury': 'float',
            'arsenic': 'float',
            'chromium': 'float'
        }
    },
    'noise_levels': {
        'day_level': 'float',
        'night_level': 'float',
        'peak_level': 'float',
        'equivalent_level': 'float'
    },
    'environmental_indicators': {
        'biodiversity_index': 'float',
        'green_coverage': 'float',
        'air_pollution_index': 'float',
        'water_pollution_index': 'float',
        'soil_contamination_index': 'float',
        'overall_health_score': 'float'
    }
}
```

**Supported Formats**: CSV, JSON, GeoJSON, API

### Urban Green Space

**Data Structure**:
```python
{
    'location': {
        'lat': 'float',
        'lng': 'float',
        'area': 'float'
    },
    'green_space_type': 'string',
    'vegetation_data': {
        'tree_density': 'float',
        'canopy_cover': 'float',
        'species_diversity': 'float',
        'vegetation_health': 'float',
        'seasonal_changes': 'list'
    },
    'ecosystem_services': {
        'carbon_sequestration': 'float',
        'air_purification': 'float',
        'water_filtration': 'float',
        'temperature_regulation': 'float',
        'biodiversity_support': 'float',
        'recreational_value': 'float'
    },
    'accessibility': {
        'walking_distance': 'float',
        'public_transport': 'boolean',
        'parking_available': 'boolean',
        'wheelchair_accessible': 'boolean',
        'opening_hours': 'string',
        'visitor_capacity': 'integer'
    },
    'maintenance_status': {
        'overall_condition': 'string',
        'last_maintenance': 'datetime',
        'next_maintenance': 'datetime',
        'maintenance_needs': 'list',
        'budget_allocated': 'float'
    }
}
```

**Supported Formats**: CSV, JSON, GeoJSON, Satellite

### Urban Water Network

**Data Structure**:
```python
{
    'network_id': 'string',
    'location': {
        'lat': 'float',
        'lng': 'float'
    },
    'timestamp': 'datetime',
    'pressure': 'float',
    'flow_rate': 'float',
    'water_quality': {
        'ph': 'float',
        'turbidity': 'float',
        'conductivity': 'float',
        'dissolved_oxygen': 'float',
        'temperature': 'float'
    },
    'infrastructure_status': {
        'pipe_condition': 'string',
        'age_years': 'integer',
        'material': 'string',
        'diameter': 'float',
        'last_inspection': 'datetime',
        'maintenance_history': 'list'
    },
    'performance_metrics': {
        'efficiency_score': 'float',
        'reliability_index': 'float',
        'water_loss_percentage': 'float',
        'customer_satisfaction': 'float',
        'response_time_minutes': 'float'
    }
}
```

**Supported Formats**: CSV, JSON, GeoJSON, API

## API Usage

### Single Import

```bash
POST /api/data-import/single
Content-Type: application/json

{
    "type": "csv",
    "module_name": "iot_water_consumption",
    "data_source": "/path/to/data.csv",
    "options": {
        "encoding": "utf-8",
        "delimiter": ","
    },
    "field_mapping": {
        "device_id": "sensor_id",
        "timestamp": "time"
    }
}
```

### Batch Import

```bash
POST /api/data-import/batch
Content-Type: application/json

{
    "tasks": [
        {
            "type": "csv",
            "module_name": "iot_water_consumption",
            "data_source": "/path/to/iot_data.csv"
        },
        {
            "type": "api",
            "module_name": "weather_data",
            "data_source": "weather_api",
            "api_config": {
                "url": "https://api.weather.com/data",
                "api_key": "your_key"
            }
        }
    ],
    "parallel": true
}
```

### File Upload

```bash
POST /api/data-import/upload-csv
Content-Type: multipart/form-data

file: [CSV file]
module_name: iot_water_consumption
field_mapping: {"device_id": "sensor_id"}
```

## Python Usage

### Basic Import

```python
from data_importers.manager import DataImportManager

# Initialize manager
manager = DataImportManager()

# Import CSV data
result = manager.import_csv_data(
    module_name="iot_water_consumption",
    file_path="data/iot_data.csv",
    field_mapping={
        "device_id": "sensor_id",
        "timestamp": "time"
    }
)

print(f"Imported {result['imported_records']} records")
```

### API Import

```python
# Import from API
api_config = {
    'url': 'https://api.weather.com/data',
    'method': 'GET',
    'api_key': 'your_api_key',
    'header_name': 'Authorization'
}

result = manager.import_api_data(
    module_name="weather_data",
    api_config=api_config,
    date_from="2024-01-01",
    date_to="2024-01-31"
)
```

### Satellite Data Import

```python
# Import satellite data
result = manager.import_satellite_data(
    module_name="satellite_data",
    file_path="data/sentinel_image.tif",
    satellite_type="sentinel",
    processing_level="L2A"
)
```

### Batch Import

```python
# Define import tasks
import_tasks = [
    {
        'type': 'csv',
        'module_name': 'iot_water_consumption',
        'data_source': 'data/iot_data.csv'
    },
    {
        'type': 'api',
        'module_name': 'weather_data',
        'data_source': 'weather_api',
        'api_config': {
            'url': 'https://api.weather.com/data',
            'api_key': 'your_key'
        }
    }
]

# Execute batch import
results = manager.batch_import(import_tasks)
```

## Data Validation

### Field Validation

```python
# Required fields validation
required_fields = ['device_id', 'timestamp', 'consumption']
if not importer.validate_required_fields(record, required_fields):
    continue

# Data type validation
field_types = {
    'consumption': float,
    'temperature': float,
    'device_id': str
}
if not importer.validate_data_types(record, field_types):
    continue
```

### Coordinate Validation

```python
# Validate geographic coordinates
if not importer.validate_coordinates(record, 'lat', 'lng'):
    continue
```

### Date Range Validation

```python
# Validate date range
min_date = datetime(2020, 1, 1)
max_date = datetime(2024, 12, 31)
if not importer.validate_date_range(record, 'timestamp', min_date, max_date):
    continue
```

## Error Handling

### Import Errors

```python
try:
    result = manager.import_csv_data(module_name, file_path)
except DataImportError as e:
    print(f"Import failed: {e}")
    # Handle specific import errors
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle general errors
```

### Error Statistics

```python
# Get import statistics
stats = manager.get_import_stats()
print(f"Total imports: {stats['total_imports']}")
print(f"Successful: {stats['successful_imports']}")
print(f"Failed: {stats['failed_imports']}")

# Get import history
history = manager.get_import_history(module_name="iot_water_consumption", limit=10)
for record in history:
    print(f"{record['timestamp']}: {record['result']['imported_records']} records")
```

## Performance Optimization

### Parallel Processing

```python
# Configure parallel processing
manager.max_workers = 8  # Increase for better performance

# Batch import with parallel execution
results = manager.batch_import(import_tasks)
```

### Memory Management

```python
# Process large files in chunks
with CSVDataImporter(module_name, data_source) as importer:
    for chunk in pd.read_csv(file_path, chunksize=1000):
        importer.import_data(chunk)
```

## Monitoring and Logging

### Import Monitoring

```python
# Monitor import progress
import logging
logging.basicConfig(level=logging.INFO)

# Import with detailed logging
result = manager.import_csv_data(module_name, file_path)
print(f"Import completed: {result['success_rate']}% success rate")
```

### Health Checks

```python
# Check import system health
stats = manager.get_import_stats()
if stats['failed_imports'] > stats['successful_imports']:
    print("Warning: High failure rate detected")
```

## Best Practices

### 1. Data Preparation

- Clean and validate data before import
- Use consistent date formats
- Ensure coordinate accuracy
- Remove duplicate records

### 2. Error Handling

- Implement comprehensive error handling
- Log all import errors
- Provide meaningful error messages
- Retry failed imports when appropriate

### 3. Performance

- Use batch imports for large datasets
- Implement parallel processing
- Monitor memory usage
- Optimize database operations

### 4. Security

- Validate all input data
- Sanitize file uploads
- Implement access controls
- Log all import activities

### 5. Monitoring

- Track import success rates
- Monitor import performance
- Alert on import failures
- Maintain import history

## Troubleshooting

### Common Issues

1. **File Not Found**: Check file paths and permissions
2. **Invalid Format**: Verify file format and encoding
3. **Missing Fields**: Ensure required fields are present
4. **Data Type Errors**: Validate data types and formats
5. **Coordinate Errors**: Check coordinate ranges and formats

### Debug Mode

```python
# Enable debug logging
logging.getLogger('data_importers').setLevel(logging.DEBUG)

# Import with detailed error reporting
result = manager.import_csv_data(module_name, file_path)
if result['error_count'] > 0:
    print(f"Errors: {result['errors']}")
```

## Sample Data Generation

### Generate Sample Data

```python
# Create sample data for testing
result = manager.create_sample_data(
    module_name="iot_water_consumption",
    num_records=1000
)
```

### Sample Data Script

```bash
# Run sample data generation
python scripts/import_sample_data.py
```

This will generate and import sample data for all modules, providing a complete test dataset for development and testing.

## Conclusion

The AquaTrak Data Import System provides a comprehensive, flexible, and robust solution for importing data from various sources and formats. With support for multiple data types, validation, error handling, and monitoring, it ensures reliable and efficient data import operations for the platform. 